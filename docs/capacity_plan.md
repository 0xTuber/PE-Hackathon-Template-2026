# 📊 Capacity Plan

How many users can this system handle, where are the limits, and how to scale.

---

## Current Architecture

| Component | Instances | Resources |
|-----------|-----------|-----------|
| Flask (Gunicorn 4 workers) | 2 replicas | 0.75 CPU, 512MB RAM each |
| Nginx | 1 | Default (minimal overhead) |
| Redis | 1 | Alpine (in-memory cache) |
| PostgreSQL | 1 (host) | Shared system resources |

**Total concurrent request handlers:** 2 replicas × 4 workers = **8 synchronous handlers**

---

## Load Test Results

### Baseline (50 Users)
- **RPS:** ~50 req/s
- **p95 Latency:** < 500ms
- **Error Rate:** 0%
- **Status:** ✅ Comfortable

### Swarm (200 Users)
- **RPS:** ~150 req/s
- **p95 Latency:** < 3s
- **Error Rate:** < 5%
- **Status:** ✅ Manageable with Redis caching

### Stress (500 Users)
- Without Redis: Error rates spike past 5%, database locks
- With Redis: Redirect (cache HIT) stays fast, write endpoints degrade

---

## Bottleneck Analysis

### 1. Database Writes (Primary Bottleneck)
Every URL creation and redirect event requires a PostgreSQL `INSERT`. Under heavy load:
- Connection pool exhausts
- Peewee's `fn.MAX(id) + 1` pattern creates contention

**Limit:** ~100-150 write-heavy req/s before degradation

### 2. Gunicorn Sync Workers
With 8 total workers (sync mode), only 8 requests can be processed simultaneously. Any request waiting on a slow DB query blocks the worker.

**Limit:** 8 concurrent requests in-flight

### 3. Redis Cache (Not a Bottleneck)
Redis handles 100K+ ops/sec. URL redirect cache hits bypass all DB work. This is our fastest path.

### 4. Nginx (Not a Bottleneck)
Nginx can handle 10K+ concurrent connections with minimal CPU. It's purely proxying.

---

## Capacity Estimates

| Scenario | Max Users | Max RPS | Constraint |
|----------|-----------|---------|------------|
| Read-heavy (redirects, cached) | ~500 | ~300 | Worker count |
| Mixed (reads + writes) | ~200 | ~150 | DB write contention |
| Write-heavy (URL creation) | ~100 | ~80 | DB connection pool |

---

## Scaling Strategy

### Short-term (Drop-in, No Architecture Changes)

| Action | Impact | Effort |
|--------|--------|--------|
| Add `web_3`, `web_4` replicas | +4 workers each | 5 min (copy block in docker-compose) |
| Increase Gunicorn workers to 8 | 2× throughput per replica | 1 min (edit Dockerfile CMD) |
| Switch to gevent async workers | 100+ concurrent per worker | 10 min (change worker class) |
| Use server-side connection pooling (PgBouncer) | Eliminate DB connection overhead | 15 min |

### Medium-term (Moderate Changes)

| Action | Impact | Effort |
|--------|--------|--------|
| Async event logging (write to Redis, flush to DB in batches) | Remove write bottleneck | 1-2 hours |
| Use UUID/ULID for IDs instead of `MAX(id)+1` | Eliminate ID contention | 30 min |
| Read replicas for PostgreSQL | Scale reads independently | 1 hour |

### Long-term (Architecture Changes)

| Action | Impact | Effort |
|--------|--------|--------|
| Kubernetes orchestration | Auto-scaling, self-healing | Days |
| Event streaming (Kafka/RabbitMQ) for analytics | Fully async writes | Days |
| CDN for redirect caching | Offload traffic globally | Hours |

---

## Monitoring Thresholds

Alerts are configured to fire before we hit hard limits:

| Metric | Warning | Critical |
|--------|---------|----------|
| p95 Latency | > 1s | > 3s |
| Error Rate | — | > 5% |
| CPU Usage | — | > 90% for 3 min |
| RAM Usage | — | > 85% for 3 min |
| Traffic | Spike > 500 RPS | Drop to 0 for 3 min |

These thresholds are defined in `monitoring/alert_rules.yml` and route to Discord via Alertmanager.
