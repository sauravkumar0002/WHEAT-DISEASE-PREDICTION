from flask import Flask, render_template, request, redirect, send_from_directory
import json
import uuid
import torch
from torchvision import models, transforms
from PIL import Image
import os
import gdown

app = Flask(__name__)

# ---------------- CONFIG ---------------- #
UPLOAD_FOLDER = "uploadimages"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- MODEL DOWNLOAD ---------------- #
MODEL_PATH = "models/combined_model_resnet50.pth"
os.makedirs("models", exist_ok=True)

# ✅ YOUR GOOGLE DRIVE FILE ID
FILE_ID = "1-XbaImiQ0oQ9DYswWOshq9wagaEFT6-m"

# Download model only if not present
if not os.path.exists(MODEL_PATH):
    print("Downloading model from Google Drive...")
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, MODEL_PATH, quiet=False)

# ---------------- MODEL LOAD ---------------- #
model = models.resnet50(weights=None)

# ✅ IMPORTANT: Match training architecture EXACTLY
model.fc = torch.nn.Sequential(
    torch.nn.ReLU(),
    torch.nn.Linear(model.fc.in_features, 32)
)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location='cpu')
)

model.eval()

# ---------------- LABELS ---------------- #
labels = [
'Aphid','Black Rust','Blast','Brown Rust','Common Root Rot',
'Fusarium Head Blight','Healthy','Leaf Blight','Mildew','Mite',
'Septoria','Smut','Stem fly','Tan spot','Yellow Rust',
'aphid_test','black_rust_test','blast_test','brown_rust_test',
'common_root_rot_test','fusarium_head_blight_test','healthy_test',
'leaf','leaf_blight_test','mildew_test','mite_test',
'non_leaf','septoria_test','smut_test','stem_fly_test',
'tan_spot_test','yellow_rust_test'
]

# ---------------- JSON LOAD ---------------- #
with open("plant_disease.json", 'r') as file:
    plant_disease = json.load(file)

# ---------------- IMAGE ROUTE ---------------- #
@app.route('/uploadimages/<path:filename>')
def uploaded_images(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------------- HOME ---------------- #
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# ---------------- PREPROCESS ---------------- #
def extract_features(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)
    return img

# ---------------- PREDICT ---------------- #
def model_predict(image_path):
    img = extract_features(image_path)

    with torch.no_grad():
        outputs = model(img)
        _, predicted = torch.max(outputs, 1)

    prediction_label = labels[predicted.item()]

    # ⚠️ Ignore weak/unwanted classes
    if "test" in prediction_label or prediction_label in ["leaf", "non_leaf"]:
        return {
            "name": "Invalid Input Image",
            "cause": "The uploaded image does not contain identifiable wheat leaf features.",
            "cure": "Please upload a clear image of a wheat leaf for accurate disease detection."
        }

    # match with JSON
    for item in plant_disease:
        if item["name"] == prediction_label:
            return item

    return {
        "name": prediction_label,
        "cause": "Not found",
        "cure": "Not found"
    }

# ---------------- UPLOAD ---------------- #
@app.route('/upload/', methods=['POST', 'GET'])
def uploadimage():
    if request.method == "POST":
        image = request.files['img']

        filename = f"{uuid.uuid4().hex}_{image.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        image.save(filepath)

        print("Saved:", filepath)

        prediction = model_predict(filepath)

        return render_template(
            'home.html',
            result=True,
            imagepath=f'/uploadimages/{filename}',
            prediction=prediction
        )

    return redirect('/')

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)