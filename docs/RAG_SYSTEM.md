# Medical AI Chatbot - RAG System Documentation

## Overview

The Medical AI Chatbot uses **RAG (Retrieval-Augmented Generation)** to provide evidence-based medical guidance for ICU clinical decision support.

### What is RAG?

RAG combines:
1. **Retrieval**: Semantic search through medical knowledge base
2. **Augmentation**: Context-aware information synthesis
3. **Generation**: LLM-powered response generation with citations

## Architecture

```
User Query
    ↓
Safety Guardrails (Emergency Detection)
    ↓
Query Processing & Expansion
    ↓
Hybrid Search (Semantic + Keyword)
    ↓
Document Retrieval (Top-K)
    ↓
Context Construction
    ↓
LLM Generation (DeepSeek/OpenAI/Claude)
    ↓
Safety Validation & Disclaimers
    ↓
Response with Citations
```

## Components

### 1. Vector Store (`api/core/vector_store.py`)
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: 1536-dimensional vectors (OpenAI) or 384-dimensional (sentence-transformers)
- **Indexing**: IVFFlat index for fast cosine similarity search
- **Features**:
  - Semantic search
  - Hybrid search (semantic + full-text)
  - Category filtering
  - Metadata storage (JSONB)

### 2. Document Processor (`api/services/document_processor.py`)
- **Chunking Strategy**:
  - Target size: 800 characters
  - Overlap: 150 characters
  - Preserves medical sections and entities
- **Features**:
  - Section-aware splitting (headers, protocols)
  - Medical entity preservation (dosages, ICD codes, SNOMED)
  - Automatic categorization (drug, disease, guideline, protocol)

### 3. Embedding Service (`api/services/embedding_service.py`)
- **Providers**:
  - `sentence-transformers` (local, free, fast)
  - `openai` (cloud, high quality)
  - `deepseek` (planned)
- **Medical Enhancements**:
  - Query expansion with medical synonyms
  - Layman-to-medical term mapping
  - Multi-query fusion

### 4. RAG Pipeline (`api/services/rag_pipeline.py`)
- **LLM Providers**:
  - **DeepSeek** (recommended for medical)
  - OpenAI GPT-4
  - Anthropic Claude
- **Features**:
  - End-to-end query processing
  - Citation tracking
  - Confidence scoring
  - Context-aware generation

### 5. Safety Guardrails (`api/services/safety_guardrails.py`)
- **Emergency Detection**:
  - Keyword matching (chest pain, difficulty breathing, etc.)
  - Critical vital signs (HR < 40 or > 150, SpO2 < 85, etc.)
  - Automatic 911 alert
- **Inappropriate Query Filtering**:
  - Harmful content detection
  - Illegal activity prevention
- **Response Validation**:
  - Checks for definitive medical advice without qualifiers
  - Ensures proper disclaimers
  - Validates emergency warnings

### 6. Knowledge Loader (`api/services/knowledge_loader.py`)
- **Supported Formats**:
  - Markdown (.md)
  - Text (.txt)
  - JSON (.json)
- **Data Sources**:
  - Local files
  - PubMed abstracts (via Biopython)
  - Custom medical documents
  - WHO/CDC guidelines

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r apps/requirements.txt

# Install PostgreSQL and pgvector
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-14-pgvector

# macOS:
brew install postgresql
brew install pgvector
```

### 2. Configure Database

```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
psql -U postgres -c "CREATE DATABASE mimic_iv;"

# pgvector will be automatically enabled by the system
```

### 3. Set Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/mimic_iv

# LLM API Key (choose one)
DEEPSEEK_API_KEY=sk-xxxxx  # Recommended
# OPENAI_API_KEY=sk-xxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxx

# LLM Provider
LLM_PROVIDER=deepseek
```

### 4. Initialize RAG System

```bash
# Run initialization script
python scripts/initialize_rag_system.py
```

This will:
- ✅ Create pgvector extension
- ✅ Create vector storage tables
- ✅ Generate sample medical knowledge base
- ✅ Index documents
- ✅ Test retrieval and generation

### 5. Start Application

```bash
# Start Streamlit app
cd apps
streamlit run streamlit_app.py
```

## Usage

### Basic Query

```python
from api.services.rag_pipeline import RAGPipeline

rag = RAGPipeline(llm_provider="deepseek")

result = rag.query(
    question="What are the criteria for diagnosing sepsis?",
    top_k=5
)

print(result['answer'])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {len(result['citations'])}")
```

### Adding Documents

```python
from api.services.knowledge_loader import MedicalKnowledgeLoader

loader = MedicalKnowledgeLoader()

# Load from file
documents = loader.load_text_file("./data/medical_knowledge/guideline.md")

# Index document
rag.index_document(
    text=documents['content'],
    source=documents['source'],
    metadata=documents['metadata']
)
```

### Retrieval Only

