"""
Evaluation script for the crop disease detection model.

Loads the saved ViT weights (best_model.pth) and class_names.json,
then evaluates on the held-out test split and prints:
  - Overall accuracy
  - Macro-averaged Precision / Recall / F1
  - Per-class accuracy table
  - Confusion matrix (saved to model/confusion_matrix.png)
"""

import os
import json
import argparse
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
from transformers import ViTForImageClassification

# Optional: pretty confusion matrix
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    _HAS_PLOT = True
except ImportError:
    _HAS_PLOT = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_model(model_dir: str, num_labels: int, device: torch.device):
    model_path = os.path.join(model_dir, "best_model.pth")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Trained weights not found at {model_path}. "
            "Run model/train.py first."
        )
    model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224",
        num_labels=num_labels,
        ignore_mismatched_sizes=True,
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model


def compute_metrics(all_preds, all_targets, num_classes):
    """
    Returns (accuracy, per_class_acc, precision_macro, recall_macro, f1_macro,
             confusion_matrix) all as plain Python objects.
    """
    # Confusion matrix
    cm = [[0] * num_classes for _ in range(num_classes)]
    for pred, true in zip(all_preds, all_targets):
        cm[true][pred] += 1

    total_correct = sum(cm[i][i] for i in range(num_classes))
    accuracy = total_correct / len(all_targets) if all_targets else 0.0

    per_class_acc = []
    precisions, recalls, f1s = [], [], []

    for i in range(num_classes):
        tp = cm[i][i]
        fn = sum(cm[i]) - tp          # row sum minus TP
        fp = sum(cm[r][i] for r in range(num_classes)) - tp  # col sum minus TP
        support = sum(cm[i])

        acc_i = tp / support if support else 0.0
        prec_i = tp / (tp + fp) if (tp + fp) else 0.0
        rec_i  = tp / (tp + fn) if (tp + fn) else 0.0
        f1_i   = (2 * prec_i * rec_i / (prec_i + rec_i)
                  if (prec_i + rec_i) else 0.0)

        per_class_acc.append(acc_i)
        precisions.append(prec_i)
        recalls.append(rec_i)
        f1s.append(f1_i)

    macro_prec = sum(precisions) / num_classes
    macro_rec  = sum(recalls) / num_classes
    macro_f1   = sum(f1s) / num_classes

    return accuracy, per_class_acc, macro_prec, macro_rec, macro_f1, cm


def save_confusion_matrix(cm, class_names, output_path):
    if not _HAS_PLOT:
        print("  [!] matplotlib/seaborn not installed – skipping confusion matrix plot.")
        return
    import numpy as np
    cm_arr = [[cm[r][c] for c in range(len(class_names))]
              for r in range(len(class_names))]
    fig, ax = plt.subplots(
        figsize=(max(10, len(class_names) // 2),
                 max(8,  len(class_names) // 2))
    )
    sns.heatmap(
        cm_arr, annot=False, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names, ax=ax
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    print(f"  Confusion matrix saved → {output_path}")


# ---------------------------------------------------------------------------
# Main evaluation function
# ---------------------------------------------------------------------------

def evaluate_model(data_root: str = "./data/raw", test_fraction: float = 0.1):
    """
    Evaluate the saved ViT model on the held-out test split.

    Parameters
    ----------
    data_root : str
        Root directory containing the raw PlantVillage class folders.
    test_fraction : float
        Fraction of the full dataset to use as the test set (mirrors train.py).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model_dir = os.path.dirname(os.path.abspath(__file__))

    # ---- Load class names ------------------------------------------------
    class_names_path = os.path.join(model_dir, "class_names.json")
    if not os.path.exists(class_names_path):
        raise FileNotFoundError(
            f"class_names.json not found at {class_names_path}. "
            "Run model/train.py first."
        )
    with open(class_names_path) as f:
        class_names = json.load(f)
    num_classes = len(class_names)
    print(f"Loaded {num_classes} classes.")

    # ---- Load model -------------------------------------------------------
    model = load_model(model_dir, num_classes, device)

    # ---- Build test DataLoader (same split seed as train.py) -------------
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    # Walk to find the actual classes directory (mirrors find_classes_dir in train.py)
    dataset_dir = data_root
    for root, dirs, _ in os.walk(data_root):
        if len(dirs) > 5 and all(
            os.path.isdir(os.path.join(root, d)) for d in dirs
        ):
            dataset_dir = root
            break

    full_dataset = datasets.ImageFolder(root=dataset_dir, transform=transform)
    total_size = len(full_dataset)
    train_size = int(0.8 * total_size)
    val_size   = int(0.1 * total_size)
    test_size  = total_size - train_size - val_size

    _, _, test_subset = random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42),
    )

    test_loader = DataLoader(
        test_subset, batch_size=32, shuffle=False, num_workers=4
    )
    print(f"Test set size: {test_size} images")

    # ---- Inference -------------------------------------------------------
    all_preds, all_targets = [], []
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            logits = model(inputs).logits
            preds  = logits.argmax(dim=1).cpu().tolist()
            all_preds.extend(preds)
            all_targets.extend(targets.tolist())

    # ---- Metrics ---------------------------------------------------------
    accuracy, per_class_acc, macro_prec, macro_rec, macro_f1, cm = \
        compute_metrics(all_preds, all_targets, num_classes)

    print("\n" + "=" * 60)
    print(f"  Overall Accuracy : {accuracy * 100:.2f}%")
    print(f"  Macro Precision  : {macro_prec * 100:.2f}%")
    print(f"  Macro Recall     : {macro_rec  * 100:.2f}%")
    print(f"  Macro F1-Score   : {macro_f1   * 100:.2f}%")
    print("=" * 60)

    # Per-class table
    print(f"\n{'Class':<45} {'Acc':>6}")
    print("-" * 53)
    for name, acc in zip(class_names, per_class_acc):
        print(f"  {name:<43} {acc * 100:>5.1f}%")

    # Confusion matrix plot
    cm_path = os.path.join(model_dir, "confusion_matrix.png")
    save_confusion_matrix(cm, class_names, cm_path)

    # Save summary JSON
    summary = {
        "accuracy":   round(accuracy, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall":    round(macro_rec,  4),
        "macro_f1":        round(macro_f1,   4),
        "per_class_accuracy": {
            name: round(acc, 4)
            for name, acc in zip(class_names, per_class_acc)
        },
    }
    summary_path = os.path.join(model_dir, "eval_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"\n  Evaluation summary saved → {summary_path}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate the trained crop disease ViT model."
    )
    parser.add_argument(
        "--data_root", type=str, default="./data/raw",
        help="Root directory of the PlantVillage dataset (default: ./data/raw)"
    )
    args = parser.parse_args()
    evaluate_model(data_root=args.data_root)
