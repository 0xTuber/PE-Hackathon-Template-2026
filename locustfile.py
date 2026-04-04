from locust import HttpUser, task, between
import random
import string

class URLShortenerUser(HttpUser):
    # Simulates a user waiting 1 to 3 seconds between actions
    wait_time = between(1, 3)

    @task(1)
    def create_short_url(self):
        """Simulates a user generating a shortened URL."""
        random_suffix = ''.join(random.choices(string.ascii_letters, k=8))
        self.client.post("/api/urls", json={
            "original_url": f"https://loadtest.com/param/{random_suffix}",
            "title": "Load Test Generated URL"
        }, name="/api/urls (POST)")

    @task(2)
    def fetch_urls(self):
        """Simulates a user looking at the publicly available URLs."""
        self.client.get("/api/urls", name="/api/urls (GET)")

    @task(3)
    def check_health(self):
        """Simulates basic gateway routing pulses."""
        self.client.get("/health", name="/health")
