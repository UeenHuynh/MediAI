# 🚀 RENDER.COM DEPLOYMENT - STEP BY STEP

**Time:** 15-20 phút
**Date:** January 3, 2026

---

## ✅ STEP 1: TẠO WEB SERVICE (Trên Render.com Dashboard)

### 1.1 Create New Service
```
1. Vào Render.com Dashboard
2. Click "New +" (góc trên phải)
3. Chọn "Web Service"
```

### 1.2 Connect Repository
```
4. Chọn repository: "MediAI" 
   (Nếu không thấy → "Configure GitHub App" → cho phép access)

5. Click "Connect" bên cạnh MediAI repo
```

---

## ✅ STEP 2: CẤU HÌNH SERVICE

### 2.1 Basic Settings

**Name:**
```
mediai-api
```

**Region:**
```
Oregon (US West) - FREE tier
```

**Branch:**
```
main
```

**Root Directory:**
```
api
```
⚠️ QUAN TRỌNG: Phải điền "api" vì Dockerfile ở trong folder api/

### 2.2 Build Settings

**Runtime:**
```
Docker
```

**Dockerfile Path:**
```
Dockerfile
```
(Đường dẫn relative từ root directory "api" → api/Dockerfile)

### 2.3 Instance Settings

**Instance Type:**
```
Free
```
⚠️ Lưu ý: Free tier có cold start 30s sau 15 phút không dùng

---

## ✅ STEP 3: ENVIRONMENT VARIABLES

Click **"Advanced"** → Scroll xuống **"Environment Variables"**

Copy-paste từng cặp key-value sau:

### 3.1 Essential Variables

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Models V2
MODEL_PATH=/app/models
SEPSIS_MODEL_FILE=sepsis_lightgbm_v2.pkl
SEPSIS_FEATURES_FILE=sepsis_feature_names_v2.pkl
MORTALITY_MODEL_FILE=mortality_lightgbm_v2.pkl
MORTALITY_FEATURES_FILE=mortality_feature_names_v2.pkl

# Data source (CSV for now)
DATA_SOURCE=csv
CSV_DATA_PATH=/app/data/sample_kaggle

# Feature counts
SEPSIS_FEATURES_COUNT=42
MORTALITY_FEATURES_COUNT=61

# Feature flags
ENABLE_PREDICTIONS=true
ENABLE_CHATBOT=false
ENABLE_DATABASE=false

# Security (Render auto-generates SECRET_KEY nếu để trống)
SECRET_KEY=your-secret-key-here-change-me

# CORS - SẼ CẬP NHẬT SAU khi có Vercel URL
CORS_ORIGINS=http://localhost:3000
```

⚠️ **LƯU Ý:** 
- `CORS_ORIGINS` sẽ update sau khi deploy Vercel
- Database/Redis KHÔNG CẦN (dùng CSV)
- Chatbot tắt (không cần LLM API keys)

---

## ✅ STEP 4: DEPLOY

```
1. Scroll xuống cuối
2. Click "Create Web Service"
3. Chờ 5-10 phút build & deploy
```

### 4.1 Theo dõi build log:

Bạn sẽ thấy:
```
Building...
  → Pulling Docker image
  → Installing dependencies (pip install)
  → Copying models (~8MB)
  → Starting server
  
Deploy live ✓
```

---

## ✅ STEP 5: LẤY URL & TEST

### 5.1 Copy URL
Sau khi deploy xong, bạn sẽ thấy:
```
https://mediai-api.onrender.com
```
hoặc
```
https://mediai-api-abcd.onrender.com
```

### 5.2 Test Health Endpoint

Mở browser hoặc curl:
```bash
curl https://mediai-api.onrender.com/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-03T..."
}
```

### 5.3 Test API Docs

Mở browser:
```
https://mediai-api.onrender.com/docs
```

Phải thấy Swagger UI với các endpoints:
- POST /api/v1/auth/login
- POST /api/v1/predict/sepsis
- POST /api/v1/predict/mortality
- GET /health

---

## ⚠️ TROUBLESHOOTING

### Build Failed?

**Lỗi "Cannot find Dockerfile":**
```
→ Kiểm tra Root Directory = "api"
→ Dockerfile Path = "Dockerfile"
```

**Lỗi "Port not found":**
```
→ Kiểm tra CMD trong Dockerfile:
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Lỗi "Models not found":**
```
→ Kiểm tra models có trong api/models/:
   - sepsis_lightgbm_v2.pkl
   - sepsis_feature_names_v2.pkl
   - mortality_lightgbm_v2.pkl
   - mortality_feature_names_v2.pkl
```

### Deploy Success nhưng không truy cập được?

**Cold Start (Free tier):**
- Lần đầu access sau 15 phút idle: ~30s
- Refresh lại page, lần 2 sẽ nhanh

**CORS Error:**
- Chưa update CORS_ORIGINS (sẽ fix sau khi có Vercel URL)

---

## ✅ STEP 6: BÁO MÌNH KHI XONG

Khi đã:
- ✅ Deploy success
- ✅ Health endpoint working
- ✅ Swagger docs accessible
- ✅ Có URL backend (https://mediai-api-xxx.onrender.com)

**→ Báo mình URL backend**

Example:
```
"xong render, URL: https://mediai-api-abcd.onrender.com"
```

Mình sẽ tiếp tục hướng dẫn deploy Vercel! 🚀

---

**Guide Version:** 1.0  
**Created:** January 3, 2026
