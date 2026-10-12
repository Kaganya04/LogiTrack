from app.locations import get_location, load_locations, resolve_address


def test_resolves_name_with_extra_spaces():
    assert resolve_address("   Madhapur   ") == "madhapur"


def test_resolves_alias_with_comma_and_case():
    assert resolve_address("MADHAPUR, Hyderabad") == "madhapur"


def test_unknown_address_is_unresolved():
    assert resolve_address("12 Unknown Street") is None


def test_partial_name_is_not_guessed():
    assert resolve_address("Madha") is None


def test_catalogue_has_depot_and_eight_stops():
    assert len(load_locations()) == 9
    assert get_location("hitec_hub") is not None
