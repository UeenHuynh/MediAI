# 🎓 Learning Features - Quick Start Guide

## Overview

This guide helps you enable and experiment with **learning features** - production technologies implemented at small scale for hands-on experience.

**Philosophy:** Learn by doing, with minimal risk và low overhead.

---

## 🚀 Quick Start

### 1. Enable All Learning Features

```bash
# Create learning environment file
cat > .env.learning << EOF
# Learning Features
FEATURE_KAFKA_STREAMING=true
FEATURE_TIMESCALEDB=true
FEATURE_DUCKDB=true
FEATURE_ADVANCED_CACHING=true

# Monitoring
FEATURE_PROMETHEUS=true

# Kafka config
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Database
POSTGRES_PASSWORD=postgres123
EOF

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.learning.yml \
  --env-file .env.learning \
  --profile streaming --profile timeseries --profile analytics \
  up -d

# Check status
docker-compose ps
```

### 2. Verify Services

```bash
# Check Kafka UI
echo "Kafka UI: http://localhost:8080"
open http://localhost:8080

# Check Jupyter
echo "Jupyter: http://localhost:8888"
open http://localhost:8888

# Check API health
curl http://localhost:8000/health | jq

# Check feature flags
curl http://localhost:8000/api/v1/features | jq
```

---

## 📚 Learning Modules

### Module 1: Kafka Streaming (Week 3-4)

**Goal:** Send prediction events to Kafka và consume them

**Steps:**

```bash
# 1. Send test event
docker exec -it mediai_api python -c "
from streaming.kafka_producer import EventProducer

producer = EventProducer('kafka:9092', enabled=True)
producer.send_prediction_event(
    prediction_type='sepsis',
    patient_id='test_123',
    prediction_result={'risk_score': 0.75, 'risk_level': 'HIGH'},
    metadata={'test': True}
)
producer.close()
print('✅ Event sent!')
"

# 2. View in Kafka UI
open http://localhost:8080/ui/clusters/local/all-topics/predictions.sepsis/messages

# 3. Check consumer processed it
docker exec -it mediai_postgres psql -U postgres -d mimic_iv -c \
  "SELECT * FROM prediction_events ORDER BY processed_at DESC LIMIT 5;"

# 4. Monitor consumer lag
docker exec -it mediai_kafka_learning kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group prediction-processor
```

**Learning Outcomes:**
- ✅ Understand Kafka topics and partitions
- ✅ Implement producer with error handling
- ✅ Build consumer with offset management
- ✅ Monitor consumer lag

**Exercise:** Modify `simple_consumer.py` to:
1. Add retry logic for failed messages
2. Implement dead letter queue (DLQ)
3. Add metrics (messages/sec processed)

---

### Module 2: TimescaleDB (Week 4-5)

**Goal:** Create hypertables and optimize time-series queries

**Steps:**

```bash
# 1. Connect to TimescaleDB
docker exec -it mediai_postgres_timescale psql -U postgres -d mimic_iv_timeseries

# 2. Create hypertable
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE patient_vitals (
    time TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    heart_rate INTEGER,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    temperature NUMERIC(4,1),
    respiratory_rate INTEGER
);

SELECT create_hypertable('patient_vitals', 'time');

# 3. Insert test data (1 week of hourly vitals for 100 patients)
INSERT INTO patient_vitals
SELECT
    time,
    'patient_' || (random() * 100)::int,
    60 + (random() * 40)::int,  -- heart rate
    100 + (random() * 40)::int, -- systolic
    60 + (random() * 20)::int,  -- diastolic
    36.0 + random() * 2,        -- temperature
    12 + (random() * 8)::int    -- respiratory rate
FROM generate_series(
    NOW() - INTERVAL '7 days',
    NOW(),
    INTERVAL '1 hour'
) AS time;

# 4. Time-bucket query (hourly averages)
SELECT
    time_bucket('1 hour', time) AS hour,
    COUNT(*) as measurements,
    AVG(heart_rate) as avg_heart_rate,
    AVG(blood_pressure_systolic) as avg_bp_systolic
FROM patient_vitals
WHERE time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

# 5. Create continuous aggregate (pre-computed hourly stats)
CREATE MATERIALIZED VIEW hourly_vital_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    patient_id,
    AVG(heart_rate) as avg_heart_rate,
    MAX(heart_rate) as max_heart_rate,
    MIN(heart_rate) as min_heart_rate,
    COUNT(*) as reading_count
FROM patient_vitals
GROUP BY hour, patient_id;

-- Refresh policy (auto-update every 1 hour)
SELECT add_continuous_aggregate_policy('hourly_vital_stats',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

# 6. Query continuous aggregate (fast!)
SELECT * FROM hourly_vital_stats
WHERE hour > NOW() - INTERVAL '24 hours'
ORDER BY hour DESC
LIMIT 10;
```

