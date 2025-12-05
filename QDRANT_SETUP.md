# Qdrant Vector Database Setup Guide

This guide explains how to set up and use Qdrant Cloud for the MediAI chatbot's vector search functionality.

## Overview

The MediAI chatbot uses **Qdrant Cloud** (free tier) for storing and retrieving medical knowledge embeddings. This enables semantic search over medical documents, guidelines, and research.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                 Hybrid RAG Pipeline                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tier 1: CAG Cache        ←  Keyword matching (~50ms)   │
│  Tier 2: Qdrant Vector    ←  Semantic search (~200ms)   │
│  Tier 3: PubMed API       ←  Latest research (~1-2s)    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Features

- **384-dimensional embeddings** using `all-MiniLM-L6-v2`
- **Cosine similarity** search
- **Metadata filtering** by category, source, etc.
- **Free tier**: 1GB storage, unlimited queries
- **Fast retrieval**: ~200ms average latency

---

## Setup Instructions

### 1. Create Qdrant Cloud Account

1. Go to https://cloud.qdrant.io/
2. Sign up with GitHub or email
3. Create a new cluster:
   - **Cluster name**: mediai-chatbot
   - **Region**: Choose closest to your location
   - **Tier**: Free (1GB storage)

### 2. Get API Credentials

After cluster is created:

1. Click on your cluster
2. Go to **API Keys** tab
3. Click **Generate API Key**
4. Copy the:
   - **Cluster URL**: `https://xyz-abc.cloud.qdrant.io`
   - **API Key**: `your-api-key-here`

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# Qdrant Configuration
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key-here
QDRANT_COLLECTION_NAME=medical_knowledge
```

**Security**: Never commit `.env` file to git!

### 4. Install Dependencies

```bash
pip install qdrant-client==1.7.0 sentence-transformers==2.2.2 biopython==1.83
```

Or use the full requirements:

```bash
pip install -r requirements.txt
```

### 5. Initialize Qdrant Collection

Run the initialization script:

```bash
python scripts/initialize_qdrant.py
```

This will:
- ✅ Connect to your Qdrant cluster
- ✅ Create the `medical_knowledge` collection
- ✅ Load documents from CAG cache
- ✅ Generate embeddings (384-dim)
- ✅ Upload to Qdrant
- ✅ Verify with test search

**Expected output:**

```
============================================================
Qdrant Vector Store Initialization
============================================================

✓ Qdrant URL: https://xyz.cloud.qdrant.io
✓ API Key: ********************abc12345

📦 Initializing components...
  ✓ CAG Cache loaded (12 documents)
  ✓ Embedding service loaded (model: all-MiniLM-L6-v2)
  ✓ Qdrant client connected

📝 Preparing documents...
  ✓ Prepared 12 documents

🔢 Generating embeddings...
  ✓ Generated 12 embeddings

☁️  Uploading to Qdrant...
  ✓ Uploaded 12 documents

✓ Verifying collection...
  ✓ Collection: medical_knowledge
  ✓ Points count: 12
  ✓ Vectors count: 12
  ✓ Status: green

🔍 Testing search...
  ✓ Query: 'What is sepsis?'
  ✓ Found 3 results:

  [1] Score: 0.892
      Category: disease
      Content: Sepsis is defined as life-threatening organ dysfunction...

============================================================
✅ Qdrant initialization complete!
============================================================
```

---

## Usage

### Using Hybrid RAG Pipeline

```python
from api.services.hybrid_rag import get_hybrid_rag

# Get RAG pipeline
rag = get_hybrid_rag()

# Search medical knowledge
results = rag.retrieve(
    query="What are the criteria for sepsis diagnosis?",
    top_k=5,
    use_cag=True,        # Enable CAG cache
    use_qdrant=True,     # Enable Qdrant vector search
    use_pubmed=False,    # Disable PubMed (slower)
    score_threshold=0.5  # Minimum similarity score
)

# Process results
for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Tier: {result['tier']}")  # cag, qdrant, or pubmed
    print()
```

### Direct Qdrant Access

```python
from api.core.qdrant_store import QdrantVectorStore
from api.services.embedding_service import EmbeddingService

