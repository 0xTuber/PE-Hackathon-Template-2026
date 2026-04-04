# 📋 Decision Log

Technical decisions made during the hackathon and the reasoning behind each.

---

## 1. Why Nginx as the Load Balancer?

**Decision:** Use Nginx as a reverse proxy load balancer in front of two Flask replicas.

**Alternatives Considered:**
- **HAProxy** — More feature-rich for TCP load balancing, but overkill for HTTP-only
- **Traefik** — Auto-discovers containers, but harder to configure statically
- **No load balancer** — Single point of failure, no horizontal scaling

**Why Nginx:**
- Minimal config (25 lines of `nginx.conf`)
- Battle-tested at massive scale (powers ~34% of the web)
- Built-in `upstream` block handles round-robin across replicas seamlessly
- `stub_status` provides basic metrics for monitoring
- Docker Hub official image is tiny and requires zero setup

---

## 2. Why Redis for Caching?

**Decision:** Add a Redis cache layer between the app and PostgreSQL for URL lookups.

**Alternatives Considered:**
- **Memcached** — Simpler but lacks persistence and data structures
- **In-app Python dict** — Per-process only, doesn't share across replicas
- **No cache** — Every redirect hits PostgreSQL; unsustainable under load

**Why Redis:**
- Shared cache across both web replicas (containers access the same Redis instance)
- `SETEX` provides automatic TTL-based expiry (1 hour for URLs)
- `INCR` replaces expensive DB click-counting writes with atomic memory operations
- Graceful degradation — app falls back to PostgreSQL if Redis is down (try/except on `ConnectionError`)
- Alpine Docker image is ~5MB

**Impact:** Redirect latency dropped significantly under load. Requests with `X-Cache-Status: HIT` bypass the database entirely.

---

## 3. Why Peewee ORM (not SQLAlchemy)?

**Decision:** Use Peewee as the ORM for database access.

**Alternatives Considered:**
- **SQLAlchemy** — Industry standard but heavyweight with a steep learning curve
- **Raw SQL** — Maximum control but error-prone and no migration support

**Why Peewee:**
- Came with the hackathon template — zero setup cost
- Lightweight (~5K lines of code vs SQLAlchemy's ~100K)
- `model_to_dict` from playhouse makes JSON serialization trivial
- `DatabaseProxy` pattern enables swapping SQLite (tests) and PostgreSQL (prod) seamlessly

---

## 4. Why Blue/Green Deployments?

**Decision:** Implement blue/green deployment via symlink switching.

**Alternatives Considered:**
- **Rolling update** — More complex orchestration, still has mixed-version traffic
- **Canary** — Needs traffic splitting logic, overkill for 2 replicas
- **Direct deploy (yolo)** — Any failure = immediate downtime

**Why Blue/Green:**
- Zero downtime — old version keeps serving while new version starts
- Instant rollback — just switch the symlink back (~1 second)
- Simple to implement with `ln -sfn` and two directories
- Staging on port 5001 allows pre-production health checks

---

## 5. Why Prometheus + Grafana (not Datadog/New Relic)?

**Decision:** Self-hosted Prometheus + Grafana + Alertmanager for observability.

**Alternatives Considered:**
- **Datadog** — Excellent but costs money and requires an agent
- **New Relic** — Free tier exists but limited retention
- **Just logs** — Missing real-time dashboards and alerting

**Why Self-hosted Stack:**
- Free and open-source — no SaaS costs or API keys needed
- Runs as Docker containers alongside the app, zero external dependencies
- `prometheus-flask-exporter` auto-instruments every Flask route
- Grafana dashboards are JSON — versionable, provisioned automatically on startup
- Alertmanager routes to Discord via webhook — no email setup needed

---

## 6. Why Gunicorn with 4 Workers?

**Decision:** Run Flask behind Gunicorn with 4 sync workers per replica.

**Alternatives Considered:**
- **Flask dev server** — Single-threaded, not production-safe
- **uWSGI** — More features but harder to configure
- **Async workers (gevent)** — Better for I/O-heavy but adds complexity

**Why 4 Sync Workers:**
- Formula: `workers = 2 × CPU_cores + 1` (server has 2 cores → 4 workers is close)
- Sync workers are simpler to debug and avoid async pitfalls
- With 2 replicas × 4 workers = 8 concurrent request handlers total
- Container resource limits (512MB RAM, 0.75 CPU) prevent runaway usage

---

## 7. Why Discord for Alerts (not PagerDuty/Slack)?

**Decision:** Send all alerts and pipeline notifications to Discord.

**Why Discord:**
- Team already uses Discord for hackathon communication
- Webhook setup is a single URL — no OAuth, no apps, no tokens
- Rich embed formatting for alert messages
- Free, no usage limits
