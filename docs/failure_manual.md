# Failure Manual (Chaos Modes)

This documentation exclusively defines exactly what natively occurs when the application encounters destructive actions, maintaining High Availability universally under all vectors!

## 1. Process Termination (The Immortal Restart)
**Scenario**: The core python web-server logic natively crashes un-gracefully, runs entirely out of server memory (`OOM`), or is explicitly and aggressively killed by operators.

**Architectural Fallback**: Every service in `docker-compose.yml` is configured with `restart: always`, instructing Docker to automatically reboot any container that exits — whether from a crash, OOM kill, or manual termination. This applies to all services: `web_1`, `web_2`, `nginx`, `redis`, `prometheus`, `grafana`, `alertmanager`, and `discord-relay`.

**Live Verification Check** — Force-kill a container and watch Docker auto-restart it:
```bash
# 1. Check current container status
docker ps --filter "name=hackathon-prod-web_1" --format "{{.ID}}  {{.Status}}"
# Output: a1b2c3d4e5f6  Up 2 hours (healthy)

# 2. Force-kill the container to simulate a crash
docker kill hackathon-prod-web_1-1

# 3. Wait 3 seconds, then verify Docker restarted it automatically
sleep 3
docker ps --filter "name=hackathon-prod-web_1" --format "{{.ID}}  {{.Status}}"
# Output: f6e5d4c3b2a1  Up 2 seconds   <-- NEW container, auto-restarted!

# 4. Confirm the service is healthy again
curl http://localhost/health
# Output: {"status":"ok"}
```

**Evidence from `docker-compose.yml`**:
```yaml
services:
  web_1:
    build: .
    restart: always   # <-- Docker auto-restarts on ANY exit
  web_2:
    build: .
    restart: always
  nginx:
    restart: always
  redis:
    restart: always
  prometheus:
    restart: always
  grafana:
    restart: always
  alertmanager:
    restart: always
  discord-relay:
    restart: always
```

## 2. Invalid or Garbage Input Delivery
**Scenario**: Users bypass our frontend web UI components and forcefully pass bad JSON structure payloads, incorrect data shapes (e.g. nested dicts instead of string urls), or unsupported binary blocks towards our core REST routers natively.
**Architectural Fallback**: Absolutely NO stack traces leak into client interfaces and the internal system architecture fundamentally blocks any crashes! We've installed a universal `Exception` catcher globally (`app/__init__.py`) which catches everything evaluated recursively, overriding native Flask exception dumps cleanly. Handled schemas natively spit back `400 Bad Requests` via polite format strings while untrapped exceptions fallback globally natively to `{ "error": "Internal server error" }`.
**Live Verification Check**:
To guarantee polite graceful failures, throw absolute broken garbage arrays natively towards the creation endpoint:
```bash
curl -X POST http://localhost:5000/api/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url": [{}, {"broken": 1}], "fake_field": null}'
```
You will receive `{ "error": ... }` JSON safely preserving application persistence seamlessly!
