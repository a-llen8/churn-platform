from fastapi import FastAPI
import mlflow.xgboost
import pandas as pd
from pydantic import BaseModel

app = FastAPI(title="Churn Prediction API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
MODEL_PATH = "mlruns/1/models/m-19ac7d3b9a2444f8a60e8c1e252e80bb/artifacts"
model = mlflow.xgboost.load_model(MODEL_PATH)

class Customer(BaseModel):
    avg_monthly_charges: float
    avg_tenure_months: float
    avg_support_tickets: float
    avg_last_login_days: float
    avg_num_products: float
    total_events: int

@app.get("/")
def root():
    return {"status": "Churn Prediction API running ✅"}

@app.post("/predict")
def predict(customer: Customer):
    data = pd.DataFrame([customer.dict()])
    prob = model.predict_proba(data)[0][1]
    risk = "HIGH" if prob > 0.5 else "LOW"
    return {
        "churn_probability": round(float(prob), 4),
        "risk_level": risk,
        "recommendation": "Contact customer" if risk == "HIGH" else "Monitor only"
    }
from fastapi.middleware.cors import CORSMiddleware

