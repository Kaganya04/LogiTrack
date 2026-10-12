import json
import re
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "locations.json"


def normalize(text: str) -> str:
    """Lowercase, replace punctuation with spaces and collapse whitespace."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


@lru_cache(maxsize=1)
def load_locations() -> dict:
    """Load the catalogue, keyed by location id."""
    with open(DATA_FILE, encoding="utf-8") as file:
        items = json.load(file)
    return {item["id"]: item for item in items}


@lru_cache(maxsize=1)
def _alias_index() -> dict:
    """Map each normalized name or alias to the location ids that use it."""
    index = {}
    for item in load_locations().values():
        for key in [item["name"], *item["aliases"]]:
            index.setdefault(normalize(key), set()).add(item["id"])
    return index


def get_location(location_id: str):
    """Return a location by id, or None if it is unknown."""
    return load_locations().get(location_id)


def resolve_address(text: str):
    """Return a location id for an exact name or alias match, else None.

    Partial street names are never guessed, and an ambiguous alias returns None.
    """
    matches = _alias_index().get(normalize(text), set())
    return next(iter(matches)) if len(matches) == 1 else None
