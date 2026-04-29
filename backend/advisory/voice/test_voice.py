"""
Standalone test suite for the voice/ module.
Run from the project root:  python voice/test_voice.py
"""

import os
import sys
import math
import struct
import time
import wave

# Bootstrap: allow running as `python voice/test_voice.py` from project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv()

os.makedirs("temp", exist_ok=True)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def _banner(title):
    print("\n" + "=" * 66)
    print("  " + title)
    print("=" * 66)

def _result(label, status, elapsed, detail=""):
    icon = {"PASS": "[+]", "FAIL": "[x]", "SKIPPED": "[-]"}.get(status, "[?]")
    line = "  {}  {:<42} {:<8} ({:.2f}s)".format(icon, label, status, elapsed)
    if detail:
        line += "\n       " + detail
    print(line)

def _make_test_wav(path, duration_s=3.0, sample_rate=16000, freq=440.0):
    n_samples = int(sample_rate * duration_s)
    amplitude = 16000
    frames = [
        struct.pack("<h", int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate)))
        for i in range(n_samples)
    ]
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))


# ---------------------------------------------------------------------------
# Test 1 - STT
# ---------------------------------------------------------------------------
def test1_stt():
    _banner("Test 1 -- STT: Gemini Audio Transcription")
    t0 = time.time()
    if not GEMINI_KEY:
        _result("STT transcription", "SKIPPED", 0.0, "GEMINI_API_KEY not set")
        return

    wav_path = "temp/test_audio.wav"
    _make_test_wav(wav_path)
    print("  Generated: " + wav_path)

    from voice.stt import transcribe_audio_bytes
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()

    result = transcribe_audio_bytes(audio_bytes, "test_audio.wav", language="en")
    elapsed = time.time() - t0
    print("  Result: " + str(result))

    if result.get("status") == "success":
        _result("STT transcription", "PASS", elapsed,
                "text='" + str(result.get("text", ""))[:80] + "'")
    else:
        _result("STT transcription", "FAIL", elapsed, result.get("error", "Unknown"))


# ---------------------------------------------------------------------------
# Test 2 - TTS English
# ---------------------------------------------------------------------------
def test2_tts_english():
    _banner("Test 2 -- TTS: English")
    t0 = time.time()

    from voice.tts import text_to_speech, cleanup_audio
    result = text_to_speech("Your tomato plant has late blight disease.", language="en")
    elapsed = time.time() - t0

    print("  Engine: " + str(result.get("engine_used")))
    if result.get("status") == "success":
        audio_path = result["audio_path"]
        size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
        print("  File: {} ({} bytes)".format(audio_path, size))
        cleanup_audio(audio_path)
        if size > 0:
            _result("TTS English", "PASS", elapsed,
                    "engine={}, size={}B".format(result["engine_used"], size))
        else:
            _result("TTS English", "FAIL", elapsed, "Audio file is empty")
    else:
        _result("TTS English", "FAIL", elapsed, result.get("error", "Unknown"))


# ---------------------------------------------------------------------------
# Test 3 - TTS Hindi
# ---------------------------------------------------------------------------
def test3_tts_hindi():
    _banner("Test 3 -- TTS: Hindi")
    t0 = time.time()

    from voice.tts import text_to_speech, cleanup_audio
    # Use romanized text to avoid cp1252 encoding issues in print()
    text = "aapke tamatar mein late blight rog hai."
    result = text_to_speech(text, language="hi")
    elapsed = time.time() - t0

    print("  Engine: " + str(result.get("engine_used")) + " (expected: gtts)")
    if result.get("status") == "success":
        audio_path = result["audio_path"]
        size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
        print("  File: {} ({} bytes)".format(audio_path, size))
        cleanup_audio(audio_path)
        if size > 0:
            _result("TTS Hindi", "PASS", elapsed,
                    "engine={}, size={}B".format(result["engine_used"], size))
        else:
            _result("TTS Hindi", "FAIL", elapsed, "Audio file is empty")
    else:
        _result("TTS Hindi", "FAIL", elapsed, result.get("error", "Unknown"))


