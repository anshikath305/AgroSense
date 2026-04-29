"""
Speech-to-Text Module
Uses Google Gemini API for transcribing audio from farmers.
Automatically tries available models from a priority list.
"""
import os
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

from .languages import LANGUAGE_MAP, detect_language_from_text

BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(BACKEND_ENV_PATH)

# Priority list — tries each in order until one works (avoids quota exhaustion on a single model)
_STT_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
]

SUPPORTED_FORMATS = {".mp3", ".wav", ".ogg", ".m4a", ".webm", ".mp4"}


def _file_state_name(file_obj) -> str:
    state = getattr(file_obj, "state", None)
    name = getattr(state, "name", None)
    return str(name or state or "").upper()


def _wait_for_active(client, file_name: str, max_wait_s: int = 120) -> bool:
    """
    Poll the Gemini File API until the file reaches ACTIVE state.
    Returns True if ACTIVE, False on timeout or FAILED state.
    """
    deadline = time.monotonic() + max_wait_s
    while time.monotonic() < deadline:
        try:
            info = client.files.get(name=file_name)
            state_str = _file_state_name(info)
            if "ACTIVE" in state_str:
                return True
            if "FAILED" in state_str:
                return False
        except Exception:
            pass
        time.sleep(2)
    return False


def _generate_with_model_failover(client, audio_file, prompt: str) -> str:
    """Try each model in _STT_MODELS until one succeeds."""
    last_error = None
    for model in _STT_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[audio_file, prompt]
            )
            return response.text.strip()
        except Exception as e:
            msg = str(e)
            if (
                "429" in msg
                or "RESOURCE_EXHAUSTED" in msg
                or "RATE_LIMIT" in msg
                or "NOT_FOUND" in msg
                or "NOT SUPPORTED" in msg
            ):
                last_error = e
                continue   # try next model
            raise          # non-quota error — don't retry
    raise last_error or RuntimeError("All STT models exhausted")


def transcribe_audio(audio_file_path: str, language: str = None) -> dict:
    """
    Input : path to audio file (.mp3, .wav, .ogg, .m4a, .webm, .mp4)
    Output: {
        "text":     "transcribed text",
        "language": "detected language code",
        "status":   "success" or "error",
        "error":    "message if failed"
    }
    """
    if not os.path.exists(audio_file_path):
        return {"status": "error", "error": "Audio file not found"}

    ext = os.path.splitext(audio_file_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        return {"status": "error", "error": f"Unsupported format: {ext}"}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "error": "GEMINI_API_KEY not set in .env"}

    try:
        from google import genai
    except ModuleNotFoundError:
        return {"status": "error", "error": "google-genai is not installed. Run pip install -r backend/requirements.txt."}

    client = genai.Client(api_key=api_key)
    audio_file = None

    try:
        # 1. Upload — no config dict; SDK auto-detects MIME from extension
        audio_file = client.files.upload(file=audio_file_path)

        # 2. Wait for ACTIVE state (usually instant for small files)
        if not _wait_for_active(client, audio_file.name, max_wait_s=60):
            return {"status": "error", "error": "Gemini file did not become ACTIVE in time"}

        # 3. Build prompt
        if language and language in LANGUAGE_MAP:
            lang_name = LANGUAGE_MAP[language]
            prompt = (
                f"Transcribe this audio. The language is {lang_name}. "
                "Return ONLY the transcribed text, nothing else."
            )
        else:
            prompt = (
                "Transcribe this audio exactly as spoken. "
                "Detect the language automatically. "
                "Return ONLY the transcribed text, nothing else."
            )

        # 4. Generate with automatic model failover on quota errors
        transcribed_text = _generate_with_model_failover(client, audio_file, prompt)

        # 5. Detect language
        detected_lang = language if language else detect_language_from_text(transcribed_text)

        return {
            "text": transcribed_text,
            "language": detected_lang,
            "status": "success"
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

    finally:
        # Always clean up from Gemini storage
        if audio_file is not None:
            try:
                client.files.delete(name=audio_file.name)
            except Exception:
                pass


def transcribe_audio_bytes(audio_bytes: bytes, filename: str, language: str = None) -> dict:
    """
    Write bytes to a named temp file, call transcribe_audio(), then clean up.
    """
    ext = os.path.splitext(filename)[1].lower() or ".webm"
    temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(audio_bytes)
        return transcribe_audio(temp_path, language)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
