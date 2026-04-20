from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import traceback
import torch # We need this to control memory
import gc    # Garbage collector to free up RAM

# ---------------------------------------------------------
# MEMORY OPTIMIZATIONS FOR RENDER FREE TIER
# ---------------------------------------------------------
# 1. Force PyTorch to only use 1 thread (stops huge RAM spikes)
torch.set_num_threads(1)

app = Flask(__name__)

try:
    model = YOLO("models/best.pt")
except Exception as e:
    print(f"FAILED TO LOAD MODEL: {e}")
    model = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if model is None:
            return jsonify({"error": "Server Error: YOLO model failed to load on startup."}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        # Read the uploaded image file into OpenCV
        img = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image format"}), 400

        # ---------------------------------------------------------
        # 2. Run inference inside a "no_grad" block. 
        # This tells PyTorch not to store memory for training.
        # ---------------------------------------------------------
        with torch.no_grad():
            results = model(img, imgsz=224)

        # Extract probabilities safely
        probs = [0] * 8
        if hasattr(results[0], 'probs') and results[0].probs is not None:
            probs = results[0].probs.data.tolist()

        # ---------------------------------------------------------
        # 3. Immediately delete heavy variables and force garbage collection
        # ---------------------------------------------------------
        del img
        del results
        gc.collect()

        return jsonify(probs)

    except Exception as e:
        print(f"BACKEND ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Python Crash: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)