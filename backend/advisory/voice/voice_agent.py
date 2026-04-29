"""
Voice Pipeline Orchestrator
Coordinates the full voice flow:
    Audio Input → STT → Advisory Agent → TTS → Audio Output

Connects to the main system via a single clean import of get_farming_advice.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from .stt import transcribe_audio, transcribe_audio_bytes
from .tts import text_to_speech, cleanup_audio

BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(BACKEND_ENV_PATH)


def process_voice_query(
    audio_path: str,
    language: str = None,
    disease_result: dict = None,
    cleanup_input: bool = False
) -> dict:
    """
    Process an incoming voice query end-to-end.

    Args:
        audio_path:     Path to the input audio file.
        language:       Optional language hint (e.g. 'hi', 'en').
                        If None, Gemini auto-detects it.
        disease_result: Optional disease detection dict from predict.py
                        to give the agent context when generating advice.
        cleanup_input:  If True, delete the input audio file after processing.

    Returns: {
        "transcribed_text": str,
        "advice_text":      str,
        "audio_response_path": str,  ← path to TTS output mp3
        "language":         str,
        "engine_used":      str,     ← "elevenlabs" or "gtts"
        "status":           "success" | "error",
        "error":            str (only on error)
    }
    """
    # ── Step 1: Transcribe audio ─────────────────────────────────────────────
    stt_result = transcribe_audio(audio_path, language=language)

    if cleanup_input:
        cleanup_audio(audio_path)

    if stt_result["status"] == "error":
        return {
            "status": "error",
            "error": f"STT failed: {stt_result['error']}"
        }

    transcribed_text = stt_result["text"]
    detected_language = stt_result.get("language", "en")

    # ── Step 2: Get farming advice from the AI agent ─────────────────────────
    try:
        # Import lazily to keep this module standalone until actually called
        from ..service import get_farming_advice

        advice_text = get_farming_advice(
            query=transcribed_text,
            disease_result=disease_result,
            lang=detected_language
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Advisory agent failed: {str(e)}"
        }

    # ── Step 3: Convert advice text back to audio ─────────────────────────────
    tts_result = text_to_speech(
        text=advice_text,
        language=detected_language
    )

    if tts_result["status"] == "error":
        # Return text advice even if TTS fails — still useful
        return {
            "transcribed_text": transcribed_text,
            "advice_text": advice_text,
            "audio_response_path": None,
            "language": detected_language,
            "engine_used": None,
            "status": "partial",
            "error": f"TTS failed: {tts_result['error']}"
        }

    return {
        "transcribed_text": transcribed_text,
        "advice_text": advice_text,
        "audio_response_path": tts_result["audio_path"],
        "language": detected_language,
        "engine_used": tts_result["engine_used"],
        "status": "success"
    }


def process_voice_query_bytes(
    audio_bytes: bytes,
    filename: str,
    language: str = None,
    disease_result: dict = None
) -> dict:
    """
    Convenience wrapper for when the caller has raw audio bytes
    (e.g. from a Flask multipart request) rather than a file path.

    Args:
        audio_bytes:    Raw audio data.
        filename:       Original filename (used to infer extension).
        language:       Optional language hint.
        disease_result: Optional disease context dict.

    Returns: Same dict as process_voice_query().
    """
    import tempfile

    ext = os.path.splitext(filename)[1].lower()
    fd, tmp_path = tempfile.mkstemp(suffix=ext)

    try:
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)

        return process_voice_query(
            audio_path=tmp_path,
            language=language,
            disease_result=disease_result,
            cleanup_input=False  # we handle cleanup in finally
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def get_voice_greeting(language: str = "hi") -> dict:
    """
    Generate a greeting audio file in the requested language.

    Returns: {
        "greeting_text": str,
        "audio_path":    str,
        "language":      str,
        "status":        "success" | "error"
    }
    """
    from .languages import get_language_config
    config = get_language_config(language)
    greeting_text = config["greeting"]

    tts_result = text_to_speech(text=greeting_text, language=language)

    if tts_result["status"] == "error":
        return {
            "status": "error",
            "error": tts_result.get("error", "TTS failed")
        }

    return {
        "greeting_text": greeting_text,
        "audio_path":    tts_result["audio_path"],
        "language":      language,
        "status":        "success"
    }
