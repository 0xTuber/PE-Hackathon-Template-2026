# Failure Manual (Chaos Modes)

This documentation exclusively defines exactly what natively occurs when the application encounters destructive actions, maintaining High Availability universally under all vectors!

## 1. Process Termination (The Immortal Restart)
**Scenario**: The core python web-server logic natively crashes un-gracefully, runs entirely out of server memory (`OOM`), or is explicitly and aggressively killed by operators.
**Architectural Fallback**: We deployed a native Ubuntu `systemd` worker file configured explicitly with `Restart=always` instructing the native operating system daemon to aggressively reboot the server within milliseconds if the main evaluation dies organically or artificially.
**Live Verification Check**: 
Go ahead, purposefully kill the app using root:
```bash
# Natively terminate the process instance instantly
sudo pkill -9 gunicorn

# Ensure the server continues evaluating smoothly via system daemon re-allocations
sudo systemctl status hackathon
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
