const labels = [
    "anger","contempt","disgust","fear",
    "happy","neutral","sad","surprised"
];

let currentMode = "webcam";

function setMode(mode) {
    currentMode = mode;

    document.getElementById("webcam-section").classList.toggle("hidden", mode !== "webcam");
    document.getElementById("upload-section").classList.toggle("hidden", mode !== "upload");
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
    const file = document.getElementById("fileInput").files[0];
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await res.json();
    updateUI(data);
}