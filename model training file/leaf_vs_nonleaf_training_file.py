import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt
import os

if __name__ == '__main__':
    # ================== SETTINGS ==================
    base_dir = r"D:\Plant Diseases Dataset\Leaf vs Non-Leaf Images\Leaf v NonLeaf"
    
    train_dir = os.path.join(base_dir, "train")
    val_dir   = os.path.join(base_dir, "val")
    
    batch_size = 32
    num_epochs = 10
    learning_rate = 0.001
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # ================== TRANSFORMS ==================
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # ================== DATASET ==================
    train_dataset = datasets.ImageFolder(root=train_dir, transform=train_transform)
    val_dataset   = datasets.ImageFolder(root=val_dir,   transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader   = DataLoader(val_dataset,   batch_size=batch_size, shuffle=False, num_workers=0)

    class_names = train_dataset.classes
    print(f"Classes: {class_names}")
    print(f"Train samples: {len(train_dataset)} | Val samples: {len(val_dataset)}")

    # Sample label check
    print("\nSample labels check:")
    for images, labels in train_loader:
        print("Unique labels:", set(labels.tolist()))
        break

    # ================== MODEL =================
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V1)


    # Freeze feature extractor
    for param in model.features.parameters():
        param.requires_grad = False

    # Change classifier to 2 classes
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, 2)

    model = model.to(device)

    # Model check
    print("Model output shape:", model(torch.randn(1, 3, 224, 224).to(device)).shape)  # torch.Size([1, 2])

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=learning_rate)

    # ================== TRAINING ==================
    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []

    print("...Training...")
    for epoch in range(num_epochs):
        # Train
        model.train()
        running_loss = 0.0
        correct = total = 0
        for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1} - Train"):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, pred = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (pred == labels).sum().item()

        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)

        # Val
        model.eval()
        val_loss = val_correct = val_total = 0.0
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc=f"Epoch {epoch+1} - Val"):
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, pred = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (pred == labels).sum().item()

        val_loss = val_loss / len(val_loader)
        val_acc = 100 * val_correct / val_total
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)

        print(f"Epoch [{epoch+1}/{num_epochs}]  Train Loss: {train_loss:.4f}  Acc: {train_acc:.2f}%")
        print(f"                          Val Loss: {val_loss:.4f}   Acc: {val_acc:.2f}%")

    # ================== SAVE MODEL & GRAPH ==================
    torch.save({
        'model_state_dict': model.state_dict(),
        'class_names': class_names
    }, 'leaf_vs_nonleaf_mobilenetv3.pth')

    print(" Model saved as 'leaf_vs_nonleaf_mobilenetv3.pth'")

    # Graph
    epochs_range = range(1, num_epochs + 1)
    plt.figure(figsize=(14, 10))
    plt.subplot(2, 1, 1)
    plt.plot(epochs_range, train_losses, 'b-o', label='Train Loss')
    plt.plot(epochs_range, val_losses, 'r--o', label='Val Loss')
    plt.title('Loss Curves')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True, alpha=0.6)

    plt.subplot(2, 1, 2)
    plt.plot(epochs_range, train_accuracies, 'g-s', label='Train Accuracy')
    plt.plot(epochs_range, val_accuracies, 'm--s', label='Val Accuracy')
    plt.title('Accuracy Curves')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.grid(True, alpha=0.6)

    plt.suptitle('MobileNetV3 Large - Leaf vs Non-Leaf Training', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('leaf_nonleaf_training_graph.png', dpi=300)
    plt.show()

    print(" Graph saved as 'leaf_nonleaf_training_graph.png'")