import pytest


def _vec(n, base=0.0, step=0.01):
    return [base + i * step for i in range(n)]


def test_api_enroll_happy_path(client):
    payload = {
        "user_id": "tim",
        "embeddings": [_vec(8, 0.10), _vec(8, 0.11), _vec(8, 0.09)],
    }
    r = client.post("/api/faceid/enroll", json=payload)
    assert r.status_code == 201

    data = r.get_json()
    assert data["status"] == "ok"
    assert data["user_id"] == "tim"
    assert data["samples_added"] == 3
    assert "recommended_threshold" in data


def test_api_enroll_rejects_missing_fields(client):
    r = client.post("/api/faceid/enroll", json={"user_id": "tim"})
    assert r.status_code == 400
    data = r.get_json()
    assert data["error"] == "validation_error"


def test_api_verify_happy_match(client):
    # enroll first
    client.post("/api/faceid/enroll", json={
        "user_id": "tim",
        "embeddings": [_vec(8, 0.10), _vec(8, 0.11), _vec(8, 0.09)],
    })

    r = client.post("/api/faceid/verify", json={"user_id": "tim", "embedding": _vec(8, 0.105)})
    assert r.status_code == 200
    data = r.get_json()

    assert data["user_id"] == "tim"
    assert data["match"] is True
    assert data["distance"] <= data["threshold"]


def test_api_verify_unknown_user(client):
    r = client.post("/api/faceid/verify", json={"user_id": "missing", "embedding": _vec(8, 0.1)})
    assert r.status_code == 404
    data = r.get_json()
    assert data["error"] == "user_not_enrolled"


def test_api_verify_rejects_invalid_embedding(client):
    r = client.post("/api/faceid/verify", json={"user_id": "tim", "embedding": [1.0, 2.0, "bad"]})
    assert r.status_code == 400
    data = r.get_json()
    assert data["error"] == "validation_error"
