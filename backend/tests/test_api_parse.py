from fastapi.testclient import TestClient

from app import main
from app.llm import LLMError

client = TestClient(main.app)

GOOD = {
    "deliveries": [
        {"id": "D1", "text": "Deliver to Madhapur"},
        {"id": "D2", "text": "kondapur"},
    ],
    "instructions": "",
}


def test_parse_success(monkeypatch):
    def fake(deliveries, instructions):
        return {
            "deliveries": [
                {
                    "id": d["id"],
                    "original_text": d["text"],
                    "extracted_address": "x",
                    "location_id": "madhapur",
                    "display_address": "Madhapur",
                }
                for d in deliveries
            ],
            "clarifications": [],
        }

    monkeypatch.setattr(main, "extract_deliveries", fake)
    response = client.post("/api/parse", json=GOOD)
    assert response.status_code == 200
    assert response.json()["deliveries"][0]["location_id"] == "madhapur"


def test_parse_llm_failure_returns_503(monkeypatch):
    def fake(deliveries, instructions):
        raise LLMError("The language model is temporarily unavailable.")

    monkeypatch.setattr(main, "extract_deliveries", fake)
    response = client.post("/api/parse", json=GOOD)
    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"]


def test_parse_blank_text_rejected():
    body = {"deliveries": [{"id": "D1", "text": "   "}], "instructions": ""}
    assert client.post("/api/parse", json=body).status_code == 422


def test_parse_duplicate_ids_rejected():
    body = {
        "deliveries": [
            {"id": "D1", "text": "Madhapur"},
            {"id": "D1", "text": "Kondapur"},
        ],
        "instructions": "",
    }
    assert client.post("/api/parse", json=body).status_code == 422
