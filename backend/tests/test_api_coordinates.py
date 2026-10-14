import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def optimize_body(*deliveries):
    return {"depot_id": "hitec_hub", "return_to_depot": True, "deliveries": list(deliveries)}


def test_coordinates_are_accepted_and_passed_on(monkeypatch):
    seen = []

    def fake(depot_id, deliveries, return_to_depot):
        seen.extend(deliveries)
        return {
            "ordered_delivery_ids": [d["id"] for d in deliveries],
            "total_distance_km": 5.0,
            "driving_time_minutes": 12.0,
            "depot_id": depot_id,
            "return_to_depot": return_to_depot,
            "assumptions": ["demo"],
        }

    monkeypatch.setattr(main, "optimize_deliveries", fake)
    body = optimize_body(
        {"id": "D1", "location_id": "madhapur"},
        {"id": "D2", "lat": 17.43, "lng": 78.41},
    )
    response = client.post("/api/optimize", json=body)
    assert response.status_code == 200
    assert seen[1]["lat"] == 17.43 and seen[1]["lng"] == 78.41
    assert seen[1]["location_id"] is None


@pytest.mark.parametrize(
    "delivery",
    [
        {"id": "D1", "location_id": "madhapur", "lat": 17.43, "lng": 78.41},
        {"id": "D1", "lat": 17.43},
        {"id": "D1", "lng": 78.41},
        {"id": "D1"},
        {"id": "D1", "lat": 19.07, "lng": 72.87},
        {"id": "D1", "lat": "north", "lng": 78.41},
    ],
)
def test_invalid_location_forms_are_rejected(delivery):
    response = client.post("/api/optimize", json=optimize_body(delivery))
    assert response.status_code == 422


def test_parse_reports_coordinate_source(monkeypatch):
    def fake(deliveries, instructions):
        return {
            "deliveries": [
                {
                    "id": "D1",
                    "original_text": "Charminar",
                    "extracted_address": "Charminar",
                    "location_id": None,
                    "display_address": "Charminar, Hyderabad",
                    "source": "geocoded",
                    "lat": 17.3616,
                    "lng": 78.4747,
                }
            ],
            "clarifications": [],
        }

    monkeypatch.setattr(main, "extract_deliveries", fake)
    body = {"deliveries": [{"id": "D1", "text": "Charminar"}], "instructions": ""}
    item = client.post("/api/parse", json=body).json()["deliveries"][0]
    assert item["source"] == "geocoded"
    assert (item["lat"], item["lng"]) == (17.3616, 78.4747)
