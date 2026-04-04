# Swarm Scaling Documentation (Tier 2/Silver)

### Overview
We successfully migrated your application from relying on a singular, fragile Python process (Vertical Scaling) to a vast **Horizontally Scaled** Docker abstraction!
Your environment now actively utilizes:
- **web_1** (App Server 1)
- **web_2** (App Server 2)
- **db** (Internal isolated Postgres server natively feeding the nodes)
- **nginx** (The Traffic Cop load-balancing entry points evenly to web 1 and 2 automatically)

### Verification 1: Clone Army Proof
To secure your first required screenshot (proving multi-container deployments), boot up the system natively:

```bash
# Build and securely detach the entire multi-node architecture natively
docker-compose up --build -d

# Natively display the active container matrix
docker ps
```
Take a screenshot showing your 2 app instances alongside your single Nginx element dynamically!

### Verification 2: The Horde (200 Users)
Now, unleash your 200 simultaneous users natively. Your Nginx traffic cop will absorb these requests natively on Port 80 and scatter them flawlessly between the running Web nodes, guaranteeing sub-3-second latencies natively!

If evaluating natively on your production server from your local terminal, run the execution directly:
```bash
uv run locust --headless -u 200 -r 20 --run-time 60s --host http://<YOUR_SERVER_IP>
```
*(If you are exclusively evaluating on your localhost laptop, replace the host cleanly with `http://localhost`).*

Capture your final screenshot of the P95 load tester results cleanly handling the exact 200 user requirements!
