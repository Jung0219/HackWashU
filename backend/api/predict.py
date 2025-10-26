# app.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI app
app = FastAPI(title="Local YOLO Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Load YOLO classification model (trained weights)
# your YOLOv8n-cls or custom model
model = YOLO(
    "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/output/train/weights/best.pt")

# 3. Define endpoint for prediction


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image bytes and open as PIL Image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 4. Run YOLO classification inference
    results = model.predict(image)

    # 5. Extract top prediction
    top_pred = results[0].probs.top1
    confidence = float(results[0].probs.top1conf)
    class_name = model.names[top_pred]

    return JSONResponse({
        "predicted_class": class_name,
        "confidence": round(confidence, 3)
    })
