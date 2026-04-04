# 🚨 RUNBOOK — In Case of Emergency

> **Target audience**: Your 3 AM self. Follow the steps. Don't think. Just execute.

---

## 🔴 Alert: HighLatency / CriticalLatency

**What it means**: Requests are taking too long (p95 > 1s or p99 > 3s).

**Steps**:
1. **Open Grafana** → Golden Signals dashboard → Latency section
2. Check **"Avg Latency by Endpoint"** → identify which endpoint is slow
3. SSH into the server:
   ```bash
   ssh root@YOUR_SERVER
   cd /var/www/hackathon  # follow the symlink
   ```
4. Check container resource usage:
   ```bash
   docker compose stats --no-stream
   ```
5. Check app logs for slow queries:
   ```bash
   docker compose logs web_1 --tail=100 | grep -i "error\|slow\|timeout"
   docker compose logs web_2 --tail=100 | grep -i "error\|slow\|timeout"
   ```
6. Check PostgreSQL:
   ```bash
   sudo -u postgres psql -d hackathon_db -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC LIMIT 5;"
   ```
7. **If DB is the bottleneck**: Kill long-running queries, check for missing indices
8. **If CPU is pegged**: Restart containers → `docker compose restart web_1 web_2`
9. **If Redis is down**: Check `docker compose logs redis`, restart if needed

---

## 🔴 Alert: TrafficDrop (Zero Traffic)

**What it means**: No requests are reaching the app. Service may be completely down.

**Steps**:
1. **Verify externally**: `curl -I http://YOUR_DOMAIN/health` from your local machine
2. If it fails — the problem is real. SSH into the server immediately.
3. Check nginx:
   ```bash
   docker compose logs nginx --tail=50
   docker compose ps
   ```
4. Check if containers are running:
   ```bash
   docker compose ps
   ```
5. If containers are down:
   ```bash
   docker compose up -d
   ```
6. If containers are up but health fails:
   ```bash
   docker compose restart web_1 web_2 nginx
   ```
7. Check DNS/firewall if external access fails but `localhost` works on server

---

## 🔴 Alert: HighErrorRate (5xx > 5%)

**What it means**: More than 1 in 20 requests are failing with server errors.

**Steps**:
1. **Open Grafana** → Errors section → check **"Top Error Endpoints"** table
2. Check application logs:
   ```bash
   docker compose logs web_1 --tail=200 | grep "500\|ERROR\|Traceback"
   docker compose logs web_2 --tail=200 | grep "500\|ERROR\|Traceback"
   ```
3. Check structured logs:
   ```bash
   cat logs/app.jsonl | tail -50 | python3 -m json.tool
   ```
4. **Common causes**:
   - **Database connection errors** → Check PostgreSQL is running: `systemctl status postgresql`
   - **Redis connection errors** → App handles gracefully, but check: `docker compose logs redis`
   - **Code bug after deployment** → Check recent commits, consider rolling back:
     ```bash
     # Switch back to previous deployment
     LIVE=$(readlink /var/www/hackathon)
     if [ "$LIVE" = "/var/www/hackathon-blue" ]; then
         ln -sfn /var/www/hackathon-green /var/www/hackathon
     else
         ln -sfn /var/www/hackathon-blue /var/www/hackathon
     fi
     cd /var/www/hackathon && docker compose up -d --build
     ```

---

## 🔴 Alert: HighCPU / HighMemory

**What it means**: Server resources are running out. Service degradation imminent.

**Steps**:
1. **Open Grafana** → Saturation section → confirm which replica is affected
2. Check system-wide:
   ```bash
   htop
   docker stats --no-stream
   ```
3. Check for runaway processes:
   ```bash
   ps aux --sort=-%cpu | head -10
   ps aux --sort=-%mem | head -10
   ```
4. **If it's the app**:
   - Restart the offending container: `docker compose restart web_1` (or web_2)
   - If persistent: check for memory leaks in recent code changes
5. **If it's the system**:
   - Check for zombie processes: `ps aux | grep defunct`
   - Check disk: `df -h` (full disk causes many issues)
   - Consider scaling the droplet

---

## 🟡 Alert: TrafficSpike

**What it means**: Unusually high request volume. Could be legitimate or a DDoS.

**Steps**:
1. Check Grafana → Traffic section → is it a specific endpoint?
2. Check access logs for suspicious patterns:
   ```bash
   docker compose logs nginx --tail=500 | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
   ```
3. **If it's a DDoS**: Block offending IPs with UFW:
   ```bash
   sudo ufw deny from SUSPICIOUS_IP
   ```
4. **If legitimate**: Monitor saturation gauges — scale if needed

---

## 📞 Escalation

If none of the above resolves the issue within 15 minutes:
1. Post in the team Discord channel with:
   - Which alert fired
   - What you've tried so far
   - Screenshot of the Grafana dashboard
2. Check the Jenkins build history: `http://YOUR_SERVER:8080/job/pe-hackathon/`
3. If a recent deploy caused it → rollback using the blue/green switch above