# ---------------------------------------------------------------------------
# Test 4 - Language Detection
# ---------------------------------------------------------------------------
def test4_language_detection():
    _banner("Test 4 -- Language Detection (Unicode Heuristic)")
    t0 = time.time()

    from voice.languages import detect_language_from_text

    # ASCII cases (no Unicode) -- all map to "en"
    ascii_cases = [
        ("My crop has insects", "en"),
        ("hello how are you",   "en"),
    ]

    # Unicode script cases -- encode as unicode_escape so cp1252 won't choke
    unicode_cases = [
        ("\u092e\u0947\u0930\u0940 \u092b\u0938\u0932", "hi"),  # Devanagari
        ("\u0b8e\u0ba9\u0bcd \u0baa\u0baf\u0bbf\u0bb0\u0bbf\u0bb2\u0bcd", "ta"),  # Tamil
        ("\u0c2e\u0c3e \u0c2a\u0c02\u0c1f", "te"),  # Telugu
    ]

    all_pass = True
    for text, expected in ascii_cases + unicode_cases:
        detected = detect_language_from_text(text)
        ok = detected == expected
        status = "[+]" if ok else "[x]"
        print("  {}  detected={}, expected={}".format(status, detected, expected))
        if not ok:
            all_pass = False

    elapsed = time.time() - t0
    _result("Language detection (5 cases)", "PASS" if all_pass else "FAIL", elapsed)


# ---------------------------------------------------------------------------
# Test 5 - Advisory
# ---------------------------------------------------------------------------
def test5_advisory():
    _banner("Test 5 -- Gemini Advisory (text query)")
    t0 = time.time()
    if not GEMINI_KEY:
        _result("Gemini advisory", "SKIPPED", 0.0, "GEMINI_API_KEY not set")
        return

    from agent.advisor import get_farming_advice
    query = "My wheat crop has yellow leaves, what is wrong?"
    response = get_farming_advice(query, lang="en")
    elapsed = time.time() - t0

    preview = response[:200].encode("ascii", errors="replace").decode("ascii")
    print("  Response preview: " + preview)

    if len(response) > 50:
        _result("Gemini advisory", "PASS", elapsed, "length={} chars".format(len(response)))
    else:
        _result("Gemini advisory", "FAIL", elapsed, "Response too short")


# ---------------------------------------------------------------------------
# Test 6 - Full Pipeline
# ---------------------------------------------------------------------------
def test6_full_pipeline():
    _banner("Test 6 -- Full Pipeline (STT + Advisory + TTS)")
    t0 = time.time()
    if not GEMINI_KEY:
        _result("Full pipeline", "SKIPPED", 0.0, "GEMINI_API_KEY not set")
        return

    wav_path = "temp/test_audio.wav"
    if not os.path.exists(wav_path):
        _make_test_wav(wav_path)

    from voice.voice_agent import process_voice_query_bytes
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()

    result = process_voice_query_bytes(audio_bytes, "test.wav", language="en")
    elapsed = time.time() - t0

    print("  Result keys: " + str(list(result.keys())))
    for k, v in result.items():
        safe = str(v).encode("ascii", errors="replace").decode("ascii")[:100]
        print("    {}: {}".format(k, safe))

    from voice.tts import cleanup_audio
    if result.get("audio_response_path"):
        cleanup_audio(result["audio_response_path"])

    final_status = result.get("status", "")
    if final_status == "success":
        _result("Full pipeline", "PASS", elapsed)
    elif final_status == "partial":
        _result("Full pipeline", "PASS", elapsed, "partial - TTS failed: " + str(result.get("error")))
    else:
        _result("Full pipeline", "FAIL", elapsed, result.get("error", "Unknown"))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_all():
    print("\n" + "=" * 66)
    print("  Voice Module -- Test Suite")
    print("=" * 66)

    if not GEMINI_KEY:
        print("\n  [!]  GEMINI_API_KEY not set -- API tests will be SKIPPED.")
    else:
        print("\n  [+]  GEMINI_API_KEY found ({}...)".format(GEMINI_KEY[:8]))

    total_start = time.time()

    for fn in [test1_stt, test2_tts_english, test3_tts_hindi,
               test4_language_detection, test5_advisory, test6_full_pipeline]:
        try:
            fn()
        except Exception as exc:
            print("\n  [x]  {} raised: {}".format(fn.__name__, exc))

    total = time.time() - total_start
    print("\n" + "=" * 66)
    print("  Completed in {:.2f}s".format(total))
    print("=" * 66 + "\n")


if __name__ == "__main__":
    run_all()