**Learning Outcomes:**
- ✅ Create and manage hypertables
- ✅ Implement time-bucket aggregations
- ✅ Use continuous aggregates for performance
- ✅ Compare query speed vs standard PostgreSQL

**Exercise:**
1. Load 1M rows of vitals data
2. Benchmark query performance (hypertable vs normal table)
3. Setup compression and retention policies

---

### Module 3: DuckDB Analytics (Week 5-6)

**Goal:** Export data to Parquet và run analytics queries

**Steps:**

```bash
# 1. Start Jupyter
docker exec -it mediai_jupyter_learning jupyter lab list

# 2. Open browser, create new notebook

# 3. In notebook:
import duckdb
import pandas as pd

# Connect to DuckDB (in-memory)
con = duckdb.connect()

# Export from PostgreSQL to Parquet
con.execute("""
    INSTALL postgres;
    LOAD postgres;

    -- Attach PostgreSQL
    ATTACH 'dbname=mimic_iv user=postgres host=postgres password=postgres123'
    AS postgres_db (TYPE POSTGRES);

    -- Export to Parquet
    COPY (
        SELECT * FROM postgres_db.prediction_events
    ) TO '/home/jovyan/data/prediction_events.parquet' (FORMAT PARQUET);
""")

# Query Parquet directly (no loading!)
df = con.execute("""
    SELECT
        event_type,
        DATE_TRUNC('day', event_timestamp::TIMESTAMP) as day,
        COUNT(*) as prediction_count,
        AVG((prediction->>'risk_score')::FLOAT) as avg_risk_score
    FROM '/home/jovyan/data/prediction_events.parquet'
    GROUP BY event_type, day
    ORDER BY day DESC
""").df()

print(df)

# Advanced: Cohort analysis
cohort_analysis = con.execute("""
    WITH patient_cohorts AS (
        SELECT
            patient_id,
            MIN(DATE_TRUNC('month', event_timestamp::TIMESTAMP)) as cohort_month
        FROM '/home/jovyan/data/prediction_events.parquet'
        GROUP BY patient_id
    )
    SELECT
        cohort_month,
        COUNT(DISTINCT patient_id) as cohort_size
    FROM patient_cohorts
    GROUP BY cohort_month
    ORDER BY cohort_month
""").df()

print(cohort_analysis)
```

**Learning Outcomes:**
- ✅ Export PostgreSQL data to Parquet
- ✅ Query Parquet files with SQL
- ✅ Perform analytics (cohort analysis, trends)
- ✅ Compare performance vs PostgreSQL

**Exercise:**
1. Create daily backup exports to Parquet
2. Build a simple dashboard in Streamlit using DuckDB
3. Implement incremental loads (only new data)

---

### Module 4: Advanced Caching (Week 6)

**Goal:** Implement multi-tier caching với Redis

**Steps:**

