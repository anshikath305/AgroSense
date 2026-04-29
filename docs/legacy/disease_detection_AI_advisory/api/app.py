"""
Flask REST API — Crop Disease AI
=================================
Endpoints
---------
POST /analyze          Image + optional text query  → disease prediction + advice
POST /ask              Plain-text query              → advisory text
POST /voice            Audio file                   → transcription + advice
POST /twilio-webhook   Twilio WhatsApp webhook      → replies to farmer on WhatsApp
"""

import os
import sys
import tempfile
import logging

import requests as http_requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient

# ---------------------------------------------------------------------------
# Bootstrap — load .env before importing local modules that use GEMINI_API_KEY
# ---------------------------------------------------------------------------
load_dotenv()

# Allow running from repo root: python api/app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.predict import predict_disease                        # noqa: E402
from agent.advisor import get_farming_advice, transcribe_voice  # noqa: E402

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
# Initialize Flask to serve frontend files as static content
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)  # Adds Access-Control-Allow-Origin: * to every response

@app.route("/")
def index():
    return app.send_static_file("index.html")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Twilio credentials (loaded lazily so the server still starts without them)
# ---------------------------------------------------------------------------
TWILIO_SID    = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM   = os.getenv("TWILIO_WHATSAPP_NUMBER", "")  # e.g. +14155238886

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
AUDIO_EXTENSIONS  = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}

MIME_TO_EXT = {
    "image/jpeg":  ".jpg",
    "image/png":   ".png",
    "image/webp":  ".webp",
    "image/bmp":   ".bmp",
    "audio/mpeg":  ".mp3",
    "audio/wav":   ".wav",
    "audio/ogg":   ".ogg",
    "audio/flac":  ".flac",
    "audio/x-m4a": ".m4a",
    "audio/mp4":   ".m4a",
}


def _allowed(filename: str, allowed_set: set) -> bool:
    return os.path.splitext(filename.lower())[1] in allowed_set


def _error(message: str, code: int = 400):
    return jsonify({"status": "error", "message": message}), code


def _save_upload(file_storage, allowed_set: set):
    """Save a werkzeug FileStorage to a temp file; return the path or raise."""
    if not _allowed(file_storage.filename, allowed_set):
        raise ValueError(
            f"Unsupported file type: '{file_storage.filename}'. "
            f"Allowed extensions: {sorted(allowed_set)}"
        )
    suffix = os.path.splitext(file_storage.filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        file_storage.save(tmp.name)
        return tmp.name


def _download_twilio_media(media_url: str) -> str | None:
    """
    Download a Twilio media attachment and save to a temp file.
    Returns the temp file path, or None on failure.
    """
    try:
        resp = http_requests.get(
            media_url,
            auth=(TWILIO_SID, TWILIO_TOKEN),
            timeout=20,
        )
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        ext = MIME_TO_EXT.get(content_type.split(";")[0].strip(), ".jpg")
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(resp.content)
            return tmp.name
    except Exception as exc:
        log.warning("Failed to download Twilio media: %s", exc)
        return None


def _build_disease_result(prediction: dict) -> dict:
    """Convert predict_disease() output to the shape advisor.py expects."""
    return {
        "plant":      prediction.get("plant", "Unknown"),
        "disease":    prediction.get("disease", "Unknown"),
        # predict_disease returns confidence as 0-1 float → convert to %
        "confidence": round(prediction.get("confidence", 0.0) * 100, 2),
        "top3": [
            (item["class"], round(item["confidence"] * 100, 2))
            for item in prediction.get("top3", [])
        ],
    }


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@app.post("/analyze")
def analyze():
    """
    Detect crop disease from an image, then return AI farming advice.

    Form-data:
        image  (file, required)   – crop photograph
        query  (str,  optional)   – farmer's question  [default: generic advice]
        lang   (str,  optional)   – language code       [default: "en"]

    Response 200:
        { "disease": {...}, "advice": "...", "status": "success" }
    """
    if "image" not in request.files:
        return _error("Field 'image' (file) is required.")

    query = request.form.get("query", "What should I do about this?").strip()
    lang  = request.form.get("lang", "en").strip()

    # ---- Save image --------------------------------------------------------
    try:
        img_path = _save_upload(request.files["image"], IMAGE_EXTENSIONS)
    except ValueError as exc:
        return _error(str(exc))

    try:
        # ---- Disease detection ---------------------------------------------
        prediction = predict_disease(img_path)
        if "error" in prediction:
            return _error(f"Disease detection failed: {prediction['error']}", 500)

        # ---- Advisory ------------------------------------------------------
        disease_result = _build_disease_result(prediction)
        advice = get_farming_advice(
            query=query,
            disease_result=disease_result,
            lang=lang,
        )
    except Exception as exc:
        log.exception("Unexpected error in /analyze")
        return _error(str(exc), 500)
    finally:
        os.unlink(img_path)

    return jsonify({"disease": prediction, "advice": advice, "status": "success"})


# ---------------------------------------------------------------------------
# POST /ask
# ---------------------------------------------------------------------------
@app.post("/ask")
def ask():
    """
    Pure-text agronomic advisory — no image required.

    JSON body:
        { "query": "...", "lang": "en" }

    Response 200:
        { "advice": "...", "status": "success" }
    """
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    lang  = data.get("lang", "en").strip()

    if not query:
        return _error("JSON field 'query' is required and must be non-empty.")

    try:
        advice = get_farming_advice(query=query, disease_result=None, lang=lang)
    except Exception as exc:
        log.exception("Unexpected error in /ask")
        return _error(str(exc), 500)

    return jsonify({"advice": advice, "status": "success"})


# ---------------------------------------------------------------------------
# POST /voice
# ---------------------------------------------------------------------------
@app.post("/voice")
def voice():
    """
    Transcribe a voice note, then return AI farming advice.

    Form-data:
        audio  (file, required)  – .mp3 / .wav / .m4a / .ogg
        lang   (str,  optional)  – language code [default: "en"]

    Response 200:
        { "transcription": "...", "advice": "...", "status": "success" }
    """
    if "audio" not in request.files:
        return _error("Field 'audio' (file) is required.")

    lang = request.form.get("lang", "en").strip()

    try:
        audio_path = _save_upload(request.files["audio"], AUDIO_EXTENSIONS)
    except ValueError as exc:
        return _error(str(exc))

    try:
        transcription = transcribe_voice(audio_path)
    except Exception as exc:
        log.exception("Transcription failed in /voice")
        os.unlink(audio_path)
        return _error(f"Transcription failed: {exc}", 500)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)

    if not transcription:
        return _error("Transcription returned empty text.", 422)

    try:
        advice = get_farming_advice(
            query=transcription,
            disease_result=None,
            lang=lang,
        )
    except Exception as exc:
        log.exception("Advisory failed in /voice")
        return _error(str(exc), 500)

    return jsonify({
        "transcription": transcription,
        "advice":        advice,
        "status":        "success",
    })


