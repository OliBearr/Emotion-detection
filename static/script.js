const labels = [
    "anger","contempt","disgust","fear",
    "happy","neutral","sad","surprised"
];

let currentMode = "webcam";

function setMode(mode) {
    currentMode = mode;

    document.getElementById("webcam-section").classList.toggle("hidden", mode !== "webcam");
    document.getElementById("upload-section").classList.toggle("hidden", mode !== "upload");

    // Reset UI slightly when switching modes
    document.getElementById("mainEmotion").innerText = "No Data";
    labels.forEach(label => {
        document.getElementById(label).style.width = "0%";
    });
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

// Live Webcam Updates (Runs every 400ms)
setInterval(async () => {
    if (currentMode !== "webcam") return;

    try {
        const res = await fetch('/probs');
        const data = await res.json();
        if (data.length) updateUI(data);
    } catch (err) {
        console.error("Error fetching live probabilities:", err);
    }
}, 400);

// Upload Analysis
async function uploadImage() {
    const input = document.getElementById("fileInput");

    if (!input.files || input.files.length === 0) {
        alert("Please select an image first");
        return;
    }

    const formData = new FormData();
    formData.append("file", input.files[0]);

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        updateUI(data);

    } catch (err) {
        console.error("Upload failed:", err);
        alert("Upload failed. Check console.");
    }
}