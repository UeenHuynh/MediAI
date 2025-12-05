# MediAI Advanced Chatbot Implementation Plan
## 6-Layer Architecture với Agentic RAG System

**Branch:** `improve-chatbot`
**Ngày tạo:** 2025-12-04
**Tình trạng:** Planning Phase

---

## 📋 Tổng Quan

Triển khai hệ thống chatbot y tế tiên tiến với 6 layer architecture, tích hợp:
- **Agentic Orchestration** (LangGraph ReAct pattern)
- **Hybrid RAG** (Cache-Augmented Generation + Vector Search)
- **Multi-modal Input** (Text, Excel, Image, PDF)
- **PII Protection** (Regex + spaCy NER)
- **100% Free-tier Services** (Groq, HuggingFace, Qdrant, Supabase)

---

## 🎯 Gap Analysis - Hiện Tại vs Mục Tiêu

### ✅ Đã Có (Current Implementation)
1. **RAG cơ bản:**
   - Vector store với PostgreSQL + pgvector
   - Sentence-transformers embeddings (all-MiniLM-L6-v2)
   - Document chunking & retrieval
   - Safety guardrails

2. **LLM Integration:**
   - DeepSeek, OpenAI, Anthropic, Gemini support
   - Basic query-response pipeline
   - Citations & confidence scoring

3. **UI Components:**
   - Streamlit chatbot interface
   - Quick templates
   - Chat history export

### ❌ Cần Thêm (Gaps to Fill)

#### Layer 1: Multi-channel Input
- ❌ Excel file upload & parsing
- ❌ Image upload (X-rays, lab results) với Groq Vision
- ❌ PDF document processing với PyMuPDF
- ❌ Batch patient data processing

#### Layer 2: PII Masking
- ❌ Regex-based PII detection (email, phone, SSN)
- ❌ spaCy NER for name detection
- ❌ Token mapping storage (in-memory dict)
- ❌ De-anonymization for output

#### Layer 3: Agentic Orchestrator
- ❌ LangGraph state machine
- ❌ ReAct agent pattern
- ❌ Intent classification
- ❌ Multi-tool orchestration
- ❌ Self-validation loop
- ❌ PubMed API integration
- ❌ Calculator/Math tools

#### Layer 4: Hybrid RAG
- ❌ CAG (Cache-Augmented Generation) với Python dict
- ❌ Static medical knowledge cache
- ❌ Qdrant Cloud integration (thay thế PostgreSQL)
- ❌ Hybrid search strategy (CAG → Qdrant → PubMed)
- ❌ Query expansion

#### Layer 5: Data Layer Enhancement
- ❌ Supabase PostgreSQL migration
- ❌ Chat history persistence
- ❌ Model metrics tracking
- ❌ Local model storage optimization

#### Layer 6: LLM Layer Upgrade
- ❌ Groq API integration (primary)
- ❌ HuggingFace models (fallback - NOT Together.ai)
- ❌ Groq Vision for image analysis
- ❌ Rate limiting & fallback logic

---

## 🏗️ Architecture Chi Tiết

### Layer 1: Streamlit Interface (Free)
```
Channels:
├── Text Chat (✅ đã có)
├── Excel Upload (batch patient data)
│   └── pandas.read_excel() → DataFrame → Agent
├── Image Upload (X-rays, lab results)
│   └── st.file_uploader(type=['png','jpg']) → Groq Vision API
└── PDF Upload (medical reports)
    └── PyMuPDF (fitz) → text extraction → chunking
```

**Files cần tạo/sửa:**
- `apps/pages/chatbot_rag.py` - Thêm file uploaders
- `api/services/file_processors.py` - NEW: Excel, PDF, Image handlers

---

### Layer 2: PII Masking (Simple - No Presidio)
```python
PII Detection Pipeline:
1. Regex patterns:
   - Email: [\w\.-]+@[\w\.-]+\.\w+
   - Phone: \d{3}-\d{3}-\d{4}
   - SSN: \d{3}-\d{2}-\d{4}
2. spaCy NER:
   - Load en_core_web_sm
   - Extract PERSON entities
3. Token Mapping:
   - Store: {<PII_TOKEN_1>: "actual_value"}
   - Session-based in st.session_state
```

