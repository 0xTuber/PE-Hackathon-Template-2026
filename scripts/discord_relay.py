"""
Lightweight webhook relay: Alertmanager → Discord.
Receives Alertmanager webhook POSTs and forwards them as Discord messages.
Uses only the Python standard library — no dependencies needed.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request

DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', '')


class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))

        for alert in data.get('alerts', []):
            status = '🔴 FIRING' if alert['status'] == 'firing' else '✅ RESOLVED'
            name = alert['labels'].get('alertname', 'Unknown')
            severity = alert['labels'].get('severity', 'unknown')
            desc = alert['annotations'].get('description', 'No description')

            message = f"**{status}: {name}**\nSeverity: `{severity}`\n> {desc}"

            req = urllib.request.Request(
                DISCORD_WEBHOOK,
                data=json.dumps({'content': message}).encode(),
                headers={'Content-Type': 'application/json'}
            )
            try:
                urllib.request.urlopen(req)
            except Exception as e:
                print(f"Failed to send to Discord: {e}")

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[discord-relay] {args[0]}")


if __name__ == '__main__':
    print(f"[discord-relay] Starting on :9095, webhook={'SET' if DISCORD_WEBHOOK else 'MISSING'}")
    HTTPServer(('0.0.0.0', 9095), AlertHandler).serve_forever()
