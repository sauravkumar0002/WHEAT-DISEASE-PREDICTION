import streamlit as st
import torch
from torchvision import models, transforms
from PIL import Image
import json
import os
import gdown

# ============================================================
# ============ STREAMLIT PAGE CONFIG ============
# ============================================================
st.set_page_config(
    page_title="Wheat Disease Detection",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ============ CUSTOM CSS STYLING ============
# ============================================================
st.markdown("""
<style>
/* ===== GLOBAL STYLES ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    scroll-behavior: smooth;
}

/* ===== BACKGROUND ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 50%, #1c3a28 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

[data-testid="stSidebar"] {
    display: none !important;
}

/* ===== MAIN CONTAINER ===== */
.main {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 2rem 1rem;
}

/* ===== CARD STYLING ===== */
[data-testid="stVerticalBlock"] > div:first-child {
    max-width: 900px;
    margin: 0 auto;
}

/* ===== MAIN CONTENT CARD ===== */
.card-container {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
    padding: 3rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* ===== HEADER SECTION ===== */
.header-section {
    text-align: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid rgba(40, 167, 69, 0.2);
}

.header-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1c1c1c;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.header-subtitle {
    font-size: 1.1rem;
    color: #666;
    font-weight: 300;
    letter-spacing: 0.3px;
}

/* ===== UPLOAD BOX ===== */
.upload-section {
    margin: 2rem 0;
}

.upload-box {
    border: 2px dashed rgba(40, 167, 69, 0.5);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    background: linear-gradient(135deg, rgba(40, 167, 69, 0.05) 0%, rgba(40, 167, 69, 0.02) 100%);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.upload-box:hover {
    border-color: #28a745;
    background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%);
    box-shadow: 0 8px 24px rgba(40, 167, 69, 0.15);
}

.upload-icon {
    font-size: 3rem;
    color: #28a745;
    margin-bottom: 1rem;
}

.upload-text {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1c1c1c;
    margin-bottom: 0.5rem;
}

.upload-hint {
    font-size: 0.95rem;
    color: #999;
    margin: 0.5rem 0;
}

/* ===== BUTTONS ===== */
.analyze-btn {
    display: inline-block;
    background: linear-gradient(135deg, #28a745 0%, #1f8a38 100%);
    color: white;
    padding: 1.2rem 3rem;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 25px rgba(40, 167, 69, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin: 1.5rem 0;
}

.analyze-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 35px rgba(40, 167, 69, 0.4);
}

.analyze-btn:active {
    transform: translateY(-2px);
}

/* ===== RESULT SECTION ===== */
.result-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid rgba(40, 167, 69, 0.1);
}

.result-image-section {
    display: flex;
    align-items: center;
    justify-content: center;
}

.result-image-wrapper {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-image-wrapper:hover {
    transform: scale(1.05);
    box-shadow: 0 16px 50px rgba(40, 167, 69, 0.2);
}

.result-details-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.disease-name {
    font-size: 2rem;
    font-weight: 700;
    color: #1c1c1c;
    line-height: 1.2;
}

/* ===== CONFIDENCE BADGE ===== */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    background: linear-gradient(135deg, rgba(40, 167, 69, 0.15) 0%, rgba(40, 167, 69, 0.05) 100%);
    color: #28a745;
    padding: 0.75rem 1.5rem;
    border-radius: 50px;
    border: 1.5px solid #28a745;
    font-weight: 700;
    font-size: 0.95rem;
    width: fit-content;
}

/* ===== INFO BLOCKS ===== */
.info-block {
    padding: 1.25rem;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
    border-radius: 12px;
    border-left: 4px solid #28a745;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.info-block:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    transform: translateX(4px);
}

.info-block-title {
    font-size: 1rem;
    font-weight: 700;
    color: #28a745;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-block-content {
    font-size: 0.95rem;
    color: #666;
    line-height: 1.6;
}

/* ===== ALERT STYLES ===== */
.alert-warning {
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%);
    border-left: 4px solid #ffc107;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1.5rem 0;
}

.alert-warning-title {
    font-weight: 700;
    color: #ff9800;
    margin-bottom: 0.5rem;
}

/* ===== LOADING SPINNER ===== */
.stSpinner {
    color: #28a745 !important;
}

/* ===== FOOTER ===== */
.footer-text {
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .card-container {
        padding: 1.5rem;
    }
    
    .header-title {
        font-size: 1.8rem;
    }
    
    .result-container {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .disease-name {
        font-size: 1.5rem;
    }
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# ============ CONFIGURATION ============
# ============================================================
MODEL_PATH = "models/combined_model_resnet50.pth"
os.makedirs("models", exist_ok=True)

# ✅ GOOGLE DRIVE FILE ID
FILE_ID = "1-XbaImiQ0oQ9DYswWOshq9wagaEFT6-m"

# ============================================================
# ============ MODEL FUNCTIONS ============
# ============================================================

@st.cache_resource
def download_model():
    """Download model from Google Drive if not exists"""
    if not os.path.exists(MODEL_PATH):
        st.info("📥 Downloading model... (first time only)")
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
    return MODEL_PATH

@st.cache_resource
def load_model():
    """Load pre-trained ResNet50 model"""
    download_model()
    
    model = models.resnet50(weights=None)
    model.fc = torch.nn.Sequential(
        torch.nn.ReLU(),
        torch.nn.Linear(model.fc.in_features, 32)
    )
    
    model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    model.eval()
    return model

@st.cache_resource
def load_plant_disease_data():
    """Load plant disease JSON data"""
    with open("plant_disease.json", "r") as f:
        return json.load(f)

# Load model and data
model = load_model()
plant_disease = load_plant_disease_data()

# ============================================================
# ============ LABELS ============
# ============================================================
labels = [
    'Aphid', 'Black Rust', 'Blast', 'Brown Rust', 'Common Root Rot',
    'Fusarium Head Blight', 'Healthy', 'Leaf Blight', 'Mildew', 'Mite',
    'Septoria', 'Smut', 'Stem fly', 'Tan spot', 'Yellow Rust',
    'aphid_test', 'black_rust_test', 'blast_test', 'brown_rust_test',
    'common_root_rot_test', 'fusarium_head_blight_test', 'healthy_test',
    'leaf', 'leaf_blight_test', 'mildew_test', 'mite_test',
    'non_leaf', 'septoria_test', 'smut_test', 'stem_fly_test',
    'tan_spot_test', 'yellow_rust_test'
]

# ============================================================
# ============ PREPROCESSING ============
# ============================================================
def preprocess_image(image):
    """Preprocess image for model inference"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return transform(image).unsqueeze(0)

# ============================================================
# ============ PREDICTION ============
# ============================================================
def predict(image):
    """Predict disease from wheat leaf image"""
    img = preprocess_image(image)
    
    with torch.no_grad():
        outputs = model(img)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)
    
    label = labels[predicted.item()]
    conf = confidence.item() * 100
    
    # Filter unwanted classes
    if "test" in label or label in ["leaf", "non_leaf"] or conf < 50:
        return {
            "name": "⚠️ Invalid Input Image",
            "cause": "Model is not confident or image is not a wheat leaf.",
            "cure": "Please upload a clear wheat leaf image.",
            "invalid": True
        }, conf
    
    # Match with JSON data
    for item in plant_disease:
        if item["name"] == label:
            return item, conf
    
    return {
        "name": label,
        "cause": "Information not available",
        "cure": "Consult an agricultural expert",
        "invalid": False
    }, conf

# ============================================================
# ============ UI LAYOUT ============
# ============================================================

# Main container
with st.container():
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    # ===== HEADER SECTION =====
    st.markdown("""
    <div class="header-section">
        <h1 class="header-title">🌾 Wheat Disease Detection</h1>
        <p class="header-subtitle">AI-powered disease identification for wheat crops</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== FILE UPLOADER =====
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📸 Upload Wheat Leaf Image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== PROCESS UPLOADED IMAGE =====
    if uploaded_file is not None:
        try:
            # Load and display image
            image = Image.open(uploaded_file).convert("RGB")
            
            # Result section
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # Image column
            st.markdown('<div class="result-image-section">', unsafe_allow_html=True)
            st.markdown(
                '<div class="result-image-wrapper">',
                unsafe_allow_html=True
            )
            st.image(image, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Details column
            st.markdown('<div class="result-details-section">', unsafe_allow_html=True)
            
            # Analyze button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                analyze_button = st.button(
                    "⚡ ANALYZE IMAGE",
                    use_container_width=True,
                    key="analyze_btn"
                )
            
            # Show results
            if analyze_button:
                with st.spinner("🔍 Analyzing image..."):
                    result, confidence = predict(image)
                
                # Disease Name
                st.markdown(f'<p class="disease-name">{result["name"]}</p>', unsafe_allow_html=True)
                
                # Confidence Badge
                confidence_color = "#28a745" if confidence >= 80 else "#ff9800" if confidence >= 50 else "#dc3545"
                st.markdown(
                    f'<div class="confidence-badge" style="border-color: {confidence_color}; color: {confidence_color};">'
                    f'✓ {confidence:.1f}% Confidence</div>',
                    unsafe_allow_html=True
                )
                
                # Invalid image warning
                if result.get("invalid"):
                    st.markdown("""
                    <div class="alert-warning">
                        <div class="alert-warning-title">⚠️ Not a Valid Wheat Leaf</div>
                        <p>The uploaded image doesn't appear to be a wheat leaf, or the confidence is too low.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Disease Cause
                    st.markdown("""
                    <div class="info-block">
                        <div class="info-block-title">🧪 Disease Cause</div>
                        <div class="info-block-content">
                    """, unsafe_allow_html=True)
                    st.write(result["cause"])
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Treatment
                    st.markdown("""
                    <div class="info-block">
                        <div class="info-block-title">💊 Recommended Treatment</div>
                        <div class="info-block-content">
                    """, unsafe_allow_html=True)
                    st.write(result["cure"])
                    st.markdown("</div></div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error processing image: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("""
<div class="footer-text">
    <p>🌾 Wheat Disease Detection System | Powered by AI</p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">Upload clear wheat leaf images for accurate disease detection</p>
</div>
""", unsafe_allow_html=True)
