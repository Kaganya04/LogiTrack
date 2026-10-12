import json

import pytest

from app import config, llm
from app.llm import LLMError, extract_deliveries

DELIVERIES = [
    {"id": "D1", "text": "Deliver to Madhapur"},
    {"id": "D2", "text": "kondapur, hyderabad"},
]


def model_reply(pairs, clarifications=None):
    return json.dumps(
        {
            "deliveries": [{"id": i, "address_text": t} for i, t in pairs],
            "clarifications": clarifications or [],
        }
    )


def mock_model(monkeypatch, text):
    monkeypatch.setattr(llm, "call_model", lambda prompt: text)


def test_valid_extraction_resolves_locations(monkeypatch):
    mock_model(monkeypatch, model_reply([("D1", "Madhapur"), ("D2", "Kondapur Hyderabad")]))
    result = extract_deliveries(DELIVERIES)
    assert [d["location_id"] for d in result["deliveries"]] == ["madhapur", "kondapur"]
    assert result["clarifications"] == []


def test_unknown_address_stays_unresolved_with_clarification(monkeypatch):
    mock_model(monkeypatch, model_reply([("D1", "Madhapur"), ("D2", "12 Unknown Street")]))
    result = extract_deliveries(DELIVERIES)
    assert result["deliveries"][1]["location_id"] is None
    assert any("D2" in c for c in result["clarifications"])


def test_missing_id_is_rejected(monkeypatch):
    mock_model(monkeypatch, model_reply([("D1", "Madhapur")]))
    with pytest.raises(LLMError):
        extract_deliveries(DELIVERIES)


def test_invented_id_is_rejected(monkeypatch):
    mock_model(
        monkeypatch,
        model_reply([("D1", "Madhapur"), ("D2", "Kondapur"), ("D9", "Gachibowli")]),
    )
    with pytest.raises(LLMError):
        extract_deliveries(DELIVERIES)


def test_repeated_id_is_rejected(monkeypatch):
    mock_model(monkeypatch, model_reply([("D1", "Madhapur"), ("D1", "Kondapur")]))
    with pytest.raises(LLMError):
        extract_deliveries(DELIVERIES)


def test_malformed_json_is_rejected(monkeypatch):
    mock_model(monkeypatch, "this is not json")
    with pytest.raises(LLMError):
        extract_deliveries(DELIVERIES)


def test_wrong_shape_is_rejected(monkeypatch):
    mock_model(monkeypatch, json.dumps({"foo": 1}))
    with pytest.raises(LLMError):
        extract_deliveries(DELIVERIES)


def test_time_constraint_clarification_is_passed_on(monkeypatch):
    note = "Time constraints are not supported in this version."
    mock_model(
        monkeypatch,
        model_reply([("D1", "Madhapur"), ("D2", "Kondapur")], [note]),
    )
    result = extract_deliveries(DELIVERIES, "Deliver D2 before 10am")
    assert note in result["clarifications"]


def test_prompt_contains_ids_texts_and_instructions(monkeypatch):
    seen = []

    def fake(prompt):
        seen.append(prompt)
        return model_reply([("D1", "Madhapur"), ("D2", "Kondapur")])

    monkeypatch.setattr(llm, "call_model", fake)
    extract_deliveries(DELIVERIES, "Be quick")
    assert "D1: Deliver to Madhapur" in seen[0]
    assert "<instructions>" in seen[0]
    assert "Be quick" in seen[0]


def test_missing_configuration_is_an_error(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    with pytest.raises(LLMError):
        llm.call_model("hello")


def test_provider_failure_becomes_readable_error_without_leaking_key(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "secret-test-key")
    monkeypatch.setattr(config, "GEMINI_MODEL", "some-model")

    def boom(*args, **kwargs):
        raise RuntimeError("network down secret-test-key")

    monkeypatch.setattr("google.genai.Client", boom)
    with pytest.raises(LLMError) as info:
        llm.call_model("hello")
    assert "secret-test-key" not in str(info.value)
