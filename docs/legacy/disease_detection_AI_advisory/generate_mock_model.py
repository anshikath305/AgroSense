import os
import json
import torch
from transformers import ViTForImageClassification

class_names = [
    "Tomato__healthy",
    "Tomato__Late_blight",
    "Tomato__Early_blight",
    "Tomato__Leaf_Mold",
    "Potato__Early_blight",
    "Potato__Late_blight",
    "Potato__healthy",
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Apple__Apple_scab",
    "Apple__Black_rot",
    "Apple__Cedar_apple_rust",
    "Apple__healthy"
]

def main():
    os.makedirs("model", exist_ok=True)
    with open("model/class_names.json", "w") as f:
        json.dump(class_names, f, indent=4)

    print("Initializing ViT model with pre-trained weights...")
    model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224",
        num_labels=len(class_names),
        ignore_mismatched_sizes=True
    )

    print("Saving model weights to model/best_model.pth...")
    torch.save(model.state_dict(), "model/best_model.pth")
    print("Dummy model generated successfully!")

if __name__ == "__main__":
    main()
