import time
from pathlib import Path

from fastapi import UploadFile

from ..advisory.service import get_disease_summary

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MODEL_NOT_TRAINED_MESSAGE = "Model not trained yet. Run train.py first"
TEMP_DIR = Path(__file__).resolve().parents[2] / "temp"


class ModelNotTrainedError(RuntimeError):
    pass


def run_disease_prediction(image_path: str) -> dict:
    try:
        from .model.predict import predict_disease
    except ModuleNotFoundError as exc:
        missing = exc.name or "vision dependency"
        raise RuntimeError(
            f"Disease model dependency '{missing}' is not installed. Run pip install -r backend/requirements.txt."
        ) from exc

    return predict_disease(image_path)


async def analyze_leaf_image(image: UploadFile, query: str, lang: str) -> dict:
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported image type. Use one of: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = TEMP_DIR / f"disease_{time.time_ns()}{suffix}"

    try:
        content = await image.read()
        if not content:
            raise ValueError("Uploaded image is empty.")
        temp_path.write_bytes(content)

        print(f"Loading image from: {temp_path}")
        prediction = run_disease_prediction(str(temp_path))

        if prediction.get("status") == "error":
            error_message = str(prediction.get("error") or "Disease prediction failed.")
            if error_message == MODEL_NOT_TRAINED_MESSAGE:
                raise ModelNotTrainedError(error_message)
            if "image" in error_message.lower():
                raise ValueError(error_message)
            raise RuntimeError(error_message)

        predicted_class = prediction["predicted_class"]
        plant = prediction["plant"]
        disease = prediction["disease"]
        confidence = float(prediction["confidence"])
        print(f"Model prediction: {predicted_class} at {confidence}%")

        summary = get_disease_summary(plant=plant, disease=disease, confidence=confidence)
        if "error" not in summary:
            print("Gemini summary fetched successfully")

        return {
            "status": "success",
            "detection": {
                "plant": plant,
                "disease": disease,
                "confidence": confidence,
                "predicted_class": predicted_class,
                "top3": prediction["top3"],
            },
            "summary": summary,
        }
    finally:
        temp_path.unlink(missing_ok=True)
