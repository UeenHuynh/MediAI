# Baseline Metrics (V1 - Pre-Migration)

**Date Captured:** 2024-12-12

## API Response Times

| Endpoint | Method | Avg (ms) | p95 (ms) | Target |
|----------|--------|----------|----------|--------|
| `/health` | GET | < 10 | < 20 | <50ms |
| `/token` | POST | < 50 | < 100 | <200ms |
| `/api/v1/predict/sepsis` | POST | TBD | TBD | <500ms |
| `/api/v1/predict/mortality` | POST | TBD | TBD | <500ms |
| `/users/me` | GET | < 20 | < 50 | <100ms |

## Resource Usage (Docker)

| Container | CPU % | RAM (MB) | Notes |
|-----------|-------|----------|-------|
| `mediai-api` | 0.19% | 93.6 | FastAPI |
| `mediai-postgres` | 0.00% | 33.6 | PostgreSQL 16 |
| `mediai-redis` | 0.10% | 10.2 | Redis 7.2 |

## Database Metrics

| Metric | Value |
|--------|-------|
| Total patients | ___ |
| Total predictions | ___ |
| DB size | ___MB |

## Notes

- Metrics to be captured using `locust` or `ab` (Apache Bench)
- Run with API under normal load
- Compare with V2 after migration

---

## How to Capture

```bash
# API response time (requires httpie or curl)
for i in {1..10}; do
  curl -w "%{time_total}s\n" -o /dev/null -s http://localhost:8000/health
done

# Docker stats
docker stats --no-stream

# Load test with locust (optional)
locust -f tests/locustfile.py --headless -u 50 -r 10 -t 1m
```
