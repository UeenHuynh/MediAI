# Phase 5: Data Engineering - Status Report

**Date**: December 30, 2024
**Status**: ⏳ **NOT STARTED** (0%)
**Timeline**: 2-3 weeks

---

## 🎯 OBJECTIVE

Migrate từ V2 (GCP/Cloud storage) sang V3 (Full Local PostgreSQL)

---

## 📊 CURRENT STATUS

### ⏳ Phase 5.1: Database Migration Strategy (0%)

**Chưa triển khai:**
- [ ] Database schema design
- [ ] Migration scripts (CSV → PostgreSQL)
- [ ] Data validation pipelines
- [ ] ETL jobs setup

### ⏳ Phase 5.2: Cutover Plan (0%)

**Chưa triển khai:**
- [ ] Data backup strategy
- [ ] Rollback procedures
- [ ] Migration testing
- [ ] Production cutover timeline

---

## ✅ FOUNDATIONS READY

**Đã có sẵn:**
1. ✅ PostgreSQL running (Docker)
2. ✅ CSV sample data (500 rows)
   - `features_sepsis_6h.csv` (42 features)
   - `features_mortality_24h.csv` (61 features)
   - `patients_lookup.csv`
3. ✅ Models trained with CSV features
4. ✅ API schemas defined (Pydantic)

---

## 🚧 BLOCKERS

**Hiện tại:**
- ✅ NO BLOCKERS - Có thể bắt đầu bất cứ lúc nào
- ✅ Phase 0-4 hoàn thành
- ✅ Models v2 đã retrained và validated

**Quyết định cần:**
- Database schema design (star schema vs normalized)
- Data retention policy
- Historical data migration (nếu có)

---

## 📋 TASKS CẦN LÀM

### Week 1: Database Design
1. [ ] Thiết kế database schema
2. [ ] Tạo Alembic migrations
3. [ ] Setup SQLAlchemy models
4. [ ] Viết validation queries

### Week 2: Data Migration
5. [ ] ETL scripts: CSV → PostgreSQL
6. [ ] Data quality checks
7. [ ] Index optimization
8. [ ] Query performance testing

### Week 3: Integration & Testing
9. [ ] Update API to use PostgreSQL (thay vì CSV)
10. [ ] E2E testing với real database
11. [ ] Performance benchmarks
12. [ ] Documentation

---

## 💡 WORKAROUND HIỆN TẠI

**API đang dùng:**
- ❌ KHÔNG đọc từ database
- ✅ Đọc trực tiếp từ CSV files
- ✅ Models predict từ request payload

**Ảnh hưởng:**
- ⚠️ Không lưu predictions history
- ⚠️ Không query historical data
- ⚠️ Không có patient lookup
- ✅ Predictions vẫn hoạt động OK

---

## 🎯 PRIORITY

**Current Priority**: 🟡 **MEDIUM**

**Lý do:**
- Phase 5 không block production deployment
- API hoạt động tốt với CSV data
- Có thể deploy Phase 0-4 trước, Phase 5 sau

**Khi nào cần Phase 5:**
- Cần lưu prediction history
- Cần analytics/reporting
- Cần patient data management
- Scale >500 patients

---

## 📊 ESTIMATED EFFORT

| Task | Effort | Priority |
|------|--------|----------|
| Schema design | 2 days | HIGH |
| Alembic setup | 1 day | HIGH |
| ETL scripts | 3 days | HIGH |
| Data validation | 2 days | MEDIUM |
| API integration | 2 days | HIGH |
| Testing | 3 days | HIGH |
| Documentation | 2 days | MEDIUM |

**Total**: ~15 days (2-3 weeks)

---

## 🚀 NEXT STEPS

**Option 1: Bắt đầu Phase 5 ngay**
- Pros: Complete full stack, production-ready database
- Cons: Delay deployment 2-3 weeks

**Option 2: Skip Phase 5, deploy Phase 0-4 trước**
- Pros: Deploy nhanh hơn, validate với users
- Cons: Cần refactor sau để add database

**Recommendation**:
- ✅ Deploy Phase 0-4 to staging FIRST
- ✅ Validate predictions với users
- ✅ Do Phase 5 parallel với user testing
- ✅ Production deployment sau khi Phase 5 xong

---

## 📁 FILES CẦN TẠO

1. `db/schema.sql` - PostgreSQL schema
2. `db/migrations/` - Alembic migrations
3. `api/database/models.py` - SQLAlchemy models
4. `scripts/etl_csv_to_postgres.py` - Migration script
5. `scripts/validate_data.py` - Validation script
6. `docs/DATABASE_SCHEMA.md` - Schema documentation

---

**Status**: ⏳ Ready to start when needed
**Blocker**: None
**Decision needed**: Timing (now vs later)
