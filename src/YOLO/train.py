"""
YOLOv8 Classification Training Script
-------------------------------------
This script trains a YOLOv8 classification model on a dataset
organized in the following structure:

    dataset/
    ├── train/
    │   ├── class1/
    │   ├── class2/
    │   └── ...
    ├── val/
    │   ├── class1/
    │   └── class2/
    └── test/
        ├── class1/
        └── class2/

Modify the `DATA_DIR` and training parameters as needed.
"""

from ultralytics import YOLO
import os

# ==== CONFIG ====
DATA_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/training"
MODEL_NAME = "yolov8n-cls.pt"     # alternatives: yolov8s-cls.pt, yolov8m-cls.pt
EPOCHS = 50
BATCH_SIZE = 32
IMAGE_SIZE = 224
PROJECT_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/models"
EXPERIMENT_NAME = "light_wounds_yolov8n"

# ==== TRAIN ====


def main():
    print(f"🚀 Starting YOLOv8 classification training on: {DATA_DIR}")
    print(f"Using model: {MODEL_NAME}")

    model = YOLO(MODEL_NAME)

    results = model.train(
        data=DATA_DIR,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        project=PROJECT_DIR,
        name=EXPERIMENT_NAME,
        device=0  # change to 'cpu' if needed
    )

    print("\n✅ Training complete!")
    print(
        f"Best model saved to: {os.path.join(PROJECT_DIR, EXPERIMENT_NAME, 'weights/best.pt')}")
    print(
        f"Run results logged under: {os.path.join(PROJECT_DIR, EXPERIMENT_NAME)}")

    # Optional: evaluate right after training
    print("\n📊 Evaluating model performance on validation set...")
    model.val(data=DATA_DIR)


if __name__ == "__main__":
    main()
