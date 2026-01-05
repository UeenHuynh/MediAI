# Learning Objectives - Phase 1 Experimental Features

## 🎯 Overview

Phase 1 includes **learning features** implemented at small scale to gain hands-on experience with production technologies. These features are:
- ✅ **Feature-flagged** - Can be enabled/disabled without code changes
- ✅ **Minimal overhead** - Small resource footprint (<512MB total)
- ✅ **Optional** - Core MVP works without them
- ✅ **Resume-worthy** - Modern tech stack experience

---

## 1️⃣ KAFKA STREAMING

### What You'll Learn

#### Core Concepts
- **Event-driven architecture** - Decouple producers and consumers
- **Message brokers** - How Kafka stores and delivers messages
- **Topics & Partitions** - Data organization and parallelism
- **Consumer Groups** - Load balancing across consumers
- **Offset Management** - Exactly-once vs at-least-once delivery

#### Technical Skills
```python
✅ Producer patterns:
   - Async message publishing
   - Serialization (JSON, Avro)
   - Error handling and retries
   - Idempotency keys

✅ Consumer patterns:
   - Poll loop architecture
   - Manual offset commits
   - Graceful shutdown handling
   - Dead letter queues (DLQ)

✅ Operations:
   - Kafka UI for monitoring
   - Topic creation and configuration
   - Partition rebalancing
   - Consumer lag monitoring
```

#### Learning Path
1. **Week 1**: Setup single-broker Kafka (KRaft mode)
2. **Week 2**: Implement simple producer/consumer
3. **Week 3**: Add error handling and monitoring
4. **Week 4**: Performance testing and optimization

#### Success Metrics
- [ ] Successfully send 1000 events/second
- [ ] Implement at-least-once delivery guarantee
- [ ] Handle consumer rebalancing gracefully
- [ ] Monitor consumer lag <100ms

#### Minimal Implementation
```yaml
Resource Usage:
  Kafka (single broker): ~256MB RAM
  Stream processor: ~128MB RAM
  Total: ~384MB

Topics:
  - predictions.sepsis (1 partition)
  - predictions.mortality (1 partition)

Consumers:
  - simple_consumer.py (1 instance)
```

#### Resume Value
- ⭐⭐⭐⭐⭐ **Very High**
- Used by: LinkedIn, Uber, Netflix, Airbnb
- Keywords: "Event-driven architecture", "Real-time data pipelines", "Apache Kafka"

---

## 2️⃣ TIMESCALEDB

### What You'll Learn

#### Core Concepts
- **Time-series data** - Optimizations for timestamp-indexed data
- **Hypertables** - Automatic partitioning by time
- **Continuous aggregates** - Materialized views for rollups
- **Data retention policies** - Automatic old data cleanup
- **Compression** - Reduce storage for historical data

#### Technical Skills
```sql
✅ Time-series queries:
   - Time-bucket aggregations
   - Moving averages
   - Gap filling (interpolation)
   - First/last value in time window

✅ Performance optimization:
   - Index strategies for time-series
   - Chunk sizing
   - Compression algorithms
   - Query planning

✅ Operations:
   - Hypertable creation
   - Retention policies
   - Continuous aggregates
   - Migration from PostgreSQL
```

#### Learning Path
1. **Week 1**: Install TimescaleDB extension, create hypertables
2. **Week 2**: Implement time-bucket queries for patient vitals
3. **Week 3**: Setup continuous aggregates (hourly/daily stats)
4. **Week 4**: Compare performance vs standard PostgreSQL

#### Success Metrics
- [ ] Create hypertable for patient vitals (1M+ rows)
- [ ] Implement 1-hour time-bucket aggregations
- [ ] Achieve >20% query performance improvement vs PostgreSQL
- [ ] Setup 90-day retention policy

#### Minimal Implementation
```yaml
Resource Usage:
  TimescaleDB: ~256MB RAM (extension on existing PostgreSQL)

Tables:
  - patient_vitals_ts (hypertable, partitioned by hour)
  - prediction_history_ts (hypertable)

Continuous Aggregates:
  - hourly_vital_stats
  - daily_prediction_summary
```

