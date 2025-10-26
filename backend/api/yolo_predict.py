from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
import io
import torch

app = Flask(__name__)

# ------------------------------
# 1. Allow CORS for frontend access
# ------------------------------


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ------------------------------
# 2. Load YOLO model
# ------------------------------
MODEL_PATH = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/output/YOLO/train/weights/best.pt"
model = YOLO(MODEL_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"✅ Model loaded on {device.upper()}")

# ------------------------------
# 3. Define /predict endpoint
# ------------------------------


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    image = Image.open(io.BytesIO(file.read())).convert("RGB")

    # Run YOLO classification inference
    results = model.predict(image)

    # Extract top prediction
    top_pred = results[0].probs.top1
    confidence = float(results[0].probs.top1conf)
    class_name = model.names[top_pred]

    return jsonify({
        "predicted_class": class_name,
        "confidence": round(confidence, 3)
    })

# ------------------------------
# 4. Health check route
# ------------------------------


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "model_path": MODEL_PATH,
        "device": device
    })


# ------------------------------
# 5. Run the app
# ------------------------------
if __name__ == "__main__":
    print("🚀 Starting Flask YOLO Classification API on http://127.0.0.1:5005")
    app.run(host="0.0.0.0", port=5005, debug=False)
