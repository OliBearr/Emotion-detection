from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# FIXED PATH (important for Render)
model = YOLO("models/best.pt")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    # We no longer need global variables since we process per-request
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    # Read the uploaded image file into OpenCV
    img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    # Run inference
    results = model(img, imgsz=224)

    # Extract probabilities safely
    probs = [0] * 8
    if results[0].probs is not None:
        probs = results[0].probs.data.tolist()

    return jsonify(probs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)