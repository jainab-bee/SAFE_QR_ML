import streamlit as st
import os
import pickle
from PIL import Image
from feature_extraction import extract_features
from url_analysis import check_url_safety, fix_url, is_upi
from qr_decoder import read_qr_code

st.set_page_config(page_title="SafeQR", page_icon="🛡️")
st.title("🛡️ SafeQR — QR Code Safety Scanner")
st.caption("Upload a QR code image to check if it's safe or phishing")


@st.cache_resource
def load_model():
    model_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")
    if os.path.exists(model_file):
        with open(model_file, "rb") as f:
            return pickle.load(f)
    return None

model = load_model()

uploaded = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg", "webp", "bmp"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded QR Code", width=300)

    if st.button("🔍 Scan QR Code"):
        if model is None:
            st.error("Model not found! Run `python train_model.py` first.")
        else:
            with st.spinner("Scanning..."):
                uploaded.seek(0)
                pil_image = Image.open(uploaded)
                qr_text = read_qr_code(pil_image)

            if not qr_text:
                st.error("No QR Code detected. Please upload a clear QR code image.")
            else:
                url = fix_url(qr_text)

                checks = check_url_safety(url)
                passed = sum(1 for c in checks if c["status"] == "pass")
                total = len(checks)
                safety_score = int((passed / total) * 100) if total > 0 else 0

                if is_upi(url):
                    failed = sum(1 for c in checks if c["status"] == "fail")
                    is_dangerous = failed > 0
                    confidence = safety_score
                else:
                    features = extract_features(url)
                    ml_prediction = model.predict([features])[0]
                    ml_probabilities = model.predict_proba([features])[0]
                    confidence = round(max(ml_probabilities) * 100, 1)
                    is_dangerous = (ml_prediction == 1) or (safety_score < 50)

                st.divider()

                if is_dangerous:
                    st.error(f"🚨 **Dangerous / Phishing QR** — Confidence: {confidence}%")
                else:
                    st.success(f"✅ **Safe QR Code** — Confidence: {confidence}%")

                col1, col2, col3 = st.columns(3)
                col1.metric("Safety Score", f"{safety_score}%")
                col2.metric("Checks Passed", f"{passed}/{total}")
                col3.metric("Confidence", f"{confidence}%")

                st.subheader("QR Content")
                st.code(url)

                st.subheader("Security Analysis")
                for check in checks:
                    icon = {"pass": "✅", "fail": "❌", "warn": "⚠️"}[check["status"]]
                    st.write(f"{icon} **{check['name']}** — {check['detail']}")