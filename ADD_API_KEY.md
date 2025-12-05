# 🔑 Hướng dẫn thêm DeepSeek API Key

## ✅ Hiện tại: Retrieval-Only Mode

Hệ thống RAG đang chạy ở **chế độ retrieval-only**:
- ✅ Tìm kiếm tài liệu y khoa hoạt động
- ✅ Hiển thị các đoạn văn bản liên quan
- ⚠️ Chưa có AI tổng hợp câu trả lời

## 🚀 Để enable AI Generation (Full RAG):

### Bước 1: Lấy DeepSeek API Key

1. Truy cập: https://platform.deepseek.com/
2. Đăng ký tài khoản (miễn phí)
3. Vào **API Keys** section
4. Tạo key mới
5. Copy key (dạng: `sk-...`)

**Chi phí**: ~$0.14 per 1M tokens (rất rẻ, khoảng $0.10/tháng cho test)

### Bước 2: Thêm vào file .env

```bash
# Mở file .env
nano /home/neeyuhuynh/Desktop/MediAI/.env

# Thêm dòng này (thay your_key_here bằng key thật):
DEEPSEEK_API_KEY=sk-your-actual-key-here

# Và thêm:
LLM_PROVIDER=deepseek

# Save và thoát (Ctrl+X, Y, Enter)
```

### Bước 3: Restart Streamlit

```bash
# Kill process hiện tại
pkill -f streamlit

# Restart
cd /home/neeyuhuynh/Desktop/MediAI/apps
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

Hoặc đơn giản chỉ cần refresh trang web!

### Bước 4: Test

1. Mở http://localhost:8501
2. Vào trang **AI Assistant**
3. Hỏi: "What are the criteria for diagnosing sepsis?"
4. Bạn sẽ thấy:
   - ✅ AI-generated answer (thay vì raw documents)
   - ✅ Citations với sources
   - ✅ Confidence score

---

## 🔄 Alternative: Sử dụng OpenAI

Nếu bạn muốn dùng OpenAI thay vì DeepSeek:

```bash
# Trong .env:
OPENAI_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
```

**Chi phí OpenAI**: ~$0.15-2.50 per 1M tokens (đắt hơn DeepSeek)

---

## ✨ So sánh Retrieval-Only vs Full RAG

### Retrieval-Only (Hiện tại - Không cần API key)
```
User: "What is sepsis?"
System:
📚 Retrieved Documents:
[1] sepsis_guidelines.md (Score: 0.85)
# Sepsis Recognition...
[raw text from document]
```

### Full RAG (Với API key)
```
User: "What is sepsis?"
System:
Sepsis is a life-threatening condition caused by the body's
extreme response to infection. According to Sepsis-3 guidelines,
it is defined as organ dysfunction due to dysregulated host
response to infection.

Key diagnostic criteria include:
- qSOFA ≥ 2 points
- SOFA score increase ≥ 2
- Evidence of infection

📚 Sources:
[1] sepsis_guidelines.md
[2] mortality_risk_assessment.md

Confidence: 87%
```

---

## 🧪 Test Commands

### Check if API key is loaded:
```bash
cd /home/neeyuhuynh/Desktop/MediAI
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', 'FOUND' if os.getenv('DEEPSEEK_API_KEY') else 'NOT FOUND')"
```

### Test RAG with API key:
```bash
python scripts/initialize_rag_system.py
```

Should see:
```
✓ RAG pipeline initialized
✓ LLM provider: deepseek
✓ LLM model: deepseek-chat
```

---

## ❓ Troubleshooting

### Issue: "API key not found"
**Fix**:
```bash
# Check .env file exists:
ls -la /home/neeyuhuynh/Desktop/MediAI/.env

# Check content:
grep DEEPSEEK /home/neeyuhuynh/Desktop/MediAI/.env

# Make sure no quotes around key:
DEEPSEEK_API_KEY=sk-abc123  # ✓ CORRECT
DEEPSEEK_API_KEY="sk-abc123"  # ✗ WRONG (remove quotes)
```

### Issue: "Authentication failed"
**Fix**: Key có thể không đúng hoặc hết hạn
- Tạo key mới trên DeepSeek platform
- Copy lại key
- Update .env
- Restart app

### Issue: System vẫn ở retrieval-only mode
**Fix**:
```bash
# Clear Streamlit cache
rm -rf /home/neeyuhuynh/Desktop/MediAI/apps/.streamlit/cache

# Restart
pkill -f streamlit
cd /home/neeyuhuynh/Desktop/MediAI/apps
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 📊 Expected Behavior

### Before API Key:
- Status: "⚠️ Retrieval-Only Mode"
- LLM Provider: "None (Retrieval-Only)"
- Responses: Raw document excerpts

### After API Key:
- Status: "✅ Full RAG Mode"
- LLM Provider: "DEEPSEEK"
- Responses: AI-generated with citations

---

## 💰 Cost Estimate

### DeepSeek (Recommended)
- Input: $0.14 per 1M tokens
- Output: $0.28 per 1M tokens
- **100 queries/day**: ~$0.10/month
- **1000 queries/day**: ~$3/month

### OpenAI GPT-4o-mini
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- **100 queries/day**: ~$0.50/month
- **1000 queries/day**: ~$15/month

---

## 🎯 Ready to Add API Key?

**Tôi sẵn sàng nhận DeepSeek API key của bạn!**

Khi bạn có key, chỉ cần:
1. Gửi cho tôi: `DEEPSEEK_API_KEY=sk-...`
2. Tôi sẽ add vào .env
3. Restart app
4. Test ngay!

Hoặc bạn có thể tự add theo hướng dẫn trên ⬆️

---

**Current Status**: ✅ System ready, waiting for API key to enable full RAG
