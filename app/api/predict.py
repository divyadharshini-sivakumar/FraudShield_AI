import time
import os
import glob
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import csv
import json

from app.schemas.prediction import PredictionRequest, PredictionResponse, ModelInfoResponse, DetectionRecordSchema, InvestigationUpdate
from app.db.models import DetectionRecord
from app.db.session import get_db, engine

router = APIRouter()

# Model globals
model_pipeline = None
model_loaded_at = None
model_name_info = "Not loaded"
model_version_info = "1.0.0"
model_path_info = ""

# Define features
CATEGORICAL_FEATURES = ["Gender", "Occupation", "Merchant_Name", "Merchant_Category", "Transaction_Type", "Payment_Method", "Payment_Channel", "Currency", "City", "State", "Country", "Device_Type", "Operating_System", "Browser", "Network_Type"]
NUMERIC_FEATURES = ["Age", "Account_Age_Months", "Amount", "Is_New_Device", "Is_New_Location", "Outside_Normal_Hours", "Amount_Deviation", "Previous_Transactions_24H", "Transactions_Last_10_Min", "Merchant_Previously_Used"]

def load_latest_model():
    global model_pipeline, model_loaded_at, model_name_info, model_path_info
    models_dir = "trained_models"
    if os.path.exists(models_dir):
        joblib_files = glob.glob(os.path.join(models_dir, "*.joblib"))
        if joblib_files:
            latest_model = max(joblib_files, key=os.path.getmtime)
            model_pipeline = joblib.load(latest_model)
            model_loaded_at = datetime.utcnow()
            model_name_info = os.path.basename(latest_model)
            model_path_info = latest_model
            print(f"Loaded model: {model_name_info}")
        else:
            print("No .joblib files found in trained_models/")
    else:
        print("trained_models/ directory does not exist")
def refresh_model_if_needed():
    global model_pipeline, model_loaded_at, model_name_info, model_path_info

    models_dir = "trained_models"

    if not os.path.exists(models_dir):
        return

    joblib_files = glob.glob(os.path.join(models_dir, "*.joblib"))

    if not joblib_files:
        return

    latest_model = max(joblib_files, key=os.path.getmtime)

    if latest_model != model_path_info:
        model_pipeline = joblib.load(latest_model)
        model_loaded_at = datetime.utcnow()
        model_name_info = os.path.basename(latest_model)
        model_path_info = latest_model
        print(f"Reloaded latest model: {model_name_info}")
load_latest_model()

@router.get("/health")
def health_check():
    db_backend = "postgres" if "postgres" in str(engine.url) else "sqlite"
    return {
        "status": "ok",
        "db_backend": db_backend,
        "model_loaded": model_pipeline is not None,
        "model_name": model_name_info
    }

