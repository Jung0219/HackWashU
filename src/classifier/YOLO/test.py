from datetime import datetime
from ultralytics import YOLO

# ==== CONFIGURATION ====
# ======================
DATA_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/training"
PROJECT_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/output"
IMG_SIZE = 224
BATCH = 32
# ========================

# Load YOLO classification model
MODEL_PATH = f"{PROJECT_DIR}/train/weights/best.pt"
model = YOLO(MODEL_PATH)

start_time = datetime.now()
print(f"[INFO] Validation started at {start_time}")

# Validate
model.val(
    data=DATA_DIR,        # YOLO will automatically use val/ inside this folder
    project=PROJECT_DIR,  # logs/results will be saved here
    split="test",
    name="test",
    imgsz=IMG_SIZE,
    batch=BATCH
)

end_time = datetime.now()
print(f"[INFO] Validation started at {start_time}")
print(f"[INFO] Finished at {end_time}")
print(f"[INFO] Total time: {end_time - start_time}")
