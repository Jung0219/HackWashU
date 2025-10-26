from datetime import datetime
from ultralytics import YOLO
import os

# ==== CONFIGURATION ====
MODEL_PATH = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/weights/yolov8n-cls.pt"
# ======================
DATA_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/training"
# ^ dataset root containing train/, val/, test/
PROJECT_DIR = "output"
EPOCHS = 10
IMG_SIZE = 224
BATCH = 32
# ========================

os.environ["WANDB_MODE"] = "disabled"

# Load YOLO classification model
model = YOLO(MODEL_PATH)

start_time = datetime.now()
print(f"[INFO] Training started at {start_time}")

# Train
model.train(
    data=DATA_DIR,        # root folder with train/ and val/
    project=PROJECT_DIR,  # training logs/checkpoints
    name="train",
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH,
    resume=False,
)


end_time = datetime.now()
print(f"[INFO] Training started at {start_time}")
print(f"[INFO] Finished at {end_time}")
print(f"[INFO] Total time: {end_time - start_time}")
