from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_every_response_has_a_request_id():
    response = client.get("/api/health")
    assert len(response.headers["x-request-id"]) == 8


def test_request_ids_differ_between_requests():
    first = client.get("/api/health").headers["x-request-id"]
    second = client.get("/api/health").headers["x-request-id"]
    assert first != second
