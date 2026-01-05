# 🚀 Phase 5: Data Engineering - FREE TIER Plan

**Created:** January 5, 2026
**Status:** ⏳ Ready to Start
**Duration:** 2-3 weeks
**Cost:** $0 (100% Free Tier)

---

## 🎯 Mục Tiêu Phase 5

Migrate từ CSV sang PostgreSQL để có:
- ✅ **Patient Management** - Quản lý bệnh nhân
- ✅ **Prediction History** - Lưu lịch sử dự đoán
- ✅ **Chat Session Persistence** - Lưu chat history
- ✅ **Analytics & Reporting** - Phân tích xu hướng
- ✅ **Production-Ready** - Chuẩn production

---

## 💰 FREE TIER Services (100% Miễn Phí)

### 1. **Neon PostgreSQL** - Database ✅ RECOMMENDED
**URL:** https://neon.tech

**Free Tier:**
- ✅ **Storage:** 0.5 GB (đủ cho project)
- ✅ **Compute:** Unlimited hours
- ✅ **Branches:** 10 database branches (như git branches!)
- ✅ **Auto-scaling:** Tự động scale xuống 0 khi không dùng
- ✅ **Backups:** Point-in-time restore
- ✅ **Connection pooling:** Built-in
- ✅ **SSL:** Included

**Ưu điểm:**
- ⚡ Rất nhanh (serverless PostgreSQL)
- 🔄 Tích hợp tốt với Vercel/Render
- 🌿 Database branching (test trên branch riêng)
- 🆓 Không cần credit card
- 📊 Dashboard đẹp, dễ dùng

**So sánh:**
| Service | Storage | Compute | Expiry | Rating |
|---------|---------|---------|--------|--------|
| **Neon** | 0.5GB | Unlimited | ∞ | ⭐⭐⭐⭐⭐ |
| Render DB | Free | 90 days | 90 days | ⭐⭐⭐ |
| Supabase | 500MB | Limited | ∞ | ⭐⭐⭐⭐ |
| Railway | N/A | $5 credit | Monthly | ⭐⭐ |

---

### 2. **Upstash Redis** - Cache & Sessions ✅ RECOMMENDED
**URL:** https://upstash.com

**Free Tier:**
- ✅ **Commands:** 10,000/day (đủ cho MVP)
- ✅ **Storage:** 256 MB
- ✅ **Max Data Size:** 1 MB per entry
- ✅ **Bandwidth:** Unlimited
- ✅ **REST API:** Included (không cần Redis client!)
- ✅ **Persistence:** Available

**Ưu điểm:**
- ⚡ Serverless Redis (REST API)
- 🌍 Global replication
- 🔒 TLS encryption
- 🆓 Không cần credit card
- 📊 Analytics dashboard

**Use Cases:**
- 💬 Chat session storage (user conversations)
- 🔍 API response caching
- 🎫 Rate limiting tokens
- 🔐 Session tokens

---

## 📊 Database Schema Design

### Tables cần tạo:

#### 1. **users** (Already exists ✅)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. **patients** (NEW - Priority 1)
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "PT-2026-001"
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    admission_date TIMESTAMP,
    department VARCHAR(100),

    -- Encrypted PII (using AES-256)
    encrypted_ssn TEXT,  -- HIPAA compliant
    encrypted_address TEXT,

    -- Clinical data
    chief_complaint TEXT,
    medical_history JSONB,
    current_medications JSONB,

    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_patients_code ON patients(patient_code);
