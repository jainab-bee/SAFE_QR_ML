import io
import os
import pickle
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from feature_extraction import extract_features
from qr_decoder import read_qr_code
from url_analysis import check_url_safety, fix_url, is_upi


app = FastAPI(
    title="SafeQR API",
    description="Scan QR codes and URLs for phishing risks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/bmp",
    "application/octet-stream",
}

model = None


class URLCheckRequest(BaseModel):
    url: str


class CheckItem(BaseModel):
    name: str
    status: str
    detail: str


class ScanResponse(BaseModel):
    qr_content: str
    is_dangerous: bool
    verdict: str
    safety_score: int
    confidence: float
    checks_passed: int
    checks_total: int
    checks: List[CheckItem]


def load_model():
    global model

    if model is not None:
        return model

    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=500,
            detail="model.pkl not found. Run train_model.py first.",
        )

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    return model


def calculate_safety_score(checks):
    passed = sum(check["status"] == "pass" for check in checks)
    total = len(checks)

    if total == 0:
        return passed, total, 0

    score = int((passed / total) * 100)
    return passed, total, score


def analyze_upi(checks, safety_score):
    failed = sum(check["status"] == "fail" for check in checks)
    return failed > 0, float(safety_score)


def analyze_url(url, safety_score, loaded_model):
    features = extract_features(url)
    prediction = loaded_model.predict([features])[0]
    probabilities = loaded_model.predict_proba([features])[0]

    confidence = round(float(max(probabilities)) * 100, 1)
    is_dangerous = prediction == 1 or safety_score < 50

    return bool(is_dangerous), confidence


def build_result(url):
    checks = check_url_safety(url)
    passed, total, safety_score = calculate_safety_score(checks)

    if is_upi(url):
        is_dangerous, confidence = analyze_upi(checks, safety_score)
    else:
        loaded_model = load_model()
        is_dangerous, confidence = analyze_url(
            url,
            safety_score,
            loaded_model,
        )

    verdict = "Dangerous / Phishing" if is_dangerous else "Safe"

    return {
        "qr_content": url,
        "is_dangerous": is_dangerous,
        "verdict": verdict,
        "safety_score": safety_score,
        "confidence": confidence,
        "checks_passed": passed,
        "checks_total": total,
        "checks": checks,
    }


def validate_image_type(file):
    if file.content_type in ALLOWED_IMAGE_TYPES:
        return

    raise HTTPException(
        status_code=415,
        detail=f"Unsupported file type: {file.content_type}",
    )


def open_image(contents):
    try:
        return Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not read the uploaded image.",
        )


@app.get("/")
def root():
    return {
        "service": "SafeQR API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_available": os.path.exists(MODEL_PATH),
    }


@app.post("/scan-qr", response_model=ScanResponse)
async def scan_qr(file: UploadFile = File(...)):
    validate_image_type(file)

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=422,
            detail="Uploaded file is empty.",
        )

    image = open_image(contents)
    qr_text = read_qr_code(image)

    if not qr_text:
        raise HTTPException(
            status_code=422,
            detail="No QR code detected.",
        )

    url = fix_url(qr_text.strip())
    return build_result(url)


@app.post("/check-url", response_model=ScanResponse)
async def check_url(payload: URLCheckRequest):
    url = payload.url.strip()

    if not url:
        raise HTTPException(
            status_code=422,
            detail="URL must not be empty.",
        )

    fixed_url = fix_url(url)
    return build_result(fixed_url)