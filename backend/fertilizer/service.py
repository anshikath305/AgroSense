from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

ASSET_DIR = Path(__file__).resolve().parent / "model_assets"


@dataclass(frozen=True)
class FertilizerFeatures:
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    crop_type: str
    nitrogen: float
    potassium: float
    phosphorous: float


FERTILIZER_GUIDE: dict[str, dict[str, str]] = {
    "Urea": {
        "instructions": "Apply in split doses and irrigate lightly after application to reduce nitrogen loss.",
        "reason": "Best when nitrogen is the limiting nutrient.",
    },
    "DAP": {
        "instructions": "Apply near the root zone before sowing or early growth; avoid direct seed contact.",
        "reason": "Supports early root development when phosphorus demand is high.",
    },
    "14-35-14": {
        "instructions": "Use as a balanced basal application during early vegetative growth.",
        "reason": "Useful when phosphorus is low but nitrogen and potassium also need support.",
    },
    "28-28": {
        "instructions": "Apply before active growth and follow with irrigation if the soil is dry.",
        "reason": "Strengthens nitrogen and phosphorus availability together.",
    },
    "17-17-17": {
        "instructions": "Use as a balanced NPK feed where all major nutrients are moderately depleted.",
        "reason": "Provides equal support for leaf, root, and flowering stages.",
    },
    "20-20": {
        "instructions": "Apply during vegetative growth where nitrogen and phosphorus are both needed.",
        "reason": "Maintains balanced growth without excessive potassium input.",
    },
    "10-26-26": {
        "instructions": "Apply as basal fertilizer for crops needing root and flowering support.",
        "reason": "Higher phosphorus and potassium fit flowering, fruiting, and root development.",
    },
}


@lru_cache(maxsize=1)
def load_assets():
    required = {
        "fertilizer_model": ASSET_DIR / "fertilizer_model.pkl",
        "quantity_model": ASSET_DIR / "quantity_model.pkl",
        "soil_encoder": ASSET_DIR / "soil_encoder.pkl",
        "crop_encoder": ASSET_DIR / "crop_encoder.pkl",
        "target_encoder": ASSET_DIR / "target_encoder.pkl",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing fertilizer assets: {', '.join(missing)}")

    return {name: joblib.load(path) for name, path in required.items()}


def get_supported_values() -> dict:
    assets = load_assets()
    return {
        "soil_types": assets["soil_encoder"].classes_.tolist(),
        "crop_types": assets["crop_encoder"].classes_.tolist(),
        "fertilizers": assets["target_encoder"].classes_.tolist(),
    }


def encode_value(encoder, value: str, label: str) -> int:
    normalized = value.strip()
    classes = encoder.classes_.tolist()
    if normalized not in classes:
        raise ValueError(f"Unsupported {label}: {value}. Supported values: {', '.join(classes)}")
    return int(encoder.transform([normalized])[0])


def predict_fertilizer(features: FertilizerFeatures) -> dict:
    assets = load_assets()
    soil_encoded = encode_value(assets["soil_encoder"], features.soil_type, "soil type")
    crop_encoded = encode_value(assets["crop_encoder"], features.crop_type, "crop type")

    values = np.array(
        [
            [
                features.temperature,
                features.humidity,
                features.moisture,
                soil_encoded,
                crop_encoded,
                features.nitrogen,
                features.potassium,
                features.phosphorous,
            ]
        ]
    )

    encoded_prediction = assets["fertilizer_model"].predict(values)
    fertilizer = str(assets["target_encoder"].inverse_transform(encoded_prediction.astype(int))[0])
    quantity_prediction = float(assets["quantity_model"].predict(values)[0])
    quantity = max(0.0, round(quantity_prediction, 2))
    guide = FERTILIZER_GUIDE.get(
        fertilizer,
        {
            "instructions": "Apply according to local agronomist guidance and soil-test recommendations.",
            "reason": "Selected by the trained model for the submitted crop and soil profile.",
        },
    )

    return {
        "recommended_fertilizer": fertilizer,
        "recommended_quantity_kg_per_acre": quantity,
        "usage_instructions": guide["instructions"],
        "why_recommended": guide["reason"],
        "nutrient_balance": {
            "nitrogen": features.nitrogen,
            "phosphorous": features.phosphorous,
            "potassium": features.potassium,
            "moisture": features.moisture,
        },
    }
