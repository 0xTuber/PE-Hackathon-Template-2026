import time
import requests
import os

# Fire Drill: Connect alerts to a channel safely
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
TARGET_URL = os.getenv("WATCHDOG_TARGET", "http://143.198.39.217") # Defaults to production

def fire_alarm(message):
    print(f"🚨 ALARM TRIGGERED 🚨: {message}")
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content": f"🚨 **PRODUCTION INCIDENT** 🚨\n{message}"}, timeout=5)
        except Exception as e:
            print(f"Failed to push to webhook: {e}")

def pull_fire_alarm():
    """Manually test the webhook integration natively"""
    fire_alarm("TEST BING! The Watchtower is successfully hooked into your channel!")

def scan_infrastructure():
    print(f"Watchdog initialized. Scanning {TARGET_URL} every 60 seconds...")
    if not WEBHOOK_URL:
        print("⚠️ WARNING: WEBHOOK_URL is not set. Alarms will only print to terminal. Add a Discord/Slack webhook to get Phone Bings!")

    while True:
        # 1. Traps: Configure alerts for "Service Down"
        try:
            health = requests.get(f"{TARGET_URL}/health", timeout=5)
            if health.status_code != 200:
                fire_alarm(f"Service Down! /health endpoint unexpectedly returned HTTP {health.status_code}")
                
            # 2. Traps: Configure alerts for CPU Bottlenecks
            try:
                metrics = requests.get(f"{TARGET_URL}/metrics", timeout=5).json()
                
                # Thresholds: "Alert if CPU > 90%"
                if metrics.get("cpu_percent", 0) > 90.0:
                    fire_alarm(f"Critical Bottleneck! Server CPU is currently pegged at {metrics['cpu_percent']}%")
            except Exception:
                pass # Safely ignored; handled cleanly by the prior Service Down check
                
        except requests.exceptions.RequestException as e:
            fire_alarm(f"Service Unreachable! Gateway timeout or fatal connection drop: {str(e)[:50]}")
            
        # Speed: Trigger must fire within 5 minutes of failure (Executing exactly every 1 minute natively!)
        time.sleep(60)

if __name__ == "__main__":
    scan_infrastructure()
