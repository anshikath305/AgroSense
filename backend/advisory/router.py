from __future__ import annotations

import html
import tempfile
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from starlette.datastructures import UploadFile

from .service import get_farming_advice
from .voice.voice_agent import process_voice_query_bytes

router = APIRouter()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
AUDIO_EXTENSIONS = {".wav", ".webm", ".mp3", ".ogg", ".m4a", ".mp4"}


class AdvisoryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    lang: str = "en"
    disease_result: dict | None = None


def _error_status(exc: Exception) -> int:
    if isinstance(exc, ValueError):
        return 400
    message = str(exc)
    if "GEMINI_API_KEY" in message or "Advisory model" in message or "google-genai" in message:
        return 503
    return 500


async def _save_upload(upload: UploadFile, allowed_extensions: set[str]) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in allowed_extensions:
        raise ValueError(f"Unsupported file type. Use one of: {', '.join(sorted(allowed_extensions))}")

    content = await upload.read()
    if not content:
        raise ValueError("Uploaded file is empty.")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        temp_file.write(content)
        return temp_file.name


def _twiml(message: str) -> Response:
    escaped_message = html.escape(message.strip() or "Sorry, AgroSense could not generate advice right now.")
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_message}</Message></Response>',
        media_type="application/xml",
    )


async def _ask_from_multipart(request: Request) -> dict:
    form = await request.form()
    query = str(form.get("query") or form.get("question") or "").strip()
    lang = str(form.get("lang") or "en")
    image = form.get("image")

    if not query:
        raise ValueError("Field 'query' is required.")

    image_path = None
    try:
        if isinstance(image, UploadFile):
            image_path = await _save_upload(image, IMAGE_EXTENSIONS)
        advice = get_farming_advice(query=query, lang=lang, image_path=image_path)
    finally:
        if image_path:
            Path(image_path).unlink(missing_ok=True)

    return {"status": "success", "advice": advice, "source": "gemini"}


@router.post("/ask")
async def ask(request: Request) -> dict:
    try:
        content_type = request.headers.get("content-type", "").lower()
        if "multipart/form-data" in content_type:
            return await _ask_from_multipart(request)

        payload = AdvisoryRequest(**await request.json())
        advice = get_farming_advice(
            query=payload.query,
            disease_result=payload.disease_result,
            lang=payload.lang,
        )
        return {"status": "success", "advice": advice, "source": "gemini"}
    except Exception as exc:
        raise HTTPException(status_code=_error_status(exc), detail=str(exc)) from exc


@router.post("/voice")
async def voice(request: Request) -> dict:
    audio_path = None
    try:
        form = await request.form()
        audio = form.get("audio") or form.get("file") or form.get("voice")
        if not isinstance(audio, UploadFile):
            raise ValueError("Multipart field 'audio' is required.")

        lang = str(form.get("lang") or form.get("language") or "en")
        audio_path = await _save_upload(audio, AUDIO_EXTENSIONS)
        audio_bytes = Path(audio_path).read_bytes()
        result = process_voice_query_bytes(audio_bytes=audio_bytes, filename=audio.filename or "voice.webm", language=lang)
        if result.get("status") == "error":
            raise RuntimeError(result.get("error", "Voice advisory failed."))
        return result
    except Exception as exc:
        raise HTTPException(status_code=_error_status(exc), detail=str(exc)) from exc
    finally:
        if audio_path:
            Path(audio_path).unlink(missing_ok=True)


@router.post("/twilio-webhook")
async def twilio_webhook(request: Request) -> Response:
    image_path = None
    try:
        form = await request.form()
        lang = str(form.get("lang") or "en")
        body = str(form.get("Body") or "").strip()
        media_count = int(str(form.get("NumMedia") or "0"))

        if media_count > 0:
            media_url = str(form.get("MediaUrl0") or "")
            if not media_url:
                raise ValueError("Twilio media URL is missing.")
            media_response = requests.get(media_url, timeout=30)
            media_response.raise_for_status()
            content_type = media_response.headers.get("content-type", "")
            suffix = ".jpg"
            if "png" in content_type:
                suffix = ".png"
            elif "webp" in content_type:
                suffix = ".webp"
            elif "bmp" in content_type:
                suffix = ".bmp"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_file.write(media_response.content)
                image_path = temp_file.name
            query = body or "Analyze this crop image and advise the farmer."
            advice = get_farming_advice(query=query, lang=lang, image_path=image_path)
        else:
            query = body or "Give me farming advice."
            advice = get_farming_advice(query=query, lang=lang)

        return _twiml(advice)
    except Exception as exc:
        return _twiml(f"AgroSense could not process this request: {exc}")
    finally:
        if image_path:
            Path(image_path).unlink(missing_ok=True)
