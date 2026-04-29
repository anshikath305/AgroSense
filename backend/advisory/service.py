from __future__ import annotations

import json
import os
import time
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(BACKEND_ENV_PATH)

SYSTEM_PROMPT = (
    "Expert Agronomist\n"
    "You are an expert agronomist helping farmers make safe, practical field decisions. "
    "Use concise, farmer-friendly advice and do not invent lab results, certainty, or chemical dosages. "
    "Format every answer with exactly these sections:\n"
    "1. Problem likely cause\n"
    "2. Immediate action\n"
    "3. Prevention\n"
    "4. Low-cost farmer friendly advice\n"
    "5. When to contact expert"
)

MODEL_CANDIDATES = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

DISEASE_SUMMARY_MODEL = "gemini-1.5-flash"

COMPATIBILITY_MODEL_CANDIDATES = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
]

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "hi-IN": "Hindi",
    "pa": "Punjabi",
    "pa-IN": "Punjabi",
    "ta": "Tamil",
    "ta-IN": "Tamil",
}

MODEL_RETRY_MARKERS = ("429", "RESOURCE_EXHAUSTED", "RATE_LIMIT", "NOT_FOUND", "NOT SUPPORTED")


@lru_cache(maxsize=1)
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to backend/.env to enable live advisory responses.")

    try:
        from google import genai
    except ModuleNotFoundError as exc:
        raise RuntimeError("google-genai is not installed. Run pip install -r backend/requirements.txt.") from exc

    return genai.Client(api_key=api_key)


def _strip_json_markdown(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


def get_disease_summary(plant: str, disease: str, confidence: float) -> dict:
    """
    Uses Gemini 1.5 Flash to generate a complete disease report.
    """
    client = get_gemini_client()

    system = """You are an expert plant pathologist and agricultural
advisor for Indian farmers. Always give practical, affordable,
locally available solutions. Use simple language."""

    user_prompt = f"""
The crop disease detection model has identified:
Plant: {plant}
Disease: {disease}
Confidence: {confidence}%

Give a complete disease report in this EXACT JSON format only,
no extra text, no markdown:
{{
  "disease_name": "full disease name",
  "description": "2 lines — what this disease is",
  "causes": "2 lines — why it happens (fungus/bacteria/virus/conditions)",
  "symptoms": "2 lines — visible signs on plant",
  "immediate_action": "2 lines — what farmer must do TODAY",
  "cure": "specific fungicide/pesticide names available in India with dosage",
  "prevention": "2 lines — how to prevent in next season",
  "organic_solution": "cheap natural remedy using neem/copper/turmeric etc",
  "severity": "High or Medium or Low"
}}

If disease is Healthy, fill all fields with positive/maintenance advice.
Return ONLY the JSON, nothing else.
"""

    raw_text = ""
    try:
        from google.genai import types

        try:
            response = client.models.generate_content(
                model=DISEASE_SUMMARY_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system),
            )
        except Exception as exc:
            if not _is_rate_limit_error(exc):
                raise
            response = client.models.generate_content(
                model=COMPATIBILITY_MODEL_CANDIDATES[0],
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system),
            )

        raw_text = (response.text or "").strip()
        return json.loads(_strip_json_markdown(raw_text))
    except json.JSONDecodeError:
        return {"error": "Could not parse Gemini response", "raw_text": raw_text}
    except Exception as exc:
        return {"error": "Could not fetch Gemini response", "raw_text": str(exc)}


def _normalized_language_code(lang: str | None) -> str:
    language = (lang or "en").strip()
    lookup = language.lower()
    if lookup in {"hi", "hi-in"}:
        return "hi-IN"
    if lookup in {"pa", "pa-in"}:
        return "pa-IN"
    if lookup in {"ta", "ta-in"}:
        return "ta-IN"
    return "en" if lookup.startswith("en") else language


def _language_name(lang: str | None) -> str:
    code = _normalized_language_code(lang)
    return LANGUAGE_NAMES.get(code, LANGUAGE_NAMES.get(code.lower(), code))


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return any(marker in message for marker in MODEL_RETRY_MARKERS)


def _state_name(file_obj) -> str:
    state = getattr(file_obj, "state", None)
    name = getattr(state, "name", None)
    return str(name or state or "").upper()


def _wait_for_active_file(client, uploaded_file, max_wait_seconds: int = 120):
    current_file = uploaded_file
    deadline = time.monotonic() + max_wait_seconds

    while _state_name(current_file) == "PROCESSING":
        if time.monotonic() >= deadline:
            raise RuntimeError("Gemini image upload timed out while processing.")
        time.sleep(2)
        current_file = client.files.get(name=current_file.name)

    file_state = _state_name(current_file)
    if file_state and file_state != "ACTIVE":
        raise RuntimeError(f"Gemini image upload failed with state: {file_state}")

    return current_file


def _upload_image_for_gemini(client, image_path: str):
    uploaded_file = client.files.upload(file=image_path)
    return _wait_for_active_file(client, uploaded_file)


def build_context(query: str, disease_result: dict | None, lang: str | None) -> str:
    language_code = _normalized_language_code(lang)
    language_name = _language_name(language_code)
    context_parts = [
        f"Requested language: {language_name} ({language_code}). Respond naturally in that language.",
        f"Farmer question: {query.strip()}",
    ]

    if disease_result:
        plant = disease_result.get("plant", "Unknown plant")
        disease = disease_result.get("disease", "Unknown disease")
        confidence = disease_result.get("confidence", 0)
        raw_prediction = disease_result.get("raw_prediction", {})
        context_parts.append(
            "Image diagnosis context: "
            f"plant={plant}, disease={disease}, confidence={confidence}%, raw_prediction={raw_prediction}"
        )

    return "\n".join(context_parts)


def get_farming_advice(
    query: str,
    disease_result: dict | None = None,
    lang: str = "en",
    image_path: str | None = None,
) -> str:
    if not query or not query.strip():
        raise ValueError("A farming question is required.")

    client = get_gemini_client()
    user_content = build_context(query=query, disease_result=disease_result, lang=lang)
    uploaded_file = None

    try:
        if image_path:
            uploaded_file = _upload_image_for_gemini(client, image_path)

        last_error: Exception | None = None
        for model in [*MODEL_CANDIDATES, *COMPATIBILITY_MODEL_CANDIDATES]:
            try:
                from google.genai import types

                contents = [uploaded_file, user_content] if uploaded_file else user_content
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                text = (response.text or "").strip()
                if not text:
                    raise RuntimeError(f"Advisory model {model} returned an empty response.")
                return text
            except Exception as exc:
                last_error = exc
                if _is_rate_limit_error(exc):
                    continue
                break

        raise RuntimeError(f"Advisory model request failed: {last_error}")
    finally:
        if uploaded_file is not None:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass
