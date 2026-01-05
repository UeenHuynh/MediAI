# 🚀 Phase 5 Setup Guide - Step by Step

**Last Updated:** January 5, 2026
**Status:** Ready for execution

---

## ✅ What I've Done (Backend Preparation)

### 1. Database Models Created ✅
Created 4 new models với SQLAlchemy:

- **`api/models/patient.py`** - Patient demographics and medical history
- **`api/models/vital.py`** - Vital signs and clinical measurements
- **`api/models/prediction.py`** - Prediction history with SHAP values
- **`api/models/chat.py`** - Chat sessions and messages

### 2. Alembic Configured ✅
- Updated `api/migrations/env.py` để import tất cả models
- Alembic sẽ tự động detect schema changes
- Sẵn sàng generate migrations

### 3. Dependencies Updated ✅
- Added `upstash-redis==0.15.0` to `api/requirements.txt`
- All required packages ready

---

## 📋 YOUR ACTION ITEMS

### Step 1: Setup Neon PostgreSQL (5 phút) 🔥

#### 1.1. Sign Up Neon (FREE)
1. Truy cập: **https://neon.tech**
2. Click **"Sign Up"**
3. Chọn **"Continue with GitHub"** (nhanh nhất)
4. Authorize Neon app

#### 1.2. Create Database
1. Sau khi đăng nhập, click **"Create Project"**
2. **Project name:** `MediAI Production`
3. **Region:** Chọn `US East (Ohio)` hoặc `EU (Frankfurt)` (gần nhất)
4. **Postgres version:** `16` (mặc định)
5. Click **"Create Project"**

#### 1.3. Get Connection String
1. Vào **Dashboard** → Tab **"Connection Details"**
2. **Connection string** sẽ hiện dạng:
   ```
   postgres://username:password@ep-cool-breeze-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Click **"Copy"** để copy connection string

#### 1.4. Đổi Database Name
⚠️ **IMPORTANT:** Neon default database name là `neondb`, chúng ta cần đổi thành `mediai`:

**Trong connection string, đổi:**
```
BEFORE: /neondb?sslmode=require
AFTER:  /mediai?sslmode=require
```

**Full example:**
```bash
# BEFORE
postgres://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# AFTER
postgres://user:pass@ep-xxx.neon.tech/mediai?sslmode=require
```

#### 1.5. Create Database `mediai`
1. Trong Neon dashboard, click **"SQL Editor"**
2. Run command:
   ```sql
   CREATE DATABASE mediai;
   ```
3. Click **"Run"**

✅ **Xong! Connection string bây giờ đã sẵn sàng.**

---

### Step 2: Add Database URL to Render.com (3 phút) 🔥

#### 2.1. Update Environment Variables
1. Truy cập: **https://dashboard.render.com**
2. Select service: **`mediai-7owz`** (backend service)
3. Click **"Environment"** (left sidebar)
4. Click **"Add Environment Variable"**

**Add these variables:**

**Variable 1:**
- **Key:** `DATABASE_URL`
- **Value:** `<paste your Neon connection string here>`
  ```
  postgres://username:password@ep-xxx.neon.tech/mediai?sslmode=require
  ```

**Variable 2:**
- **Key:** `ENABLE_DATABASE`
- **Value:** `true`

**Variable 3:**
- **Key:** `DATA_SOURCE`
- **Value:** `database`

#### 2.2. Save & Deploy
1. Click **"Save Changes"** ở bottom
2. Render sẽ **auto-redeploy** (~2-3 phút)
3. Đợi deployment complete (màu xanh ✅)

---

### Step 3: Test Database Connection (2 phút) 🔥

#### 3.1. Test từ Local Machine
```bash
cd /home/neeyuhuynh/Desktop/MediAI/api

# Install dependencies (nếu chưa)
pip install -r requirements.txt

# Test connection
python -c "from core.database import test_connection; test_connection()"
```

**Expected output:**
```
INFO:core.database:Database connection successful
```

❌ **Nếu lỗi:**
- Check connection string đúng format
- Check database `mediai` đã tạo chưa
- Check network connection

---

### Step 4: Generate First Migration (2 phút) 🔥

```bash
cd /home/neeyuhuynh/Desktop/MediAI/api