@router.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    refresh_model_if_needed()
    if not model_pipeline:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {
        "model_name": model_name_info,
        "model_version": model_version_info,
        "model_path": model_path_info,
        "features_count": len(CATEGORICAL_FEATURES) + len(NUMERIC_FEATURES),
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "loaded_at": model_loaded_at or datetime.utcnow()
    }

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    refresh_model_if_needed()
    
    if not model_pipeline:
        raise HTTPException(status_code=503, detail="Model not initialized")
        
    data = request.transaction_data.copy()
    
    # Preprocess binary strings to 1/0
    binary_cols = ["Is_New_Device", "Is_New_Location", "Outside_Normal_Hours", "Merchant_Previously_Used"]
    for col in binary_cols:
        if col in data:
            data[col] = 1 if data[col] == 'Yes' else 0

    # Ensure all features are present
    row = {}
    for col in CATEGORICAL_FEATURES + NUMERIC_FEATURES:
        row[col] = data.get(col, 0 if col in NUMERIC_FEATURES else "Unknown")
        
    df = pd.DataFrame([row])
    
    # Predict
    probabilities = model_pipeline.predict_proba(df)[0]
    fraud_prob = float(probabilities[1]) if len(probabilities) > 1 else 0.0
    
    risk_level = "Low"
    if fraud_prob >= 0.85:
        risk_level = "Critical"
    elif fraud_prob >= 0.6:
        risk_level = "High"
    elif fraud_prob >= 0.3:
        risk_level = "Medium"
        
    prediction_label = "Fraud" if fraud_prob >= 0.5 else "Legitimate"
    
    # Generate mock contributing factors based on values
    factors = []
    if float(data.get("Amount", 0)) > 1000:
        factors.append(f"High transaction amount: {data.get('Amount')}")
    if data.get("Is_New_Device", 0) == 1:
        factors.append("New device detected")
    if data.get("Is_New_Location", 0) == 1:
        factors.append("New location detected")
        
    latency_ms = (time.time() - start_time) * 1000
    
    record = DetectionRecord(
        transaction_id=str(data.get("Transaction_ID", "UNKNOWN")),
        user_id=str(data.get("User_ID", "UNKNOWN")),
        amount=float(data.get("Amount", 0)),
        merchant=str(data.get("Merchant_Name", "UNKNOWN")),
        merchant_category=str(data.get("Merchant_Category", "UNKNOWN")),
        payment_method=str(data.get("Payment_Method", "UNKNOWN")),
        payment_channel=str(data.get("Payment_Channel", "UNKNOWN")),
        city=str(data.get("City", "UNKNOWN")),
        state=str(data.get("State", "UNKNOWN")),
        country=str(data.get("Country", "UNKNOWN")),
        device_type=str(data.get("Device_Type", "UNKNOWN")),
        fraud_prediction=prediction_label,
        fraud_probability=fraud_prob,
        risk_score=fraud_prob * 100,
        risk_level=risk_level,
        applied_threshold=0.5,
        model_name=model_name_info,
        model_version=model_version_info,
        dataset_source="API",
        anomaly_factors=factors,
        recommendation="Investigate" if risk_level in ["High", "Critical"] else "Approve",
        prediction_latency_ms=latency_ms,
        input_data=request.transaction_data
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return PredictionResponse(
        prediction=prediction_label,
        fraud_probability=fraud_prob,
        risk_score=fraud_prob * 100,
        risk_level=risk_level,
        applied_threshold=0.5,
        model_name=model_name_info,
        model_version=model_version_info,
        dataset_source="API",
        prediction_timestamp=record.prediction_timestamp,
        contributing_factors=factors,
        recommendation=record.recommendation,
        detection_id=record.id
    )

@router.get("/detections", response_model=List[DetectionRecordSchema])
def list_detections(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DetectionRecord)
    if status:
        query = query.filter(DetectionRecord.investigation_status == status)
    if risk_level:
        query = query.filter(DetectionRecord.risk_level == risk_level)
    return query.all()

@router.get("/detections/export/csv")
def export_csv(db: Session = Depends(get_db)):
    records = db.query(DetectionRecord).all()
    output = io.StringIO()
    writer = csv.writer(output)
    if records:
        headers = [c.name for c in DetectionRecord.__table__.columns]
        writer.writerow(headers)
        for r in records:
            writer.writerow([getattr(r, h) for h in headers])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=detections.csv"})

@router.get("/detections/export/json")
def export_json(db: Session = Depends(get_db)):
    records = db.query(DetectionRecord).all()
    data = []
    for r in records:
        r_dict = {c.name: getattr(r, c.name) for c in DetectionRecord.__table__.columns}
        if 'prediction_timestamp' in r_dict and r_dict['prediction_timestamp']:
            r_dict['prediction_timestamp'] = r_dict['prediction_timestamp'].isoformat()
        data.append(r_dict)
    return data

@router.get("/detections/{id}", response_model=DetectionRecordSchema)
def get_detection(id: int, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection not found")
    return record

@router.put("/detections/{id}/investigate", response_model=DetectionRecordSchema)
def investigate_detection(id: int, update: InvestigationUpdate, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection not found")
    record.investigation_status = update.investigation_status
    record.analyst_notes = update.analyst_notes
    db.commit()
    db.refresh(record)
    return record