CREATE INDEX idx_patients_admission ON patients(admission_date DESC);
```

**Estimate:** 500 patients × 2KB = **1 MB**

---

#### 3. **vitals** (NEW - Priority 1)
```sql
CREATE TABLE vitals (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP DEFAULT NOW(),

    -- Vital signs
    heart_rate INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    temperature DECIMAL(4,1),
    respiratory_rate INTEGER,
    spo2 INTEGER,

    -- GCS components
    gcs_eye INTEGER,
    gcs_verbal INTEGER,
    gcs_motor INTEGER,
    gcs_total INTEGER,

    -- Notes
    notes TEXT,
    recorded_by INTEGER REFERENCES users(id),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vitals_patient ON vitals(patient_id, recorded_at DESC);
```

**Estimate:** 500 patients × 5 vitals × 0.5KB = **1.25 MB**

---

#### 4. **predictions** (NEW - Priority 1)
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    prediction_type VARCHAR(20) NOT NULL,  -- 'sepsis' or 'mortality'

    -- Input features (JSONB for flexibility)
    input_features JSONB NOT NULL,

    -- Prediction results
    risk_score DECIMAL(5,4) NOT NULL,  -- 0.0000 to 1.0000
    risk_percentage DECIMAL(5,2) NOT NULL,  -- 0.00 to 100.00
    confidence DECIMAL(5,4),

    -- Model metadata
    model_version VARCHAR(20) DEFAULT 'v2',
    model_file VARCHAR(100),

    -- SHAP explanations
    shap_values JSONB,
    top_features JSONB,

    -- User & timing
    predicted_by INTEGER REFERENCES users(id),
    predicted_at TIMESTAMP DEFAULT NOW(),

    -- Outcome tracking (for model evaluation)
    actual_outcome BOOLEAN,  -- NULL until outcome known
    outcome_recorded_at TIMESTAMP
);

CREATE INDEX idx_predictions_patient ON predictions(patient_id, predicted_at DESC);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_time ON predictions(predicted_at DESC);
```

**Estimate:** 500 patients × 10 predictions × 1KB = **5 MB**

---

#### 5. **chat_sessions** (NEW - Priority 2)
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),

    -- Session metadata
    title VARCHAR(200),
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,

    -- Message count
    message_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, last_activity_at DESC);
```

---

#### 6. **chat_messages** (NEW - Priority 2)
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(session_id) ON DELETE CASCADE,

    -- Message content
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,

    -- RAG metadata (for assistant messages)
    sources JSONB,  -- PubMed citations
    retrieval_context JSONB,

    -- PII redaction
    pii_redacted BOOLEAN DEFAULT false,
    redaction_applied JSONB,

    -- Timing
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);
```

**Estimate:** 100 sessions × 20 messages × 1KB = **2 MB**

---

### **Total Storage Estimate:** ~10-15 MB
✅ **Well within Neon's 500 MB free tier!**

---

## 🗺️ Implementation Roadmap

### **Week 1: Database Setup & Core Models**

#### Day 1-2: Database Setup ✅
- [ ] Sign up for Neon PostgreSQL (free, no credit card)
- [ ] Create database: `mediai_production`
- [ ] Get connection string
- [ ] Add to Render.com environment variables
- [ ] Test connection from backend

#### Day 3-4: Alembic Migrations ✅
- [ ] Install Alembic: `pip install alembic`
- [ ] Initialize: `alembic init alembic`
- [ ] Configure `alembic.ini` with Neon URL
- [ ] Create first migration: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Apply migration: `alembic upgrade head`

#### Day 5-7: Core Models ✅
- [ ] Create `api/models/patient.py`
- [ ] Create `api/models/vital.py`
- [ ] Create `api/models/prediction.py`
- [ ] Create `api/models/chat.py`
- [ ] Update `api/models/__init__.py`
- [ ] Generate migration for new models

---

### **Week 2: CRUD Operations & API Integration**

#### Day 8-10: Patient CRUD ✅
- [ ] Create `api/services/patient_service.py`
  - `create_patient()`
  - `get_patient(id)`
  - `list_patients(filters)`
  - `update_patient(id, data)`
  - `delete_patient(id)` (soft delete)

- [ ] Create `api/routers/patients.py`
  - `POST /patients` - Create patient
  - `GET /patients/{id}` - Get patient
  - `GET /patients` - List patients (with pagination)
  - `PUT /patients/{id}` - Update patient
  - `DELETE /patients/{id}` - Soft delete

- [ ] Add RBAC permissions
  - `patients:read` - View patients
  - `patients:write` - Create/edit patients
  - `patients:delete` - Delete patients

#### Day 11-12: Vitals CRUD ✅
- [ ] Create `api/services/vital_service.py`
- [ ] Create `api/routers/vitals.py`
  - `POST /patients/{id}/vitals` - Add vital signs
  - `GET /patients/{id}/vitals` - Get vital history
  - `GET /vitals/{id}` - Get specific vital

#### Day 13-14: Prediction History ✅
- [ ] Update `api/services/prediction_service.py`
  - Add `save_prediction()` after each prediction
  - Store input features, results, SHAP values

- [ ] Create `api/routers/prediction_history.py`
  - `GET /patients/{id}/predictions` - Patient's prediction history
  - `GET /predictions` - All predictions (admin)
  - `GET /predictions/{id}` - Specific prediction with details

---

