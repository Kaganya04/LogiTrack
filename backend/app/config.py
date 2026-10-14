import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

VROOM_URL = os.getenv("VROOM_URL", "http://127.0.0.1:3000")
VALHALLA_URL = os.getenv("VALHALLA_URL", "http://127.0.0.1:8002")
REQUEST_TIMEOUT_SECONDS = 60

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")
LLM_TIMEOUT_SECONDS = 30
# Development only: simulate the model reply instead of calling Gemini.
LLM_STUB = os.getenv("LLM_STUB", "false").strip().lower() == "true"

# Nominatim (OpenStreetMap) usage policy: at most one request per second,
# an identifying User-Agent, and results cached on our side.
NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "")
GEOCODER_ENABLED = os.getenv("GEOCODER_ENABLED", "true").strip().lower() == "true"
GEOCODER_TIMEOUT_SECONDS = 10
GEOCODER_MIN_INTERVAL_SECONDS = 1.0
GEOCODER_CACHE_SIZE = 256

# Only coordinates inside this box are accepted, from the geocoder or from clients.
HYDERABAD_BBOX = {"min_lat": 17.20, "max_lat": 17.65, "min_lng": 78.20, "max_lng": 78.70}
