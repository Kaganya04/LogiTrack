import httpx
import pytest

from app import routing
from app.routing import RoutingError, optimize_deliveries

DELIVERIES = [
    {"id": "D1", "location_id": "madhapur"},
    {"id": "D2", "location_id": "kondapur"},
]


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def vroom_reply(job_ids, distance=12000, duration=1800):
    steps = [{"type": "start"}]
    steps += [{"type": "job", "id": job_id} for job_id in job_ids]
    steps.append({"type": "end"})
    return {
        "code": 0,
        "unassigned": [],
        "routes": [{"distance": distance, "duration": duration, "steps": steps}],
    }


def mock_vroom(monkeypatch, reply):
    sent = []

    def fake_post(url, json, timeout):
        sent.append(json)
        return FakeResponse(reply)

    monkeypatch.setattr(routing.httpx, "post", fake_post)
    return sent


def test_request_uses_auto_profile_and_lng_lat_order(monkeypatch):
    sent = mock_vroom(monkeypatch, vroom_reply([1, 2]))
    optimize_deliveries("hitec_hub", DELIVERIES, True)
    payload = sent[0]
    assert payload["vehicles"][0]["profile"] == "auto"
    assert payload["vehicles"][0]["start"] == [78.376, 17.447]
    assert payload["jobs"][0]["location"] == [78.391, 17.448]


def test_round_trip_sets_vehicle_end(monkeypatch):
    sent = mock_vroom(monkeypatch, vroom_reply([1, 2]))
    optimize_deliveries("hitec_hub", DELIVERIES, True)
    vehicle = sent[0]["vehicles"][0]
    assert vehicle["end"] == vehicle["start"]


def test_open_trip_has_no_end(monkeypatch):
    sent = mock_vroom(monkeypatch, vroom_reply([1, 2]))
    optimize_deliveries("hitec_hub", DELIVERIES, False)
    assert "end" not in sent[0]["vehicles"][0]


def test_ids_are_mapped_back_and_units_converted(monkeypatch):
    mock_vroom(monkeypatch, vroom_reply([2, 1], distance=12500, duration=1800))
    result = optimize_deliveries("hitec_hub", DELIVERIES, True)
    assert result["ordered_delivery_ids"] == ["D2", "D1"]
    assert result["total_distance_km"] == 12.5
    assert result["driving_time_minutes"] == 30


def test_two_deliveries_at_same_location_stay_separate(monkeypatch):
    sent = mock_vroom(monkeypatch, vroom_reply([1, 2]))
    same = [
        {"id": "D1", "location_id": "kondapur"},
        {"id": "D2", "location_id": "kondapur"},
    ]
    result = optimize_deliveries("hitec_hub", same, True)
    assert len(sent[0]["jobs"]) == 2
    assert sorted(result["ordered_delivery_ids"]) == ["D1", "D2"]


def test_unknown_location_and_depot_are_rejected():
    with pytest.raises(ValueError):
        optimize_deliveries("hitec_hub", [{"id": "D1", "location_id": "nowhere"}], True)
    with pytest.raises(ValueError):
        optimize_deliveries("nowhere", DELIVERIES, True)


def test_timeout_becomes_routing_error(monkeypatch):
    def fake_post(url, json, timeout):
        raise httpx.ConnectTimeout("timed out")

    monkeypatch.setattr(routing.httpx, "post", fake_post)
    with pytest.raises(RoutingError):
        optimize_deliveries("hitec_hub", DELIVERIES, True)


def test_nonzero_code_is_an_error(monkeypatch):
    mock_vroom(monkeypatch, {"code": 3, "routes": []})
    with pytest.raises(RoutingError):
        optimize_deliveries("hitec_hub", DELIVERIES, True)


def test_unassigned_job_is_an_error(monkeypatch):
    reply = vroom_reply([1])
    reply["unassigned"] = [{"id": 2}]
    mock_vroom(monkeypatch, reply)
    with pytest.raises(RoutingError):
        optimize_deliveries("hitec_hub", DELIVERIES, True)


def test_missing_route_is_an_error(monkeypatch):
    mock_vroom(monkeypatch, {"code": 0, "unassigned": [], "routes": []})
    with pytest.raises(RoutingError):
        optimize_deliveries("hitec_hub", DELIVERIES, True)


def test_repeated_job_ids_are_an_error(monkeypatch):
    mock_vroom(monkeypatch, vroom_reply([1, 1]))
    with pytest.raises(RoutingError):
        optimize_deliveries("hitec_hub", DELIVERIES, True)
