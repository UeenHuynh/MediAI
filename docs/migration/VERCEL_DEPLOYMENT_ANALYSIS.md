# Vercel Deployment - Vấn Đề và Giải Pháp

**Date**: December 30, 2024
**Issue**: Làm sao deploy frontend Next.js lên Vercel?

---

## 🔍 PHÂN TÍCH VẤN ĐỀ

### Frontend Architecture Hiện Tại:

```
┌─────────────────────┐
│ Frontend (Next.js)  │
│ localhost:3000      │  ← Chạy local
└─────────┬───────────┘
          │ API calls
          ↓
┌─────────────────────┐
│ Backend (FastAPI)   │
│ localhost:8000      │  ← Chạy local
└─────────────────────┘
```

### Sau khi deploy lên Vercel:

```
┌─────────────────────┐
│ Frontend (Next.js)  │
│ vercel.app          │  ← Deploy trên Vercel cloud
└─────────┬───────────┘
          │ API calls
          ↓
┌─────────────────────┐
│ Backend (FastAPI)   │
│ localhost:8000      │  ← ❌ KHÔNG THỂ ACCESS TỪ VERCEL!
└─────────────────────┘
```

### ⚠️ VẤN ĐỀ CHÍNH:

**Frontend trên Vercel không thể gọi API backend ở localhost:8000**

Lý do:
- `localhost` chỉ hoạt động trên máy local
- Vercel chạy trên cloud → không thể truy cập `localhost` của bạn
- CORS issues nếu không config đúng

---

## 💡 CÁC GIẢI PHÁP

### Option 1: Deploy Backend lên Cloud (RECOMMENDED)

**Ưu điểm**:
- ✅ Production-ready
- ✅ Scalable
- ✅ Stable
- ✅ Free tier available

**Platform lựa chọn**:

#### A. Railway.app (Easiest)
```bash
# Pros:
✅ Free $5/month credit
✅ Deploy trong 5 phút
✅ Auto Docker build
✅ Database included
✅ HTTPS automatic

# Cons:
⚠️ Cần credit card (không charge nếu dưới $5)
⚠️ Giới hạn 500 hours/month (free tier)
```

**Deploy Steps**:
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Init project
cd MediAI
railway init

# 4. Deploy API
cd api
railway up

# 5. Get URL: https://your-app.railway.app
```

---

#### B. Render.com (Recommended)
```bash
# Pros:
✅ Hoàn toàn FREE
✅ Không cần credit card
✅ Database PostgreSQL free
✅ HTTPS automatic
✅ Docker support

# Cons:
⚠️ Spin down after 15 mins inactive (free tier)
⚠️ Cold start ~30s
```

**Deploy Steps**:
```bash
# 1. Tạo account: https://render.com

# 2. Connect GitHub repo

# 3. Create New Web Service:
   - Name: mediai-api
   - Environment: Docker
   - Dockerfile path: api/Dockerfile
   - Instance Type: Free

# 4. Add Environment Variables:
   DATABASE_URL=...
   REDIS_URL=...
   MODEL_PATH=/app/models

# 5. Deploy → Get URL
```

---

#### C. Fly.io
```bash
# Pros:
✅ Free tier generous (3 VMs)
✅ Good performance
✅ Global edge network

# Cons:
⚠️ Cần credit card
⚠️ Setup phức tạp hơn
```

---

#### D. Oracle Cloud (From Phase 8 Plan)
```bash
# Pros:
✅ Hoàn toàn FREE forever
✅ 24GB RAM, 4 cores
✅ 200GB storage
✅ Full control (VM)

# Cons:
⚠️ Setup phức tạp (VPS, Docker, Nginx)
⚠️ Mất nhiều thời gian
⚠️ Cần kiến thức DevOps
```

---

### Option 2: Vercel Serverless Functions (NOT RECOMMENDED)

**Vấn đề**:
- ❌ Không thể chạy LightGBM models (file size lớn)
- ❌ Cần refactor toàn bộ API
- ❌ Timeout 10s (predictions có thể lâu hơn)
- ❌ Cold start issues

**Kết luận**: KHÔNG KHUYẾN KHÍCH cho ML models

---

### Option 3: Ngrok/Cloudflare Tunnel (TEMPORARY ONLY)

**Ngrok**:
```bash
# 1. Install
brew install ngrok  # macOS
# hoặc download: https://ngrok.com