#### Resume Value
- ⭐⭐⭐⭐ **High**
- Used by: Samsung, Cisco, Comcast
- Keywords: "Time-series database", "IoT data", "Hypertables"

---

## 3️⃣ DUCKDB ANALYTICS

### What You'll Learn

#### Core Concepts
- **OLAP vs OLTP** - Analytical vs transactional workloads
- **Columnar storage** - Parquet files and column-oriented queries
- **Embedded database** - No server needed, runs in-process
- **SQL-on-files** - Query CSV/Parquet without loading to database

#### Technical Skills
```python
✅ Analytics queries:
   - Complex aggregations (GROUP BY, ROLLUP)
   - Window functions
   - CTEs (Common Table Expressions)
   - JOINs across multiple Parquet files

✅ Data engineering:
   - Export PostgreSQL → Parquet
   - Incremental data loads
   - Schema evolution
   - Data validation

✅ Performance:
   - Vectorized execution
   - Predicate pushdown
   - Parallel query execution
```

#### Learning Path
1. **Week 1**: Setup DuckDB, import data from PostgreSQL
2. **Week 2**: Write analytics queries (cohort analysis, trend detection)
3. **Week 3**: Create Jupyter notebooks with DuckDB
4. **Week 4**: Build simple dashboard with Streamlit + DuckDB

#### Success Metrics
- [ ] Export 1M patient records to Parquet
- [ ] Query Parquet files faster than PostgreSQL
- [ ] Implement cohort analysis (30-day readmission rates)
- [ ] Create interactive analytics notebook

#### Minimal Implementation
```yaml
Resource Usage:
  DuckDB: ~128MB RAM (embedded, no server)
  Jupyter: ~256MB RAM (optional)
  Total: ~384MB

Data Files:
  - patient_cohorts.parquet (versioned backups)
  - prediction_results.parquet

Use Cases:
  - Offline analytics
  - Data science exploration
  - Report generation
```

#### Resume Value
- ⭐⭐⭐⭐ **High**
- Trending technology (2024-2025)
- Keywords: "OLAP", "Columnar database", "Data analytics"

---

## 4️⃣ ADVANCED CACHING (Redis Multi-Tier)

### What You'll Learn

#### Core Concepts
- **Cache hierarchies** - L1 (in-memory) → L2 (Redis) → L3 (database)
- **Cache invalidation** - TTL, event-driven, manual purge
- **Cache-aside pattern** - Application manages cache
- **Write-through vs write-back** - Synchronous vs async writes

#### Technical Skills
```python
✅ Caching strategies:
   - Feature cache (patient data)
   - Model cache (predictions)
   - API response cache
   - Session cache

✅ Redis data structures:
   - Strings (simple KV)
   - Hashes (nested objects)
   - Sets (unique items)
   - Sorted sets (leaderboards)

✅ Advanced features:
   - Pub/Sub for cache invalidation
   - Redis streams (alternative to Kafka)
   - Lua scripts (atomic operations)
   - Redis Cluster (sharding)
```

#### Learning Path
1. **Week 1**: Implement L2 cache for patient features
2. **Week 2**: Add cache invalidation on data updates
3. **Week 3**: Monitor cache hit rates, tune TTLs
4. **Week 4**: Implement Pub/Sub for distributed cache invalidation

#### Success Metrics
- [ ] Achieve >80% cache hit rate for predictions
- [ ] Reduce database load by >50%
- [ ] Implement cache warming on startup
- [ ] Handle cache failover gracefully

#### Minimal Implementation
```yaml
Resource Usage:
  Redis: 256MB maxmemory (already running)

Cache Keys:
  - features:{patient_id} (TTL: 1 hour)
  - prediction:{patient_id}:{type} (TTL: 24 hours)
  - model:metadata (TTL: ∞)

Eviction Policy:
  - allkeys-lru (least recently used)
```

