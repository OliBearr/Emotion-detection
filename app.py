from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Load your full model
model = YOLO("models/best.pt")

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Global variable to store the latest webcam probabilities
last_probs = [0] * 8

def generate():
    global last_probs
    while True:
        success, frame = cap.read()
        if not success:
            continue

        # Run inference on the webcam frame
        results = model(frame, imgsz=224)

        # Update the global probabilities
        if results[0].probs is not None:
            last_probs = results[0].probs.data.tolist()

        # Get the frame with YOLO bounding boxes/labels drawn on it
        annotated = results[0].plot()

        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpg', annotated)
        frame = buffer.tobytes()

        # Yield the frame to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    # Route to stream the live webcam video
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/probs")
def probs():
    # Route for the JS to fetch the latest probabilities
    return jsonify(last_probs)

@app.route("/upload", methods=["POST"])
def upload():
    global last_probs

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    results = model(img, imgsz=224)

    if results[0].probs is not None:
        last_probs = results[0].probs.data.tolist()

    return jsonify(last_probs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)