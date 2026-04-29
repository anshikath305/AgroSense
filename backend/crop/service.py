from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent / "model_assets" / "RandomForest.pkl"


@dataclass(frozen=True)
class CropFeatures:
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


CROP_PROFILES: dict[str, dict[str, str]] = {
    "rice": {
        "season": "Kharif / monsoon",
        "benefits": "Strong fit for high rainfall and humid conditions with reliable staple demand.",
    },
    "maize": {
        "season": "Kharif or spring",
        "benefits": "Balanced nutrient demand and flexible market use for grain, feed, and silage.",
    },
    "chickpea": {
        "season": "Rabi / winter",
        "benefits": "Improves soil nitrogen balance and performs well in moderate rainfall.",
    },
    "kidneybeans": {
        "season": "Kharif in hills / mild winter zones",
        "benefits": "High-value pulse option for moderately cool and well-drained fields.",
    },
    "pigeonpeas": {
        "season": "Kharif",
        "benefits": "Drought-tolerant pulse crop with strong soil-restoration value.",
    },
    "mothbeans": {
        "season": "Kharif / arid season",
        "benefits": "Works well in low-rainfall fields and supports dryland farming economics.",
    },
    "mungbean": {
        "season": "Kharif or summer",
        "benefits": "Short-duration pulse with low water requirement and good rotation value.",
    },
    "blackgram": {
        "season": "Kharif or summer",
        "benefits": "Nitrogen-fixing crop suited to warm, moderately humid fields.",
    },
    "lentil": {
        "season": "Rabi / winter",
        "benefits": "Low-input pulse crop with good fit for cool, drier post-monsoon conditions.",
    },
    "pomegranate": {
        "season": "Spring or monsoon planting",
        "benefits": "High-value fruit crop that suits slightly alkaline, well-drained soils.",
    },
    "banana": {
        "season": "Year-round in irrigated warm zones",
        "benefits": "High productivity crop for warm, humid fields with steady water access.",
    },
    "mango": {
        "season": "Monsoon planting",
        "benefits": "Long-term orchard crop with strong value in warm tropical conditions.",
    },
    "grapes": {
        "season": "Winter pruning cycle",
        "benefits": "Premium horticulture fit for controlled irrigation and balanced pH.",
    },
    "watermelon": {
        "season": "Summer",
        "benefits": "Fast cash crop for warm fields with moderate water and sandy-loam soil.",
    },
    "muskmelon": {
        "season": "Summer",
        "benefits": "Short-duration fruit crop with good returns in warm, well-drained soils.",
    },
    "apple": {
        "season": "Temperate winter dormancy",
        "benefits": "High-value orchard option for cool climates with sufficient chilling hours.",
    },
    "orange": {
        "season": "Monsoon planting",
        "benefits": "Perennial citrus crop suited to moderate rainfall and well-drained fields.",
    },
    "papaya": {
        "season": "Spring or monsoon",
        "benefits": "Quick-bearing fruit crop for warm, humid, nutrient-rich fields.",
    },
    "coconut": {
        "season": "Monsoon planting",
        "benefits": "Perennial crop that benefits from humid coastal or high-rainfall regions.",
    },
    "cotton": {
        "season": "Kharif",
        "benefits": "Commercial fiber crop suited to warm temperatures and moderate rainfall.",
    },
    "jute": {
        "season": "Kharif / monsoon",
        "benefits": "Fiber crop that performs well in warm, humid, high-rainfall regions.",
    },
    "coffee": {
        "season": "Post-monsoon planting",
        "benefits": "Premium plantation crop for humid, shaded, mildly acidic conditions.",
    },
}


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Crop model not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def build_reason(features: CropFeatures, crop: str) -> str:
    signals: list[str] = []
    if features.ph < 5.8:
        signals.append("the soil is acidic")
    elif features.ph > 7.8:
        signals.append("the soil is alkaline")
    else:
        signals.append("the soil pH is close to a balanced range")

    if features.rainfall > 180:
        signals.append("rainfall is high")
    elif features.rainfall < 60:
        signals.append("rainfall is limited")
    else:
        signals.append("rainfall is moderate")

    if features.humidity > 70:
        signals.append("humidity supports moisture-loving crops")
    elif features.humidity < 40:
        signals.append("humidity is low enough to favor hardier crops")
    else:
        signals.append("humidity is moderate")

    return f"{crop.title()} ranks highest because {', '.join(signals)} for the supplied soil and weather profile."


def predict_crop(features: CropFeatures) -> dict:
    model = load_model()
    values = np.array(
        [
            [
                features.nitrogen,
                features.phosphorus,
                features.potassium,
                features.temperature,
                features.humidity,
                features.ph,
                features.rainfall,
            ]
        ]
    )

    probabilities = model.predict_proba(values)[0]
    labels = model.classes_
    ranked = sorted(zip(labels, probabilities, strict=True), key=lambda item: item[1], reverse=True)
    top_crop = str(ranked[0][0])
    confidence = round(float(ranked[0][1]) * 100, 2)
    profile = CROP_PROFILES.get(
        top_crop,
        {
            "season": "Based on local sowing calendar",
            "benefits": "Matches the supplied nutrient and weather profile better than the alternatives.",
        },
    )

    return {
        "recommended_crop": top_crop.title(),
        "confidence": confidence,
        "why_recommended": build_reason(features, top_crop),
        "best_season": profile["season"],
        "expected_benefits": profile["benefits"],
        "alternatives": [
            {"crop": str(label).title(), "confidence": round(float(score) * 100, 2)}
            for label, score in ranked[:3]
        ],
    }
