# 🚀 VERCEL.COM DEPLOYMENT - STEP BY STEP

**Time:** 10-15 phút
**Date:** January 4, 2026
**Backend URL:** https://mediai-7owz.onrender.com

---

## ✅ PREREQUISITE

Backend đã deploy thành công:
- ✅ Render.com: https://mediai-7owz.onrender.com
- ✅ Health check: https://mediai-7owz.onrender.com/health
- ✅ API docs: https://mediai-7owz.onrender.com/docs

---

## ✅ STEP 1: TẠO VERCEL ACCOUNT

### 1.1 Sign Up
```
1. Vào https://vercel.com/signup
2. Chọn "Continue with GitHub"
3. Authorize Vercel to access GitHub
4. Verify email (nếu cần)
```

### 1.2 Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

---

## ✅ STEP 2: IMPORT PROJECT

### Method 1: Vercel Dashboard (RECOMMENDED)

#### 2.1 Import Repository
```
1. Vào Vercel Dashboard: https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Find "MediAI" repository
4. Click "Import"
```

#### 2.2 Configure Build Settings

**Project Name:**
```
mediai-frontend
```

**Framework Preset:**
```
Next.js
```

**Root Directory:**
```
frontend
```
⚠️ QUAN TRỌNG: Phải chọn folder "frontend", không phải root!

**Build Command:**
```
npm run build
```

**Output Directory:**
```
.next
```

**Install Command:**
```
npm install
```

---

## ✅ STEP 3: ENVIRONMENT VARIABLES

Click **"Environment Variables"** và thêm các biến sau:

### 3.1 Required Variables

**NEXT_PUBLIC_API_URL**
```
Value: https://mediai-7owz.onrender.com/api/v1
Environment: Production, Preview, Development
```

**NEXT_PUBLIC_ENV**
```
Value: production
Environment: Production
```

**NEXT_PUBLIC_APP_NAME**
```
Value: MediAI
Environment: Production, Preview, Development
```

**NEXT_PUBLIC_APP_VERSION**
```
Value: 2.0.0
Environment: Production
```

### 3.2 Feature Flags

**NEXT_PUBLIC_ENABLE_PREDICTIONS**
```
Value: true
Environment: Production, Preview, Development
```

**NEXT_PUBLIC_ENABLE_CHAT**
```
Value: false
Environment: Production
```
⚠️ Chatbot tắt (không có LLM API keys)

**NEXT_PUBLIC_ENABLE_MOCK_API**
```
Value: false
Environment: Production
```

**NEXT_PUBLIC_ENABLE_ANALYTICS**
```
Value: false
Environment: Production
```

### 3.3 Configuration Variables

**NEXT_PUBLIC_SESSION_TIMEOUT**
```
Value: 30
Environment: Production
```

**NEXT_PUBLIC_API_TIMEOUT**
```
Value: 30000
Environment: Production
```

**NEXT_PUBLIC_PREDICTION_TIMEOUT**
```
Value: 60000
Environment: Production
```

**NEXT_PUBLIC_SHOW_DEBUG_INFO**
```
Value: false
Environment: Production
```

---

## ✅ STEP 4: DEPLOY

```
1. Scroll xuống cuối
2. Click "Deploy"
3. Chờ 2-5 phút build & deploy
```

### 4.1 Theo dõi build log:

Bạn sẽ thấy:
```
Building...
  → Installing dependencies (npm install)
  → Building Next.js app (npm run build)
  → Optimizing production build
  → Generating static pages

Deploy successful ✓
```

---

## ✅ STEP 5: LẤY URL & TEST

### 5.1 Copy URL

Sau khi deploy xong, bạn sẽ thấy:
```
https://mediai-frontend.vercel.app
```
hoặc
```
https://mediai-frontend-xxx.vercel.app
```

### 5.2 Test Frontend

Mở browser:
```
https://mediai-frontend.vercel.app
```

**Phải thấy:**
- ✅ Login page loads
- ✅ MediAI logo and UI
- ✅ No console errors

### 5.3 Test Login

```
Username: demo
Password: demo123
```

**Kết quả mong đợi:**
- ✅ Login successful
- ✅ Redirect to dashboard
- ✅ No CORS errors

### 5.4 Test Predictions

1. Click "Predictions" tab
2. Try a sepsis or mortality prediction
3. Should see results in <5 seconds

---

## ✅ STEP 6: UPDATE CORS ON BACKEND

**Quan trọng:** Cập nhật CORS để backend chấp nhận requests từ Vercel!

### 6.1 Vào Render.com Dashboard

```
1. Vào https://dashboard.render.com/
2. Click vào service "mediai-api"
3. Click "Environment" tab
```

### 6.2 Update CORS_ORIGINS

Tìm biến `CORS_ORIGINS` và sửa thành:
```
http://localhost:3000,https://mediai-frontend.vercel.app,https://mediai-frontend-*.vercel.app
```

⚠️ **Lưu ý:** Thay `mediai-frontend-*.vercel.app` bằng URL thực tế của bạn

