
import joblib
import numpy as np
import pandas as pd
import re
import string
import warnings
import os # New: Needed to read the PORT environment variable
import uvicorn # New: Web server runner
from fastapi import FastAPI # New: Core framework
from fastapi.middleware.cors import CORSMiddleware # New: Handles cross-origin requests
from pydantic import BaseModel # New: Used to define the structure of the incoming request body
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV 
from sklearn.base import ClassifierMixin 

# Suppress warnings during local execution
warnings.filterwarnings("ignore")

# -------------------------
# Configuration
# -------------------------
SVC_MODEL_FILE = "fake_news_model_fixed_svc.pkl"
GRANULAR_MODEL_FILE = "granular_fake_news_model_final_C1.0.pkl"

# Global model variables
binary_model = None
binary_vectorizer = None
granular_model = None
granular_vectorizer = None

# -----------------------------------------------------------
# Utility function for SVC Confidence (RETAINS raw SVC fallback logic)
# -----------------------------------------------------------
def get_svc_confidence_fallback(model, vector):
    """
    Calculates the pseudo-confidence score for a raw LinearSVC model 
    using the decision_function and a sigmoid/softmax approximation.
    
    Returns: prediction, C_True (for binary), C_Predicted (for multi-class), all_class_confidences (dict or None)
    """
    decision_scores = model.decision_function(vector)[0]
    all_class_confidences = None

    if len(decision_scores.shape) == 0:
        # Binary case (simple score)
        decision_score = decision_scores

        # Sigmoid function gives the pseudo-probability for the POSITIVE class (1/True)
        C_True = 1 / (1 + np.exp(-decision_score)) * 100
        
        prediction = 1 if C_True >= 50.0 else 0
        
        # C_Predicted is the confidence in the *predicted* class (used for bin_conf)
        C_Predicted = C_True if prediction == 1 else (100.0 - C_True)
        
        return prediction, C_True, C_Predicted, None 

    else:
        # Multi-class case (Granular)
        predicted_index = np.argmax(decision_scores)
        predicted_class = model.classes_[predicted_index]

        # Softmax approximation
        e_x = np.exp(decision_scores - np.max(decision_scores))
        softmax_probs = e_x / e_x.sum()
        
        C_Predicted = softmax_probs[predicted_index] * 100
        
        # Generate the dictionary of all class confidences
        all_class_confidences = {
            cls.strip('"'): round(p*100, 2)
            for cls, p in zip(model.classes_, softmax_probs)
        }
        
        return predicted_class, None, C_Predicted, all_class_confidences


# -------------------------
# Load models
# -------------------------
try:
    binary_data = joblib.load(SVC_MODEL_FILE)
    binary_model = binary_data["model"]
    binary_vectorizer = binary_data["vectorizer"] 

    granular_model = joblib.load(GRANULAR_MODEL_FILE)
    granular_vectorizer = binary_vectorizer
    
    if isinstance(binary_model, LinearSVC) and not hasattr(binary_model, 'predict_proba'):
        print(f"WARNING: Binary model is raw LinearSVC and will use decision_function fallback.")
    if isinstance(granular_model, LinearSVC) and not hasattr(granular_model, 'predict_proba'):
        print(f"WARNING: Granular model is raw LinearSVC and will use decision_function fallback.")

    print(f"Models loaded successfully: Binary SVC from {SVC_MODEL_FILE}, Granular from {GRANULAR_MODEL_FILE}.")
except FileNotFoundError as e:
    # We must exit if models fail to load, as the API cannot function without them.
    print(f"Error loading model files: {e}. Please ensure required files are in the directory.")
    exit(1)