# 2. Start tunnel
ngrok http 8000

# 3. Get public URL: https://abc123.ngrok.io

# 4. Update frontend .env:
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io/api/v1
```

**Ưu điểm**:
- ✅ Setup nhanh (2 phút)
- ✅ Test ngay lập tức

**Nhược điểm**:
- ❌ Chỉ dùng cho demo/testing
- ❌ URL thay đổi mỗi lần restart
- ❌ Không stable cho production
- ❌ Cần máy local chạy 24/7

---

## 🎯 KHUYẾN NGHỊ

### Giải pháp tốt nhất cho từng trường hợp:

#### 1. Development/Testing (Ngay bây giờ):
```
✅ Option: Ngrok hoặc Cloudflare Tunnel
✅ Time: 5 phút
✅ Cost: FREE
✅ Use case: Demo, UAT, testing
```

#### 2. Staging (Tuần này):
```
✅ Option: Render.com
✅ Time: 30 phút
✅ Cost: FREE (with cold start)
✅ Use case: UAT, user testing
```

#### 3. Production (Sau UAT):
```
✅ Option: Railway.app hoặc Oracle Cloud
✅ Time: 1-3 giờ
✅ Cost: FREE (Railway $5 credit) hoặc Oracle FREE forever
✅ Use case: Real users, production workload
```

---

## 📋 DEPLOYMENT PLAN - 3 STEPS

### STEP 1: Deploy Backend (Chọn 1 option)

#### Option A: Render.com (FREE, Recommended)

1. **Tạo account**: https://render.com/signup
2. **Connect GitHub**:
   - Settings → Connect GitHub
   - Authorize Render
3. **Create Web Service**:
   - Dashboard → New → Web Service
   - Select repo: `MediAI`
   - Name: `mediai-api`
   - Environment: `Docker`
   - Dockerfile path: `api/Dockerfile`
   - Instance Type: `Free`
4. **Environment Variables**:
   ```
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   MODEL_PATH=/app/models
   ENVIRONMENT=production
   ```
5. **Deploy** → Wait 5-10 mins
6. **Get URL**: `https://mediai-api.onrender.com`

---

#### Option B: Railway (Easier, $5 free credit)

```bash
# 1. Install CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy API
cd /home/neeyuhuynh/Desktop/MediAI/api
railway init
railway up

# 4. Add services
railway add  # PostgreSQL
railway add  # Redis

# 5. Get URL from dashboard
```

---

#### Option C: Ngrok (Fastest, testing only)

```bash
# 1. Download
# https://ngrok.com/download

# 2. Start API local
docker-compose up api  # localhost:8000

# 3. Start tunnel
ngrok http 8000

# 4. Copy URL
# https://abc123.ngrok-free.app
```

---

### STEP 2: Deploy Frontend lên Vercel

#### Method 1: Vercel Dashboard (Easiest)

1. **Tạo account**: https://vercel.com/signup
2. **Import Project**:
   - Dashboard → Add New → Project
   - Import Git Repository
   - Select: `MediAI`
   - Root Directory: `frontend`
3. **Configure**:
   - Framework Preset: `Next.js`
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://mediai-api.onrender.com/api/v1
   NEXT_PUBLIC_ENV=production
   NEXT_PUBLIC_ENABLE_PREDICTIONS=true
   ```
5. **Deploy** → Wait 2-3 mins
6. **Get URL**: `https://mediai.vercel.app`

---

#### Method 2: Vercel CLI

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy from frontend folder
cd /home/neeyuhuynh/Desktop/MediAI/frontend

# 4. Deploy
vercel

# Follow prompts:
# - Setup and deploy? Y
# - Which scope? Your account
# - Link to existing project? N
# - Project name? mediai-frontend
# - Directory? ./
# - Override settings? N

# 5. Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter value: https://mediai-api.onrender.com/api/v1

vercel env add NEXT_PUBLIC_ENV production
# Enter value: production

# 6. Redeploy with env vars
vercel --prod
```

---

### STEP 3: Test Deployment

```bash
# 1. Open frontend URL
https://mediai.vercel.app