### 6.3 Redeploy Backend

Click "Manual Deploy" → "Deploy latest commit"

Hoặc backend sẽ tự restart sau khi update env vars.

---

## ✅ STEP 7: VERIFY E2E

Test toàn bộ flow:

```bash
# 1. Frontend loads
curl -s https://mediai-frontend.vercel.app | grep "MediAI"

# 2. API accessible from frontend
# Login với browser
# Try predictions
```

**Checklist:**
- [ ] ✅ Frontend loads (no 404)
- [ ] ✅ Login works
- [ ] ✅ Dashboard shows
- [ ] ✅ Predictions work
- [ ] ✅ No CORS errors in browser console

---

## ⚠️ TROUBLESHOOTING

### Build Failed?

**Lỗi "Cannot find module..."**
```
→ Check package.json dependencies
→ Try: npm install locally first
→ Fix any TypeScript errors
```

**Lỗi "Build timeout"**
```
→ Vercel free tier: 45 min build limit
→ Should build in <3 mins for Next.js
→ Check for infinite loops in build scripts
```

### CORS Errors?

**Lỗi "Access-Control-Allow-Origin"**
```
→ Update CORS_ORIGINS trên Render.com (Step 6)
→ Include wildcard: https://*.vercel.app
→ Redeploy backend
```

### API Connection Failed?

**Lỗi "Failed to fetch"**
```
→ Check NEXT_PUBLIC_API_URL đúng URL
→ Check backend health: https://mediai-7owz.onrender.com/health
→ Check CORS headers với browser DevTools
```

**Cold Start (Backend)**
```
→ First request sau 15 phút: ~30s
→ Bình thường với Render free tier
→ Refresh lại, lần 2 sẽ nhanh
```

### Environment Variables Not Working?

```bash
# Vercel CLI
vercel env ls  # List all variables
vercel env pull .env.production  # Download to local

# Redeploy
vercel --prod
```

---

## 📋 DEPLOYMENT CHECKLIST

**Pre-deployment:**
- [x] ✅ Backend deployed (Render.com)
- [x] ✅ Backend health check passing
- [ ] 🔄 Vercel account created
- [ ] 🔄 Repository imported

**During deployment:**
- [ ] 🔄 Root directory = "frontend"
- [ ] 🔄 Environment variables configured
- [ ] 🔄 Build successful
- [ ] 🔄 Deploy successful

**Post-deployment:**
- [ ] 🔄 Frontend URL accessible
- [ ] 🔄 CORS updated on backend
- [ ] 🔄 Login working
- [ ] 🔄 Predictions working
- [ ] 🔄 No console errors

---

## 🎯 QUICK COMMANDS

### Check frontend build locally:
```bash
cd /home/neeyuhuynh/Desktop/MediAI/frontend
npm run build
npm start  # Test production build
```

### Deploy with Vercel CLI (Alternative):
```bash
cd /home/neeyuhuynh/Desktop/MediAI/frontend
vercel login
vercel --prod
```

### Check deployment logs:
```bash
vercel logs https://mediai-frontend.vercel.app
```

---

## 📊 EXPECTED PERFORMANCE

**Build Time:**
- Next.js build: ~2 minutes
- Total deployment: ~3 minutes

**Runtime Performance:**
- Page load: <1s (CDN cached)
- API calls: <100ms (+ backend latency)
- First contentful paint: <800ms

**Cold Start:**
- Frontend: No cold start (Vercel Edge)
- Backend: ~30s first request (Render free tier)

---

## ✅ SUCCESS CRITERIA

Deployment thành công khi:

1. ✅ Frontend accessible at Vercel URL
2. ✅ Login with demo/demo123 works
3. ✅ Dashboard loads patient data
4. ✅ Predictions return results
5. ✅ No CORS errors in console
6. ✅ No 500/404 errors
7. ✅ Mobile responsive
8. ✅ HTTPS enabled (automatic on Vercel)

---

## 🚀 NEXT STEPS

Sau khi deploy thành công:

1. **Custom Domain (Optional)**
   - Vercel Settings → Domains
   - Add your domain (e.g., mediai.yourdomain.com)
   - Update DNS records

2. **Analytics (Optional)**
   - Vercel Analytics (free)
   - Google Analytics
   - Sentry for error tracking

3. **Performance Monitoring**
   - Vercel Speed Insights
   - Lighthouse CI
   - Web Vitals tracking

4. **CI/CD**
   - Auto-deploy on git push (enabled by default)
   - Preview deployments for PRs
   - Production branch protection

---

**Guide Version:** 1.0
**Created:** January 4, 2026
**Backend:** Render.com (https://mediai-7owz.onrender.com)
**Frontend:** Vercel.com (TBD)

---

## 📝 NOTES

- Vercel free tier: Unlimited deployments
- Build time limit: 45 minutes (plenty for Next.js)
- Bandwidth: 100GB/month (free tier)
- Edge Functions: 100,000 requests/month
- **No cold start** on frontend (unlike Render backend)
