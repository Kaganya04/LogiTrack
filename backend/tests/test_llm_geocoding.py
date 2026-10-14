import json

from app import llm
from app.geocoding import GeocodingError
from app.llm import extract_deliveries

DELIVERIES = [
    {"id": "D1", "text": "Deliver to Madhapur"},
    {"id": "D2", "text": "Road No 36, Jubilee Hills"},
    {"id": "D3", "text": "Charminar"},
]
ADDRESSES = [("D1", "Madhapur"), ("D2", "Road No 36, Jubilee Hills"), ("D3", "Charminar")]
MATCH = {"lat": 17.43, "lng": 78.41, "display_name": "Road No 36, Jubilee Hills, Hyderabad"}


def setup(monkeypatch, geocoder, pairs=ADDRESSES):
    reply = json.dumps(
        {"deliveries": [{"id": i, "address_text": t} for i, t in pairs], "clarifications": []}
    )
    monkeypatch.setattr(llm, "call_model", lambda prompt: reply)
    calls = []

    def fake_geocode(text):
        calls.append(text)
        return geocoder(text)

    monkeypatch.setattr(llm, "geocode", fake_geocode)
    return calls


def test_catalogue_match_never_calls_geocoder(monkeypatch):
    calls = setup(monkeypatch, lambda text: MATCH)
    first = extract_deliveries(DELIVERIES)["deliveries"][0]
    assert first["source"] == "catalogue"
    assert first["location_id"] == "madhapur"
    assert (first["lat"], first["lng"]) == (17.448, 78.391)
    assert "Madhapur" not in calls


def test_unmatched_address_is_geocoded(monkeypatch):
    setup(monkeypatch, lambda text: MATCH)
    result = extract_deliveries(DELIVERIES)
    second = result["deliveries"][1]
    assert second["source"] == "geocoded"
    assert second["location_id"] is None
    assert (second["lat"], second["lng"]) == (17.43, 78.41)
    assert second["display_address"] == "Road No 36, Jubilee Hills, Hyderabad"
    assert result["clarifications"] == []


def test_no_geocoder_match_is_unresolved_with_clarification(monkeypatch):
    setup(monkeypatch, lambda text: MATCH if "Jubilee" in text else None)
    result = extract_deliveries(DELIVERIES)
    third = result["deliveries"][2]
    assert third["source"] == "none"
    assert third["lat"] is None and third["display_address"] is None
    assert any("D3" in c for c in result["clarifications"])


def test_geocoder_outage_keeps_catalogue_and_adds_notes(monkeypatch):
    def down(text):
        raise GeocodingError("The address lookup service is not available.")

    calls = setup(monkeypatch, down)
    result = extract_deliveries(DELIVERIES)
    sources = [d["source"] for d in result["deliveries"]]
    assert sources == ["catalogue", "none", "none"]
    assert len(calls) == 1
    notes = [c for c in result["clarifications"] if "unavailable" in c]
    assert any("D2" in c for c in notes) and any("D3" in c for c in notes)


def test_blank_address_is_not_geocoded(monkeypatch):
    calls = setup(monkeypatch, lambda text: MATCH, [("D1", "Madhapur"), ("D2", " "), ("D3", "Charminar")])
    result = extract_deliveries(DELIVERIES)
    assert result["deliveries"][1]["source"] == "none"
    assert calls == ["Charminar"]