# 2. Test API connection
curl https://mediai-api.onrender.com/health

# 3. Test authentication
# Login với demo/demo123

# 4. Test predictions
# Try sepsis/mortality prediction
```

---

## 🚀 QUICK START (30 phút)

**Cách nhanh nhất để có frontend working**:

```bash
# === BACKEND: Ngrok (5 phút) ===
# Terminal 1: Start API
cd /home/neeyuhuynh/Desktop/MediAI
docker-compose up api

# Terminal 2: Start ngrok
ngrok http 8000
# Copy URL: https://abc123.ngrok-free.app

# === FRONTEND: Vercel CLI (10 phút) ===
# Install Vercel
npm install -g vercel

# Deploy
cd /home/neeyuhuynh/Desktop/MediAI/frontend
vercel login
vercel

# Set API URL
vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://abc123.ngrok-free.app/api/v1

# Deploy with env
vercel --prod

# === DONE ===
# Frontend: https://your-app.vercel.app
# Backend: https://abc123.ngrok-free.app
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### CORS Configuration

Backend cần allow frontend domain:

```python
# api/main.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://mediai.vercel.app",  # Add Vercel URL
    "https://*.vercel.app",  # Allow preview deployments
]
```

### Environment Variables

**Vercel tự động set**:
- `VERCEL=1`
- `VERCEL_URL` = deployment URL
- `VERCEL_ENV` = production/preview/development

**Bạn cần set**:
- `NEXT_PUBLIC_API_URL` = Backend URL
- All NEXT_PUBLIC_* variables

### Cold Start (Render Free Tier)

Backend sẽ sleep sau 15 phút không dùng:
- First request: ~30s (wake up)
- Subsequent requests: normal speed

**Giải pháp**:
- Upgrade to paid ($7/month - no cold start)
- Hoặc dùng Railway/Oracle Cloud

---

## 📊 SO SÁNH PLATFORMS

| Platform | Cost | Setup Time | Cold Start | Database | Pros |
|----------|------|------------|------------|----------|------|
| **Render** | FREE | 30 mins | 30s | ✅ Free | Easiest |
| **Railway** | $5 free | 15 mins | No | ✅ Included | Fast |
| **Fly.io** | FREE | 45 mins | No | ✅ Free | Performance |
| **Oracle Cloud** | FREE forever | 3 hours | No | ✅ Full VM | Full control |
| **Ngrok** | FREE | 2 mins | No | ❌ None | Testing only |

---

## ✅ CHECKLIST

**Before Deployment**:
- [ ] API chạy stable local
- [ ] Models v2 trong api/models/
- [ ] Frontend build thành công (`npm run build`)
- [ ] Environment variables prepared

**Backend Deployment**:
- [ ] Platform selected (Render/Railway/Ngrok)
- [ ] API deployed
- [ ] Health check working: `/health`
- [ ] Auth working: `/api/v1/auth/login`
- [ ] Predictions working: `/api/v1/predict/sepsis`

**Frontend Deployment**:
- [ ] Vercel account created
- [ ] Project imported
- [ ] Environment variables set
- [ ] Domain configured
- [ ] Build successful

**Post-Deployment**:
- [ ] Frontend loads
- [ ] API connection works
- [ ] Login successful
- [ ] Predictions working
- [ ] No CORS errors

---

## 🆘 TROUBLESHOOTING

### Frontend build fails:
```bash
# Check build locally first
cd frontend
npm run build

# Fix TypeScript errors
# Fix missing dependencies
```

### CORS errors:
```python
# api/main.py - Add Vercel URL
origins = [
    "https://*.vercel.app",
]
```

### API not reachable:
```bash
# Check backend health
curl https://your-backend.onrender.com/health

# Check CORS
curl -H "Origin: https://your-frontend.vercel.app" \
  https://your-backend.onrender.com/health
```

### Environment variables not working:
```bash
# Vercel CLI
vercel env ls  # List all vars
vercel env pull  # Pull to local
vercel --prod  # Redeploy
```

---

**Cần deploy ngay?**
Chọn: **Ngrok (5 phút) + Vercel (10 phút) = 15 phút total**

**Cần production stable?**
Chọn: **Render.com (30 phút) + Vercel (10 phút) = 40 phút total**
