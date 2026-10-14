import logging

import pytest

from app import config, llm
from app.llm import STUB_NOTE, TIME_NOTE, LLMError, build_prompt, extract_deliveries
from app.schemas import LLMExtraction

DELIVERIES = [
    {"id": "D1", "text": "Deliver to Madhapur"},
    {"id": "D2", "text": "deliver at Kondapur, Hyderabad"},
    {"id": "D3", "text": "Charminar"},
]


@pytest.fixture
def stub_on(monkeypatch):
    monkeypatch.setattr(config, "LLM_STUB", True)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")

    def no_gemini(*args, **kwargs):
        raise AssertionError("Stub mode must not call Gemini")

    monkeypatch.setattr("google.genai.Client", no_gemini)


def test_stub_reply_has_the_model_shape_and_every_id_once(stub_on):
    raw = llm.call_model(build_prompt(DELIVERIES, ""))
    extraction = LLMExtraction.model_validate_json(raw)
    assert [d.id for d in extraction.deliveries] == ["D1", "D2", "D3"]
    assert [d.address_text for d in extraction.deliveries] == [
        "Madhapur",
        "Kondapur, Hyderabad",
        "Charminar",
    ]
    assert extraction.clarifications == [STUB_NOTE]


def test_stub_flows_through_catalogue_matching(stub_on):
    result = extract_deliveries(DELIVERIES)
    assert [d["location_id"] for d in result["deliveries"][:2]] == ["madhapur", "kondapur"]
    assert STUB_NOTE in result["clarifications"]


@pytest.mark.parametrize(
    "instructions",
    ["Deliver D2 before 10am", "D1 by 5 pm", "Use the morning window", "Deadline is noon"],
)
def test_time_words_add_scheduling_note(stub_on, instructions):
    result = extract_deliveries(DELIVERIES, instructions)
    assert TIME_NOTE in result["clarifications"]


@pytest.mark.parametrize("instructions", ["", "Be careful with the parcels", "Ring the bell"])
def test_no_time_words_no_scheduling_note(stub_on, instructions):
    result = extract_deliveries(DELIVERIES, instructions)
    assert TIME_NOTE not in result["clarifications"]


def test_stub_logs_warning_without_address_text(stub_on, monkeypatch, caplog):
    monkeypatch.setattr(logging.getLogger("logitrack"), "propagate", True)
    caplog.set_level(logging.INFO)
    extract_deliveries(DELIVERIES)
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("LLM stub mode is ON" in r.getMessage() for r in warnings)
    for word in ("Madhapur", "Kondapur", "Charminar"):
        assert word not in caplog.text


def test_stub_off_keeps_real_path(monkeypatch):
    monkeypatch.setattr(config, "LLM_STUB", False)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    with pytest.raises(LLMError):
        llm.call_model(build_prompt(DELIVERIES, ""))
