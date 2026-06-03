# 🛡️ SafeQR — QR Code Safety Scanner

🚀 Live Demo: https://safe-qr-ml-by-jainab.streamlit.app/

A Streamlit web app that scans QR code images and detects whether they lead to safe or phishing/malicious URLs. It combines rule-based URL analysis with a trained machine learning model for accurate threat detection.

---

## Features

- 📷 Upload QR code images (PNG, JPG, JPEG, WEBP, BMP)
- 🔍 Decodes QR codes using multiple fallback libraries (zxing-cpp, pyzbar, OpenCV)
- 🤖 ML-based phishing detection using a Random Forest classifier
- ✅ Rule-based URL safety checks (HTTPS, domain reputation, TLD, IP address, phishing keywords, etc.)
- 💳 Special handling for UPI payment QR codes
- 📊 Safety score, confidence metric, and per-check breakdown

---

## Project Structure

```
safeqr/
├── app.py                 # Streamlit frontend
├── config.py              # Safe domains, bad TLDs, UPI handles
├── feature_extraction.py  # URL feature engineering for ML
├── url_analysis.py        # Rule-based URL safety checks
├── qr_decoder.py          # QR code decoding (multi-library)
├── train_model.py         # Model training script
├── requirements.txt       # Python dependencies
└── model.pkl              # Trained model (generated after training)
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jainab-bee/SAFE_QR_ML.git
cd safeqr
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** For better QR decoding accuracy, optionally install:
> ```bash
> pip install pyzbar zxing-cpp
> ```
> On Linux, `pyzbar` may require: `sudo apt install libzbar0`

---

## Training the Model

The app requires a trained `model.pkl` file. To generate it, you need a labeled CSV dataset with `url` and `label` columns (0 = safe, 1 = phishing).

```bash
python train_model.py
```

The script will automatically look for `qr.csv` in:
- The project directory
- `~/Downloads/qr.csv`
- `C:\Users\<user>\Downloads\qr.csv`

Or specify a custom path:

```bash
python train_model.py --data /path/to/your/dataset.csv
```

After training, `model.pkl` will be saved in the project directory.

---

## Running the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`, upload a QR code image, and click **Scan QR Code**.

---

## How It Works

### QR Decoding (`qr_decoder.py`)
Tries multiple decoding strategies in order:
1. **zxing-cpp** — fast and robust
2. Upscaled/thresholded image variants for low-quality QR codes
3. **pyzbar** — fallback decoder
4. **OpenCV** built-in QR detector

### URL Safety Checks (`url_analysis.py`)
Runs up to 9 checks per URL:

| Check | What it looks for |
|---|---|
| HTTPS Encryption | Whether the URL uses HTTPS |
| Domain Reputation | Compares against a list of trusted domains |
| Domain Extension | Flags suspicious TLDs (`.xyz`, `.tk`, `.ml`, etc.) |
| IP Address | Detects raw IP addresses instead of domain names |
| @ Symbol | Flags `@` in URLs, which can redirect users |
| Phishing Keywords | Detects words like `login`, `verify`, `bank`, `secure` |
| URL Length | Warns on unusually long URLs |
| Domain Hyphens | Flags excessive hyphens in domain names |

UPI payment links (`upi://`) get a separate set of checks including handle validation, payee presence, and keyword scanning.

### ML Prediction (`feature_extraction.py`)
Extracts 8 features from the URL:
- URL length
- Dot count
- HTTPS presence
- `@` symbol presence
- Hyphen count
- Slash count
- Count of suspicious keywords
- Domain length

These feed into a **Random Forest classifier** trained on a labeled URL dataset.

### Final Verdict (`app.py`)
- For **UPI links**: based purely on rule checks
- For **web URLs**: flagged as dangerous if the ML model predicts phishing **or** the rule-based safety score is below 50%

---

## Configuration (`config.py`)

You can customize the detection behavior by editing `config.py`:

- `SAFE_DOMAINS` — whitelist of trusted domains (e.g. `google.com`, `github.com`)
- `BAD_TLDS` — suspicious top-level domains to flag
- `UPI_HANDLES` — known legitimate UPI payment handles

---

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies

---
