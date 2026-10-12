import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

VROOM_URL = os.getenv("VROOM_URL", "http://127.0.0.1:3000")
VALHALLA_URL = os.getenv("VALHALLA_URL", "http://127.0.0.1:8002")
REQUEST_TIMEOUT_SECONDS = 60