**Files cần tạo:**
- `api/services/pii_masker.py` - NEW: PII detection & masking
- Dependency: `spacy`, `en_core_web_sm` model

**Ví dụ:**
```python
Input:  "Patient John Doe, email john@example.com"
Masked: "Patient <PERSON_1>, email <EMAIL_1>"
Mapping: {"<PERSON_1>": "John Doe", "<EMAIL_1>": "john@example.com"}
```

---

### Layer 3: Agentic Orchestrator (LangGraph + Groq)

#### 3.1 LangGraph State Machine
```python
from langgraph.graph import StateGraph, END

class AgentState:
    query: str
    masked_query: str
    intent: str
    plan: List[str]
    tool_results: Dict
    answer: str
    validation_status: str
    retry_count: int

workflow = StateGraph(AgentState)
workflow.add_node("intent_classifier", classify_intent)
workflow.add_node("planner", plan_execution)
workflow.add_node("tool_executor", execute_tools)
workflow.add_node("synthesizer", synthesize_answer)
workflow.add_node("validator", validate_answer)

workflow.add_edge("intent_classifier", "planner")
workflow.add_edge("planner", "tool_executor")
workflow.add_edge("tool_executor", "synthesizer")
workflow.add_edge("synthesizer", "validator")
workflow.add_conditional_edges("validator", should_retry, {
    "retry": "synthesizer",
    "pass": END
})
```

#### 3.2 Available Tools
```python
tools = [
    # Database
    SupabasePatientLookup(),

    # ML Models
    LightGBMPredictor(model_type="sepsis"),
    LightGBMPredictor(model_type="mortality"),
    SHAPExplainer(),

    # RAG Components
    CAGCache(),
    QdrantVectorSearch(),

    # External APIs
    PubMedSearch(),  # NCBI E-utilities

    # Utilities
    Calculator(),
]
```

#### 3.3 ReAct Loop Example
```
User: "What's the sepsis risk for patient with WBC 18, lactate 4.2?"

[Intent Classifier]
→ Intent: "clinical_prediction"

[Planner]
→ Plan:
  1. Extract patient vitals from query
  2. Run LightGBM sepsis model
  3. Get SHAP explanation
  4. Search medical guidelines for context
  5. Synthesize clinical recommendation

[Tool Executor]
→ LightGBMPredictor: {"sepsis_risk": 0.78, "confidence": 0.85}
→ SHAPExplainer: {"top_features": ["lactate", "wbc", "temperature"]}
→ QdrantVectorSearch: [guideline_docs...]

[Synthesizer] (Groq Llama 3.1 70B)
→ Draft answer with citations

[Validator]
→ Check: medical accuracy, citation presence, disclaimer
→ Status: PASS → return to user
```

**Files cần tạo:**
- `api/agents/langgraph_orchestrator.py` - NEW: Main agent
- `api/agents/tools/` - NEW: Tool implementations
  - `database_tools.py`
  - `ml_tools.py`
  - `rag_tools.py`
  - `external_tools.py`
  - `utility_tools.py`

**Dependencies:**
```
langgraph>=0.0.20
langchain>=0.1.0
langchain-core>=0.1.0
groq>=0.4.0
```

---

### Layer 4: Hybrid RAG Engine

