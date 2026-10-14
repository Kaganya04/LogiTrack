import logging

import httpx
import pytest

from app import config, geocoding
from app.geocoding import GeocodingError, geocode, inside_hyderabad
from app.logging_config import setup_logging

ADDRESS = "Road No 36, Jubilee Hills"
USER_AGENT = "LogiTrack-test (https://example.test/logitrack)"


class FakeClock:
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class FakeResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", f"https://example.test/search?q={ADDRESS}")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(f"error for {request.url}", request=request, response=response)

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    monkeypatch.setattr(config, "NOMINATIM_USER_AGENT", USER_AGENT)
    monkeypatch.setattr(config, "GEOCODER_ENABLED", True)
    fake = FakeClock()
    monkeypatch.setattr(geocoding, "time", fake)
    return fake


def mock_nominatim(monkeypatch, reply):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append({"url": url, "params": params, "headers": headers})
        if isinstance(reply, Exception):
            raise reply
        return reply if isinstance(reply, FakeResponse) else FakeResponse(reply)

    monkeypatch.setattr(geocoding.httpx, "get", fake_get)
    return calls


def place(lat, lng, name="Road No 36, Jubilee Hills, Hyderabad"):
    return [{"lat": str(lat), "lon": str(lng), "display_name": name}]


def test_request_is_bounded_to_hyderabad_and_identified(monkeypatch):
    calls = mock_nominatim(monkeypatch, place(17.43, 78.41))
    geocode(ADDRESS)
    params = calls[0]["params"]
    assert params["q"] == ADDRESS
    assert params["countrycodes"] == "in"
    assert params["bounded"] == 1
    assert params["limit"] == 1
    assert params["viewbox"] == "78.2,17.65,78.7,17.2"
    assert calls[0]["headers"]["User-Agent"] == USER_AGENT


def test_match_inside_box_is_returned(monkeypatch):
    mock_nominatim(monkeypatch, place(17.43, 78.41))
    assert geocode(ADDRESS) == {
        "lat": 17.43,
        "lng": 78.41,
        "display_name": "Road No 36, Jubilee Hills, Hyderabad",
    }


def test_match_outside_box_is_rejected(monkeypatch):
    mock_nominatim(monkeypatch, place(19.07, 72.87, "Mumbai"))
    assert geocode(ADDRESS) is None


def test_no_match_returns_none(monkeypatch):
    mock_nominatim(monkeypatch, [])
    assert geocode(ADDRESS) is None


def test_results_are_cached_by_normalized_text(monkeypatch):
    calls = mock_nominatim(monkeypatch, place(17.43, 78.41))
    first = geocode(ADDRESS)
    second = geocode("  road no 36   JUBILEE hills ")
    assert first == second
    assert len(calls) == 1


def test_misses_are_cached_too(monkeypatch):
    calls = mock_nominatim(monkeypatch, [])
    geocode(ADDRESS)
    geocode(ADDRESS)
    assert len(calls) == 1


def test_timeout_is_an_error_and_is_not_cached(monkeypatch):
    calls = mock_nominatim(monkeypatch, httpx.ConnectTimeout("timed out"))
    for _ in range(2):
        with pytest.raises(GeocodingError):
            geocode(ADDRESS)
    assert len(calls) == 2


def test_server_error_is_an_error(monkeypatch):
    mock_nominatim(monkeypatch, FakeResponse([], status=503))
    with pytest.raises(GeocodingError):
        geocode(ADDRESS)


@pytest.mark.parametrize(
    "reply",
    [
        FakeResponse(ValueError("not json")),
        {"error": "Unable to geocode"},
        [{"lat": "abc", "lon": "78.4"}],
        [{"display_name": "no coordinates"}],
    ],
)
def test_malformed_answer_is_an_error(monkeypatch, reply):
    mock_nominatim(monkeypatch, reply)
    with pytest.raises(GeocodingError):
        geocode(ADDRESS)


def test_requests_are_at_least_one_second_apart(monkeypatch, clock):
    mock_nominatim(monkeypatch, place(17.43, 78.41))
    geocode(ADDRESS)
    geocode("Charminar")
    geocode(ADDRESS)  # cache hit, no request and no wait
    assert clock.sleeps == [1.0]


@pytest.mark.parametrize(
    "enabled, agent",
    [(False, USER_AGENT), (True, ""), (True, "replace_with_app_name_and_public_repo_url")],
)
def test_disabled_or_unidentified_geocoder_makes_no_request(monkeypatch, enabled, agent):
    monkeypatch.setattr(config, "GEOCODER_ENABLED", enabled)
    monkeypatch.setattr(config, "NOMINATIM_USER_AGENT", agent)
    calls = mock_nominatim(monkeypatch, place(17.43, 78.41))
    with pytest.raises(GeocodingError):
        geocode(ADDRESS)
    assert calls == []


def test_logs_and_errors_never_contain_the_address(monkeypatch, caplog):
    monkeypatch.setattr(logging.getLogger("logitrack"), "propagate", True)
    caplog.set_level(logging.INFO)
    mock_nominatim(monkeypatch, place(17.43, 78.41))
    geocode(ADDRESS)
    mock_nominatim(monkeypatch, FakeResponse([], status=503))
    with pytest.raises(GeocodingError) as info:
        geocode("Charminar")

    assert caplog.records
    assert "Jubilee" not in caplog.text
    assert "Charminar" not in caplog.text
    assert "Charminar" not in str(info.value)
    assert info.value.__cause__ is None


def test_httpx_request_urls_are_not_logged():
    setup_logging()
    assert logging.getLogger("httpx").getEffectiveLevel() >= logging.WARNING


def test_inside_hyderabad_box_edges():
    assert inside_hyderabad(17.20, 78.20)
    assert inside_hyderabad(17.65, 78.70)
    assert not inside_hyderabad(17.19, 78.40)
    assert not inside_hyderabad(17.40, 78.71)
