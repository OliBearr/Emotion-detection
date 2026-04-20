from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import traceback

app = Flask(__name__)

# FIXED PATH (important for Render)
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

        # Run inference
        results = model(img, imgsz=224)

        # Extract probabilities safely
        probs = [0] * 8
        if hasattr(results[0], 'probs') and results[0].probs is not None:
            probs = results[0].probs.data.tolist()

        return jsonify(probs)

    except Exception as e:
        # This catches the crash and sends the exact Python error to your screen
        print(f"BACKEND ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Python Crash: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)