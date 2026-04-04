# 🚀 Deploy Guide

## Overview

This app uses a **blue/green deployment** strategy via Jenkins CI/CD. Two deployment directories exist on the server:
- `/var/www/hackathon-blue`
- `/var/www/hackathon-green`

A symlink `/var/www/hackathon` always points to the **live** directory. Deployments go to the **inactive** directory, are health-checked, then the symlink is switched.

---

## Deployment Flow

```
Push to main
    │
    ▼
Jenkins Pipeline Triggers
    │
    ├── Build: Install dependencies (uv sync)
    ├── Test: pytest --cov=app --cov-fail-under=70
    ├── Deploy to Staging: rsync to inactive dir, docker compose up (port 5001)
    ├── Health Check Staging: curl -f http://localhost:5001/health
    ├── Approval Gate: Manual "Deploy to Production?" prompt (15 min timeout)
    ├── Switch Traffic: Stop staging → Start production (port 80)
    └── Health Check Production: curl -f http://localhost/health
```

## How to Deploy

### Automatic (CI/CD)
Simply push to `main`:
```bash
git push origin main
```

Jenkins will automatically run the full pipeline. After staging passes, you'll get a manual approval prompt in the Jenkins UI at `http://<server>:8080`.

### Manual Deployment

```bash
# 1. SSH into the server
ssh root@YOUR_SERVER

# 2. Determine active directory
readlink /var/www/hackathon   # shows current live dir

# 3. Deploy to the OTHER directory
DEPLOY_DIR=/var/www/hackathon-green  # or -blue, whichever is NOT live
rsync -av --exclude='.git' --exclude='.venv' --exclude='.env' . $DEPLOY_DIR/

# 4. Set up database tables
cd $DEPLOY_DIR && PYTHONPATH=. uv run python scripts/db_setup.py

# 5. Start staging (verify before going live)
cd $DEPLOY_DIR
export PROXY_PORT=5001
export PROMETHEUS_PORT=19090
export GRAFANA_PORT=13000
export ALERTMANAGER_PORT=19093
export COMPOSE_PROJECT_NAME=hackathon-staging
docker compose up -d --build

# 6. Verify staging
curl http://localhost:5001/health

# 7. Switch to production
docker compose down                            # stop staging
unset PROXY_PORT PROMETHEUS_PORT GRAFANA_PORT ALERTMANAGER_PORT
export COMPOSE_PROJECT_NAME=hackathon-prod
docker compose up -d
ln -sfn $DEPLOY_DIR /var/www/hackathon         # switch symlink

# 8. Verify production
curl http://localhost/health
```

---

## How to Rollback

Rolling back means switching the symlink back to the previous directory:

```bash
# 1. Identify current and previous directories
CURRENT=$(readlink /var/www/hackathon)
echo "Currently live: $CURRENT"

# 2. Determine rollback target
if [ "$CURRENT" = "/var/www/hackathon-blue" ]; then
    ROLLBACK=/var/www/hackathon-green
else
    ROLLBACK=/var/www/hackathon-blue
fi

# 3. Stop current production
cd $CURRENT
export COMPOSE_PROJECT_NAME=hackathon-prod
docker compose down

# 4. Start the old version
cd $ROLLBACK
export COMPOSE_PROJECT_NAME=hackathon-prod
docker compose up -d

# 5. Switch symlink
ln -sfn $ROLLBACK /var/www/hackathon

# 6. Verify
curl http://localhost/health
```

**Rollback time: ~30 seconds.** The old code is already on disk — no rebuild needed.

---

## Port Reference

| Service | Production | Staging |
|---------|-----------|---------|
| Nginx (app) | 80 | 5001 |
| Prometheus | 9090 | 19090 |
| Grafana | 3000 | 13000 |
| Alertmanager | 9093 | 19093 |