# Generate migration for all new models
alembic revision --autogenerate -m "Add patient, vital, prediction, and chat models"
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'patients'
INFO  [alembic.autogenerate.compare] Detected added table 'vitals'
INFO  [alembic.autogenerate.compare] Detected added table 'predictions'
INFO  [alembic.autogenerate.compare] Detected added table 'chat_sessions'
INFO  [alembic.autogenerate.compare] Detected added table 'chat_messages'
  Generating /path/to/migrations/versions/xxxxx_add_patient_vital_prediction_and_chat_models.py ...  done
```

✅ **Migration file đã được tạo trong `api/migrations/versions/`**

---

### Step 5: Run Migration (1 phút) 🔥

```bash
# Apply migration to database
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Add patient, vital, prediction, and chat models
```

✅ **All tables created in Neon database!**

---

### Step 6: Verify Tables Created (1 phút) 🔥

#### 6.1. Check in Neon Dashboard
1. Vào Neon dashboard → **SQL Editor**
2. Run query:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

**Expected result:**
```
table_name
--------------
chat_messages
chat_sessions
patients
predictions
users
vitals
```

✅ **All 6 tables created successfully!**

---

## 🎯 Summary Checklist

Use this checklist để track progress:

- [ ] **Step 1:** Neon PostgreSQL account created
- [ ] **Step 1:** Database `mediai` created
- [ ] **Step 1:** Connection string copied
- [ ] **Step 2:** DATABASE_URL added to Render.com
- [ ] **Step 2:** ENABLE_DATABASE=true added
- [ ] **Step 2:** Render redeployed successfully
- [ ] **Step 3:** Local database connection tested ✅
- [ ] **Step 4:** Alembic migration generated
- [ ] **Step 5:** Migration applied to database
- [ ] **Step 6:** All 6 tables verified in Neon

---

## 🚨 Common Errors & Solutions

### Error 1: "No module named 'alembic'"
**Solution:**
```bash
cd api
pip install -r requirements.txt
```

### Error 2: "could not connect to server"
**Solution:**
- Check DATABASE_URL có đúng không
- Check database `mediai` đã tạo chưa
- Check sslmode=require ở cuối connection string

### Error 3: "relation already exists"
**Solution:**
```bash
# Drop and recreate (ONLY on first setup!)
alembic downgrade base
alembic upgrade head
```

### Error 4: Render deployment failed
**Solution:**
- Check logs: `https://dashboard.render.com/web/srv-xxx/logs`
- Check DATABASE_URL format
- Check all env variables saved

---

## 📊 Database Schema Overview

After migration, you'll have:

```
public schema
├── users (existing)
│   └── id, username, email, role, ...
│
├── patients (NEW)
│   ├── id, patient_code, full_name, ...
│   └── vitals (1:N)
│   └── predictions (1:N)
│
├── vitals (NEW)
│   └── id, patient_id, heart_rate, bp, temp, ...
│
├── predictions (NEW)
│   └── id, patient_id, prediction_type, risk_score, ...
│
├── chat_sessions (NEW)
│   ├── id, session_id (UUID), user_id, ...
│   └── messages (1:N)
│
└── chat_messages (NEW)
    └── id, session_id, role, content, sources, ...
```

---

## ✅ Next Steps (After This Setup)

Once all tables are created:

1. **Week 2:** Create Patient CRUD API endpoints
2. **Week 2:** Implement prediction history storage
3. **Week 3:** Setup Upstash Redis
4. **Week 3:** Implement chat persistence

---

## 📞 Need Help?

If you encounter any issues:

1. **Check logs:**
   ```bash
   # Local
   tail -f api/logs/app.log

   # Render
   https://dashboard.render.com/web/srv-xxx/logs
   ```

2. **Test connection:**
   ```bash
   python -c "from core.database import test_connection; test_connection()"
   ```

3. **Check migration status:**
   ```bash
   alembic current
   alembic history
   ```

---

## 🎉 Completion Criteria

You'll know setup is successful when:

✅ Neon database có 6 tables (users, patients, vitals, predictions, chat_sessions, chat_messages)
✅ Local connection test passes
✅ Render backend connects to Neon successfully
✅ No errors in Render logs

**Ready to proceed?** Let me know when you complete these steps! 🚀

---

**Guide Version:** 1.0.0
**Last Updated:** January 5, 2026
**Estimated Time:** 15-20 minutes total
