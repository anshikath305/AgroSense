"""
test_pipeline.py -- End-to-end pipeline tests for Crop Disease AI
==================================================================
Run with:
    python test_pipeline.py

Tests
-----
1. Model prediction  -- predict_disease() on a downloaded PlantVillage image
2. Text advisory     -- get_farming_advice() with a plain text query
3. Combined flow     -- get_farming_advice() with Test-1 disease_result injected
4. Flask API         -- /ask endpoint hit via HTTP (subprocess)
"""

# Force UTF-8 on Windows so print() never raises UnicodeEncodeError
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import sys
import json
import time
import shutil
import signal
import socket
import tempfile
import subprocess
import textwrap

import requests

# ---------------------------------------------------------------------------
# Ensure repo root is on the path so local packages resolve correctly
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

# ---------------------------------------------------------------------------
# Colour / formatting helpers
# ---------------------------------------------------------------------------
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

WIDTH = 70


def _header(title: str):
    print(f"\n{BOLD}{CYAN}{'=' * WIDTH}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * WIDTH}{RESET}")


def _pass(label: str, elapsed: float):
    print(f"{GREEN}{BOLD}  [PASS]{RESET}  {label}  "
          f"{YELLOW}({elapsed:.2f}s){RESET}")


def _fail(label: str, elapsed: float, reason: str = ""):
    print(f"{RED}{BOLD}  [FAIL]{RESET}  {label}  "
          f"{YELLOW}({elapsed:.2f}s){RESET}")
    if reason:
        for line in textwrap.wrap(f"     Reason: {reason}", WIDTH):
            print(f"  {RED}{line}{RESET}")


def _print_json(data: dict, indent: int = 4):
    print(textwrap.indent(json.dumps(data, indent=indent), "    "))


def _print_text(text: str, max_chars: int = 500):
    snippet = text[:max_chars] + ("…" if len(text) > max_chars else "")
    for line in snippet.splitlines():
        print(f"    {line}")


# ---------------------------------------------------------------------------
# Shared state passed between tests
# ---------------------------------------------------------------------------
# Mock disease result used by Test 3 when Test 1 is skipped (model not trained)
MOCK_DISEASE_RESULT = {
    "predicted_class": "Tomato__Late_blight",
    "confidence": 0.91,
    "plant": "Tomato",
    "disease": "Late blight",
    "top3": [
        {"class": "Tomato__Late_blight",      "confidence": 0.91},
        {"class": "Tomato__Early_blight",     "confidence": 0.06},
        {"class": "Tomato__Leaf_Mold",        "confidence": 0.02},
    ],
}

results: dict = {
    "test1_status":     "pending",   # 'pass' | 'fail' | 'skip'
    "test1_prediction": None,
}

# ---------------------------------------------------------------------------
# Public PlantVillage-style sample images (tried in order; PIL fallback last)
# ---------------------------------------------------------------------------
SAMPLE_IMAGE_URLS = [
    # iNaturalist open-access observation (JPEG, no auth required)
    "https://inaturalist-open-data.s3.amazonaws.com/photos/1043?",
    # USDA ARS photo (public domain)
    "https://www.ars.usda.gov/ARSUserFiles/20800500/images/TomatoLateBlight.jpg",
    # Wikimedia with proper referer
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "4/44/Tomato_-_late_blight_%281%29.jpg/"
        "320px-Tomato_-_late_blight_%281%29.jpg"
    ),
]

FLASK_PORT = 5123   # use a non-standard port to avoid collisions


