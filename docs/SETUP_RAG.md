# RAG System Setup Guide

This guide will walk you through setting up the Medical AI Chatbot with RAG (Retrieval-Augmented Generation).

## Prerequisites

- Python 3.8+
- PostgreSQL 14+ (with pgvector extension)
- 4GB+ RAM (for embedding models)
- LLM API key (DeepSeek, OpenAI, or Anthropic)

## Step-by-Step Setup

### 1. Install PostgreSQL with pgvector

#### Ubuntu/Debian:
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install pgvector
sudo apt-get install postgresql-14-pgvector

# Start PostgreSQL
sudo service postgresql start

# Check status
sudo service postgresql status
```

#### macOS:
```bash
# Install PostgreSQL
brew install postgresql@14

# Install pgvector
brew install pgvector

# Start PostgreSQL
brew services start postgresql@14
```

#### Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install pgvector from: https://github.com/pgvector/pgvector#installation
3. Start PostgreSQL service

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE mimic_iv;

# Connect to database
\c mimic_iv

# Enable pgvector extension
CREATE EXTENSION vector;

# Verify extension
SELECT * FROM pg_extension WHERE extname = 'vector';

# Exit
\q
```

### 3. Install Python Dependencies

```bash
# Navigate to project directory
cd /path/to/MediAI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r apps/requirements.txt

# Verify installation
python -c "import sentence_transformers; print('✓ sentence-transformers installed')"
python -c "import psycopg2; print('✓ psycopg2 installed')"
python -c "import pgvector; print('✓ pgvector installed')"
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required configurations:**

```bash
# Database URL
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mimic_iv

# LLM API Key (choose one)
# Option 1: DeepSeek (recommended for medical, cost-effective)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
LLM_PROVIDER=deepseek

# Option 2: OpenAI (high quality, more expensive)
# OPENAI_API_KEY=sk-your-openai-key-here
# LLM_PROVIDER=openai

# Option 3: Anthropic Claude (excellent for medical reasoning)
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
# LLM_PROVIDER=anthropic
```

**Optional configurations:**

```bash
# RAG System
RAG_EMBEDDING_PROVIDER=sentence-transformers  # Local, free
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=150
RAG_TOP_K=5

# Knowledge Base
KNOWLEDGE_BASE_DIR=./data/medical_knowledge
```

### 5. Get LLM API Keys

#### DeepSeek (Recommended)
1. Visit: https://platform.deepseek.com/
2. Sign up for account
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `.env` file

**Pricing**: ~$0.14 per 1M input tokens, $0.28 per 1M output tokens (very affordable)

#### OpenAI (Alternative)
1. Visit: https://platform.openai.com/
2. Sign up and add payment method
3. Go to API Keys section
4. Create new key
5. Copy to `.env` file

**Pricing**: ~$0.15 per 1M tokens (gpt-4o-mini) to $2.50 per 1M tokens (gpt-4)

#### Anthropic Claude (Alternative)
1. Visit: https://console.anthropic.com/
2. Sign up for account
3. Generate API key
4. Copy to `.env` file

**Pricing**: ~$3 per 1M input tokens, $15 per 1M output tokens (Claude Sonnet)

### 6. Initialize RAG System

```bash
# Run initialization script
python scripts/initialize_rag_system.py
```

This script will:
1. ✅ Create pgvector extension (if not exists)
2. ✅ Create vector storage tables
3. ✅ Generate sample medical knowledge base
4. ✅ Download embedding model (first run only)
5. ✅ Index sample documents
6. ✅ Test retrieval system
7. ✅ Test full RAG pipeline (if API key set)

**Expected Output:**
```
============================================================
Initializing Medical AI RAG System
============================================================

[1/5] Creating sample medical knowledge base...
✓ Created: data/medical_knowledge/sepsis_guidelines.md
✓ Created: data/medical_knowledge/mortality_risk_assessment.md
✓ Created: data/medical_knowledge/icu_medications.md

[2/5] Setting up vector store with pgvector...
✓ Vector store initialized successfully

[3/5] Initializing embedding service...
Downloading model: all-MiniLM-L6-v2 (first time only)
✓ Embedding service initialized (dimension: 384)

[4/5] Initializing RAG pipeline...
✓ RAG pipeline initialized

[5/5] Indexing medical knowledge base...
Found 3 documents to index
  ✓ Indexed: sepsis_guidelines.md (15 chunks)
  ✓ Indexed: mortality_risk_assessment.md (18 chunks)
  ✓ Indexed: icu_medications.md (22 chunks)

✓ Indexing complete: 55 total chunks indexed

============================================================
RAG System Statistics
============================================================
total_documents: 55
embedding_dimension: 384
llm_provider: deepseek
llm_model: deepseek-chat

by_category:
  guideline: 33
  general: 15
  drug: 7

============================================================
Testing RAG System
============================================================

Test Query: What are the criteria for diagnosing sepsis?

[Retrieval Test]
Retrieved 3 relevant documents:
  [1] Source: sepsis_guidelines.md (score: 0.892)
      Category: guideline
      Preview: # Sepsis Recognition and Management Guidelines

## Definition
Sepsis is a life-threatening organ dysfunction...

[Full RAG Test]
Answer:
Based on the Sepsis-3 consensus definitions, sepsis is diagnosed when...
[Full answer with citations]

Confidence: 0.87
Sources: 3

