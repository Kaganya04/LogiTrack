from app import routing
from app.routing import optimize_deliveries


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def test_coordinate_delivery_becomes_lng_lat_job(monkeypatch):
    sent = []
    reply = {
        "code": 0,
        "unassigned": [],
        "routes": [
            {
                "distance": 9000,
                "duration": 1200,
                "steps": [{"type": "start"}, {"type": "job", "id": 2}, {"type": "job", "id": 1}],
            }
        ],
    }

    def fake_post(url, json, timeout):
        sent.append(json)
        return FakeResponse(reply)

    monkeypatch.setattr(routing.httpx, "post", fake_post)
    deliveries = [
        {"id": "D1", "location_id": "madhapur", "lat": None, "lng": None},
        {"id": "D2", "location_id": None, "lat": 17.3616, "lng": 78.4747},
    ]
    result = optimize_deliveries("hitec_hub", deliveries, False)
    jobs = sent[0]["jobs"]
    assert jobs[0]["location"] == [78.391, 17.448]
    assert jobs[1]["location"] == [78.4747, 17.3616]
    assert result["ordered_delivery_ids"] == ["D2", "D1"]