# ===========================================================================
# TEST 1 — Model prediction
# ===========================================================================
def test_model_prediction() -> bool | None:
    """
    Returns True=pass, False=fail, None=skip.
    Skips gracefully when model weights/class_names have not been generated yet.
    """
    _header("Test 1 — Model Prediction (predict_disease)")
    t0 = time.perf_counter()
    label = "predict_disease() on downloaded image"

    # ---- Pre-flight: check model files exist -----------------------------
    model_dir        = os.path.join(ROOT, "model")
    model_weights    = os.path.join(model_dir, "best_model.pth")
    class_names_file = os.path.join(model_dir, "class_names.json")

    missing = [p for p in (model_weights, class_names_file) if not os.path.exists(p)]
    if missing:
        print(f"  {YELLOW}[SKIP] Model not trained yet. Missing files:{RESET}")
        for p in missing:
            print(f"    - {os.path.relpath(p, ROOT)}")
        print(f"  {YELLOW}  Run `python model/train.py` first, then re-run tests.{RESET}")
        print(f"  {YELLOW}  Test 3 will use a mock disease result instead.{RESET}")
        results["test1_status"]     = "skip"
        results["test1_prediction"] = MOCK_DISEASE_RESULT
        return None   # signal SKIP

    # ---- Acquire sample image (try URLs then PIL fallback) ----------------
    tmp_img = None
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Referer": "https://en.wikipedia.org/",
    }

    for url in SAMPLE_IMAGE_URLS:
        try:
            print(f"  Trying: {url[:80]}...")
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(resp.content)
                tmp_img = f.name
            print(f"  Downloaded -> {tmp_img}")
            break
        except Exception as exc:
            print(f"  {YELLOW}  -> failed ({exc}){RESET}")

    # PIL synthetic fallback — green leaf with brown spots
    if tmp_img is None:
        print(f"  {YELLOW}All URLs failed — generating synthetic test image via PIL.{RESET}")
        try:
            from PIL import Image, ImageDraw
            img  = Image.new("RGB", (224, 224), color=(34, 139, 34))
            draw = ImageDraw.Draw(img)
            for bbox in [(60,60,90,90),(130,100,160,130),(80,150,110,180),(150,50,175,75)]:
                draw.ellipse(bbox, fill=(101, 67, 33))
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                img.save(f.name, "JPEG")
                tmp_img = f.name
            print(f"  Synthetic image -> {tmp_img}")
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            _fail(label, elapsed, f"Could not create test image: {exc}")
            results["test1_status"] = "fail"
            return False

    # ---- Run prediction --------------------------------------------------
    try:
        from model.predict import predict_disease
        prediction = predict_disease(tmp_img)
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        _fail(label, elapsed, str(exc))
        results["test1_status"] = "fail"
        return False
    finally:
        if tmp_img and os.path.exists(tmp_img):
            os.unlink(tmp_img)

    elapsed = time.perf_counter() - t0
    print("\n  Result:")
    _print_json(prediction)

    # ---- Assertions ------------------------------------------------------
    if "error" in prediction:
        _fail(label, elapsed, prediction["error"])
        results["test1_status"] = "fail"
        return False

    predicted_class = prediction.get("predicted_class", "")
    confidence      = prediction.get("confidence", 0.0)

    if not predicted_class:
        _fail(label, elapsed, "predicted_class is empty")
        results["test1_status"] = "fail"
        return False
    if confidence <= 0:
        _fail(label, elapsed, f"confidence must be > 0, got {confidence}")
        results["test1_status"] = "fail"
        return False

    results["test1_status"]     = "pass"
    results["test1_prediction"] = prediction
    _pass(label, elapsed)
    return True


# ===========================================================================
# TEST 2 — Text advisory
# ===========================================================================
def test_text_advisory() -> bool:
    _header("Test 2 — Text Advisory (get_farming_advice, no image)")
    t0 = time.perf_counter()
    label = "get_farming_advice() — plain text query"

    query = "My tomato leaves have brown spots, what should I do?"
    print(f"  Query: \"{query}\"")

    try:
        from agent.advisor import get_farming_advice
        advice = get_farming_advice(query=query, disease_result=None, lang="en")
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        _fail(label, elapsed, str(exc))
        return False

    elapsed = time.perf_counter() - t0
    print(f"\n  Response ({len(advice)} chars):")
    _print_text(advice)

    if len(advice) < 50:
        _fail(label, elapsed,
              f"Response too short ({len(advice)} chars, need ≥ 50)")
        return False

    _pass(label, elapsed)
    return True


# ===========================================================================
# TEST 3 — Combined flow (prediction + advisory)
# ===========================================================================
def test_combined_flow() -> bool:
    _header("Test 3 — Combined Flow (predict -> advise)")
    t0 = time.perf_counter()
    label = "get_farming_advice() with disease_result"

    pred   = results["test1_prediction"]  # real or MOCK_DISEASE_RESULT
    status = results["test1_status"]

    if pred is None:
        print(f"  {YELLOW}Skipped — no prediction available (Test 1 failed).{RESET}")
        return False

    if status == "skip":
        print(f"  {YELLOW}Note: using MOCK disease result (model not trained yet).{RESET}")

    # Normalise to the shape advisor.py expects (confidence as %)
    conf_raw = pred.get("confidence", 0.0)
    conf_pct = round(conf_raw * 100, 2) if conf_raw <= 1.0 else round(conf_raw, 2)
    disease_result = {
        "plant":      pred.get("plant", "Unknown"),
        "disease":    pred.get("disease", "Unknown"),
        "confidence": conf_pct,
        "top3": [
            (item["class"], round(item["confidence"] * 100, 2) if item["confidence"] <= 1.0
             else round(item["confidence"], 2))
            for item in pred.get("top3", [])
        ],
    }

    query = "What fertilizer should I use and how can I treat this disease?"
    print(f"  Plant   : {disease_result['plant']}")
    print(f"  Disease : {disease_result['disease']}")
    print(f"  Conf    : {disease_result['confidence']}%")
    print(f"  Query   : \"{query}\"")

    try:
        from agent.advisor import get_farming_advice
        advice = get_farming_advice(
            query=query,
            disease_result=disease_result,
            lang="en",
        )
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        _fail(label, elapsed, str(exc))
        return False

    elapsed = time.perf_counter() - t0
    print(f"\n  Response ({len(advice)} chars):")
    _print_text(advice)

    if len(advice) < 50:
        _fail(label, elapsed,
              f"Response too short ({len(advice)} chars, need ≥ 50)")
        return False

    _pass(label, elapsed)
    return True


