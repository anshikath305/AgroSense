from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification

BASE_MODEL_ID = "google/vit-base-patch16-224"
MODEL_NAME = "PlantDiseaseDetectorVit2"
MODEL_NOT_TRAINED_MESSAGE = "Model not trained yet. Run train.py first"
MODEL_LOAD_ERROR_MESSAGE = "PlantDiseaseDetectorVit2 weights could not load."

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "best_model.pth"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

_MODEL = None
_CLASS_NAMES: list[str] | None = None
_DEVICE: torch.device | None = None
_TRANSFORM = None
_PROCESSOR = None


def _extract_state_dict(checkpoint: Any) -> dict[str, torch.Tensor]:
    if hasattr(checkpoint, "state_dict") and not isinstance(checkpoint, dict):
        checkpoint = checkpoint.state_dict()

    if isinstance(checkpoint, dict):
        state_dict = (
            checkpoint.get("state_dict")
            or checkpoint.get("model_state_dict")
            or checkpoint.get("model")
            or checkpoint
        )
    else:
        state_dict = checkpoint

    if not isinstance(state_dict, dict):
        raise TypeError("Unsupported PlantDiseaseDetectorVit2 checkpoint format.")

    return {
        str(key).removeprefix("module."): value
        for key, value in state_dict.items()
    }


def _load_class_names() -> list[str]:
    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(f"Disease class labels not found at {CLASS_NAMES_PATH}")

    with CLASS_NAMES_PATH.open() as file:
        class_names = json.load(file)

    if isinstance(class_names, dict):
        return [class_names[str(index)] for index in range(len(class_names))]
    if isinstance(class_names, list):
        return [str(name) for name in class_names]

    raise TypeError("class_names.json must contain a list or an index-to-label object.")


def _load_model_once() -> None:
    global _MODEL, _CLASS_NAMES, _DEVICE, _TRANSFORM, _PROCESSOR

    if _MODEL is not None:
        return

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_NOT_TRAINED_MESSAGE)

    class_names = _load_class_names()
    _PROCESSOR = AutoImageProcessor.from_pretrained(BASE_MODEL_ID)
    config = AutoConfig.from_pretrained(BASE_MODEL_ID)
    config.num_labels = len(class_names)
    config.id2label = {index: name for index, name in enumerate(class_names)}
    config.label2id = {name: index for index, name in enumerate(class_names)}

    model = AutoModelForImageClassification.from_config(config)
    checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    state_dict = _extract_state_dict(checkpoint)
    model.load_state_dict(state_dict, strict=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    _MODEL = model
    _CLASS_NAMES = class_names
    _DEVICE = device
    _TRANSFORM = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def _load_image(image_path: str) -> Image.Image:
    print(f"Loading image from: {image_path}")
    try:
        with Image.open(image_path) as image:
            image.verify()
        with Image.open(image_path) as image:
            return image.convert("RGB")
    except Exception as exc:
        raise ValueError(f"Invalid image file: {exc}") from exc


def _split_class_name(predicted_class: str) -> tuple[str, str]:
    if "__" in predicted_class:
        plant, disease = predicted_class.split("__", 1)
    else:
        plant, disease = "Unknown", predicted_class

    plant = re.sub(r"\s+", " ", plant.replace("_", " ")).strip() or "Unknown"
    disease = re.sub(r"\s+", " ", disease.replace("_", " ")).strip() or "Unknown"
    if "healthy" in predicted_class.lower():
        disease = "Healthy"

    return plant, disease


def predict_disease(image_path: str) -> dict:
    try:
        _load_model_once()
    except FileNotFoundError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception:
        return {"status": "error", "error": MODEL_LOAD_ERROR_MESSAGE}

    try:
        image = _load_image(image_path)
        tensor = _TRANSFORM(image).unsqueeze(0).to(_DEVICE)

        with torch.no_grad():
            outputs = _MODEL(pixel_values=tensor)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=1)[0]

        top_count = min(3, len(_CLASS_NAMES))
        top_probabilities, top_indices = torch.topk(probabilities, top_count)
        predicted_index = int(torch.argmax(probabilities).item())
        predicted_class = _CLASS_NAMES[predicted_index]
        confidence = round(float(probabilities[predicted_index].item()) * 100, 2)
        plant, disease = _split_class_name(predicted_class)

        top3 = []
        for probability, class_index in zip(top_probabilities.cpu().tolist(), top_indices.cpu().tolist(), strict=False):
            top3.append(
                {
                    "class": _CLASS_NAMES[int(class_index)],
                    "confidence": round(float(probability) * 100, 2),
                }
            )

        print(f"Raw logits: {logits.detach().cpu().tolist()[0]}")
        print(f"Top 3 probabilities: {top3}")
        print(f"Model prediction: {predicted_class} at {confidence}%")

        return {
            "predicted_class": predicted_class,
            "plant": plant,
            "disease": disease,
            "confidence": confidence,
            "top3": top3,
        }
    except Exception as exc:
        return {"status": "error", "error": f"Disease inference failed: {exc}"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict crop disease from an image.")
    parser.add_argument("--image", type=str, required=True, help="Path to the crop image")
    args = parser.parse_args()
    result = predict_disease(args.image)
    print(json.dumps(result, indent=4))
