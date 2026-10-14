import os
import sys

sys.path.insert(0, "backend")

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.llm import SYSTEM_INSTRUCTION, build_prompt
from app.schemas import LLMExtraction

load_dotenv("backend/.env")
key = os.getenv("GEMINI_API_KEY", "")
model = os.getenv("GEMINI_MODEL", "").removeprefix("models/")
print("model:", model)
deliveries = [{"id": "D1", "text": "Madhapur"}, {"id": "D2", "text": "Charminar"}]
try:
    client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=30000))
    reply = client.models.generate_content(
        model=model,
        contents=build_prompt(deliveries, ""),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=LLMExtraction,
            temperature=0,
        ),
    )
    print("REPLY:", reply.text)
except Exception as error:
    print("ERROR TYPE:", type(error).__name__)
    print("MESSAGE:", str(error).replace(key, "[KEY]") if key else str(error))
