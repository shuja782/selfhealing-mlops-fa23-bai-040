from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import time, random, os

app = Flask(__name__)
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english")

LOG_FILE = "/app/logs/predictions.log"
os.makedirs("/app/logs", exist_ok=True)
_request_count = 0
_drift_injected = False


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "distilbert-sentiment-v1",
                     "model_version": "unstable-v1"})


@app.route("/predict", methods=["POST"])
def predict():
    global _request_count, _drift_injected
    _request_count += 1
    data = request.get_json()
    text = data.get("text", "")
    result = classifier(text)[0]
    confidence = result["score"]
    if _drift_injected:
        confidence = confidence * random.uniform(0.3, 0.6)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.time()},{confidence:.4f}\n")
    return jsonify({"label": result["label"], "confidence": round(confidence, 4),
                     "model_version": "unstable-v1", "request_count": _request_count})


@app.route("/api/latest-confidence", methods=["GET"])
def latest_confidence():
    """Polled by exporter.py on EC2."""
    try:
        with open(LOG_FILE, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if lines:
            _, conf = lines[-1].split(",")
            return jsonify({"confidence": float(conf)})
    except Exception:
        pass
    return jsonify({"confidence": 1.0})


@app.route("/inject-drift", methods=["POST"])
def inject_drift():
    global _drift_injected
    _drift_injected = True
    return jsonify({"status": "drift_injected"})


@app.route("/reset", methods=["POST"])
def reset():
    global _drift_injected, _request_count
    _drift_injected = False
    _request_count = 0
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
