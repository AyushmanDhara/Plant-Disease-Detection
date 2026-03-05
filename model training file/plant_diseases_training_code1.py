import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import numpy as np
 
torch.set_num_threads(6)      # limit CPU threads (adjust as per your CPU cores)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.enabled = False

# ====================== CHOOSE YOUR MODEL HERE ======================
MODEL_NAME = "mobilenet_v3_large"   # ← CHANGE THIS ONLY
NUM_CLASSES = 38
# Valid options:
#   "mobilenet_v3_large"
#   "efficientnet_v2_s"
#   "mobilevit_s"      # MobileViT variants (recommended)
#   "mobilevit_xs"
#   "mobilevit_xxs"

# For MobileViT variants only → install once:
# pip install timm
# ===================================================================

# ──── Config ────────────────────────────────────────────────────────────────
BATCH_SIZE = 32 
EPOCHS = 10
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Using device: {DEVICE}")
print(f"Selected model: {MODEL_NAME}")

# ──── Model + Image Size Selection ──────────────────────────────────────────
if MODEL_NAME == "mobilenet_v3_large":
    IMG_SIZE = 224 
    model = models.mobilenet_v3_large(weights="DEFAULT")
    # Replace head
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, NUM_CLASSES)   # NUM_CLASSES will be set later

elif MODEL_NAME == "efficientnet_v2_s":
    IMG_SIZE = 384
    model = models.efficientnet_v2_s(weights="DEFAULT")
    # Replace head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, NUM_CLASSES)   # NUM_CLASSES set later
    )

elif MODEL_NAME.startswith("mobilevit"):
    IMG_SIZE = 256
    import timm
    model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=NUM_CLASSES)  # NUM_CLASSES set later

else:
    raise ValueError(f"Unknown model: {MODEL_NAME}")

# ──── Freeze backbone, unfreeze only head/classifier (works for ALL models) ──
for name, param in model.named_parameters():
    if any(keyword in name.lower() for keyword in ["classifier", "head", "fc"]):
        param.requires_grad = True
    else:
        param.requires_grad = False

model = model.to(DEVICE)

# ──── Data transforms ───────────────────────────────────────────────────────
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.75, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(25),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

valid_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ──── Datasets & Loaders ────────────────────────────────────────────────────
# Change these paths if your folder structure is different
# DATA_ROOT = "path/to/your/dataset"   # ←←← SET THIS (from kagglehub.dataset_download)

train_dir = os.path.join(r"D:\dataset\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\train")
valid_dir = os.path.join(r"D:\dataset\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\valid")

train_ds = datasets.ImageFolder(train_dir, transform=train_transform)
valid_ds = datasets.ImageFolder(valid_dir, transform=valid_transform)

class_names = train_ds.classes
NUM_CLASSES = len(class_names)

print(f"Classes: {NUM_CLASSES} | Train: {len(train_ds):,} | Valid: {len(valid_ds):,}")
print(f"Input size: {IMG_SIZE}×{IMG_SIZE}")

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=0, pin_memory=False)
valid_loader = DataLoader(valid_ds, batch_size=BATCH_SIZE*2, shuffle=False,
                          num_workers=0, pin_memory=False)

# ──── Optimizer, Loss, Scheduler ────────────────────────────────────────────
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

# Only trainable parameters (head) are optimized
optimizer = optim.AdamW(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
)

scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=5, T_mult=2, eta_min=1e-6
)

# ──── Training Loop ─────────────────────────────────────────────────────────
best_acc = 0.0
history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

for epoch in range(EPOCHS):
    # Train
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS} [Train]")

    for images, labels in pbar:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        pbar.set_postfix(loss=f"{loss.item():.4f}")

    train_loss = running_loss / len(train_loader)
    train_acc = correct / total

    # Validation
    model.eval()
    val_loss, val_correct, val_total = 0.0, 0, 0
    all_preds, all_labels = [], []

    with torch.no_grad():
        for images, labels in valid_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)

            val_loss += loss.item()
            _, predicted = outputs.max(1)
            val_total += labels.size(0)
            val_correct += predicted.eq(labels).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    val_loss /= len(valid_loader)
    val_acc = val_correct / val_total

    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)

    print(f"Epoch {epoch+1:2d} | Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), f"{MODEL_NAME}_Plant_disease.pth")
        print(f"   → New best model saved! (Val Acc: {val_acc:.4f})")

    scheduler.step()

print(f"\nTraining completed! Best validation accuracy: {best_acc:.4f} with {MODEL_NAME}")

# ──── Plots & Report ────────────────────────────────────────────────────────
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history["train_loss"], label="Train")
plt.plot(history["val_loss"], label="Validation")
plt.title("Loss"); plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history["train_acc"], label="Train")
plt.plot(history["val_acc"], label="Validation")
plt.title("Accuracy"); plt.legend()
plt.show()

print("\nDetailed Classification Report:")
print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))