#### 4.1 CAG (Cache-Augmented Generation)
```python
# Static medical knowledge cache
MEDICAL_KNOWLEDGE_CACHE = {
    "sepsis_protocol": {
        "content": "Sepsis-3 definition: SOFA score ≥2...",
        "keywords": ["sepsis", "sofa", "qsofa", "infection"],
        "category": "protocol"
    },
    "sofa_score": {
        "content": "Sequential Organ Failure Assessment...",
        "keywords": ["sofa", "organ failure", "icu scoring"],
        "category": "scoring"
    },
    "aki_guidelines": {
        "content": "KDIGO AKI definition: SCr increase...",
        "keywords": ["aki", "kidney", "creatinine", "kdigo"],
        "category": "guideline"
    },
    # ... ~50 curated medical topics
}

def cag_lookup(query: str) -> Optional[Dict]:
    """Keyword-based cache lookup - ~50ms response"""
    query_lower = query.lower()
    for key, data in MEDICAL_KNOWLEDGE_CACHE.items():
        if any(keyword in query_lower for keyword in data["keywords"]):
            return data
    return None
```

#### 4.2 Qdrant Cloud Integration
**Thay thế PostgreSQL + pgvector bằng Qdrant Cloud (1GB free)**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore:
    def __init__(self):
        # Qdrant Cloud credentials
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = "medical_knowledge"

        # Create collection if not exists
        self._init_collection()

    def _init_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 dimension
                    distance=Distance.COSINE
                )
            )

    def add_documents(self, docs: List[Dict]):
        points = [
            PointStruct(
                id=idx,
                vector=doc["embedding"],
                payload={
                    "content": doc["content"],
                    "source": doc["source"],
                    "category": doc["category"]
                }
            )
            for idx, doc in enumerate(docs)
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_embedding: List[float], top_k: int = 5):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        return [
            {
                "content": hit.payload["content"],
                "source": hit.payload["source"],
                "category": hit.payload["category"],
                "score": hit.score
            }
            for hit in results
        ]
```

#### 4.3 Hybrid Search Strategy
```python
def hybrid_rag_query(query: str) -> List[Dict]:
    """
    3-tier search:
    1. CAG Cache (instant)
    2. Qdrant Vector Search (fast)
    3. PubMed API (fallback for latest research)
    """
    results = []

    # Tier 1: CAG cache
    cache_result = cag_lookup(query)
    if cache_result:
        results.append({
            "content": cache_result["content"],
            "source": "Internal Cache",
            "score": 1.0,
            "tier": "cag"
        })

    # Tier 2: Qdrant vector search
    embedding = embed_query(query)
    vector_results = qdrant_store.search(embedding, top_k=3)
    results.extend([{**r, "tier": "vector"} for r in vector_results])

    # Tier 3: PubMed (if medical terms detected)
    if has_medical_terms(query) and len(results) < 3:
        pubmed_results = search_pubmed(query, max_results=2)
        results.extend([{**r, "tier": "pubmed"} for r in pubmed_results])

    return results[:5]  # Top 5 overall
```

**Files cần tạo/sửa:**
- `api/core/cag_cache.py` - NEW: Static knowledge cache
- `api/core/qdrant_store.py` - NEW: Qdrant client
- `api/core/vector_store.py` - MODIFY: Add Qdrant adapter
- `api/services/hybrid_rag.py` - NEW: Hybrid search orchestrator

**Migration Steps:**
1. Keep PostgreSQL for patient data & predictions
2. Move document vectors to Qdrant Cloud
3. Initialize Qdrant with existing embeddings
4. Update RAG pipeline to use hybrid search

**Dependencies:**
```
qdrant-client>=1.7.0
```

**Environment Variables:**
```
QDRANT_URL=https://xyz.cloud.qdrant.io
QDRANT_API_KEY=your_api_key
```

---

### Layer 5: Data Layer (Supabase + Local)

#### 5.1 Supabase PostgreSQL Schema
```sql
-- Patient data (existing)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE,
    demographics JSONB,
    vitals JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Predictions (existing)
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50),
    model_type VARCHAR(20),
    risk_score FLOAT,
    shap_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- NEW: Chat history
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    query TEXT,
    response TEXT,
    citations JSONB,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- NEW: Model metrics
