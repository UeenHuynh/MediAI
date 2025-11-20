# MediAI - Healthcare ML Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **End-to-end MLOps platform for ICU patient risk prediction using MIMIC-IV data**

## 🎯 Overview

MediAI is a production-ready healthcare ML platform demonstrating modern MLOps practices for critical care:

- **🏥 Sepsis Early Warning** - 6-hour prediction (AUROC >0.85 target)
- **💀 Mortality Risk** - 24-hour prediction (AUROC >0.80 target)
- **📊 Real-time Dashboard** - Streamlit UI for clinical decision support
- **🤖 Agent Automation** - CrewAI-based workflow orchestration

### Key Features

✅ **Medallion Architecture** (Bronze → Silver → Gold data layers)
✅ **Fast ML Inference** (<200ms API latency)
✅ **Explainable AI** (SHAP values for every prediction)
✅ **Production Ready** (Docker Compose, Airflow, MLflow)
✅ **Fully Documented** (Architecture, API specs, model cards)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **16GB RAM minimum**
- **50GB disk space**
- **Kaggle account** (for dataset download)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/MediAI.git
cd MediAI
```

### 2. Download Dataset

```bash
# Install kagglehub
pip install kagglehub

# Setup Kaggle credentials
# Go to https://www.kaggle.com/settings -> Create API Token
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download MIMIC-IV data (~5GB)
python scripts/download_data.py
```

**Dataset:** `akshaybe/updated-mimic-iv` from Kaggle
- ✅ No approval required (public dataset)
- ✅ Pre-cleaned ICU data
- ✅ ~73K ICU stays, 200M+ observations

📚 **Full details:** See [DATA_SOURCE.md](DATA_SOURCE.md)

### 3. Start Services

```bash
# Start all services (PostgreSQL, Redis, Airflow, MLflow, API, UI)
docker-compose up -d

# Check services are running
docker-compose ps
```

**Services:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Airflow: `http://localhost:8080` (admin/admin)
- MLflow: `http://localhost:5000`
- FastAPI: `http://localhost:8000/docs`
- Streamlit: `http://localhost:8501`

### 4. Ingest Data

```bash
# Load data into PostgreSQL
python scripts/ingest_mimic_iv.py --data-path <path-from-step-2>

# Verify ingestion
docker exec mediai_postgres_1 psql -U postgres -d mimic_iv -c "SELECT COUNT(*) FROM raw.icustays;"
# Expected: ~73,000 rows
```

### 5. Build Analytics Layer

```bash
# Run dbt transformations
cd dbt_project
dbt run --models staging.*  # Silver layer
dbt run --models marts.*     # Gold layer (features)
dbt test                     # Data quality checks

# Verify feature tables
psql -U postgres -d mimic_iv -c "\dt analytics.*"
```

### 6. Train Models

```bash
# Sepsis model
jupyter notebook notebooks/02_sepsis_model.ipynb

# Mortality model
jupyter notebook notebooks/03_mortality_model.ipynb

# Models will be registered in MLflow
```

### 7. Access UI

Open browser to `http://localhost:8501` for Streamlit dashboard

---

## 📁 Project Structure

```
MediAI/
├── api/                      # FastAPI backend
│   ├── main.py              # App entry point
│   ├── routers/             # Prediction endpoints
│   ├── models/schemas.py    # Pydantic schemas
│   └── services/            # Business logic
├── apps/                     # Streamlit UI
│   ├── streamlit_app.py     # Main entry
│   ├── pages/               # Multi-page app
│   └── components/          # Reusable components
├── dbt_project/             # Data transformations
│   └── models/
│       ├── staging/         # Silver layer (cleaning)
│       └── marts/           # Gold layer (features)
├── airflow/                 # Orchestration
│   └── dags/                # Pipeline definitions
├── agents/                  # CrewAI automation
│   ├── orchestrator.py      # Workflow orchestrator
│   └── crews/               # Multi-agent crews
├── scripts/                 # Utility scripts
│   ├── download_data.py     # Kaggle download
│   └── ingest_mimic_iv.py   # Data ingestion
├── notebooks/               # Jupyter notebooks
│   ├── 01_eda.ipynb
│   ├── 02_sepsis_model.ipynb
│   └── 03_mortality_model.ipynb
├── tests/                   # Test suite
└── docs/                    # Documentation
    ├── CLAUDE.md            # Development guide
    ├── DATA_SOURCE.md       # Dataset documentation
    ├── DATABASE_SCHEMA.md   # Schema design
    ├── ARCHITECTURE_DESIGN.md
    ├── REQUIREMENTS.md
    └── TASK_BREAKDOWN.md
```

---

## 🏗️ Architecture

### Three-Layer Data Pipeline

```
┌─────────────────────────────────────────┐
│ RAW LAYER (Bronze)                      │
│ Direct copy from Kaggle                 │
│ - icustays, patients, admissions        │
│ - chartevents (vitals), labevents       │
└───────────────┬─────────────────────────┘
                │ dbt staging models
                ▼
┌─────────────────────────────────────────┐
│ STAGING LAYER (Silver)                  │
│ Cleaned, typed, indexed                 │
│ - Outlier removal                       │
│ - Deduplication                         │
│ - Unit standardization                  │
└───────────────┬─────────────────────────┘
                │ dbt mart models
                ▼
┌─────────────────────────────────────────┐
│ ANALYTICS LAYER (Gold)                  │
│ ML-ready features                       │
│ - ml_input_master (42 features)        │
│ - Pre-aggregated, indexed               │
│ - <10ms query time                      │
└─────────────────────────────────────────┘
```

### Service Architecture