# ===========================================================================
# TEST 4 — Flask API (/ask endpoint via subprocess)
# ===========================================================================
def _wait_for_port(host: str, port: int, timeout: float = 20.0) -> bool:
    """Poll until the TCP port is open or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def test_flask_api() -> bool:
    _header("Test 4 — Flask API (POST /ask via subprocess)")
    t0 = time.perf_counter()
    label = "POST /ask → { 'status': 'success' }"

    api_script = os.path.join(ROOT, "api", "app.py")
    if not os.path.exists(api_script):
        elapsed = time.perf_counter() - t0
        _fail(label, elapsed, f"api/app.py not found at {api_script}")
        return False

    env = os.environ.copy()
    env["API_HOST"] = "127.0.0.1"
    env["API_PORT"] = str(FLASK_PORT)
    env["FLASK_DEBUG"] = "false"   # quieter logs during tests

    proc = None
    passed = False
    try:
        # ---- Start Flask server in background ----------------------------
        print(f"  Starting Flask on 127.0.0.1:{FLASK_PORT} …")
        proc = subprocess.Popen(
            [sys.executable, api_script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
        )

        if not _wait_for_port("127.0.0.1", FLASK_PORT, timeout=25):
            stderr_out = proc.stderr.read(2000).decode(errors="replace")
            elapsed = time.perf_counter() - t0
            _fail(label, elapsed,
                  f"Flask did not start within 25 s.\nSTDERR:\n{stderr_out}")
            return False

        print(f"  Flask is up ({time.perf_counter() - t0:.1f}s).")

        # ---- Send POST /ask ----------------------------------------------
        url   = f"http://127.0.0.1:{FLASK_PORT}/ask"
        query = "How to prevent fungal disease in wheat?"
        print(f"\n  POST {url}")
        print(f"  Body: {{\"query\": \"{query}\"}}")

        resp = requests.post(url, json={"query": query, "lang": "en"}, timeout=240)
        data = resp.json()

        print(f"\n  HTTP {resp.status_code}  Response:")
        _print_json(data)

        elapsed = time.perf_counter() - t0

        # ---- Assertions --------------------------------------------------
        if resp.status_code != 200:
            _fail(label, elapsed, f"Expected HTTP 200, got {resp.status_code}")
        elif data.get("status") != "success":
            _fail(label, elapsed,
                  f"Expected status='success', got '{data.get('status')}'")
        else:
            _pass(label, elapsed)
            passed = True

    except Exception as exc:
        elapsed = time.perf_counter() - t0
        _fail(label, elapsed, str(exc))
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    return passed


# ===========================================================================
# Runner
# ===========================================================================
def _skip(label: str):
    print(f"{YELLOW}{BOLD}  [SKIP]{RESET}  {label}")


def main():
    print(f"\n{BOLD}{'=' * WIDTH}")
    print("  Crop Disease AI -- Pipeline Test Suite")
    print(f"{'=' * WIDTH}{RESET}")

    suite = [
        ("Test 1 -- Model Prediction",  test_model_prediction),
        ("Test 2 -- Text Advisory",      test_text_advisory),
        ("Test 3 -- Combined Flow",      test_combined_flow),
        ("Test 4 -- Flask API",          test_flask_api),
    ]

    passed_count = 0
    skipped_count = 0
    summary_rows = []   # (name, status)  status: 'pass'|'fail'|'skip'

    for name, fn in suite:
        result = fn()   # True=pass, False=fail, None=skip
        if result is True:
            status = "pass"
            passed_count += 1
        elif result is None:
            status = "skip"
            skipped_count += 1
        else:
            status = "fail"
        summary_rows.append((name, status))

    # ---- Summary table ---------------------------------------------------
    print(f"\n{BOLD}{CYAN}{'=' * WIDTH}")
    print("  SUMMARY")
    print(f"{'=' * WIDTH}{RESET}")
    for name, status in summary_rows:
        if status == "pass":
            icon, label_colour = f"{GREEN}[+]{RESET}", GREEN
            tag = f"{GREEN}PASS{RESET}"
        elif status == "skip":
            icon, label_colour = f"{YELLOW}[~]{RESET}", YELLOW
            tag = f"{YELLOW}SKIP{RESET}"
        else:
            icon, label_colour = f"{RED}[-]{RESET}", RED
            tag = f"{RED}FAIL{RESET}"
        print(f"  {icon}  {name:<42}  {tag}")

    total    = len(suite)
    runnable = total - skipped_count
    colour   = GREEN if passed_count == runnable else (YELLOW if passed_count > 0 else RED)
    print(
        f"\n{colour}{BOLD}  {passed_count}/{runnable} runnable tests passed"
        f"  ({skipped_count} skipped).{RESET}\n"
    )

    sys.exit(0 if passed_count == runnable else 1)


if __name__ == "__main__":
    main()
