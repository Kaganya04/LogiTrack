import httpx

depot = [78.376, 17.447]
points = [
    [78.391, 17.448], [78.357, 17.462],
    [78.365, 17.440], [78.400, 17.440],
    [78.385, 17.460], [78.405, 17.455],
    [78.355, 17.450], [78.395, 17.465],
]

for count in (5, 8):
    for round_trip in (True, False):
        vehicle = {
            "id": 1, "description": "Delivery van",
            "profile": "auto", "start": depot,
        }
        if round_trip:
            vehicle["end"] = depot
        payload = {
            "vehicles": [vehicle],
            "jobs": [
                {"id": i + 1, "location": point}
                for i, point in enumerate(points[:count])
            ],
        }
        response = httpx.post(
            "http://127.0.0.1:3000/", json=payload, timeout=60
        )
        response.raise_for_status()
        data = response.json()
        assert data["code"] == 0
        assert not data["unassigned"]
        assert len(data["routes"]) == 1
        route = data["routes"][0]
        jobs = [s["id"] for s in route["steps"]
                if s["type"] == "job"]
        assert sorted(jobs) == list(range(1, count + 1))
        assert route["distance"] >= 0
        assert route["duration"] >= 0
        print("PASS", count, round_trip, jobs)