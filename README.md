# 🔗 Watchtower — URL Shortener Platform

A production-grade URL shortener built for the MLH Production Engineering Hackathon. Features horizontal scaling, Redis caching, blue/green deployments, full observability, and a CI/CD pipeline.

**Stack:** Flask · Peewee ORM · PostgreSQL · Redis · Nginx · Docker · Prometheus · Grafana · Jenkins

---

## Architecture

```
                         ┌──────────────┐
                         │   Internet   │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                 :80/:5001│    Nginx     │
                         │ (Load Bal.)  │
                         └──┬───────┬───┘
                            │       │
                   ┌────────▼──┐ ┌──▼────────┐
                   │   web_1   │ │   web_2   │
                   │Flask:5000 │ │Flask:5000 │
                   └────┬──┬───┘ └──┬──┬─────┘
                        │  │        │  │
               ┌────────▼──▼────────▼──▼────────┐
               │                                │
        ┌──────▼──────┐               ┌─────────▼─────────┐
        │  PostgreSQL  │               │   Redis (Cache)   │
        │  (Host:5432) │               │   (Container)     │
        └──────────────┘               └───────────────────┘

        ┌──────────────────────────────────────────────────┐
        │              Monitoring Stack                    │
        │  Prometheus :9090 → Grafana :3000                │
        │  Alertmanager :9093 → Discord Webhook            │
        └──────────────────────────────────────────────────┘
```

---

## Prerequisites

- **uv** — fast Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **PostgreSQL** running locally or via Docker
- **Docker** and **Docker Compose** (for containerized deployment)

---

## Quick Start

```bash
# 1. Clone the repo
git clone git@github.com:0xTuber/PE-Hackathon-Template-2026.git
cd PE-Hackathon-Template-2026

# 2. Install dependencies
uv sync

# 3. Set up environment
cp .env.example .env   # edit DB credentials if yours differ

# 4. Create the database
createdb hackathon_db

# 5. Set up tables and seed data
PYTHONPATH=. uv run python scripts/db_setup.py

# 6. Run the server
uv run run.py

# 7. Verify
curl http://localhost:5000/health
# → {"status":"ok"}
```

### Running with Docker (Production-like)

```bash
# Start the full stack (2 replicas + nginx + redis + monitoring)
docker compose up -d --build

# Check health
curl http://localhost/health

# Open Grafana dashboard
open http://localhost:3000   # admin / hackathon
```

---

## API Reference

### System Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/health` | Health check | `{"status": "ok"}` → `200` |
| `GET` | `/metrics` | System metrics (JSON) | CPU%, RAM%, replica ID → `200` |
| `GET` | `/prom-metrics` | Prometheus metrics | Prometheus text format → `200` |
| `GET` | `/logs` | Last 100 structured log entries | JSON array → `200` |

### User Endpoints (`/api`)

| Method | Endpoint | Description | Body | Response |
|--------|----------|-------------|------|----------|
| `GET` | `/api/users` | List all users | — | `[{user}]` → `200` |
| `GET` | `/api/users/:id` | Get user by ID | — | `{user}` → `200` or `404` |
| `POST` | `/api/users` | Create user | `{"username": "...", "email": "..."}` | `{user}` → `201` or `409` |

### URL Endpoints (`/api`)

| Method | Endpoint | Description | Body | Response |
|--------|----------|-------------|------|----------|
| `GET` | `/api/urls` | List all URLs | — | `[{url}]` → `200` |
| `POST` | `/api/urls` | Create short URL | `{"original_url": "https://...", "title": "..."}` | `{url}` → `201` |

### Redirect Endpoint

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/:short_code` | Redirect to original URL | `302` redirect (cache HIT/MISS via `X-Cache-Status` header) |

### Example Requests

```bash
# Create a user
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@test.com"}'

# Shorten a URL
curl -X POST http://localhost/api/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "title": "GitHub"}'

# Follow a short link (replace abc123 with actual short code)
curl -L http://localhost/abc123
```

---

## Project Structure

```
PE-Hackathon-Template-2026/
├── app/
│   ├── __init__.py            # App factory, Prometheus instrumentation, routes
│   ├── database.py            # Peewee DatabaseProxy + connection hooks
│   ├── models/                # Peewee ORM models
│   │   ├── user.py            # User model
│   │   ├── url.py             # URL model (short_code, original_url)
│   │   └── event.py           # Click tracking events
│   └── routes/
│       ├── user.py            # CRUD for users
│       ├── url.py             # CRUD for URLs
│       └── redirect.py        # Short code redirect + Redis cache
├── deployment/
│   └── jenkinsfile            # CI/CD pipeline (blue/green)
├── docs/                      # Documentation
├── monitoring/
│   ├── prometheus.yml         # Prometheus scrape config
│   ├── alert_rules.yml        # Alert rules (4 golden signals)
│   ├── alertmanager.yml       # Discord webhook routing
│   └── grafana/               # Dashboard provisioning
├── nginx/
│   └── nginx.conf             # Load balancer config
├── scripts/
│   ├── db_setup.py            # Table creation + CSV seed loader
│   └── watchdog.py            # Health check + Discord alerts
├── seeds/                     # CSV seed data (users, urls, events)
├── tests/                     # Pytest test suite
├── docker-compose.yml         # Full stack: web×2, nginx, redis, prometheus, grafana
├── Dockerfile
├── pyproject.toml
└── locustfile.py              # Load testing scenarios
```

---

## Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov=app --cov-fail-under=70

# Run a specific test file
uv run pytest tests/test_health.py -v
```

---

## Monitoring

After deploying with Docker Compose, the monitoring stack is available at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | `http://<server>:3000` | `admin` / `hackathon` (anonymous viewing enabled) |
| **Prometheus** | `http://<server>:9090` | — |
| **Alertmanager** | `http://<server>:9093` | — |

The Grafana dashboard **"Golden Signals — Command Center"** is auto-provisioned on startup and tracks:
- **Latency**: p50/p95/p99 + per-endpoint averages
- **Traffic**: RPS by method + endpoint
- **Errors**: 5xx rate gauge + status breakdown + top error endpoints
- **Saturation**: CPU and RAM gauges per replica

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [Deploy Guide](docs/deploy_guide.md) | How to deploy and rollback |
| [Runbook](docs/runbook.md) | Step-by-step incident response |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and fixes |
| [Config Reference](docs/config_reference.md) | All environment variables |
| [Decision Log](docs/decision_log.md) | Why we chose each technology |
| [Capacity Plan](docs/capacity_plan.md) | Load limits and scaling strategy |
| [Sherlock Mode](docs/sherlock_mode.md) | Root-cause analysis walkthrough |
| [Bottleneck Report](docs/bottleneck_report.md) | Redis caching optimization |
| [Load Test Baseline](docs/load_test_baseline.md) | 50-user baseline test |
| [Load Test Swarm](docs/load_test_swarm.md) | 200-user swarm test |
