import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader

# ============== CONFIG ==============
DATA_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/training"
BATCH_SIZE = 32
EPOCHS = 10
LR = 1e-4
NUM_CLASSES = 8
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# ====================================

# Data augmentation and normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # make all images uniform
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])  # ResNet expects normalized input
])

# Datasets and loaders
train_ds = datasets.ImageFolder(
    f"{DATA_DIR}/train", transform=transform)
val_ds = datasets.ImageFolder(f"{DATA_DIR}/val", transform=transform)
train_loader = DataLoader(
    train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE,
                        shuffle=False, num_workers=4)

# Model
model = models.resnet101(weights="IMAGENET1K_V2")
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(DEVICE)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

# Training loop
for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Validation
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    val_acc = 100 * correct / total
    print(
        f"Epoch [{epoch+1}/{EPOCHS}] Loss: {running_loss/len(train_loader):.4f} | Val Acc: {val_acc:.2f}%")

torch.save(model.state_dict(
), "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/output/ResNet101/resnet101_8cls.pt")
print("Training complete. Model saved as resnet101_8cls.pt")
