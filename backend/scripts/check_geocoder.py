import sys

sys.path.insert(0, "backend")

from app import config
from app.geocoding import GeocodingError, geocode

print("geocoder enabled:", config.GEOCODER_ENABLED)
for text in ["Hitec City Metro Station", "Charminar", "qwerty asdf"]:
    try:
        found = geocode(text)
    except GeocodingError as error:
        print(text, "-> ERROR:", error)
        continue
    if found is None:
        print(text, "-> not found")
    else:
        print(text, "->", found["lat"], found["lng"], "|", found["display_name"])