# ---------------------------------------------------------------------------
# POST /twilio-webhook
# ---------------------------------------------------------------------------
@app.post("/twilio-webhook")
def twilio_webhook():
    """
    Receives incoming WhatsApp messages forwarded by Twilio.

    Twilio sends form-data with (among others):
        Body        – the farmer's text message
        From        – sender's WhatsApp number  (whatsapp:+91XXXXXXXXXX)
        MediaUrl0   – URL of the first attached image (if any)
        MediaContentType0 – MIME type of the attachment

    The handler:
        1. If an image is attached → download → run /analyze flow
        2. Otherwise              → run /ask flow
    Replies with TwiML MessagingResponse so Twilio delivers it to the farmer.
    """
    if not TWILIO_SID or not TWILIO_TOKEN:
        log.warning("/twilio-webhook called but Twilio credentials are not set.")

    body      = request.form.get("Body", "").strip()
    media_url = request.form.get("MediaUrl0", "").strip()
    lang      = "en"  # Could be inferred from Body later

    twiml = MessagingResponse()
    reply_text = ""

    # ---- Branch: image attached -------------------------------------------
    if media_url:
        img_path = _download_twilio_media(media_url)

        if img_path is None:
            reply_text = (
                "Sorry, I couldn't download your image. "
                "Please try again or describe your problem in text."
            )
        else:
            try:
                prediction = predict_disease(img_path)
                if "error" in prediction:
                    reply_text = (
                        f"Disease detection failed: {prediction['error']}. "
                        "Please send a clearer image."
                    )
                else:
                    disease_result = _build_disease_result(prediction)
                    query = body if body else "What should I do about this crop disease?"
                    advice = get_farming_advice(
                        query=query,
                        disease_result=disease_result,
                        lang=lang,
                    )
                    plant    = prediction.get("plant", "Unknown")
                    disease  = prediction.get("disease", "Unknown")
                    conf     = round(prediction.get("confidence", 0.0) * 100, 1)
                    reply_text = (
                        f"🌿 *Detected:* {plant} — {disease} ({conf}% confidence)\n\n"
                        f"💡 *Advice:*\n{advice}"
                    )
            except Exception as exc:
                log.exception("Error processing image in /twilio-webhook")
                reply_text = f"An error occurred while analysing your image: {exc}"
            finally:
                if os.path.exists(img_path):
                    os.unlink(img_path)

    # ---- Branch: text-only message ----------------------------------------
    else:
        query = body
        if not query:
            reply_text = (
                "Hello! 🌾 Send me a crop photo or ask me any farming question."
            )
        else:
            try:
                advice = get_farming_advice(
                    query=query,
                    disease_result=None,
                    lang=lang,
                )
                reply_text = f"💡 *Advice:*\n{advice}"
            except Exception as exc:
                log.exception("Error in /twilio-webhook text advisory")
                reply_text = f"Sorry, I couldn't process your question: {exc}"

    twiml.message(reply_text)
    return str(twiml), 200, {"Content-Type": "application/xml"}


# ---------------------------------------------------------------------------
# Global error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_):
    return _error("Endpoint not found.", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return _error("HTTP method not allowed for this endpoint.", 405)


@app.errorhandler(500)
def internal_error(exc):
    log.exception("Unhandled 500 error")
    return _error(f"Internal server error: {exc}", 500)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    host  = os.environ.get("API_HOST", "0.0.0.0")
    port  = int(os.environ.get("API_PORT", 5000))
    app.run(host=host, port=port, debug=True)