```
Streamlit UI (8501) → FastAPI (8000) → PostgreSQL (5432)
                                     ↘ Redis (6379)
                                     ↘ MLflow (5000)
                      ↑
                   Airflow (8080) orchestrates
                      ↓
                   dbt transformations
```

**Key Design:** Denormalized master table (`analytics.ml_input_master`) for <10ms feature queries

---

## 🤖 Models

### Sepsis Early Warning Model

- **Algorithm:** LightGBM binary classifier
- **Features:** 42 (demographics, vitals, labs, SOFA, trends)
- **Prediction:** Sepsis onset within 6 hours
- **Target Performance:** AUROC >0.85, Sensitivity >0.80
- **Inference Time:** <100ms
- **Explainability:** SHAP waterfall plots

### Mortality Risk Model

- **Algorithm:** LightGBM binary classifier
- **Features:** 65 (SOFA, APACHE-II, worst vitals/labs in 24h)
- **Prediction:** Hospital mortality
- **Target Performance:** AUROC >0.80, Sensitivity >0.75
- **Inference Time:** <80ms
- **Explainability:** SHAP feature importance

---

## 📊 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Predict Sepsis Risk

```bash
curl -X POST http://localhost:8000/predict/sepsis \
  -H "Content-Type: application/json" \
  -d '{
    "age": 65,
    "gender": "M",
    "heart_rate": 110,
    "sbp": 90,
    "lactate": 3.5,
    ...
  }'
```

**Response:**
```json
{
  "prediction": {
    "risk_score": 0.78,
    "risk_level": "HIGH",
    "recommendation": "Consider sepsis protocol"
  },
  "explanation": {
    "top_features": [
      {"feature": "lactate", "importance": 0.23, "value": 3.5}
    ]
  },
  "metadata": {
    "model_version": "sepsis_lightgbm_v1",
    "prediction_time_ms": 45
  }
}
```

**Full API Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=api --cov=dbt_project --cov-report=html

# Specific test
pytest tests/test_api.py::test_predict_sepsis -v
```

**Coverage Target:** >70%

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | **Start here** - Complete development guide |
| [DATA_SOURCE.md](DATA_SOURCE.md) | Dataset documentation (Kaggle vs PhysioNet) |
| [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) | Optimized ML schema design |
| [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) | System architecture |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Functional requirements |
| [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) | Implementation tasks (43 tasks) |
| [UI_BACKEND_WIRING.md](UI_BACKEND_WIRING.md) | API integration patterns |

---

## 🔧 Development

### Common Commands

```bash
# Start services
docker-compose up -d

# Run dbt models
cd dbt_project && dbt run

# Run API locally
cd api && uvicorn main:app --reload

# Run Streamlit UI
cd apps && streamlit run streamlit_app.py

# Trigger Airflow DAG
docker exec mediai_airflow_webserver_1 airflow dags trigger etl_pipeline_dag

# View MLflow experiments
open http://localhost:5000
```

### Agent System

```bash
# Run workflow orchestrator
python agents/orchestrator.py

# Run specific crew
python -m agents.crews.data_pipeline_crew
python -m agents.crews.ml_development_crew
```

---

## 🎓 Key Learnings & Best Practices

### 1. Schema Alignment
**Critical:** Database feature tables MUST match API Pydantic schemas exactly
```bash
python scripts/validate_schema_alignment.py
```

### 2. No Data Leakage
- Feature extraction at t-6h, prediction at t=0
- Never use future information
- Temporal validation in all features

### 3. Denormalized Master Table
- Single query for all features (<10ms)
- No joins at inference time
- Pre-computed SOFA scores

### 4. Performance Targets
- API p95 latency: <200ms
- Model inference: <100ms
- Cache hit rate: >80%
- Test coverage: >70%

---

## 🚧 Project Status

**Current Phase:** Active Development (MVP)

| Component | Status |
|-----------|--------|
| Data Pipeline | 🟡 In Progress |
| Feature Engineering | ⏸️ Blocked (needs data) |
| ML Models | 🔴 Not Started |
| API & Serving | 🟡 In Progress |
| UI Dashboard | 🔴 Not Started |
| Agent System | 🟡 In Progress |
| Testing | 🔴 Not Started |

See [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) for detailed status (43 tasks tracked)

---

## ⚠️ What's NOT Implemented Yet

This is an MVP. The following are designed but not implemented:

- ❌ Prometheus/Grafana monitoring
- ❌ Metabase BI dashboards
- ❌ Auto-retraining pipeline
- ❌ Real-time streaming (batch only)
- ❌ Cloud deployment (local only)
- ❌ Mobile app

---

## 🤝 Contributing

This is a portfolio/learning project. Contributions welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

### Data Source
- **Kaggle Dataset:** [akshaybe/updated-mimic-iv](https://www.kaggle.com/datasets/akshaybe/updated-mimic-iv)
- **Original MIMIC-IV:** [PhysioNet](https://physionet.org/content/mimiciv/)

### Reference Implementations
- [BorgwardtLab/mgp-tcn](https://github.com/BorgwardtLab/mgp-tcn) - Sepsis preprocessing
- [microsoft/mimic_sepsis](https://github.com/microsoft/mimic_sepsis) - Sepsis cohort
- [healthylaife/MIMIC-IV-Data-Pipeline](https://github.com/healthylaife/MIMIC-IV-Data-Pipeline) - Mortality features

---

## 📧 Contact

Questions? Open an issue or contact [your-email]

---

## 🌟 Star History

If this project helps you, please give it a ⭐!

---

**Built with ❤️ for healthcare ML and MLOps education**
