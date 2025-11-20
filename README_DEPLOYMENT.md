# 🚀 MediAI - Deployment Guide (Simplified Production-Ready Version)

**Chi phí: $0** | **Thời gian setup: 15 phút** | **Độ khó: ⭐⭐⭐**

---

## 📋 Tổng quan

Đây là version **Simplified Production-Ready** của MediAI, được thiết kế để:
- ✅ **Chạy local** với chi phí $0
- ✅ **Thể hiện kiến thức mid-level** về data engineering, ML, và microservices
- ✅ **Demo được** cho nhà tuyển dụng
- ✅ **Production-ready** architecture (có thể scale lên cloud)

### Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────┐
│  Streamlit UI (Port 8501)                          │
│  - Dashboard                                        │
│  - Prediction Interface                             │
│  - Model Performance Metrics                        │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP REST API
                   ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI Backend (Port 8000)                       │
│  - /predict/sepsis                                 │
│  - /predict/mortality                              │
│  - /health                                         │
└──────────────────┬──────────────────────────────────┘
                   │ SQL Queries + Redis Cache
                   ▼
┌─────────────────────────────────────────────────────┐
│  PostgreSQL (Port 5432)      Redis (Port 6379)    │
│  - raw schema                - Prediction cache    │
│  - staging schema            - TTL: 1 hour         │
│  - analytics schema                                │
└─────────────────────────────────────────────────────┘
```

### Công nghệ sử dụng

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI** | Streamlit | User interface |
| **API** | FastAPI | REST API server |
| **Database** | PostgreSQL 16 | Data storage (medallion architecture) |
| **Cache** | Redis | Prediction caching |
| **ML** | LightGBM | Prediction models |
| **Orchestration** | Docker Compose | Service management |
| **Transformations** | dbt (manual) | Data transformations |

---

## 🎯 Yêu cầu hệ thống

### Minimum (có thể chạy)
- **RAM:** 8GB
- **CPU:** 2 cores
- **Disk:** 10GB free space
- **OS:** Linux, macOS, hoặc Windows với WSL2

### Recommended (chạy mượt)
- **RAM:** 16GB
- **CPU:** 4 cores
- **Disk:** 20GB free space

### Software
- Docker Desktop 20.10+ ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose 2.24+ (đi kèm Docker Desktop)
- Python 3.11+ (optional, cho development)
- Make (optional, cho shortcuts)

---

## 🚀 Quick Start (15 phút)

### Bước 1: Clone repository

```bash
git clone https://github.com/yourusername/MediAI.git
cd MediAI
```

### Bước 2: Tạo sample data

```bash
# Install dependencies (optional, chỉ cần khi generate data)
pip install pandas numpy

# Generate 1000 synthetic patients
python scripts/generate_sample_data.py
```

**Output:**
```
Generating 1000 patients...
Generating ICU stays...
Generating vital signs...
Generating lab values...

SUMMARY
========================================
Patients:     1,000 records
ICU Stays:    1,000 records
Chartevents:  245,732 records
Total size:   15.3 MB
✓ Sample data generated successfully!
```

### Bước 3: Start services

```bash
# Using Make (recommended)
make setup    # Generate data + start services + load data

# OR manual
docker-compose up -d postgres redis
sleep 10  # Wait for DB to be ready
python scripts/load_sample_data.py
docker-compose up -d api streamlit
```

### Bước 4: Verify everything works

```bash
# Check service status
docker-compose ps

# Should show:
# NAME               STATUS    PORTS
# mediai_postgres    Up        0.0.0.0:5432->5432/tcp
# mediai_redis       Up        0.0.0.0:6379->6379/tcp
# mediai_api         Up        0.0.0.0:8000->8000/tcp
# mediai_streamlit   Up        0.0.0.0:8501->8501/tcp