#### Resume Value
- ⭐⭐⭐⭐ **High**
- Used by: Twitter, GitHub, Snapchat
- Keywords: "Distributed caching", "Redis", "Performance optimization"

---

## 📊 RESOURCE SUMMARY

### With All Learning Features Enabled

```yaml
Core Services (Always):
  - PostgreSQL: ~512MB
  - Redis: ~256MB
  - API: ~512MB
  Subtotal: ~1.28GB

Learning Features (Optional):
  - Kafka: ~256MB
  - TimescaleDB: ~256MB (uses existing PostgreSQL)
  - DuckDB: ~128MB
  - Stream Processor: ~128MB
  - Jupyter: ~256MB
  Subtotal: ~768MB

Total: ~2GB RAM (fits comfortably in 8GB system)
```

### Profiles Usage

```bash
# Core only (MVP)
docker-compose up

# Core + Kafka streaming
docker-compose -f docker-compose.yml -f docker-compose.learning.yml --profile streaming up

# Core + TimescaleDB
docker-compose -f docker-compose.yml -f docker-compose.learning.yml --profile timeseries up

# Core + Analytics (Jupyter + DuckDB)
docker-compose -f docker-compose.yml -f docker-compose.learning.yml --profile analytics up

# Everything (for learning)
docker-compose -f docker-compose.yml -f docker-compose.learning.yml \
  --profile streaming --profile timeseries --profile analytics up
```

---

## 🎓 LEARNING TIMELINE

### Phase 1.0 (Weeks 1-2): Core MVP
- ✅ PostgreSQL + Redis
- ✅ FastAPI + LangChain
- ✅ Basic caching
- ✅ Health checks

### Phase 1.5 (Weeks 3-4): Learning Features
- 🎯 Week 3: Kafka streaming
- 🎯 Week 4: TimescaleDB hypertables

### Phase 1.7 (Weeks 5-6): Analytics & Optimization
- 🎯 Week 5: DuckDB analytics
- 🎯 Week 6: Advanced caching patterns

### Phase 2 (Weeks 7+): Frontend Development
- Next.js with feature flag UI toggles
- Monitoring dashboards (Kafka lag, cache hits, etc.)

---

## 🚀 QUICK START

### 1. Enable Learning Features

```bash
# Copy environment template
cp .env.example .env.learning

# Edit .env.learning
FEATURE_KAFKA_STREAMING=true
FEATURE_TIMESCALEDB=true
FEATURE_DUCKDB=true
```

### 2. Start Services

```bash
# Start with all learning features
docker-compose -f docker-compose.yml -f docker-compose.learning.yml \
  --profile streaming --profile timeseries --profile analytics up -d

# Check Kafka UI
open http://localhost:8080

# Check Jupyter
open http://localhost:8888
```

### 3. Run Examples

```bash
# Send test event to Kafka
python streaming/kafka_producer.py

# Check events in database
docker exec -it mediai_postgres psql -U postgres -d mimic_iv \
  -c "SELECT * FROM prediction_events ORDER BY processed_at DESC LIMIT 5;"

# View in Kafka UI
open http://localhost:8080
```

---

## ✅ UPDATED RECOMMENDATION

**Original:** Remove Kafka, TimescaleDB from Phase 1
**Revised:** Implement at small scale with feature flags

**Rationale:**
- ✅ Gain production tech experience
- ✅ Build resume-worthy portfolio
- ✅ Learn distributed systems patterns
- ✅ Low risk (feature-flagged, optional)
- ✅ Minimal overhead (~768MB for all learning features)

**Trade-off:**
- ⚠️ Extra complexity (+2-3 weeks timeline)
- ⚠️ More debugging/troubleshooting
- ⚠️ Need to learn Kafka operations

**Worth it?** **YES** - for career development và hands-on experience!

---

**Next Steps:** Complete Phase 0 → Start Phase 1 MVP → Add learning features incrementally