### **Week 3: Chat Persistence & Redis Caching**

#### Day 15-16: Upstash Redis Setup ✅
- [ ] Sign up for Upstash (free, no credit card)
- [ ] Create Redis database
- [ ] Get REST API URL + token
- [ ] Add to Render.com environment variables
- [ ] Install SDK: `pip install upstash-redis`

#### Day 17-18: Chat Session Storage ✅
- [ ] Create `api/services/chat_service.py`
  - `create_session(user_id)`
  - `get_session(session_id)`
  - `save_message(session_id, role, content, sources)`
  - `get_chat_history(session_id)`

- [ ] Update `api/routers/chat.py`
  - Auto-create session on first message
  - Save all messages to database
  - Return session_id to frontend

- [ ] Update frontend `app/chat/page.tsx`
  - Store session_id in localStorage
  - Load chat history on mount
  - Display previous conversations

#### Day 19-20: Redis Caching ✅
- [ ] Create `api/core/cache.py`
  - Cache wrapper for expensive operations
  - Cache prediction results (key: input features hash)
  - Cache RAG responses (key: question hash)

- [ ] Implement caching in services
  - Sepsis prediction cache (1 hour TTL)
  - Mortality prediction cache (1 hour TTL)
  - RAG response cache (24 hours TTL)

#### Day 21: Testing & Documentation ✅
- [ ] Write unit tests for CRUD operations
- [ ] Write integration tests for database
- [ ] Update API documentation (OpenAPI)
- [ ] Create migration guide for CSV → Database
- [ ] Performance testing (query optimization)

---

## 🔧 Technical Implementation

### 1. Neon PostgreSQL Setup

```bash
# 1. Sign up at https://neon.tech
# 2. Create project: "MediAI Production"
# 3. Copy connection string (looks like):
postgres://username:password@ep-cool-breeze-123456.us-east-2.aws.neon.tech/mediai_production?sslmode=require
```

**Add to Render.com:**
1. Go to https://dashboard.render.com
2. Select backend service: `mediai-7owz`
3. Environment → Add Environment Variable:
   - Key: `DATABASE_URL`
   - Value: `<Neon connection string>`
4. Key: `ENABLE_DATABASE`
   - Value: `true`
5. Save changes (auto-redeploy)

---

### 2. Upstash Redis Setup

```bash
# 1. Sign up at https://upstash.com
# 2. Create Redis database: "MediAI Cache"
# 3. Copy REST URL and token
```

**Add to Render.com:**
- Key: `UPSTASH_REDIS_REST_URL`
  - Value: `https://your-endpoint.upstash.io`
- Key: `UPSTASH_REDIS_REST_TOKEN`
  - Value: `<your-token>`

---

### 3. Alembic Configuration

**Install:**
```bash
cd api
pip install alembic psycopg2-binary
```

**Initialize:**
```bash
alembic init alembic
```

**Configure `alembic/env.py`:**
```python
from core.config import settings
from core.database import Base
from models import User, Patient, Vital, Prediction, ChatSession, ChatMessage

# Set target metadata
target_metadata = Base.metadata

# Set database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Add patient and prediction tables"
alembic upgrade head
```

---

### 4. Example: Patient Service

**`api/services/patient_service.py`:**
```python
from typing import List, Optional
from sqlalchemy.orm import Session
from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate
from core.encryption import encrypt_field, decrypt_field

class PatientService:

    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate, created_by: int) -> Patient:
        """Create new patient with encrypted PII"""
        patient = Patient(
            patient_code=patient_data.patient_code,
            full_name=patient_data.full_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            department=patient_data.department,
            # Encrypt sensitive data
            encrypted_ssn=encrypt_field(patient_data.ssn) if patient_data.ssn else None,
            created_by=created_by,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        return db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.is_active == True
        ).first()

    @staticmethod
    def list_patients(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        department: Optional[str] = None
    ) -> List[Patient]:
        """List patients with pagination"""
        query = db.query(Patient).filter(Patient.is_active == True)

        if department:
            query = query.filter(Patient.department == department)

        return query.order_by(Patient.admission_date.desc()).offset(skip).limit(limit).all()
```

---

### 5. Example: Redis Cache

