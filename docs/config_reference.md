# ⚙️ Configuration Reference

All environment variables used by the application. Copy `.env.example` to `.env` and adjust as needed.

---

## Application

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (never in production) |

## Database (PostgreSQL)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_NAME` | `hackathon_db` | PostgreSQL database name |
| `DATABASE_HOST` | `localhost` | Database host (Docker containers override to `host.docker.internal`) |
| `DATABASE_PORT` | `5432` | Database port |
| `DATABASE_USER` | `postgres` | Database username |
| `DATABASE_PASSWORD` | `postgres` | Database password |

> **Note:** Inside Docker, `DATABASE_HOST` is hardcoded to `host.docker.internal` in `docker-compose.yml`. The `.env` value is only used for host-level scripts like `db_setup.py`.

## Cache (Redis)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis host (Docker defaults to `redis` service name) |

## Alerts

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_WEBHOOK` | _(empty)_ | Discord webhook URL for alerts and telemetry |
| `WATCHDOG_TARGET` | `http://localhost` | Target URL for the watchdog health checker |

## Docker Compose Overrides

These are set via `export` in the Jenkinsfile, not in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXY_PORT` | `80` | Nginx external port |
| `PROMETHEUS_PORT` | `9090` | Prometheus external port |
| `GRAFANA_PORT` | `3000` | Grafana external port |
| `ALERTMANAGER_PORT` | `9093` | Alertmanager external port |
| `COMPOSE_PROJECT_NAME` | — | Docker Compose project name (`hackathon-prod` or `hackathon-staging`) |

## Grafana

| Variable | Default | Description |
|----------|---------|-------------|
| `GF_SECURITY_ADMIN_USER` | `admin` | Grafana admin username |
| `GF_SECURITY_ADMIN_PASSWORD` | `hackathon` | Grafana admin password |
| `GF_AUTH_ANONYMOUS_ENABLED` | `true` | Allow anonymous read-only access |

---

## .env.example

```env
FLASK_DEBUG=true
DATABASE_NAME=hackathon_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```
