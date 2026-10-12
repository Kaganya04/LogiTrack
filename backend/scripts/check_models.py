import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv("backend/.env")
key = os.getenv("GEMINI_API_KEY", "")
print("key set:", bool(key) and not key.startswith("replace_with"))
client = genai.Client(api_key=key)
for name in ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"]:
    try:
        reply = client.models.generate_content(model=name, contents="Reply with the word ok")
        print("WORKS:", name)
    except errors.APIError as error:
        print("FAILS:", name, "status", getattr(error, "code", "?"))
    except Exception as error:
        print("FAILS:", name, type(error).__name__)
