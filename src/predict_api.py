# src/predict_api.py

import joblib
import pandas as pd
from fastapi import FastAPI
from .schema import CustomerData # Import our Pydantic model
from prometheus_fastapi_instrumentator import Instrumentator # For monitoring

# Initialize the FastAPI app
app = FastAPI(
    title="Customer Churn Prediction API",
    description="An API to predict customer churn based on their data."
)

# --- Add this ---
# This creates a /metrics endpoint for Prometheus
Instrumentator().instrument(app).expose(app)
# ---------------

# --- 1. Load the Model Pipeline ---
# This path is relative to where you'll run uvicorn (the root folder)
PIPELINE_PATH = "models/churn_pipeline.joblib"
try:
    pipeline = joblib.load(PIPELINE_PATH)
    print("Pipeline loaded successfully.")
except FileNotFoundError:
    print(f"Error: Model pipeline not found at {PIPELINE_PATH}")
    # In a real app, you might want to exit or handle this gracefully
    pipeline = None 

# --- 2. Define the Home Endpoint ---
@app.get("/")
def home():
    return {"message": "Welcome to the Churn Prediction API. Go to /docs for more info."}

# --- 3. Define the Prediction Endpoint ---
@app.post("/predict")
def predict(data: CustomerData):
    """
    Receives customer data as input and returns a churn prediction.
    """
    if pipeline is None:
        return {"error": "Model pipeline not loaded. Please check server logs."}

    # --- Convert Pydantic data to DataFrame ---
    # The pipeline expects a DataFrame as input
    # We use .model_dump() (for Pydantic V2) to convert the Pydantic model to a dictionary
    # and wrap it in a list to create a DataFrame with 1 row.
    input_data = pd.DataFrame([data.model_dump()])

    # --- Make Prediction ---
    # Use predict_proba to get probabilities (more useful)
    # [:, 1] gets the probability of the 'positive' class (Churn=1)
    try:
        churn_probability = pipeline.predict_proba(input_data)[:, 1][0]
        
        # You can set a threshold (e.g., 0.5) to decide 'Yes' or 'No'
        prediction = 1 if churn_probability > 0.5 else 0
        
        return {
            "prediction_label": "Churn" if prediction == 1 else "No Churn",
            "prediction_value": prediction,
            "churn_probability": float(churn_probability) # Ensure it's a standard float
        }
    except Exception as e:
        return {"error": f"Error during prediction: {str(e)}"}