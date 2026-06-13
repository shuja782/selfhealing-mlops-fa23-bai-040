import requests

BASE_URL = "http://localhost:5000"


def test_health_endpoint():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "model_version" in data


def test_predict_returns_label_and_confidence():
    resp = requests.post(f"{BASE_URL}/predict",
                          json={"text": "This is a great product"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["label"] in ["POSITIVE", "NEGATIVE"]
    assert 0 <= data["confidence"] <= 1
    assert "model_version" in data


def test_predict_negative_text():
    resp = requests.post(f"{BASE_URL}/predict",
                          json={"text": "This is a terrible and horrible experience"})
    assert resp.status_code == 200


def test_health_returns_model_version_unstable():
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    assert data["model_version"] == "unstable-v1"
