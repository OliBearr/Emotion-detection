from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

model = YOLO("models/best.pt")

last_probs = [0] * 8


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global last_probs

    file = request.files["file"]
    img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    results = model(img, imgsz=224)

    if results[0].probs is not None:
        last_probs = results[0].probs.data.tolist()

    return jsonify(last_probs)


@app.route("/probs")
def probs():
    return jsonify(last_probs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 5000)))