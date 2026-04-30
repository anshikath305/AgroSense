"""
Prediction script for the crop disease detection model.
"""
import os
import json
import argparse
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

# Global variables for caching
_MODEL = None
_CLASS_NAMES = None
_DEVICE = None
_TRANSFORM = None

def load_model_and_classes():
    """
    Loads a fully-trained plant disease model directly from Hugging Face.
    Caches them globally to avoid reloading on subsequent calls.
    """
    global _MODEL, _CLASS_NAMES, _DEVICE, _TRANSFORM
    
    if _MODEL is not None:
        return
        
    _DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # We use a highly robust, fine-tuned Vision Transformer (ViT) for much higher accuracy
    model_id = "Abhiram4/PlantDiseaseDetectorVit2"
    
    # Load the model directly from HuggingFace
    _MODEL = AutoModelForImageClassification.from_pretrained(model_id)
    _MODEL.to(_DEVICE)
    _MODEL.eval()
    
    # Get the ID to Label mapping provided by the HF model
    _CLASS_NAMES = _MODEL.config.id2label
    
    # Setup the image processor dynamically from the model's config
    processor = AutoImageProcessor.from_pretrained(model_id)
    
    _TRANSFORM = transforms.Compose([
        transforms.Resize((processor.size["height"], processor.size["width"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=processor.image_mean, std=processor.image_std)
    ])

def parse_class_name(class_name: str) -> tuple:
    """
    Parses a class name like 'Apple___Apple_scab' into ('Apple', 'Apple scab').
    """
    if "___" in class_name:
        parts = class_name.split("___", 1)
        plant = parts[0].replace("_", " ").strip()
        disease = parts[1].replace("_", " ").strip()
        
        # Strip out duplicate plant names in disease if present (e.g. Apple Apple scab)
        if disease.lower().startswith(plant.lower()):
            disease = disease[len(plant):].strip()
            
        if disease.lower() == "healthy":
            disease = "Healthy"
            
        return plant, disease
        
    return "Unknown", class_name

def predict_disease(image_path: str) -> dict:
    """
    Input: path to a crop image (jpg/png)
    Output: dict with keys:
        - predicted_class: str (e.g., "Tomato__Late_blight")
        - confidence: float (0-1)
        - plant: str (e.g., "Tomato")
        - disease: str (e.g., "Late blight") or "Healthy"
        - top3: list of {class, confidence} for top 3 predictions
    """
    try:
        load_model_and_classes()
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}
        
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to load image at {image_path}: {str(e)}"}
        
    try:
        # Preprocess the image
        input_tensor = _TRANSFORM(image).unsqueeze(0).to(_DEVICE)
        
        # Inference
        with torch.no_grad():
            outputs = _MODEL(input_tensor).logits
            probabilities = F.softmax(outputs, dim=1)[0]
            
        # Get top 3 predictions
        top3_prob, top3_idx = torch.topk(probabilities, 3)
        
        top3_prob = top3_prob.cpu().numpy()
        top3_idx = top3_idx.cpu().numpy()
        
        top3 = []
        for i in range(3):
            prob_float = float(top3_prob[i])
            # The class name is stored in the id2label dict
            class_str = _CLASS_NAMES[int(top3_idx[i])]
            top3.append({
                "class": class_str,
                "confidence": round(prob_float, 4) 
            })
            
        best_class_idx = int(top3_idx[0])
        best_class_name = _CLASS_NAMES[best_class_idx]
        best_confidence = float(top3_prob[0])
        
        plant, disease = parse_class_name(best_class_name)
        
        return {
            "predicted_class": best_class_name,
            "confidence": round(best_confidence, 4),
            "plant": plant,
            "disease": disease,
            "top3": top3
        }
        
    except Exception as e:
        return {"error": f"An error occurred during prediction: {str(e)}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict crop disease from an image.")
    parser.add_argument("--image", type=str, required=True, help="Path to the crop image (jpg/png)")
    
    args = parser.parse_args()
    
    result = predict_disease(args.image)
    print(json.dumps(result, indent=4))