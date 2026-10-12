import pytest

from app.preprocessing import clean_lines, clean_text, validate_lines


def test_clean_text_trims_and_collapses_spaces():
    assert clean_text("   Madhapur    Hyderabad  ") == "Madhapur Hyderabad"


def test_clean_lines_drops_blank_lines():
    assert clean_lines("Madhapur\n\n   \nKondapur") == ["Madhapur", "Kondapur"]


def test_validate_rejects_empty_list():
    with pytest.raises(ValueError):
        validate_lines([])


def test_validate_rejects_nine_deliveries():
    with pytest.raises(ValueError):
        validate_lines(["Madhapur"] * 9)


def test_validate_accepts_eight_deliveries():
    validate_lines(["Madhapur"] * 8)


def test_validate_rejects_oversized_text():
    with pytest.raises(ValueError):
        validate_lines(["a" * 301])
