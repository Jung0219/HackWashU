from flask import Flask, request, jsonify
from PIL import Image
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models

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
# 2. Load ResNet101 model
# ------------------------------
MODEL_PATH = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/output/ResNet101/resnet101_8cls.pt"
NUM_CLASSES = 8

classes = [
    "Abrasion",
    "Bruise",
    "Burn",
    "Cut",
    "Foot_ulcer",
    "Ingrown_nail",
    "Stab_wound"
]

device = "cuda" if torch.cuda.is_available() else "cpu"

model = models.resnet101(weights=None)
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

print(f"✅ ResNet101 model loaded on {device.upper()}")


# ------------------------------
# 3. Image transform (224×224)
# ------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ------------------------------
# 4. Define /predict endpoint
# ------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    image = Image.open(io.BytesIO(file.read())).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, pred_class = torch.max(probs, dim=1)

    class_index = pred_class.item()
    confidence = conf.item()
    class_name = classes[class_index] if class_index < len(
        classes) else f"Unknown ({class_index})"

    return jsonify({
        "predicted_class": class_name,
        "confidence": round(confidence, 3)
    })


# ------------------------------
# 5. Health check route
# ------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "model_path": MODEL_PATH,
        "device": device
    })


# ------------------------------
# 6. Run the app
# ------------------------------
if __name__ == "__main__":
    print("🚀 Starting Flask ResNet101 Classification API on http://127.0.0.1:5005")
    app.run(host="0.0.0.0", port=5005, debug=False)