CREATE TABLE model_metrics (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(20),
    metric_name VARCHAR(50),
    metric_value FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### 5.2 Local Storage
```
/home/neeyuhuynh/Desktop/MediAI/
├── models/
│   ├── sepsis_model.pkl         # LightGBM sepsis
│   ├── mortality_model.pkl      # LightGBM mortality
│   └── shap_explainer.pkl       # SHAP explainer
├── cache/
│   └── huggingface/             # sentence-transformers cache
└── data/
    └── medical_knowledge/       # Seed documents for Qdrant
```

**Files cần sửa:**
- `api/core/config.py` - Add Supabase credentials
- `api/services/database.py` - Add chat_history methods

---

### Layer 6: LLM Layer (Groq + HuggingFace)

#### 6.1 Groq API (Primary)
```python
from groq import Groq

class GroqLLM:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-70b-versatile"
        self.vision_model = "llama-3.2-11b-vision-preview"

    def chat(self, messages: List[Dict], max_tokens: int = 800):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content

    def analyze_image(self, image_url: str, prompt: str):
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
        )
        return response.choices[0].message.content
```

**Groq Free Tier:**
- **30 requests/minute** (14,400/day)
- **Llama 3.1 70B**: ~500 tokens/sec
- **Vision API**: Free for Llama 3.2 11B Vision

#### 6.2 HuggingFace Fallback (LƯU Ý: KHÔNG dùng Together.ai)
```python
from transformers import pipeline

class HuggingFaceLLM:
    """Fallback khi Groq rate limit"""
    def __init__(self):
        # Load smaller model for local inference
        self.generator = pipeline(
            "text-generation",
            model="microsoft/phi-2",  # 2.7B params - chạy local
            device=-1  # CPU
        )

    def chat(self, prompt: str, max_tokens: int = 500):
        result = self.generator(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.3,
            do_sample=True
        )
        return result[0]["generated_text"]
```

**LƯU Ý QUAN TRỌNG:**
- ❌ **KHÔNG dùng Together.ai** (theo kiến trúc mới)
- ✅ **Dùng HuggingFace models** chạy local làm fallback
- Groq là primary, HuggingFace là backup khi rate limit

#### 6.3 Rate Limiting & Fallback Logic
```python
class LLMOrchestrator:
    def __init__(self):
        self.groq = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
        self.hf = HuggingFaceLLM()
        self.rate_limiter = RateLimiter(max_calls=30, period=60)

    def generate(self, messages: List[Dict]) -> str:
        try:
            if self.rate_limiter.can_proceed():
                return self.groq.chat(messages)
            else:
                logger.warning("Groq rate limit, using HuggingFace fallback")
                return self.hf.chat(messages[0]["content"])
        except Exception as e:
            logger.error(f"Groq error: {e}, using HuggingFace")
            return self.hf.chat(messages[0]["content"])
```

**Files cần tạo/sửa:**
- `api/services/llm_provider.py` - MODIFY: Add Groq + HuggingFace
- `api/services/rate_limiter.py` - NEW: Rate limiting logic

**Dependencies:**
```
groq>=0.4.0
transformers>=4.35.0
torch>=2.0.0  # For HuggingFace models
```

**Environment Variables:**
```
GROQ_API_KEY=your_groq_api_key
LLM_PRIMARY=groq
LLM_FALLBACK=huggingface
```

---

## 📦 Dependencies Tổng Hợp

### Cần Thêm (New)
```txt
# Agentic Orchestration
langgraph>=0.0.20
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.10

# LLM Providers
groq>=0.4.0
transformers>=4.35.0
torch>=2.0.0

# Vector Store
qdrant-client>=1.7.0

# PII Masking
spacy>=3.7.0
# Run: python -m spacy download en_core_web_sm

# Document Processing
PyMuPDF>=1.23.0  # fitz for PDF
openpyxl>=3.1.0  # Excel support
pillow>=10.0.0   # Image processing

# External APIs
biopython>=1.83  # PubMed E-utilities
```

### Đã Có (Existing)
```txt
streamlit==1.51.0
sentence-transformers==2.2.2
psycopg2-binary==2.9.9
lightgbm==4.3.0
pandas==2.2.0
numpy==1.26.3
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. **Setup Environment**
   - Install new dependencies
   - Setup Groq API key
   - Setup Qdrant Cloud account
   - Download spaCy model

2. **Layer 6: LLM Integration**
   - Implement Groq client
   - Add HuggingFace fallback
   - Test rate limiting
   - Update LLM provider in RAG pipeline

3. **Layer 2: PII Masking**
   - Implement regex patterns
   - Integrate spaCy NER
   - Create token mapping storage
   - Add de-anonymization

### Phase 2: RAG Enhancement (Week 2)
4. **Layer 4: CAG Cache**
   - Create static medical knowledge dict
   - Implement keyword matching
   - Add ~50 curated medical topics

5. **Layer 4: Qdrant Migration**
   - Setup Qdrant client
   - Migrate existing embeddings from PostgreSQL
   - Test vector search
   - Implement hybrid search strategy

6. **Layer 4: PubMed Integration**
   - Implement E-utilities wrapper
   - Add medical term detection
   - Integrate into hybrid RAG

### Phase 3: Agentic System (Week 3)
7. **Layer 3: Tool Development**
   - Implement all tool classes
   - Create tool registry
   - Test individual tools

8. **Layer 3: LangGraph Orchestrator**
   - Build state machine
   - Implement ReAct loop
   - Add intent classifier
   - Create validation node

### Phase 4: Multi-modal Input (Week 4)
9. **Layer 1: File Uploaders**
   - Excel upload & parsing
   - PDF upload & extraction
   - Image upload

10. **Layer 1: Groq Vision**
    - Integrate vision API
    - Add medical image analysis
    - Create image-to-text pipeline

### Phase 5: Data & Testing (Week 5)
11. **Layer 5: Supabase Enhancement**
    - Add chat_history table
    - Add model_metrics table
    - Update database service

12. **Integration Testing**
    - End-to-end workflow test
    - Performance benchmarking
    - Error handling validation

13. **UI Polish**
    - Update chatbot UI
    - Add file upload interfaces
    - Improve visual feedback

---

## 🔧 Migration Strategy

### Database Migration
1. **Keep PostgreSQL for:**
   - Patient data
   - Predictions
   - Chat history (new table)
   - Model metrics (new table)

2. **Move to Qdrant:**
   - Document embeddings
   - Vector search
   - Medical knowledge chunks

### Backward Compatibility
- Keep existing RAG pipeline as fallback
- Gradual rollout of new features
- Feature flags for testing

---

## 📊 Success Metrics

### Performance
- **Response Time:** <2s for 90% of queries
- **CAG Hit Rate:** >30% (instant responses)
- **Qdrant Search:** <500ms
- **Agent Planning:** <1s

### Quality
- **Citation Accuracy:** >95%
- **Medical Accuracy:** Validated by medical professionals
- **PII Protection:** 100% coverage

### Cost
- **Groq API:** Stay within free tier (30 req/min)
- **Qdrant:** Stay within 1GB free tier
- **Supabase:** Stay within 500MB free tier

---

## 🛡️ Safety & Compliance

### Medical Disclaimers
- All responses include clinical disclaimer
- Emergency detection with urgent referral
- No specific treatment recommendations without context

### PII Protection
- All PHI masked before LLM processing
- Audit logging for all PII access
- De-anonymization only when safe

### Rate Limiting
- Groq: 30 req/min
- PubMed: 3 req/sec (NCBI limit)
- Fallback to HuggingFace when needed

---

## 📝 Next Steps

1. **Review & Approve Plan** ✅
2. **Create branch:** `improve-chatbot` ✅
3. **Start Phase 1:** LLM Layer + PII Masking
4. **Weekly check-ins:** Track progress against roadmap

---

## 📞 Support

- **Documentation:** `/docs/CHATBOT_ARCHITECTURE.md`
- **Issues:** GitHub Issues on `improve-chatbot` branch
- **Testing:** `/scripts/test_chatbot_layers.py`

---

**Prepared by:** Claude Code
**Last Updated:** 2025-12-04
**Status:** Ready for Implementation