# Initialize
qdrant = QdrantVectorStore()
embedder = EmbeddingService(provider="sentence-transformers")

# Generate query embedding
query = "acute kidney injury criteria"
query_embedding = embedder.embed(query)

# Search Qdrant
results = qdrant.search(
    query_embedding=query_embedding.tolist(),
    top_k=5,
    category_filter="guideline",  # Optional: filter by category
    score_threshold=0.6
)

# Process results
for result in results:
    print(f"{result['score']:.3f} - {result['content'][:100]}")
```

### Adding New Documents

```python
from api.core.qdrant_store import QdrantVectorStore
from api.services.embedding_service import EmbeddingService

qdrant = QdrantVectorStore()
embedder = EmbeddingService(provider="sentence-transformers")

# Prepare documents
documents = [
    {
        "content": "New medical guideline text...",
        "source": "CDC Guidelines 2024",
        "category": "guideline",
        "metadata": {"year": 2024, "author": "CDC"}
    }
]

# Generate embeddings
for doc in documents:
    embedding = embedder.embed(doc["content"])
    doc["embedding"] = embedding.tolist()

# Upload to Qdrant
count = qdrant.add_documents(documents)
print(f"Added {count} documents")
```

---

## Health Check

Check if Qdrant is accessible:

```python
from api.services.hybrid_rag import get_hybrid_rag

rag = get_hybrid_rag()
health = rag.health_check()

print(health)
```

**Expected output:**

```python
{
    "cag_cache": {
        "status": "healthy",
        "documents_count": 12
    },
    "qdrant": {
        "status": "healthy",
        "collection_info": {
            "name": "medical_knowledge",
            "points_count": 12,
            "vectors_count": 12,
            "status": "green"
        }
    },
    "embedding_service": {
        "status": "healthy",
        "provider": "sentence-transformers",
        "model": "all-MiniLM-L6-v2"
    }
}
```

---

## Troubleshooting

### Error: "Qdrant credentials not configured"

**Solution**: Set environment variables in `.env`:

```bash
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key
```

### Error: "Failed to connect to Qdrant"

**Possible causes:**

1. **Invalid API key**: Check credentials in Qdrant dashboard
2. **Wrong URL**: Ensure URL includes `https://` and cluster ID
3. **Network issue**: Check firewall/proxy settings
4. **Cluster sleeping**: Free tier clusters may sleep after inactivity

**Solution**: Verify credentials and try pinging the URL

### Error: "sentence-transformers not installed"

**Solution**: Install dependencies:

```bash
pip install sentence-transformers==2.2.2
```

### Empty search results

**Possible causes:**

1. **Collection not initialized**: Run `initialize_qdrant.py`
2. **Score threshold too high**: Lower `score_threshold` parameter
3. **Query mismatch**: Try broader medical terms

**Solution**: Check collection status and adjust search parameters

---

## Monitoring

### Check Collection Stats

```python
from api.core.qdrant_store import QdrantVectorStore

qdrant = QdrantVectorStore()
info = qdrant.get_collection_info()
print(info)
```

### Search Performance

Typical latencies:
- **CAG cache**: 10-50ms
- **Qdrant search**: 100-300ms
- **PubMed API**: 1000-2000ms

---

## Free Tier Limits

Qdrant Cloud Free Tier:
- **Storage**: 1GB (~250,000 documents with 384-dim vectors)
- **Queries**: Unlimited
- **Cluster uptime**: May sleep after inactivity
- **Collections**: Unlimited

**Current usage**: ~12 documents = 0.05MB (<1% of quota)

---

## Next Steps

1. ✅ Set up Qdrant Cloud account
2. ✅ Configure environment variables
3. ✅ Run initialization script
4. ✅ Test search functionality
5. ⏭️ Integrate with chatbot (Phase 2)
6. ⏭️ Add more medical documents
7. ⏭️ Implement PubMed integration

---

## Additional Resources

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **sentence-transformers**: https://www.sbert.net/
- **PubMed API**: https://www.ncbi.nlm.nih.gov/books/NBK25501/

---

## Support

For issues related to:
- **Qdrant setup**: Check Qdrant documentation or Discord
- **Integration code**: Create issue in MediAI repository
- **API keys**: Never share in public issues/commits
