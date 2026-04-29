"""
Text-to-Speech Module
Uses ElevenLabs (primary) or gTTS (secondary) to convert text responses to audio.
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv

BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(BACKEND_ENV_PATH)

# Create temp directory for output files if it doesn't exist
os.makedirs("temp", exist_ok=True)

def text_to_speech(text: str, language: str = "en", output_path: str = None) -> dict:
    """
    Input: text string + language code + optional output path
    Output: {
        "audio_path": "path/to/output.mp3",
        "engine_used": "elevenlabs" or "gtts",
        "language": "en",
        "status": "success" or "error",
        "error": "..."
    }
    """
    if output_path is None:
        output_path = f"temp/voice_output_{int(time.time())}.mp3"
        
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
    
    # Try ElevenLabs if English and API key is present
    if language == "en" and api_key:
        try:
            # Using the newest ElevenLabs SDK pattern
            try:
                from elevenlabs.client import ElevenLabs
                client = ElevenLabs(api_key=api_key)
                
                # generate returns an iterator of bytes
                audio_stream = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2"
                )
                
                with open(output_path, "wb") as f:
                    for chunk in audio_stream:
                        if chunk:
                            f.write(chunk)
                            
            except ImportError:
                # Support the < 1.0 SDK if installed
                from elevenlabs import generate, save
                audio = generate(
                    text=text,
                    voice=voice_id,
                    model="eleven_multilingual_v2",
                    api_key=api_key
                )
                save(audio, output_path)
            
            return {
                "audio_path": output_path,
                "engine_used": "elevenlabs",
                "language": language,
                "status": "success"
            }
        except Exception as e:
            print(f"[TTS] ElevenLabs failed: {e}. Falling back to gTTS.")
            # Fall through to gTTS
            
    # Fallback / Non-English handling with gTTS
    gtts_lang_map = {
        "hi": "hi", "hi-IN": "hi", "pa": "pa", "pa-IN": "pa", "bn": "bn", "ta": "ta", "ta-IN": "ta",
        "te": "te", "mr": "mr", "gu": "gu", "kn": "kn", "en": "en"
    }
    
    gtts_lang = gtts_lang_map.get(language, "en")
    
    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(output_path)
        
        return {
            "audio_path": output_path,
            "engine_used": "gtts",
            "language": gtts_lang,
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def cleanup_audio(file_path: str) -> None:
    """
    Safely delete audio file after it's been served
    Silently ignore if file doesn't exist
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
