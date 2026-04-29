"""
Language Configurations
Defines supported Indian languages with full config for STT, TTS, and UI messages.
Unicode-based heuristic detection requires no external API calls.
"""

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "whisper_code": "en",
        "gtts_code": "en",
        "greeting": "Hello! I am your crop assistant. How can I help you today?",
        "error_msg": "Sorry, I could not understand. Please try again.",
        "processing_msg": "Processing your query..."
    },
    "hi": {
        "name": "Hindi",
        "whisper_code": "hi",
        "gtts_code": "hi",
        "greeting": "नमस्ते! मैं आपका फसल सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
        "error_msg": "माफ करें, मैं समझ नहीं पाया। कृपया फिर से कोशिश करें।",
        "processing_msg": "आपकी query process हो रही है..."
    },
    "pa": {
        "name": "Punjabi",
        "whisper_code": "pa",
        "gtts_code": "pa",
        "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ ਫਸਲ ਸਹਾਇਕ ਹਾਂ।",
        "error_msg": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਸਮਝ ਨਹੀਂ ਪਾਇਆ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "processing_msg": "ਤੁਹਾਡੀ query process ਹੋ ਰਹੀ ਹੈ..."
    },
    "ta": {
        "name": "Tamil",
        "whisper_code": "ta",
        "gtts_code": "ta",
        "greeting": "வணக்கம்! நான் உங்கள் பயிர் உதவியாளர்.",
        "error_msg": "மன்னிக்கவும், புரியவில்லை. மீண்டும் முயற்சிக்கவும்.",
        "processing_msg": "உங்கள் கேள்வி செயலாக்கப்படுகிறது..."
    },
    "te": {
        "name": "Telugu",
        "whisper_code": "te",
        "gtts_code": "te",
        "greeting": "నమస్కారం! నేను మీ పంట సహాయకుడిని.",
        "error_msg": "క్షమించండి, అర్థం కాలేదు. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "processing_msg": "మీ ప్రశ్న ప్రాసెస్ అవుతోంది..."
    },
    "mr": {
        "name": "Marathi",
        "whisper_code": "mr",
        "gtts_code": "mr",
        "greeting": "नमस्कार! मी तुमचा पीक सहाय्यक आहे.",
        "error_msg": "माफ करा, मला समजले नाही. कृपया पुन्हा प्रयत्न करा.",
        "processing_msg": "तुमची query process होत आहे..."
    }
}

# Also keep a flat LANGUAGE_MAP for quick name lookups used by stt.py
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "pa": "Punjabi",
    "bn": "Bengali",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
}

DEFAULT_LANGUAGE = "hi"   # Default to Hindi for Indian farmers


def get_language_config(lang_code: str) -> dict:
    """Return the full language config dict for the given code, or English default."""
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])


def detect_language_from_text(text: str) -> str:
    """
    Simple heuristic: check for Devanagari, Tamil, Telugu unicode ranges.
    No external API call — pure offline detection.
    Returns a 2-letter language code string.
    """
    for char in text:
        code = ord(char)
        if 0x0900 <= code <= 0x097F:  return "hi"   # Devanagari (Hindi / Marathi)
        if 0x0A00 <= code <= 0x0A7F:  return "pa"   # Gurmukhi (Punjabi)
        if 0x0B80 <= code <= 0x0BFF:  return "ta"   # Tamil
        if 0x0C00 <= code <= 0x0C7F:  return "te"   # Telugu
        if 0x0A80 <= code <= 0x0AFF:  return "gu"   # Gujarati
        if 0x0C80 <= code <= 0x0CFF:  return "kn"   # Kannada
        if 0x0980 <= code <= 0x09FF:  return "bn"   # Bengali
    return "en"