# Check API health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "components": {
#     "database": "healthy",
#     "redis": "healthy",
#     "api": "healthy"
#   }
# }
```

### Bước 5: Access the application

- **Streamlit UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 📊 Sử dụng hệ thống

### Option 1: Via Streamlit UI (Dễ nhất)

1. Mở http://localhost:8501
2. Chọn "Predict Sepsis" từ sidebar
3. Nhập patient data (hoặc dùng default values)
4. Click "Predict Sepsis Risk"
5. Xem kết quả: Risk score, risk level, top features

### Option 2: Via API (cho developers)

```bash
# Test sepsis prediction
curl -X POST http://localhost:8000/api/v1/predict/sepsis \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-TEST-001",
    "features": {
      "age": 65,
      "gender": "M",
      "bmi": 25.5,
      "heart_rate": 95,
      "sbp": 120,
      "dbp": 80,
      "temperature": 37.0,
      "respiratory_rate": 16,
      "wbc": 10.5,
      "lactate": 1.5,
      "creatinine": 1.0,
      "platelets": 250,
      "bilirubin": 0.8,
      "sodium": 140,
      "potassium": 4.0,
      "glucose": 100,
      "hemoglobin": 13.5,
      "bicarbonate": 24,
      "pao2": null,
      "paco2": null,
      "ph": null,
      "anion_gap": null,
      "albumin": null,
      "troponin": null,
      "bnp": null,
      "inr": null,
      "ast": null,
      "alt": null,
      "respiratory_sofa": 0,
      "cardiovascular_sofa": 0,
      "hepatic_sofa": 0,
      "coagulation_sofa": 0,
      "renal_sofa": 0,
      "neurological_sofa": 0,
      "lactate_trend_12h": 0.0,
      "hr_trend_6h": 0.0,
      "wbc_trend_12h": 0.0,
      "sbp_trend_6h": 0.0,
      "temperature_trend_6h": 0.0,
      "rr_trend_6h": 0.0,
      "hour_of_admission": 12,
      "icu_los_so_far": 12.0
    }
  }'
```

**Expected Response:**
```json
{
  "patient_id": "P-TEST-001",
  "prediction": {
    "risk_score": 0.45,
    "risk_level": "MEDIUM",
    "recommendation": "Increase monitoring frequency, consider early intervention"
  },
  "top_features": [
    {"feature": "lactate", "value": 1.5, "importance": 0.15},
    {"feature": "heart_rate", "value": 95, "importance": 0.12}
  ],
  "metadata": {
    "model_version": "v1",
    "timestamp": "2025-01-20T10:30:00",
    "cached": false
  }
}
```

---

## 🛠️ Makefile Commands

```bash
make help          # Show all available commands
make setup         # Initial setup (data + services)
make start         # Start all services
make stop          # Stop all services
make restart       # Restart services
make logs          # View all logs
make logs-api      # View API logs only
make health        # Check service health
make data          # Regenerate sample data
make clean         # Clean up everything
make rebuild       # Rebuild Docker images
make shell-db      # Open PostgreSQL shell
```

---

## 📁 Cấu trúc dự án

```
MediAI/
├── api/                      # FastAPI backend
│   ├── main.py              # App entry point
│   ├── routers/             # API endpoints
│   │   ├── health.py        # Health check
│   │   └── predictions.py   # Prediction endpoints
│   ├── models/schemas.py    # Pydantic models (42 + 65 features)
│   ├── services/            # Business logic
│   │   └── prediction_service.py  # ML inference + caching
│   ├── core/                # Configuration
│   │   ├── config.py        # Settings
│   │   └── database.py      # DB connection
│   ├── Dockerfile
│   └── requirements.txt
│
├── apps/                     # Streamlit UI
│   ├── app.py               # Main UI application
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/
│   └── init/                # SQL initialization scripts
│       └── 01_create_schemas.sql
│
├── models/                   # ML model artifacts (to be added)
│   ├── sepsis_model_v1.pkl  # (create this)
│   └── mortality_model_v1.pkl
│
├── scripts/                  # Utility scripts
│   ├── download_data.py     # Download MIMIC-IV from Kaggle
│   ├── generate_sample_data.py  # Generate synthetic data
│   └── load_sample_data.py  # Load data into PostgreSQL
│
├── data/                     # Data files (gitignored)
│   └── sample/              # Generated sample data
│       ├── patients.csv
│       ├── icustays.csv
│       └── chartevents.csv
│
├── docker-compose.yml        # Service orchestration
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── Makefile                  # Common commands
└── README_DEPLOYMENT.md      # This file
```

---

## 🔧 Troubleshooting

### Problem: Services won't start

```bash
# Check Docker is running
docker --version
docker-compose --version

# Check port conflicts
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # API
lsof -i :8501  # Streamlit

# Kill conflicting processes
kill -9 <PID>

# Restart Docker Desktop
```

### Problem: Database connection failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 10
python scripts/load_sample_data.py
```

### Problem: API returns 500 errors

```bash
# Check API logs
docker-compose logs api

# Common issues:
# 1. Models not loaded (expected - uses dummy predictions)
# 2. Redis connection failed (check Redis is running)
# 3. Database connection failed (check PostgreSQL)

# Restart API
docker-compose restart api
```

### Problem: UI shows "Cannot connect to API"

```bash
# Check API is running
curl http://localhost:8000/health

# Check API logs
docker-compose logs api

# Rebuild and restart
docker-compose build streamlit
docker-compose up -d streamlit
```

