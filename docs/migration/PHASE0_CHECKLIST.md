# Phase 0: Pre-Migration Checklist

## 📋 Deliverables

### 0.1 Code Audit ✅ DONE
- [x] Review Streamlit code structure
- [x] Identify reusable logic (JWT, prediction service, RAG)
- [x] Document API contracts → See `walkthrough.md`

### 0.2 Baseline Metrics
- [ ] **API Response Time**
  ```
  GET /health: ___ms (target: <50ms)
  POST /api/v1/predict/sepsis: ___ms (target: <500ms)
  POST /api/v1/predict/mortality: ___ms (target: <500ms)
  ```
- [ ] **Resource Usage**
  ```
  API Container: CPU ___% | RAM ___MB
  PostgreSQL: CPU ___% | RAM ___MB
  Redis: RAM ___MB
  ```
- [ ] **Output:** `BASELINE_METRICS.md`

### 0.3 API Contracts
- [ ] Export OpenAPI spec from `/docs`
- [ ] Document request/response examples
- [ ] **Output:** `API_CONTRACTS.yaml`

### 0.4 Docker Baseline
- [ ] Verify current `docker-compose.yml` works
- [ ] Document all service versions
- [ ] **Output:** `docker-compose.baseline.yml` (copy of working config)

### 0.5 Dependencies
- [ ] Run `pip freeze > DEPENDENCIES.txt`
- [ ] Check for security vulnerabilities: `safety check`
- [ ] **Output:** `DEPENDENCIES.txt`

### 0.6 Branching Strategy
- [ ] Define branching model (trunk-based recommended)
  ```
  main (production)
  └── feature/v2-migration (long-lived)
      ├── feature/phase1-api
      ├── feature/phase2-frontend
      └── ...
  ```
- [ ] **Output:** `BRANCHING_STRATEGY.md`

### 0.7 Communication Setup
- [ ] Create Slack/Discord channel: `#mediai-v2-migration`
- [ ] Schedule weekly sync (Fridays)
- [ ] Define escalation contacts

---

## ✅ Definition of Done

Phase 0 is complete when:
1. All 5 output files exist in `docs/migration/`
2. Docker compose starts without errors
3. All baseline metrics are documented
4. Branching strategy is agreed upon

---

## 📁 Output Files Location

```
docs/migration/
├── BASELINE_METRICS.md
├── API_CONTRACTS.yaml
├── docker-compose.baseline.yml
├── DEPENDENCIES.txt
└── BRANCHING_STRATEGY.md
```