**`api/core/cache.py`:**
```python
import json
import hashlib
from typing import Any, Optional
from upstash_redis import Redis
from core.config import settings

redis = Redis(
    url=settings.UPSTASH_REDIS_REST_URL,
    token=settings.UPSTASH_REDIS_REST_TOKEN
)

def generate_cache_key(prefix: str, data: dict) -> str:
    """Generate cache key from data hash"""
    data_str = json.dumps(data, sort_keys=True)
    hash_obj = hashlib.md5(data_str.encode())
    return f"{prefix}:{hash_obj.hexdigest()}"

def get_cached_prediction(input_features: dict, prediction_type: str) -> Optional[dict]:
    """Get cached prediction result"""
    key = generate_cache_key(f"pred:{prediction_type}", input_features)
    result = redis.get(key)
    return json.loads(result) if result else None

def cache_prediction(input_features: dict, prediction_type: str, result: dict, ttl: int = 3600):
    """Cache prediction result for 1 hour"""
    key = generate_cache_key(f"pred:{prediction_type}", input_features)
    redis.setex(key, ttl, json.dumps(result))
```

**Usage in prediction service:**
```python
# Check cache first
cached = get_cached_prediction(input_features, "sepsis")
if cached:
    return cached

# Run prediction
result = model.predict(features)

# Cache result
cache_prediction(input_features, "sepsis", result)

return result
```

---

## 📈 Expected Benefits

### Performance:
- ⚡ **Prediction Cache:** ~50ms → ~5ms (10x faster for repeated queries)
- 🔍 **Patient Lookup:** Direct database query vs CSV scan
- 📊 **Analytics:** SQL aggregations vs manual CSV processing

### Features:
- ✅ **Patient Profiles:** Full medical history tracking
- ✅ **Prediction Trends:** Track risk over time
- ✅ **Chat History:** Persistent conversations
- ✅ **User Analytics:** Track model usage, accuracy

### Production-Ready:
- ✅ **Data Persistence:** No data loss on restart
- ✅ **Scalability:** Database handles concurrent users
- ✅ **HIPAA Compliance:** Encrypted PII, audit logs
- ✅ **Backup & Recovery:** Neon automatic backups

---

## 🎯 Success Criteria

### Week 1:
- [ ] Neon database connected to Render backend
- [ ] Alembic migrations working
- [ ] All models created and migrated
- [ ] Database connection health check passing

### Week 2:
- [ ] Patient CRUD API endpoints working
- [ ] Vitals recording functional
- [ ] Predictions saving to database
- [ ] API returns prediction history

### Week 3:
- [ ] Upstash Redis connected
- [ ] Chat sessions persisting
- [ ] Prediction caching working (hit rate >30%)
- [ ] Performance improved vs CSV baseline

### Final Deliverables:
- [ ] 100% free tier usage (no costs)
- [ ] All CRUD operations tested
- [ ] Migration from CSV complete
- [ ] Documentation updated
- [ ] Production deployment successful

---

## 🚨 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Free tier limits exceeded | Low | Medium | Monitor usage, upgrade if needed ($20/mo) |
| Migration data loss | Low | High | Test on staging branch first |
| Performance degradation | Low | Medium | Add indexes, optimize queries |
| Upstash rate limit | Medium | Low | Implement graceful degradation |

---

## 💡 Cost Breakdown (FREE vs PAID)

### FREE TIER (Our Choice):
```
Neon PostgreSQL:     $0/month (0.5GB, unlimited compute)
Upstash Redis:       $0/month (10k commands/day)
Total:               $0/month
```

### PAID (If Needed Later):
```
Neon Pro:            $20/month (3GB, better performance)
Upstash Pro:         $10/month (100k commands/day)
Total:               $30/month
```

**Decision:** Start with FREE, upgrade if usage grows beyond free tier limits.

---

## 📚 Resources

### Documentation:
- Neon Docs: https://neon.tech/docs
- Upstash Docs: https://docs.upstash.com/redis
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- SQLAlchemy ORM: https://docs.sqlalchemy.org/en/20/orm/

### Tutorials:
- Neon + Render: https://neon.tech/docs/guides/render
- Upstash + Python: https://github.com/upstash/upstash-redis-python
- FastAPI + SQLAlchemy: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

## ✅ Next Steps

**Bước tiếp theo:**
1. ✅ Review kế hoạch này
2. ✅ Confirm muốn bắt đầu Phase 5
3. ✅ Tôi sẽ hướng dẫn setup từng bước

**Có muốn bắt đầu ngay không?** 🚀

---

**Document Version:** 1.0.0
**Last Updated:** January 5, 2026
**Status:** Ready to implement
**Cost:** $0 (100% FREE TIER)
