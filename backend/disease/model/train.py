"""
Training script for the crop disease detection model.
"""
import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split, Dataset
from torchvision import datasets, transforms
from transformers import ViTForImageClassification

def download_dataset(dataset_slug="emmarex/plantdisease", download_path="./data/raw"):
    """
    Downloads and extracts the dataset from Kaggle.
    Requires kaggle API credentials configured (e.g., ~/.kaggle/kaggle.json).
    """
    import kaggle
    if not os.path.exists(download_path):
        os.makedirs(download_path, exist_ok=True)
    
    # Simple check if already downloaded
    if not any(os.path.isdir(os.path.join(download_path, d)) for d in os.listdir(download_path) if os.path.isdir(os.path.join(download_path, d))):
        print(f"Downloading dataset {dataset_slug} to {download_path}...")
        kaggle.api.dataset_download_files(dataset_slug, path=download_path, unzip=True)
        print("Download and extraction complete.")
    else:
        print("Dataset appears to already be downloaded.")

def find_classes_dir(base_path):
    """
    Recursively find the directory containing the class folders.
    Useful since zip files often have nested root folders.
    """
    for root, dirs, files in os.walk(base_path):
        if len(dirs) > 5 and all(os.path.isdir(os.path.join(root, d)) for d in dirs):
            return root
    return base_path

class TransformWrapper(Dataset):
    """
    Wrapper to apply transforms to a subset created by random_split.
    """
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform
        
    def __getitem__(self, index):
        x, y = self.subset[index]
        if self.transform:
            x = self.transform(x)
        return x, y
        
    def __len__(self):
        return len(self.subset)

def setup_model(class_names):
    """
    Initializes ViT model and unfreezes the specific layers for fine-tuning.
    """
    num_labels = len(class_names)
    
    # 1. Load ViTForImageClassification with proper config
    model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224",
        num_labels=num_labels,
        ignore_mismatched_sizes=True,
        id2label={str(i): name for i, name in enumerate(class_names)},
        label2id={name: i for i, name in enumerate(class_names)}
    )
    
    # 2. Freeze all layers
    for param in model.parameters():
        param.requires_grad = False
        
    unfrozen_blocks = []
    unfrozen_classifier = []
    
    # Unfreeze the last 4 transformer blocks (layers 8, 9, 10, 11), layernorm, and classifier
    for name, param in model.named_parameters():
        if any(f"vit.encoder.layer.{i}." in name for i in range(8, 12)) or "vit.layernorm" in name:
            param.requires_grad = True
            unfrozen_blocks.append(param)
        elif "classifier" in name:
            param.requires_grad = True
            unfrozen_classifier.append(param)
            
    return model, unfrozen_blocks, unfrozen_classifier


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Download the PlantVillage dataset
    data_root = "./data/raw"
    download_dataset("emmarex/plantdisease", data_root)
    
    # Locate the actual directory containing class folders
    dataset_dir = find_classes_dir(data_root)
    print(f"Using dataset directory: {dataset_dir}")

    # Parse folder structure
    full_dataset = datasets.ImageFolder(root=dataset_dir)
    class_names = full_dataset.classes
    
    # Print class names and counts after loading
    print(f"\nFound {len(class_names)} classes.")
    targets = full_dataset.targets
    class_counts = {class_name: 0 for class_name in class_names}
    for target in targets:
        class_counts[class_names[target]] += 1
        
    for class_name, count in class_counts.items():
        print(f" - {class_name}: {count} images")

    # Save class_names list to model/class_names.json
    os.makedirs("model", exist_ok=True)
    with open("model/class_names.json", "w") as f:
        json.dump(class_names, f, indent=4)
    print("\nSaved class_names to model/class_names.json")

    # Split into 80% train / 10% val / 10% test
    total_size = len(full_dataset)
    train_size = int(0.8 * total_size)
    val_size = int(0.1 * total_size)
    test_size = total_size - train_size - val_size
    
    print(f"\nSplitting dataset: Train={train_size}, Val={val_size}, Test={test_size}")
    
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Apply transforms
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(),
        transforms.ToTensor(),
        normalize,
    ])

    val_test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize,
    ])

    train_dataset = TransformWrapper(train_dataset, train_transform)
    val_dataset = TransformWrapper(val_dataset, val_test_transform)
    test_dataset = TransformWrapper(test_dataset, val_test_transform)

    # Use batch_size=32, num_workers=4
    batch_size = 32
    num_workers = 4
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    print("DataLoaders are ready!")

    # Setup Model
    print("\nInitializing model...")
    model, unfrozen_blocks, unfrozen_classifier = setup_model(class_names)
    model.to(device)

    # 3. Training config
    epochs = 15
    patience = 3
    
    optimizer = torch.optim.AdamW([
        {"params": unfrozen_blocks, "lr": 2e-5},
        {"params": unfrozen_classifier, "lr": 2e-4}
    ])
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    print("\nStarting Training...")
    best_val_acc = 0.0
    patience_counter = 0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs).logits
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * inputs.size(0)
            
        train_loss /= train_size
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs).logits
                loss = criterion(outputs, targets)
                val_loss += loss.item() * inputs.size(0)
                
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
                
        val_loss /= val_size
        val_acc = correct / total
        
        # 4. Print epoch results
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f} - Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.4f}")
        
        scheduler.step()
        
        # Early stopping logic
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # 5. Save best model and config
            torch.save(model.state_dict(), "model/best_model.pth")
            model.config.to_json_file("model/vit_config.json")
            print("  [*] Saved new best model.")
        else:
            patience_counter += 1
            
        if patience_counter >= patience:
            print(f"Early stopping triggered after {epoch+1} epochs.")
            break

    # 6. Final Evaluation on Test Set
    print("\nEvaluating on Test Set...")
    model.load_state_dict(torch.load("model/best_model.pth"))
    model.eval()
    test_correct = 0
    test_total = 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs).logits
            _, predicted = outputs.max(1)
            test_total += targets.size(0)
            test_correct += predicted.eq(targets).sum().item()
            
    test_acc = test_correct / test_total
    print(f"Final Test Accuracy: {test_acc:.4f}")

if __name__ == "__main__":
    main()