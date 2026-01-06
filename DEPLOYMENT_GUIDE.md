# 🚀 Deployment Guide - MediAI Production

**Date:** January 6, 2026
**Status:** Ready to Deploy
**Cost:** $0/month (100% FREE tier)

---

## 📋 Deployment Checklist

### ✅ Prerequisites (Already Done)
- ✅ GitHub repository connected
- ✅ Neon PostgreSQL database running
- ✅ Code pushed to main branch
- ✅ Deployment files created (render.yaml, Procfile, etc.)

---

## 🔧 Step 1: Deploy Backend to Render.com

### 1.1 Access Render Dashboard
1. Go to: https://dashboard.render.com
2. Sign in with your account
3. You should see existing service (if any) or click "New +"

### 1.2 Check Auto-Deploy Status
Since GitHub is already connected, Render should **auto-deploy** when you push!

**Check:**
- Dashboard → Services → Find "mediai-api" (or similar name)
- Look for "Deploying..." or "Live" status
- Build logs will show progress

### 1.3 Configure Environment Variables

**CRITICAL:** Add these environment variables in Render:

Go to: **Service → Environment → Environment Variables**

Add these:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql://neondb_owner:npg_yaqlcoF94Hwg@ep-winter-waterfall-agu4f908-pooler.c-2.eu-central-1.aws.neon.tech/mediai?sslmode=require

# Feature Flags
ENABLE_DATABASE=true
ENABLE_PREDICTIONS=true
ENABLE_CHATBOT=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=10000
ENVIRONMENT=production
DEBUG=false

# Security (Generate a random secret)
SECRET_KEY=your-super-secret-key-change-this-to-random-string

# Data Paths
MODEL_PATH=./models
CSV_DATA_PATH=./data/sample_kaggle

# Model Configuration
SEPSIS_MODEL_VERSION=v2
MORTALITY_MODEL_VERSION=v2
SEPSIS_MODEL_FILE=sepsis_lightgbm_v2.pkl
SEPSIS_FEATURES_FILE=sepsis_feature_names_v2.pkl
MORTALITY_MODEL_FILE=mortality_lightgbm_v2.pkl
MORTALITY_FEATURES_FILE=mortality_feature_names_v2.pkl

# Optional: Redis (if using cache)
# REDIS_URL=redis://localhost:6379/0

# Optional: Qdrant (if using RAG)
# QDRANT_URL=
# QDRANT_API_KEY=
```

**After adding:** Click "Save Changes" → Render will redeploy automatically

---

### 1.4 Wait for Deployment

**Time:** ~5-10 minutes for first deploy

**Watch build logs:**
- Installing dependencies from requirements-prod.txt
- Running migrations (alembic upgrade head) - if configured
- Starting uvicorn server

**Success indicators:**
```
==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

### 1.5 Get Your API URL

After deployment succeeds:
- Render will give you a URL like: `https://mediai-api.onrender.com`
- **Copy this URL** - you'll need it for frontend

### 1.6 Test Backend API

**Test the health endpoint:**
```bash
curl https://your-api-url.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-06T..."
}
```

**Test API docs:**
- Visit: `https://your-api-url.onrender.com/docs`
- You should see Swagger UI with all endpoints

---

## 🎨 Step 2: Deploy Frontend to Vercel

### 2.1 Check Frontend Structure

First, verify you have a frontend:

```bash
ls -la frontend/
```

If you see Next.js/React files, continue. If not, skip to Step 3.

### 2.2 Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

Or deploy via Vercel Dashboard (easier):

### 2.3 Deploy via Vercel Dashboard

1. Go to: https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your GitHub repository: `UeenHuynh/MediAI`
5. Configure:
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `frontend` (if frontend is in subdirectory)
   - **Build Command:** `npm run build` or `yarn build`
   - **Output Directory:** `.next`

6. **Environment Variables:**

```bash
# Backend API URL (from Render step 1.5)
NEXT_PUBLIC_API_URL=https://your-api-url.onrender.com

# Optional: Other configs
NEXT_PUBLIC_ENVIRONMENT=production
```

7. Click "Deploy"

### 2.4 Wait for Deployment

**Time:** ~2-5 minutes

**Success:**
- Vercel will give you a URL like: `https://mediai-xyz.vercel.app`
- Visit the URL to see your frontend

---

## 🔗 Step 3: Connect Frontend to Backend

### 3.1 Update Frontend API Configuration

If your frontend has API configuration file:

**Example: `frontend/src/config.ts`**
```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 3.2 Update CORS (Already Done ✅)

Your backend already allows:
- `https://*.vercel.app`
- `https://*.onrender.com`

