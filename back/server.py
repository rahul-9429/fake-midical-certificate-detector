import os
import joblib
import numpy as np
import requests
from flask import Flask, request, jsonify
from PIL import Image
from pyzbar.pyzbar import decode
from urllib.parse import urlparse

app = Flask(__name__)

# Load the XGBoost model
def load_model():
    return joblib.load("hospital_url_xgb.pkl")

model = load_model()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List of common shortened URL services
SHORTENED_DOMAINS = ["qrco.de", "bit.ly", "goo.gl", "t.co", "tinyurl.com"]

# Function to check if a URL is shortened
def is_shortened_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return any(shortened_domain in domain for shortened_domain in SHORTENED_DOMAINS)

# Function to resolve shortened URL
def resolve_shortened_url(shortened_url):
    try:
        response = requests.get(shortened_url, allow_redirects=True)
        return response.url  # Returns the resolved URL
    except requests.exceptions.RequestException as e:
        print(f"Error resolving shortened URL: {e}")
        return None

# Function to extract URL from QR code
def extract_url_from_qr(image_path):
    image = Image.open(image_path)
    decoded_objects = decode(image)
    
    if decoded_objects:
        url = decoded_objects[0].data.decode("utf-8")  # Extract first QR code URL
        print(f"Extracted URL from QR: {url}")
        return url
    return None

# Function to convert URL into numeric features (Placeholder)
def extract_features(url):
    """
    Convert URL into features. This should match the feature extraction 
    process used when training the model.
    """
    parsed_url = urlparse(url)
    features = [
        len(url),                      # URL length
        len(parsed_url.netloc),        # Domain length
        url.count('/'),                # Count of '/'
        url.count('.'),                # Count of '.'
        url.count('-'),                # Count of '-'
        1 if is_shortened_url(url) else 0  # 1 if shortened, else 0
    ]
    return features

@app.route('/predict', methods=['POST'])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)
    print(f"Image saved at: {filepath}")

    try:
        # Extract URL from QR code
        url = extract_url_from_qr(filepath)
        if not url:
            return jsonify({"error": "No QR code detected or unable to extract URL"}), 400

        # Resolve shortened URL if necessary
        if is_shortened_url(url):
            resolved_url = resolve_shortened_url(url)
            if resolved_url:
                print(f"Resolved URL: {resolved_url}")
                url = resolved_url

        # Convert URL to numeric features
        url_features = extract_features(url)

        # Ensure model input shape is correct
        url_features = np.array(url_features).reshape(1, -1)

        # Predict using the model
        result = model.predict(url_features)
        
        print(f"Model Prediction: {result}")  # Debug log

        return jsonify({"prediction": str(result[0])})

    except Exception as e:
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(debug=True)
