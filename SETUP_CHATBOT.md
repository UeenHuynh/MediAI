# 🚀 MediAI Advanced Chatbot - Setup Guide

## 📋 Checklist Trước Khi Bắt Đầu

### 1️⃣ Đăng Ký API Keys & Services (MIỄN PHÍ)

#### **Groq API** (BẮT BUỘC - Primary LLM)
- [ ] Truy cập: https://console.groq.com/
- [ ] Đăng ký tài khoản (GitHub/Google)
- [ ] Tạo API Key: API Keys → Create API Key
- [ ] Copy key vào `.env` → `GROQ_API_KEY`
- **Free Tier:** 30 requests/minute, 14,400/day

#### **Qdrant Cloud** (BẮT BUỘC - Vector Database)
- [ ] Truy cập: https://cloud.qdrant.io/
- [ ] Đăng ký tài khoản
- [ ] Tạo Cluster: Clusters → Create → Free Tier (1GB)
- [ ] Đợi cluster khởi động (~2 phút)
- [ ] Copy Cluster URL: `https://xxxxx.cloud.qdrant.io`
- [ ] Tạo API Key: Data Access Control → Create API Key
- [ ] Copy vào `.env`:
  - `QDRANT_URL=https://xxxxx.cloud.qdrant.io`
  - `QDRANT_API_KEY=your_key`

#### **Supabase** (BẮT BUỘC - PostgreSQL Database)
- [ ] Truy cập: https://supabase.com/
- [ ] Đăng ký tài khoản
- [ ] Tạo Project mới: New Project → MediAI
- [ ] Chọn region gần nhất, đặt password mạnh
- [ ] Đợi project khởi động (~2 phút)
- [ ] Copy credentials từ Project Settings → API:
  - `SUPABASE_URL` (Project URL)
  - `SUPABASE_KEY` (anon/public key)
- [ ] Copy Database URL từ Project Settings → Database → Connection String → URI
  - Thay `[YOUR-PASSWORD]` bằng password bạn đã đặt
  - `SUPABASE_DB_URL=postgresql://...`

#### **NCBI E-utilities** (TÙY CHỌN - PubMed API)
- [ ] Truy cập: https://www.ncbi.nlm.nih.gov/account/
- [ ] Đăng ký tài khoản NCBI
- [ ] Settings → API Key Management → Create API Key
- [ ] Copy vào `.env`: `NCBI_API_KEY` và `NCBI_EMAIL`
- **Không bắt buộc:** Có thể dùng PubMed mà không cần key (rate limit thấp hơn)

#### **HuggingFace** (TÙY CHỌN - Model Downloads)
- [ ] Truy cập: https://huggingface.co/settings/tokens
- [ ] Tạo Access Token (Read)
- [ ] Copy vào `.env`: `HUGGINGFACE_TOKEN`
- **Không bắt buộc:** Chỉ cần nếu muốn tăng tốc download models

---

## 🔧 Installation Steps

### Step 1: Cập Nhật .env File

```bash
# Copy template vào .env chính
cat .env.chatbot >> .env

# Hoặc edit thủ công
nano .env
```

**Điền các giá trị:**
- `GROQ_API_KEY=` → Paste Groq API key
- `QDRANT_URL=` → Paste Qdrant cluster URL
- `QDRANT_API_KEY=` → Paste Qdrant API key
- `SUPABASE_URL=` → Paste Supabase project URL
- `SUPABASE_KEY=` → Paste Supabase anon key
- `SUPABASE_DB_URL=` → Paste Supabase database URI

### Step 2: Install Dependencies

```bash
# Chạy script cài đặt
chmod +x scripts/install_chatbot_deps.sh
./scripts/install_chatbot_deps.sh

# Hoặc cài thủ công:
pip install -r requirements.chatbot.txt

# Download spaCy model cho PII masking
python -m spacy download en_core_web_sm
```

### Step 3: Initialize Database & Vector Store

```bash
# Tạo tables trong Supabase
python scripts/init_chatbot_database.py

# Initialize Qdrant collection
python scripts/init_qdrant_store.py

# Load seed medical knowledge
python scripts/seed_medical_knowledge.py
```

### Step 4: Test Components

```bash
# Test Groq API
python scripts/test_groq_api.py

# Test Qdrant connection
python scripts/test_qdrant.py

# Test PII masking
python scripts/test_pii_masker.py

# Test toàn bộ chatbot
python scripts/test_chatbot_integration.py
```

### Step 5: Run Application

```bash
# Khởi động Streamlit app
cd apps
streamlit run streamlit_app.py --server.port=8501
```

Truy cập: http://localhost:8501

---

## 📁 File Structure (Sau Khi Setup)