So no changes needed!

### 3.3 Redeploy Frontend (if needed)

If you made config changes:
```bash
git add .
git commit -m "Update API URL for production"
git push origin main
```

Vercel will auto-deploy.

---

## ✅ Step 4: Test End-to-End

### 4.1 Test Backend Endpoints

**Via Swagger UI:**
- Visit: `https://your-api-url.onrender.com/docs`

**Test predictions:**
1. Open `/api/v1/predictions/sepsis` endpoint
2. Click "Try it out"
3. Fill in sample patient data
4. Click "Execute"
5. Should get prediction response ✅

**Test patient creation:**
1. Open `/api/v1/patients` POST endpoint
2. Create a sample patient
3. Check database on Neon dashboard to verify ✅

### 4.2 Test Frontend

**Visit your Vercel URL:**
- Homepage should load ✅
- Navigation works ✅
- Can submit prediction form ✅
- Results display correctly ✅

### 4.3 Test Database Connection

**Via Neon Dashboard:**
1. Go to: https://console.neon.tech
2. Select project: MediAI
3. Go to "Tables" → "public"
4. Check if data appears after creating patients/predictions ✅

---

## 🎉 Deployment Complete!

### Your Production URLs:

**Backend API:**
```
https://your-api-url.onrender.com
```

**API Documentation:**
```
https://your-api-url.onrender.com/docs
https://your-api-url.onrender.com/redoc
```

**Frontend:**
```
https://your-frontend.vercel.app
```

**Database:**
```
Neon PostgreSQL Console:
https://console.neon.tech
```

---

## 📊 Monitoring & Maintenance

### Check Backend Logs
- Render Dashboard → Your Service → "Logs" tab
- Real-time logs of API requests, errors, etc.

### Check Database
- Neon Dashboard → Query Editor
- Run SQL queries to check data

### Performance Monitoring
- Render: Check "Metrics" tab for CPU/Memory usage
- Neon: Check "Monitoring" for DB queries

---

## 🚨 Troubleshooting

### Backend won't start?
**Check logs in Render:**
- Missing environment variables? Add them
- Migration errors? Check DATABASE_URL is correct
- Import errors? Check requirements-prod.txt includes all deps

### Frontend can't connect to backend?
**Check:**
1. Backend URL in environment variables is correct
2. Backend has `/health` endpoint returning 200 OK
3. CORS is configured (already done ✅)
4. Network tab in browser for actual error

### Database connection fails?
**Check:**
1. DATABASE_URL format is correct (must include `?sslmode=require`)
2. Neon database is active (not suspended)
3. Connection pooling settings (should be fine with defaults)

### Predictions not saving to database?
**Check:**
1. `ENABLE_DATABASE=true` in Render environment
2. Check backend logs for database errors
3. Verify table `predictions` exists in Neon

---

## 🔄 Update Deployment

### To deploy new changes:

1. **Make changes locally**
2. **Commit to git:**
   ```bash
   git add .
   git commit -m "Your changes"
   ```
3. **Push to GitHub:**
   ```bash
   git push origin main
   ```
4. **Auto-deploy:**
   - Render: Auto-deploys in ~5 min
   - Vercel: Auto-deploys in ~2 min

---

## 💰 Cost Breakdown

### Current (FREE Tier):
- **Neon PostgreSQL:** $0/month (0.5 GB storage)
- **Render.com:** $0/month (512 MB RAM, spins down after inactivity)
- **Vercel:** $0/month (hobby plan)

**Total: $0/month** ✅

### If You Need to Upgrade:
- **Render:** $7/month (keeps service always on, 512MB RAM)
- **Neon Pro:** $20/month (3 GB storage, better performance)
- **Vercel Pro:** $20/month (unlimited deployments)

**Total if scaled:** ~$27-50/month

---

## 🎯 Next Steps After Deployment

1. **Test thoroughly** - Try all features
2. **Monitor errors** - Check logs regularly
3. **Set up alerts** - Render can email you on errors
4. **Add custom domain** (optional):
   - Render: Add custom domain in settings
   - Vercel: Add custom domain in project settings
5. **Enable HTTPS** (automatic on both Render & Vercel ✅)
6. **Backup database** - Neon has automatic backups ✅

---

## 📞 Support

**Render Issues:**
- https://render.com/docs

**Vercel Issues:**
- https://vercel.com/docs

**Neon Issues:**
- https://neon.tech/docs

---

**Good luck with deployment!** 🚀

You're deploying a production-grade medical AI application for **$0/month**! 🎉