============================================================
Initialization Complete!
============================================================
```

### 7. Start the Application

```bash
# Start Streamlit application
cd apps
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### 8. Test the RAG Chatbot

1. **Log in** (use demo credentials or create account)
2. **Navigate to** "AI Assistant" page
3. **Verify RAG Status** in sidebar:
   - Should show "✅ Online"
   - Display document count
   - Show LLM provider

4. **Try sample queries**:
   - "What are the criteria for diagnosing sepsis?"
   - "Explain the SOFA score components"
   - "What is the recommended dosing for norepinephrine?"

5. **Check features**:
   - ✅ Source citations displayed
   - ✅ Confidence score shown
   - ✅ Evidence-based responses
   - ✅ Medical disclaimers included

## Troubleshooting

### Issue: pgvector extension not found

**Error**: `could not open extension control file "vector.control"`

**Solution**:
```bash
# Install pgvector
sudo apt-get install postgresql-14-pgvector

# Restart PostgreSQL
sudo service postgresql restart

# Verify
psql -U postgres -d mimic_iv -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: Database connection failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check PostgreSQL status
sudo service postgresql status

# Start if not running
sudo service postgresql start

# Check DATABASE_URL in .env
# Format: postgresql://username:password@host:port/database
```

### Issue: Import error for sentence_transformers

**Error**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution**:
```bash
# Install dependencies
pip install sentence-transformers==2.2.2

# If still fails, try:
pip install --upgrade sentence-transformers torch
```

### Issue: LLM API key invalid

**Error**: `Authentication failed` or `Invalid API key`

**Solution**:
1. Check API key is correctly copied to `.env`
2. Remove any quotes or extra spaces
3. Verify key is valid on provider's dashboard
4. Check LLM_PROVIDER matches your key

### Issue: Slow first query

**Observation**: First query takes 10-30 seconds

**Explanation**: This is normal! The embedding model downloads on first use (~80MB).

**Solution**: Subsequent queries will be fast. To pre-download:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Issue: Out of memory

**Error**: `RuntimeError: out of memory`

**Solution**:
1. Use smaller embedding model:
   ```bash
   RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2  # Smaller, 384-dim
   ```

2. Reduce batch size in code:
   ```python
   embeddings = embedding_service.embed_batch(texts, batch_size=16)
   ```

3. Reduce top_k:
   ```python
   result = rag.query(question, top_k=3)  # Instead of 5
   ```

## Adding Custom Medical Documents

### Method 1: Add Markdown/Text Files

```bash
# Create your document
echo "# Your Medical Guideline

## Content
Your medical content here...
" > data/medical_knowledge/custom_guideline.md

# Reindex
python scripts/initialize_rag_system.py
```

### Method 2: Programmatic Indexing

```python
from api.services.rag_pipeline import RAGPipeline

rag = RAGPipeline(llm_provider="deepseek")

# Index document
rag.index_document(
    text=your_document_text,
    source="custom_source",
    metadata={"category": "guideline", "author": "Dr. Smith"}
)
```

### Method 3: Load from PubMed

```python
from api.services.knowledge_loader import MedicalKnowledgeLoader

loader = MedicalKnowledgeLoader()

# Fetch PubMed abstracts
documents = loader.load_pubmed_abstracts(
    query="sepsis management ICU",
    max_results=10
)

# Index documents
for doc in documents:
    rag.index_document(
        text=doc['content'],
        source=doc['source'],
        metadata=doc['metadata']
    )
```

## Performance Optimization

### For Development (Fast, Good Quality)

```bash
# .env settings
RAG_EMBEDDING_PROVIDER=sentence-transformers
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2  # 384-dim, fast
RAG_TOP_K=3
LLM_PROVIDER=deepseek  # Cost-effective
```

### For Production (Best Quality)

```bash
# .env settings
RAG_EMBEDDING_PROVIDER=openai
RAG_EMBEDDING_MODEL=text-embedding-3-small  # 1536-dim
RAG_TOP_K=5
LLM_PROVIDER=openai  # or anthropic for best medical reasoning
```

## Next Steps

1. **Add More Documents**: Build comprehensive medical knowledge base
2. **Customize Prompts**: Adjust system prompts in `rag_pipeline.py`
3. **Tune Parameters**: Experiment with chunk_size, top_k, similarity thresholds
4. **Add Feedback**: Implement user feedback loop for continuous improvement
5. **Monitor Usage**: Track query patterns and response quality
6. **Integrate with Predictions**: Connect RAG explanations to sepsis/mortality models

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review logs: `tail -f logs/app.log`
3. Search GitHub issues
4. Create new issue with error details

## Security Notes

⚠️ **Important**:
- Never commit `.env` file with real API keys
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage and costs
- Implement rate limiting for production

## Costs Estimate

### Development/Testing (100 queries/day)
- DeepSeek: ~$0.10/month
- Embedding (local): Free
- PostgreSQL: Free (self-hosted)
- **Total**: ~$0.10/month

### Production (1000 queries/day)
- DeepSeek: ~$3/month
- OR OpenAI (GPT-4o-mini): ~$5/month
- OR Anthropic (Claude): ~$15/month
- PostgreSQL: Free (self-hosted) or $25/month (managed)
- **Total**: $3-40/month depending on provider

## Resources

- [RAG System Documentation](./RAG_SYSTEM.md)
- [API Documentation](./API.md)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [DeepSeek API](https://platform.deepseek.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
