import time
import requests
from prometheus_client import start_http_server, Gauge

APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5

confidence_gauge = Gauge(
    "prediction_confidence_score",
    "Latest prediction confidence score from the sentiment API"
)


def poll():
    while True:
        try:
            resp = requests.get(APP_URL, timeout=3)
            data = resp.json()
            confidence = float(data.get("confidence", 1.0))
        except Exception:
            confidence = 1.0

        confidence_gauge.set(confidence)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    start_http_server(8000)
    poll()