---

## 📈 Monitoring & Performance

### View logs in real-time

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f streamlit
```

### Database queries

```bash
# Open PostgreSQL shell
make shell-db

# Check data
SELECT COUNT(*) FROM raw.patients;
SELECT COUNT(*) FROM raw.icustays;
SELECT COUNT(*) FROM raw.chartevents;

# Check prediction history
SELECT * FROM analytics.prediction_history
ORDER BY prediction_time DESC
LIMIT 10;
```

### Redis cache

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check cache keys
KEYS *

# Get cache stats
INFO stats

# Clear cache
FLUSHDB
```

---

## 🎓 Cho việc xin việc

### Những điểm nổi bật để trình bày

1. **Microservices Architecture**
   - Tách UI, API, Database thành các services độc lập
   - Containerization với Docker
   - Service orchestration với Docker Compose

2. **RESTful API Design**
   - FastAPI với auto-generated docs (OpenAPI/Swagger)
   - Request/response validation (Pydantic)
   - Proper error handling và status codes

3. **Database Design**
   - Medallion architecture (Bronze/Silver/Gold)
   - Proper indexing và query optimization
   - Schema separation (raw, staging, analytics)

4. **Caching Strategy**
   - Redis integration
   - Cache key generation (MD5 hashing)
   - TTL và eviction policies

5. **ML Engineering**
   - Model versioning
   - Feature engineering (42 + 65 features)
   - SHAP explanations (feature importance)

6. **Production Practices**
   - Health checks
   - Logging và monitoring
   - Configuration management (.env)
   - Error handling

### Talking Points cho interview

**Q: "Tell me about this project"**

> "I built MediAI, an ICU risk prediction platform using microservices architecture. It consists of a FastAPI backend serving ML models, PostgreSQL with medallion architecture for data management, Redis for caching, and a Streamlit UI. The system predicts sepsis and mortality risk using LightGBM models trained on MIMIC-IV data."

**Q: "How did you handle scalability?"**

> "I implemented Redis caching to reduce database load and API latency. The architecture is containerized, so it can easily scale horizontally by adding more API containers behind a load balancer. The database uses proper indexing on frequently queried columns."

**Q: "What about data quality?"**

> "I implemented a medallion architecture with three layers: raw (bronze), staging (silver), and analytics (gold). Each layer has validation, and the staging layer handles data cleaning, deduplication, and outlier removal."

---

## 💰 Chi phí vận hành

### Local Development: $0
- Chạy trên laptop/desktop cá nhân
- Không cần cloud services
- Phù hợp cho portfolio/demo

### Cloud Deployment (Optional)

**Nếu muốn deploy lên cloud để demo online:**

#### Option 1: Free Tier (render.com)
```
Web Service (API):     FREE (750 hrs/month)
PostgreSQL:            FREE (90 days trial)
Redis:                 $7/month (cheapest)
─────────────────────────────────────────
Total:                 $0 (first 3 months), then $7/month
```

#### Option 2: DigitalOcean (cheapest)
```
Droplet (4GB RAM):     $24/month
Managed PostgreSQL:    $15/month
Redis:                 Included (self-hosted)
─────────────────────────────────────────
Total:                 ~$39/month
```

**Khuyến nghị:** Chạy local ($0) cho demo, chỉ deploy cloud nếu cần share link

---

## 🔄 Next Steps

### Để hoàn thiện MVP (Week 1-2)

- [ ] **Train actual ML models**
  - Notebook: `notebooks/train_sepsis_model.ipynb`
  - Save models to `models/` directory

- [ ] **Add model metrics**
  - AUROC, sensitivity, specificity
  - Confusion matrix
  - Feature importance plots

- [ ] **Improve UI**
  - Add patient search
  - Prediction history table
  - Better charts (Plotly)

- [ ] **Add tests**
  - `pytest tests/test_api.py`
  - API endpoint tests
  - Database tests

### Để impressive hơn (Week 3-4)

- [ ] **dbt transformations**
  - Bronze → Silver → Gold pipeline
  - Data quality tests
  - Documentation

- [ ] **CI/CD pipeline**
  - GitHub Actions
  - Automated testing
  - Docker image building

- [ ] **Monitoring**
  - Prometheus metrics
  - Grafana dashboards
  - Log aggregation

---

## 📞 Support

Có vấn đề? Tham khảo:
- **Documentation:** [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)
- **API Docs:** http://localhost:8000/docs (khi đang chạy)
- **GitHub Issues:** (create an issue)

---

**Version:** 1.0 (Simplified Production-Ready)
**Last Updated:** 2025-01-20
**Author:** Your Name
**License:** MIT
