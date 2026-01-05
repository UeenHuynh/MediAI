# Vercel Deployment - ✅ DEPLOYED SUCCESSFULLY

## 🚀 Live URLs (January 5, 2026)

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend** | https://mediai-frontend-five.vercel.app | ✅ LIVE |
| **Backend** | https://mediai-7owz.onrender.com | ✅ LIVE |

---

## Issue (RESOLVED)
Build local thành công, nhưng Vercel Dashboard không deploy được.

## Solution: Deploy bằng Vercel CLI

### Step 1: Login Vercel CLI

```bash
cd /home/neeyuhuynh/Desktop/MediAI/frontend
vercel login
```

**Vercel sẽ:**
1. Mở browser
2. Yêu cầu confirm login
3. Click "Confirm" trên browser

**Hoặc nếu đã login rồi:**
```bash
vercel whoami
```

---

### Step 2: Deploy to Production

```bash
cd /home/neeyuhuynh/Desktop/MediAI/frontend

# Deploy với tất cả settings
vercel --prod \
  --yes \
  --name mediai-frontend \
  --env NEXT_PUBLIC_API_URL=https://mediai-7owz.onrender.com/api/v1 \
  --env NEXT_PUBLIC_ENV=production \
  --env NEXT_PUBLIC_ENABLE_PREDICTIONS=true \
  --env NEXT_PUBLIC_ENABLE_CHAT=false \
  --env NEXT_PUBLIC_APP_NAME=MediAI \
  --env NEXT_PUBLIC_APP_VERSION=2.0.0 \
  --env NEXT_PUBLIC_SESSION_TIMEOUT=30 \
  --env NEXT_PUBLIC_API_TIMEOUT=30000 \
  --env NEXT_PUBLIC_PREDICTION_TIMEOUT=60000 \
  --env NEXT_PUBLIC_SHOW_DEBUG_INFO=false
```

Hoặc đơn giản:

```bash
cd /home/neeyuhuynh/Desktop/MediAI/frontend
vercel --prod
```

CLI sẽ hỏi:
- Project name? → `mediai-frontend` (hoặc enter để dùng default)
- Deploy? → `Y`

---

### Step 3: Sau khi deploy xong

Vercel sẽ trả về URL:
```
✓ Production: https://mediai-frontend-xxx.vercel.app
```

Copy URL này!

---

## Alternative: Fix Vercel Dashboard Deploy

Nếu vẫn muốn dùng Dashboard:

### 1. Check Build Logs

Vào Vercel Dashboard:
- Click project "mediai-frontend" (hoặc "MediAI")
- Click "Deployments" tab
- Click deployment failed (nếu có)
- Xem "Build Logs" để tìm error

### 2. Common Issues

**A. Root Directory sai:**
```
Settings → Root Directory → "frontend" (không phải ".")
```

**B. Environment Variables thiếu:**
```
Settings → Environment Variables
→ Add tất cả biến trong .env.production
```

**C. Build Command sai:**
```
Settings → Build & Development
→ Build Command: "npm run build" (hoặc để trống)
→ Output Directory: ".next" (hoặc để trống)
```

### 3. Trigger Redeploy

Sau khi fix settings:
- Deployments tab
- Click "..." menu
- "Redeploy"

---

## Fastest Solution (RECOMMENDED)

```bash
# 1. Login (one time only)
cd /home/neeyuhuynh/Desktop/MediAI/frontend
vercel login

# 2. Deploy
vercel --prod

# 3. Done!
```

CLI sẽ tự động:
- Detect Next.js
- Build project
- Deploy to production
- Set up domain

---

## Verify Deployment

```bash
# Check deployment URL
vercel ls

# Check production URL
vercel inspect
```

Test trên browser:
```
https://your-url.vercel.app
```

Should see login page!

---

## Update CORS After Deploy

Khi đã có Vercel URL, update backend CORS:

1. Vào Render.com → mediai-api
2. Environment → CORS_ORIGINS
3. Thêm: `https://your-vercel-url.vercel.app`
4. Save → Redeploy

---

**Next:** Report Vercel URL sau khi deploy thành công!
