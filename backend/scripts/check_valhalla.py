import httpx

payload = {
    "locations": [
        {"lat": 17.447, "lon": 78.376},
        {"lat": 17.448, "lon": 78.391},
    ],
    "costing": "auto",
    "units": "kilometers",
}

response = httpx.post(
    "http://127.0.0.1:8002/route", json=payload, timeout=60
)
response.raise_for_status()
trip = response.json()["trip"]
assert trip["status"] == 0
assert trip["summary"]["length"] > 0
assert trip["summary"]["time"] > 0
print("PASS", trip["summary"])