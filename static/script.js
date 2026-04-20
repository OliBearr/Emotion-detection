const labels = [
    "anger","contempt","disgust","fear",
    "happy","neutral","sad","surprised"
];

let currentMode = "webcam";

function setMode(mode) {
    currentMode = mode;

    document.getElementById("webcam-section").classList.toggle("hidden", mode !== "webcam");
    document.getElementById("upload-section").classList.toggle("hidden", mode !== "upload");

    resetUI();
}

document.getElementById("fileInput").addEventListener("change", function () {
    const label = document.querySelector(".file-label");
    if (this.files.length > 0) {
        label.innerText = this.files[0].name;
    }
});

// Update UI bars + dominant emotion
function updateUI(data) {
    let maxVal = 0;
    let maxIdx = 0;

    data.forEach((val, i) => {
        document.getElementById(labels[i]).style.width = (val * 100) + "%";

        if (val > maxVal) {
            maxVal = val;
            maxIdx = i;
        }
    });

    document.getElementById("mainEmotion").innerText =
        labels[maxIdx].toUpperCase() + " (" + maxVal.toFixed(2) + ")";
}

// Webcam updates
setInterval(async () => {
    if (currentMode !== "webcam") return;

    const res = await fetch('/probs');
    const data = await res.json();

    if (data.length) updateUI(data);

}, 400);

// Upload
async function uploadImage() {
    const input = document.getElementById("fileInput");

    if (!input.files || input.files.length === 0) {
        alert("Please select an image first");
        return;
    }

    const formData = new FormData();
    formData.append("file", input.files[0]); // MUST be "file"

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        updateUI(data);

    } catch (err) {
        console.error("Upload failed:", err);
        alert("Upload failed. Check console.");
    }
}