```python
# Retrieve relevant documents without generation
docs = rag.retrieve(
    query="sepsis management",
    top_k=5,
    category="guideline",  # Filter by category
    use_hybrid=True        # Use hybrid search
)

for doc in docs:
    print(f"Source: {doc['source']}")
    print(f"Score: {doc['hybrid_score']:.3f}")
    print(f"Content: {doc['content'][:200]}...")
```

## Knowledge Base Structure

```
data/medical_knowledge/
├── sepsis_guidelines.md        # Sepsis recognition & management
├── mortality_risk_assessment.md # ICU mortality risk factors
├── icu_medications.md          # Common ICU drug reference
├── procedures/
│   ├── central_line.md
│   └── intubation.md
├── diseases/
│   ├── ards.md
│   └── aki.md
└── drugs/
    ├── vasopressors.md
    └── antibiotics.md
```

### Document Categories

- **drug**: Medication information (dosing, indications, adverse effects)
- **disease**: Disease information (diagnosis, pathophysiology, treatment)
- **guideline**: Clinical practice guidelines
- **protocol**: Step-by-step protocols
- **general**: General medical information

## Performance Tuning

### Embedding Model Selection

| Model | Dimension | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | Development, testing |
| all-mpnet-base-v2 | 768 | Medium | Better | Production (local) |
| text-embedding-3-small | 1536 | API | Best | Production (cloud) |

### Chunk Size Optimization

```python
# Smaller chunks (500-600): Better precision, more chunks
# Medium chunks (800-1000): Balanced (recommended)
# Larger chunks (1200-1500): Better context, fewer chunks

processor = MedicalDocumentProcessor(
    chunk_size=800,
    chunk_overlap=150
)
```

### Search Strategy

```python
# Pure semantic search (fast, good for general queries)
docs = rag.retrieve(query, use_hybrid=False)

# Hybrid search (better accuracy, recommended)
docs = rag.retrieve(query, use_hybrid=True)

# Adjust semantic vs keyword weight
vector_store.hybrid_search(
    query_embedding=embedding,
    query_text=text,
    semantic_weight=0.7  # 70% semantic, 30% keyword
)
```

## Safety Features

### Emergency Detection

```python
from api.services.safety_guardrails import SafetyGuardrails

safety = SafetyGuardrails()

query_safety = safety.process_query("Patient has chest pain and can't breathe")

if query_safety['is_emergency']:
    print(query_safety['special_response'])  # Shows 911 alert
```

### Response Validation

```python
response = rag.query("What should I do for sepsis?")

# Response automatically includes:
# - Medical disclaimer
# - Source citations
# - Confidence score
# - Emergency warnings (if applicable)
```

## API Integration

### REST API Endpoint (Planned)

```python
# api/routers/rag.py
@router.post("/rag/query")
async def query_rag(
    question: str,
    top_k: int = 5,
    category: Optional[str] = None
):
    result = rag_pipeline.query(question, top_k, category)
    return result
```

## Monitoring & Evaluation

### Metrics

```python
stats = rag.get_stats()

print(f"Total documents: {stats['total_documents']}")
print(f"By category: {stats['by_category']}")
print(f"Embedding dimension: {stats['embedding_dimension']}")
print(f"LLM provider: {stats['llm_provider']}")
```

### Query Performance

```python
import time

start = time.time()
result = rag.query("What is sepsis?")
latency = time.time() - start

print(f"Latency: {latency:.2f}s")
print(f"Retrieved docs: {result['num_sources']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Troubleshooting

### pgvector not found

```bash
# Install pgvector extension
# PostgreSQL 14+
sudo apt-get install postgresql-14-pgvector

# Then connect and enable
psql -U postgres -d mimic_iv -c "CREATE EXTENSION vector;"
```

### Slow retrieval

- **Solution 1**: Reduce `top_k` (from 10 to 5)
- **Solution 2**: Add index: `CREATE INDEX ON medical_documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`
- **Solution 3**: Use category filtering

### Low quality answers

- **Solution 1**: Add more relevant documents to knowledge base
- **Solution 2**: Use better embedding model (OpenAI embeddings)
- **Solution 3**: Increase `top_k` to retrieve more context
- **Solution 4**: Use query expansion

### LLM API errors

```python
# Set fallback mode
try:
    result = rag.query(question)
except Exception as e:
    # Fallback: Return retrieved documents without generation
    docs = rag.retrieve(question, top_k=5)
    # Show documents to user
```

## Future Enhancements

1. **Multi-query Fusion**: Combine results from multiple query variations
2. **Reranking**: Use cross-encoder to rerank retrieved documents
3. **Streaming**: Stream LLM responses for better UX
4. **Feedback Loop**: Learn from user feedback to improve retrieval
5. **Integration with Predictions**: Link RAG responses with sepsis/mortality predictions
6. **Medical NER**: Extract and highlight medical entities in responses
7. **Multilingual Support**: Vietnamese medical terminology

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [DeepSeek API](https://platform.deepseek.com/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/mediai/issues
- Documentation: /docs/
- Email: support@mediai.com
