import pytest

from app import config, geocoding, llm


@pytest.fixture(autouse=True)
def llm_stub_off(monkeypatch):
    """Tests use the real model path unless they turn the stub on themselves."""
    monkeypatch.setattr(config, "LLM_STUB", False)


@pytest.fixture(autouse=True)
def no_real_geocoding(monkeypatch):
    """Keep tests offline: the parser gets no geocoder matches and real lookups fail."""

    def no_network(*args, **kwargs):
        raise AssertionError("Tests must not make real geocoding requests")

    monkeypatch.setattr(geocoding.httpx, "get", no_network)
    monkeypatch.setattr(llm, "geocode", lambda text: None)
    geocoding.reset()
    yield
    geocoding.reset()