```
MediAI/
├── .env                          # ← ĐIỀN API KEYS VÀO ĐÂY
├── .env.chatbot                  # ← Template
├── SETUP_CHATBOT.md             # ← Guide này
│
├── api/
│   ├── core/
│   │   ├── cag_cache.py         # NEW - Static medical cache
│   │   ├── qdrant_store.py      # NEW - Qdrant client
│   │   └── config.py            # UPDATED - New configs
│   │
│   ├── services/
│   │   ├── llm_provider.py      # NEW - Groq + HuggingFace
│   │   ├── pii_masker.py        # NEW - PII detection
│   │   ├── file_processors.py   # NEW - Excel/PDF/Image
│   │   └── hybrid_rag.py        # NEW - Hybrid search
│   │
│   └── agents/
│       ├── langgraph_orchestrator.py  # NEW - Main agent
│       └── tools/               # NEW - Tool implementations
│
├── scripts/
│   ├── install_chatbot_deps.sh  # NEW - Dependency installer
│   ├── init_chatbot_database.py # NEW - DB setup
│   ├── init_qdrant_store.py     # NEW - Qdrant setup
│   ├── seed_medical_knowledge.py # NEW - Load seed data
│   ├── test_groq_api.py         # NEW - Test Groq
│   ├── test_qdrant.py           # NEW - Test Qdrant
│   ├── test_pii_masker.py       # NEW - Test PII
│   └── test_chatbot_integration.py # NEW - E2E test
│
├── requirements.chatbot.txt      # NEW - New dependencies
│
└── apps/
    └── pages/
        └── chatbot_rag.py       # UPDATED - Enhanced chatbot
```

---

## ✅ Verification Checklist

### Phase 1: Foundation
- [ ] Groq API key working (test với `test_groq_api.py`)
- [ ] Qdrant cluster connected (test với `test_qdrant.py`)
- [ ] Supabase tables created (check Supabase dashboard)
- [ ] spaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] PII masking functional (test với `test_pii_masker.py`)
- [ ] HuggingFace fallback working (optional)

### Phase 2: RAG Enhancement
- [ ] CAG cache loaded với 50+ medical topics
- [ ] Qdrant collection populated với embeddings
- [ ] Hybrid search working (CAG → Qdrant → PubMed)
- [ ] PubMed API integrated (optional)

### Phase 3: Agentic System
- [ ] LangGraph orchestrator functional
- [ ] All tools registered và tested
- [ ] ReAct loop executing correctly
- [ ] Validation node working

### Phase 4: Multi-modal
- [ ] Excel upload parsing patient data
- [ ] PDF extraction working
- [ ] Image upload với Groq Vision
- [ ] File processors integrated vào UI

### Phase 5: Integration
- [ ] End-to-end chatbot flow working
- [ ] Performance benchmarks met (<2s response)
- [ ] Error handling validated
- [ ] UI polished

---

## 🐛 Troubleshooting

### Groq API Error: "Invalid API Key"
```bash
# Kiểm tra key trong .env
grep GROQ_API_KEY .env

# Test key trực tiếp
python scripts/test_groq_api.py
```

### Qdrant Connection Error
```bash
# Verify URL format (phải có https://)
echo $QDRANT_URL

# Check API key
echo $QDRANT_API_KEY

# Test connection
python scripts/test_qdrant.py
```

### spaCy Model Not Found
```bash
# Download lại
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

### Supabase Database Error
```bash
# Check database URL format
echo $SUPABASE_DB_URL

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('$SUPABASE_DB_URL'); print(engine.connect())"
```

### Rate Limit Errors (Groq)
- Groq free tier: 30 requests/minute
- Nếu vượt → Fallback tự động sang HuggingFace
- Check logs: `tail -f logs/chatbot.log`

---

## 📚 Resources

### API Documentation
- **Groq:** https://console.groq.com/docs
- **Qdrant:** https://qdrant.tech/documentation/
- **Supabase:** https://supabase.com/docs
- **PubMed E-utilities:** https://www.ncbi.nlm.nih.gov/books/NBK25501/

### Model Information
- **Groq Llama 3.1 70B:** https://groq.com/
- **Groq Vision (Llama 3.2 11B):** https://console.groq.com/docs/vision
- **HuggingFace Phi-2:** https://huggingface.co/microsoft/phi-2
- **Sentence Transformers:** https://www.sbert.net/

### LangGraph
- **Documentation:** https://langchain-ai.github.io/langgraph/
- **Examples:** https://github.com/langchain-ai/langgraph/tree/main/examples

---

## 🎯 Next Steps After Setup

1. **Verify All Tests Pass:**
   ```bash
   ./scripts/run_all_tests.sh
   ```

2. **Seed Medical Knowledge:**
   ```bash
   python scripts/seed_medical_knowledge.py
   ```

3. **Start Chatbot:**
   ```bash
   streamlit run apps/streamlit_app.py
   ```

4. **Try Example Queries:**
   - "What are the sepsis-3 criteria?"
   - "Explain SOFA score calculation"
   - "Acute kidney injury KDIGO guidelines"

---

## 💡 Tips

- **Groq rate limit:** Nếu develop nhiều, consider thêm delay giữa các request
- **Qdrant free tier:** 1GB = ~2-3 triệu vectors (384-dim), đủ cho medical knowledge base
- **Supabase free tier:** 500MB database, 2GB bandwidth/month
- **Local HuggingFace models:** Phi-2 (2.7B) chạy được trên CPU, nhưng chậm hơn Groq

---

**Prepared by:** Claude Code
**Last Updated:** 2025-12-04
**Support:** GitHub Issues on `improve-chatbot` branch
