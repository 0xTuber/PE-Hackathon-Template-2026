# 🔍 Sherlock Mode — Root Cause Analysis

> Demonstrating how we diagnosed a real production issue using only our observability tools.

---

## The Incident

**Date**: April 4, 2026  
**Alert**: Health Check Staging failed — pipeline aborted  
**Symptom**: `curl -f http://localhost:5001/health` returned HTTP 500

---

## Investigation Timeline

### Step 1: Check the Error Panel

The **Errors** section of our Golden Signals dashboard immediately showed:
- **Error Rate gauge** spiked to **100%** — every single request was failing
- **HTTP Status Code Breakdown** showed only `500` responses, zero `200`s
- **Top Error Endpoints** table highlighted `/health` as the failing endpoint

This told us: *the app is running but every request triggers an internal server error.*

### Step 2: Read the Structured Logs

We checked the structured JSON logs at `/logs` endpoint (or `logs/app.jsonl`):

```json
{
  "asctime": "2026-04-04 20:26:44,807",
  "levelname": "INFO", 
  "message": "Watchtower Framework Initialized",
  "component": "system"
}
```

The app initialized successfully — so it's not a crash. The error must happen at request time.

### Step 3: Read the Health Endpoint Response

The raw health check response gave us the smoking gun:

```json
{
  "details": "connection to server at \"localhost\" (::1), port 5432 failed: Connection refused",
  "error": "Internal server error"
}
```

**Key clue**: The app was trying to connect to PostgreSQL at `localhost:5432`.

### Step 4: Check Saturation Gauges

The **Saturation** panel showed:
- **CPU**: Normal (~5%) — no resource exhaustion
- **RAM**: Normal (~40%) — no memory pressure

This confirmed: *the issue was not resource-related.* It was a connectivity problem.

### Step 5: Cross-Reference the Configuration

The `docker-compose.yml` environment variable was set as:
```yaml
DATABASE_HOST=${DATABASE_HOST:-host.docker.internal}
```

But Docker Compose automatically reads the `.env` file, which contained:
```
DATABASE_HOST=localhost
```

Inside a Docker container, `localhost` resolves to the **container itself** — not the host machine where PostgreSQL is running. The default `host.docker.internal` was being overridden.

---

## Root Cause

**Docker Compose's `.env` file loading** caused `DATABASE_HOST=localhost` to override the default `host.docker.internal`. Inside the container, `localhost` points to the container's own network namespace, where no PostgreSQL instance exists.

## Resolution

Hardcoded `DATABASE_HOST=host.docker.internal` directly in the Docker Compose environment block, making it immune to `.env` overrides:

```diff
environment:
-  - DATABASE_HOST=${DATABASE_HOST:-host.docker.internal}
+  - DATABASE_HOST=host.docker.internal
```

## How the Dashboard Helped

| Dashboard Panel | What It Told Us |
|---|---|
| **Error Rate Gauge** | 100% failure rate → total outage, not intermittent |
| **Status Code Breakdown** | Only 500s → app is running but every handler fails |
| **Top Error Endpoints** | `/health` failing → DB connectivity issue (health checks the DB) |
| **CPU/RAM Gauges** | Normal → ruled out resource exhaustion |
| **Latency Panel** | No data → requests failing before completing |

The dashboard let us go from "something is broken" to "it's a database connectivity issue" in under 60 seconds, and the logs pinpointed the exact cause.
