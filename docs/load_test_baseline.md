# Baseline Load Test Documentation

### Execution Command
To gather your terminal screenshot containing exactly **50 concurrent users**, test directly against your live production server by running:

```bash
uv run locust --headless -u 50 -r 10 --run-time 30s --host http://<YOUR_SERVER_IP>
```
This instructs `Locust` to spin up 50 isolated concurrent user streams (spawning 10 per second) completely isolated from a web interface (Terminal Mode), attacking the target backend dynamically. 

### Metrics to Record
When the test completes after 30 seconds, Locust will print a final aggregate array:
- Take your screenshot demonstrating `50 users`. 
- Look under the **"p95"** column (95th PERCENTILE RESPONSE TIME)—that is the baseline millisecond marker you need to submit for your p95 latency.
- Look under the **"Fails"** and **"Error Rate"** columns. These verify if any dropped packets hit a 500 server crash.
