import os
import joblib
import requests
import cv2
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from pyzbar.pyzbar import decode
from urllib.parse import urlparse
from PIL import Image

app = Flask(__name__)

# Load trained model
model = joblib.load("hospital_url_xgb.pkl")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List of common URL shorteners
SHORTENED_DOMAINS = ["qrco.de", "bit.ly", "goo.gl", "t.co", "tinyurl.com"]

def is_shortened_url(url):
    """Check if the given URL is from a known URL shortener."""
    parsed_url = urlparse(url)
    return any(shortened in parsed_url.netloc for shortened in SHORTENED_DOMAINS)

def resolve_shortened_url(shortened_url):
    """Resolve a shortened URL to its original destination."""
    try:
        response = requests.get(shortened_url, allow_redirects=True)
        return response.url
    except requests.exceptions.RequestException:
        return None

def extract_url_features(url):
    """Extract numerical features from a URL for prediction."""
    if pd.isna(url):
        return {
            "domain_length": 0,
            "num_subdomains": 0,
            "contains_hospital": 0,
            "contains_medical": 0,
            "contains_clinic": 0,
            "path_length": 0
        }

    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    return {
        "domain_length": len(domain),
        "num_subdomains": domain.count('.'),
        "contains_hospital": int("hospital" in domain.lower()),
        "contains_medical": int("medical" in domain.lower()),
        "contains_clinic": int("clinic" in domain.lower()),
        "path_length": len(path)
    }

def predict_url(url):
    """Predict whether a given URL is real or fake using the trained model."""
    features = extract_url_features(url)
    features_df = pd.DataFrame([features])
    prediction = model.predict(features_df)

    return "Real Hospital URL" if prediction[0] == 1 else "Fake Hospital URL"

def read_qr_code(image_path):
    """Extract a URL from a QR code in an image."""
    img = cv2.imread(image_path)
    decoded_objects = decode(img)

    for obj in decoded_objects:
        return obj.data.decode("utf-8")

    return None

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint to predict if a hospital URL is real or fake."""
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    url = read_qr_code(filepath)
    if not url:
        return jsonify({"error": "No QR code detected"}), 400

    if is_shortened_url(url):
        original_url = resolve_shortened_url(url)
        if not original_url:
            return jsonify({"error": "Could not resolve shortened URL"}), 400
        url = original_url

    prediction = predict_url(url)
    return jsonify({"url": url, "prediction": prediction})

if __name__ == "__main__":
    app.run(debug=True)
