from flask import Flask, request, jsonify
import re

app = Flask(__name__)

POSITIVE_WORDS = {"good","great","excellent","happy","love",
 "wonderful","best","amazing","fantastic","superb"}
NEGATIVE_WORDS = {"bad","terrible","horrible","hate","worst",
 "awful","poor","dreadful","disgusting"}

_last_confidence = 0.95


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "rule-based-stable-v0",
                     "model_version": "stable-v0-3E4E"})


@app.route("/predict", methods=["POST"])
def predict():
    global _last_confidence
    data = request.get_json()
    words = set(re.findall(r'\w+', data.get('text', '').lower()))
    if len(words & NEGATIVE_WORDS) > len(words & POSITIVE_WORDS):
        label, confidence = "NEGATIVE", 0.92
    else:
        label, confidence = "POSITIVE", 0.95
    _last_confidence = confidence
    return jsonify({"label": label, "confidence": confidence,
                     "model_version": "stable-v0-3E4E"})


@app.route("/api/latest-confidence", methods=["GET"])
def latest_confidence():
    return jsonify({"confidence": _last_confidence})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