# -------------------------
# Preprocessing function
# -------------------------
def clean_text_harmonized(text):
    if pd.isnull(text) or not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|\S+\.com\S+|rss\s*2\.0|\bcomments\b|\bpinging\b|filed under\b', ' ', text)
    text = re.sub(r'\b\d+\s*(read|file|link)\S*', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------
# Layered prediction
# -------------------------
def layered_predict(text):
    """Core prediction logic for the FastAPI endpoint."""
    text_clean = clean_text_harmonized(text)
    if not text_clean:
        return {"error": "Input text is empty or contains only non-alphanumeric characters."}

    bin_vec = binary_vectorizer.transform([text_clean])
    
    # --- Binary Prediction and Confidence ---
    if hasattr(binary_model, 'predict_proba'):
        bin_probs = binary_model.predict_proba(bin_vec)[0]
        C_True = bin_probs[1] * 100 
        
        bin_prediction = 1 if C_True >= 50.0 else 0
        bin_conf_predicted = C_True if bin_prediction == 1 else (100.0 - C_True)
    else:
        # FALLBACK: Use pseudo-confidence function
        _, C_True, bin_conf_predicted, _ = get_svc_confidence_fallback(binary_model, bin_vec)

    C_True_rounded = round(C_True, 2)
    bin_conf_predicted_rounded = round(bin_conf_predicted, 2)

    # IMPLEMENTATION OF NEW THRESHOLDS (C_True >= 60% is final 'True' decision)
    if C_True >= 60.0:
        return {
            "binary_prediction": "True",
            "binary_confidence": bin_conf_predicted_rounded, 
            "C_True_confidence": C_True_rounded,
            "granular_prediction": "N/A",
            "granular_confidence_top": "N/A",
            "granular_confidence_all": "N/A",
            "top_features_input": "N/A",
            "top_features_overall": "N/A"
        }
    else:
        # Decision for FAKE / UNKNOWN (Proceed to granular analysis)
        if C_True >= 50.0:
            bin_label_str = "Unknown / Borderline"
        else:
            bin_label_str = "Fake"

        # --- Granular Prediction, Top Confidence, and All Confidences ---
        gran_vec = granular_vectorizer.transform([text_clean])
        gran_conf_all = {"warning": "No probability function available."}
        
        if hasattr(granular_model, 'predict_proba'):
            gran_label = granular_model.predict(gran_vec)[0]
            gran_probs = granular_model.predict_proba(gran_vec)[0]
            predicted_index = list(granular_model.classes_).index(gran_label)
            gran_conf_top = gran_probs[predicted_index] * 100
            
            gran_conf_all = {
                cls.strip('"'): round(p*100, 2) 
                for cls, p in zip(granular_model.classes_, gran_probs)
            }
        else:
            # FALLBACK
            gran_label, _, gran_conf_top, gran_conf_all = get_svc_confidence_fallback(granular_model, gran_vec)
        
        # --- Explainability & Insights ---
        top_input_features = "Feature support not available."
        top_global_features = "Feature support not available."

        if hasattr(granular_model, 'coef_'):
            class_idx = list(granular_model.classes_).index(gran_label)
            coefs = granular_model.coef_[class_idx]

            feature_names = granular_vectorizer.get_feature_names_out()
            # FIX: Increased search depth
            top_idx = np.argsort(coefs)[-200:][::-1] 

            input_words = set(text_clean.split())
            
            top_input_features = [(feature_names[i], round(coefs[i],4))
                                    for i in top_idx if feature_names[i] in input_words][:10]

            top_global_features = [(feature_names[i], round(coefs[i],4)) for i in top_idx[:10]]

        return {
            "binary_prediction": bin_label_str,
            "binary_confidence": bin_conf_predicted_rounded,
            "C_True_confidence": C_True_rounded,
            "granular_prediction": gran_label.strip('"'),
            "granular_confidence_top": round(gran_conf_top, 2), 
            "granular_confidence_all": gran_conf_all,
            "top_features_input": top_input_features,
            "top_features_overall": top_global_features
        }

# ==========================================================
# FastAPI Setup and Endpoints
# ==========================================================

app = FastAPI(title="Fake News Detection API")

# Add CORS middleware
origins = [
    "http://localhost:5173",  # React dev server
    # Add your production frontend URL if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allowing all origins for easy deployment/testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    """Defines the expected JSON body for the request."""
    text: str

@app.get("/")
def home():
    """Simple check to ensure the API is running."""
    return {"status": "ok", "message": "Fake News Detector API is running."}

@app.post("/predict")
def predict(request: TextRequest):
    """
    Accepts text and returns the layered prediction result,
    including binary classification, granular label, and explainability features.
    """
    # Calls the main prediction logic
    return layered_predict(request.text)

# -------------------------
# Run the server for Cloud Run / Local Testing
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Note: host="0.0.0.0" is essential for Docker/Cloud deployment
    uvicorn.run(app, host="0.0.0.0", port=port)