```python
# Create: api/services/advanced_cache.py

import redis
from typing import Optional, Any
import json
import hashlib
from datetime import timedelta

class AdvancedCache:
    """
    Multi-tier caching strategy.

    Tiers:
    1. L1: In-memory dict (fastest, smallest)
    2. L2: Redis (fast, larger)
    3. L3: Database (slowest, source of truth)
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.l1_cache = {}  # In-memory cache
        self.l1_max_size = 100  # Limit L1 size

    def get_features(self, patient_id: str) -> Optional[dict]:
        """Get patient features with L1 → L2 → L3 fallback."""

        # Try L1 (in-memory)
        if patient_id in self.l1_cache:
            print(f"✅ L1 cache HIT: {patient_id}")
            return self.l1_cache[patient_id]

        # Try L2 (Redis)
        key = f"features:{patient_id}"
        cached = self.redis.get(key)
        if cached:
            print(f"✅ L2 cache HIT: {patient_id}")
            data = json.loads(cached)

            # Promote to L1
            self._add_to_l1(patient_id, data)
            return data

        # L3 miss - caller will fetch from database
        print(f"❌ Cache MISS: {patient_id}")
        return None

    def set_features(self, patient_id: str, data: dict, ttl: int = 3600):
        """Set features in both L1 and L2."""

        # Set in L2 (Redis)
        key = f"features:{patient_id}"
        self.redis.setex(key, ttl, json.dumps(data))

        # Set in L1 (in-memory)
        self._add_to_l1(patient_id, data)

    def _add_to_l1(self, patient_id: str, data: dict):
        """Add to L1 with size limit (LRU)."""
        if len(self.l1_cache) >= self.l1_max_size:
            # Remove oldest (simple FIFO, could use OrderedDict for true LRU)
            self.l1_cache.pop(next(iter(self.l1_cache)))

        self.l1_cache[patient_id] = data

    def invalidate(self, patient_id: str):
        """Invalidate cache for patient."""
        # Remove from L1
        self.l1_cache.pop(patient_id, None)

        # Remove from L2
        key = f"features:{patient_id}"
        self.redis.delete(key)

# Test
cache = AdvancedCache(redis.Redis(host='localhost', port=6379, db=0))

# First access (L3 miss)
data = cache.get_features("patient_123")  # None

# Set data
cache.set_features("patient_123", {"age": 45, "heart_rate": 72})

# Second access (L2 hit)
data = cache.get_features("patient_123")  # From Redis

# Third access (L1 hit - fastest)
data = cache.get_features("patient_123")  # From memory
```

**Learning Outcomes:**
- ✅ Implement cache hierarchies
- ✅ Measure cache hit rates
- ✅ Understand TTL strategies
- ✅ Handle cache invalidation

**Exercise:**
1. Add cache warming (pre-load frequently accessed patients)
2. Implement cache-aside pattern in prediction endpoint
3. Monitor cache hit rate with Prometheus metrics

---

## 📊 Monitoring Dashboard

### Create Grafana Dashboard

```bash
# Access Grafana
open http://localhost:3001  # admin/admin

# Add Prometheus data source
# URL: http://prometheus:9090

# Create dashboard panels:
# 1. Kafka consumer lag
# 2. Cache hit rate
# 3. API response times
# 4. TimescaleDB query performance
```

---

## 🎯 Success Criteria

### After completing all modules, you should be able to:

**Kafka:**
- [ ] Explain topics, partitions, consumer groups
- [ ] Implement producer with error handling
- [ ] Build consumer with manual offset commits
- [ ] Monitor consumer lag

**TimescaleDB:**
- [ ] Create hypertables
- [ ] Write time-bucket queries
- [ ] Use continuous aggregates
- [ ] Benchmark performance improvements

**DuckDB:**
- [ ] Export PostgreSQL → Parquet
- [ ] Query Parquet files with SQL
- [ ] Perform cohort analysis
- [ ] Compare OLAP vs OLTP workloads

**Advanced Caching:**
- [ ] Implement L1/L2 cache hierarchy
- [ ] Measure cache hit rates >80%
- [ ] Handle cache invalidation
- [ ] Monitor with Prometheus

---

## 🛠️ Troubleshooting

### Kafka not starting

```bash
# Check logs
docker logs mediai_kafka_learning

# Common issue: insufficient memory
# Solution: Increase KAFKA_HEAP_OPTS in docker-compose.learning.yml
```

### TimescaleDB extension not found

```bash
# Install extension manually
docker exec -it mediai_postgres_timescale psql -U postgres -d mimic_iv_timeseries \
  -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
```

### DuckDB import fails

```bash
# Install postgres extension
docker exec -it mediai_jupyter_learning bash
pip install duckdb psycopg2-binary
```

---

## 📚 Additional Resources

**Kafka:**
- Official docs: https://kafka.apache.org/documentation/
- Kafka UI: http://localhost:8080

**TimescaleDB:**
- Docs: https://docs.timescale.com/
- Tutorial: https://docs.timescale.com/timescaledb/latest/quick-start/

**DuckDB:**
- Docs: https://duckdb.org/docs/
- Parquet guide: https://duckdb.org/docs/data/parquet

**Redis:**
- Caching patterns: https://redis.io/docs/manual/patterns/
- Best practices: https://redis.io/docs/manual/patterns/bulk-loading/

---

## ✅ Next Steps

1. **Complete Module 1** (Kafka) - Week 3-4
2. **Complete Module 2** (TimescaleDB) - Week 4-5
3. **Complete Module 3** (DuckDB) - Week 5-6
4. **Complete Module 4** (Caching) - Week 6
5. **Build portfolio project** showcasing all technologies

**Good luck learning! 🚀**
