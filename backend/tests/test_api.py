from fastapi.testclient import TestClient

from app import main
from app.routing import RoutingError

client = TestClient(main.app)

GOOD = {
    "depot_id": "hitec_hub",
    "return_to_depot": True,
    "deliveries": [
        {"id": "D1", "location_id": "madhapur"},
        {"id": "D2", "location_id": "kondapur"},
    ],
}


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_optimize_success(monkeypatch):
    def fake(depot_id, deliveries, return_to_depot):
        return {
            "ordered_delivery_ids": ["D2", "D1"],
            "total_distance_km": 12.5,
            "driving_time_minutes": 30.0,
            "depot_id": depot_id,
            "return_to_depot": return_to_depot,
            "assumptions": ["demo"],
        }

    monkeypatch.setattr(main, "optimize_deliveries", fake)
    response = client.post("/api/optimize", json=GOOD)
    assert response.status_code == 200
    assert response.json()["ordered_delivery_ids"] == ["D2", "D1"]


def test_nine_deliveries_rejected():
    body = {**GOOD, "deliveries": [
        {"id": f"D{i}", "location_id": "madhapur"} for i in range(9)
    ]}
    assert client.post("/api/optimize", json=body).status_code == 422


def test_duplicate_delivery_ids_rejected():
    body = {**GOOD, "deliveries": [
        {"id": "D1", "location_id": "madhapur"},
        {"id": "D1", "location_id": "kondapur"},
    ]}
    assert client.post("/api/optimize", json=body).status_code == 422


def test_string_boolean_rejected():
    body = {**GOOD, "return_to_depot": "yes"}
    assert client.post("/api/optimize", json=body).status_code == 422


def test_unknown_location_rejected():
    body = {**GOOD, "deliveries": [{"id": "D1", "location_id": "nowhere"}]}
    assert client.post("/api/optimize", json=body).status_code == 422


def test_engine_failure_returns_503(monkeypatch):
    def fake(depot_id, deliveries, return_to_depot):
        raise RoutingError("The routing engine is temporarily unavailable.")

    monkeypatch.setattr(main, "optimize_deliveries", fake)
    response = client.post("/api/optimize", json=GOOD)
    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"]
