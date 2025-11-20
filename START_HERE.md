# 🚀 START HERE - MediAI Quick Reference

**New to this project? Read this first!**

---

## 📖 What is MediAI?

Healthcare ML platform for ICU risk prediction:
- ✅ Sepsis early warning (6-hour prediction)
- ✅ Mortality risk assessment (24-hour prediction)
- ✅ Real-time dashboard for clinicians
- ✅ Full MLOps pipeline (data → models → API → UI)

---

## 🎯 Quick Navigation

### For Development
1. **[README.md](README.md)** - Project overview & quick start ⭐
2. **[CLAUDE.md](CLAUDE.md)** - Complete development guide
3. **[DATA_SOURCE.md](DATA_SOURCE.md)** - Dataset documentation

### For Architecture
4. **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Optimized ML schema
5. **[ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)** - System design
6. **[UI_BACKEND_WIRING.md](UI_BACKEND_WIRING.md)** - API patterns

### For Implementation
7. **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** - 43 tasks tracked
8. **[REQUIREMENTS.md](REQUIREMENTS.md)** - Functional requirements

### For Reference
9. **[DATASET_UNIFIED.md](DATASET_UNIFIED.md)** - Dataset unification summary
10. **[MODEL_ALIGNMENT.md](MODEL_ALIGNMENT.md)** - Research references

---

## 🏃‍♂️ 5-Minute Setup

```bash
# 1. Install kagglehub
pip install kagglehub

# 2. Download dataset (~5GB, no approval needed!)
python scripts/download_data.py

# 3. Start services
docker-compose up -d

# 4. Ingest data
python scripts/ingest_mimic_iv.py --data-path <path-from-step-2>

# 5. Build analytics
cd dbt_project && dbt run

# 6. Access UI
open http://localhost:8501
```

---

## 📊 Data Source (IMPORTANT!)

**✅ USE THIS:** Kaggle `akshaybe/updated-mimic-iv`
- Public dataset (no approval!)
- 5GB pre-cleaned ICU data
- Download via `kagglehub`

**❌ DON'T USE:** PhysioNet MIMIC-IV
- Requires 1-3 days approval
- 15GB raw data
- More complex setup

**See:** [DATA_SOURCE.md](DATA_SOURCE.md) for complete details

---

## 🏗️ Tech Stack

```
Frontend:  Streamlit
API:       FastAPI
Database:  PostgreSQL
Cache:     Redis
ML Ops:    MLflow, Airflow
Transform: dbt
Agents:    CrewAI
Deploy:    Docker Compose
```

---

## 📁 Key Directories

```
api/         - FastAPI backend
apps/        - Streamlit UI
dbt_project/ - Data transformations
scripts/     - Utility scripts
notebooks/   - Jupyter notebooks
agents/      - Automation workflows
tests/       - Test suite
docs/        - Documentation
```

---

## 🎓 Development Workflow

```
1. Download data  (scripts/download_data.py)
2. Start services (docker-compose up -d)
3. Ingest data    (scripts/ingest_mimic_iv.py)
4. Transform data (dbt run)
5. Train models   (notebooks/)
6. Start API      (already in docker-compose)
7. Open UI        (http://localhost:8501)
```

---

## 🔧 Common Commands

```bash
# Services
docker-compose up -d              # Start all
docker-compose ps                 # Check status
docker-compose logs -f api        # View logs

# Database
psql -U postgres -d mimic_iv      # Connect to DB
\dt analytics.*                   # List tables

# dbt
dbt run --models staging.*        # Run staging
dbt test                          # Run tests

# API
curl http://localhost:8000/docs   # API docs
```

---

## ❓ Common Questions

**Q: Do I need PhysioNet approval?**
A: No! Use Kaggle dataset (public, instant access)

**Q: How big is the dataset?**
A: ~5GB (vs 15GB for PhysioNet)

**Q: How long to setup?**
A: ~30 minutes (vs 2-3 days for PhysioNet)

**Q: Where are the models?**
A: Train in `notebooks/`, stored in MLflow

**Q: How fast is the API?**
A: Target <200ms p95 latency

**Q: Is this production ready?**
A: MVP quality - not for actual clinical use!

---

## 🚨 Important Notes

1. **Schema Alignment:** Database features MUST match API schemas
   - Validate: `python scripts/validate_schema_alignment.py`

2. **No Data Leakage:** Features at t-6h, predict at t=0
   - Always check temporal ordering

3. **Master Table:** Use `analytics.ml_input_master` for fast queries
   - Single query for all 42 features (<10ms)

---

## 📚 Documentation Index

| File | Purpose | When to Read |
|------|---------|--------------|
| START_HERE.md | You are here! | First time |
| README.md | Project overview | Getting started |
| CLAUDE.md | Dev guide | Development |
| DATA_SOURCE.md | Dataset docs | Data setup |
| DATABASE_SCHEMA.md | Schema design | DB queries |
| ARCHITECTURE_DESIGN.md | System design | Understanding arch |
| REQUIREMENTS.md | Requirements | Planning |
| TASK_BREAKDOWN.md | Task tracking | Implementation |

---

## 🎯 Next Steps

**First time here?**
1. Read [README.md](README.md) (5 min)
2. Follow Quick Start (30 min)
3. Read [CLAUDE.md](CLAUDE.md) when developing

**Developing?**
1. Check [CLAUDE.md](CLAUDE.md) for commands
2. Reference [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for queries
3. See [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) for status

**Questions?**
- Check [DATA_SOURCE.md](DATA_SOURCE.md) for dataset
- See [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) for design
- Review [UI_BACKEND_WIRING.md](UI_BACKEND_WIRING.md) for API

---

## ✅ Quick Checklist

Before starting development:
- [ ] Read README.md
- [ ] Downloaded Kaggle dataset
- [ ] Docker Compose running
- [ ] Data ingested to PostgreSQL
- [ ] dbt models built
- [ ] Can access Streamlit UI

---

**Ready to start? Go to [README.md](README.md)! 🚀**

---

Last Updated: 2025-01-21
