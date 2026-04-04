# 🔧 Troubleshooting Guide

Real issues encountered during this hackathon and how they were resolved.

---

## Issue 1: Health Check Returns 500 — Database Connection Refused

**Symptoms:**
```json
{
  "details": "connection to server at \"localhost\" (::1), port 5432 failed: Connection refused",
  "error": "Internal server error"
}
```

**Root Cause:**
Docker Compose reads the `.env` file automatically. The `.env` had `DATABASE_HOST=localhost`, which overrides the `host.docker.internal` default in `docker-compose.yml`. Inside a container, `localhost` points to the container itself — not the host machine running PostgreSQL.

**Fix:**
Hardcode `DATABASE_HOST=host.docker.internal` in the Docker Compose environment (not using `${DATABASE_HOST:-...}` substitution):
```yaml
environment:
  - DATABASE_HOST=host.docker.internal  # NOT ${DATABASE_HOST:-host.docker.internal}
```

---

## Issue 2: Port Conflict During Blue/Green Switch

**Symptoms:**
```
Error response from daemon: Bind for 0.0.0.0:9090 failed: port is already allocated
```

**Root Cause:**
The Jenkinsfile started production containers before stopping staging. Both tried to bind ports 9090 (Prometheus), 3000 (Grafana), and 9093 (Alertmanager).

**Fix:**
1. Assign offset ports for staging monitoring services (19090, 13000, 19093)
2. Reorder the Switch Traffic stage to stop staging BEFORE starting production

---

## Issue 3: `prometheus-flask-instrumentator` Dependency Not Found

**Symptoms:**
```
No solution found: prometheus-flask-instrumentator>=6.1.0 are unsatisfiable
```

**Root Cause:**
The package `prometheus-flask-instrumentator` hasn't been updated since 2020 (v4.1.1). Version >=6.1.0 doesn't exist.

**Fix:**
Switch to `prometheus-flask-exporter` (actively maintained, v0.23.2):
```toml
"prometheus-flask-exporter>=0.23.0"
```

---

## Issue 4: Gunicorn Workers Not Starting (Container)

**Symptoms:**
Workers boot but the app log says "Watchtower Framework not Initialized" or responses hang.

**Possible Causes:**
1. Database not created → run `scripts/db_setup.py`
2. `.env` missing in deploy directory → check rsync exclusions
3. Redis not reachable → check container networking

**Fix:**
```bash
# Check container logs
docker compose logs web_1 --tail=50

# Verify database connectivity from container
docker compose exec web_1 python -c "from app.database import db; db.connect(); print('OK')"

# Rebuild
docker compose up -d --build
```

---

## Issue 5: Tests Fail Locally but Pass in CI

**Possible Causes:**
1. Stale `test_db.sqlite` from a previous run
2. Missing dependencies

**Fix:**
```bash
rm test_db.sqlite
uv sync
uv run pytest
```

---

## General Debugging

```bash
# Check all container statuses
docker compose ps

# View live logs
docker compose logs -f

# Check resource usage
docker stats --no-stream

# Check PostgreSQL on host
sudo systemctl status postgresql
sudo -u postgres psql -d hackathon_db -c "SELECT 1;"

# Check Redis
docker compose exec redis redis-cli ping    # → PONG
```
