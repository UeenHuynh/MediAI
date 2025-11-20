# 🚀 MediAI - Quick Start (5 Minutes)

## Prerequisites
- Docker Desktop installed and running
- 10GB free disk space
- 8GB RAM minimum

## Setup Steps

### 1. Generate Sample Data (2 min)
```bash
pip install pandas numpy
python scripts/generate_sample_data.py
```

### 2. Start Services (2 min)
```bash
docker-compose up -d postgres redis
sleep 10  # Wait for DB initialization
python scripts/load_sample_data.py
docker-compose up -d api streamlit
```

### 3. Verify (1 min)
```bash
# Check all services are up
docker-compose ps

# Test API
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

### 4. Access the Application
- **UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

## Using Make (Easier)

```bash
# One command setup
make setup

# Or step by step
make install    # Install Python dependencies
make data       # Generate sample data
make start      # Start all services
make health     # Check health
```

## Demo the Application

1. Open http://localhost:8501
2. Click "Predict Sepsis" in sidebar
3. Enter patient data (or use defaults)
4. Click "Predict Sepsis Risk"
5. View results with risk score and top contributing features

## Stop Services

```bash
docker-compose down
```

## Troubleshooting

**Port conflicts?**
```bash
# Check what's using the ports
lsof -i :5432 :6379 :8000 :8501

# Kill conflicting processes
kill -9 <PID>
```

**Database not ready?**
```bash
# Wait longer, then retry
sleep 20
python scripts/load_sample_data.py
```

**See full guide:** [README_DEPLOYMENT.md](README_DEPLOYMENT.md)
