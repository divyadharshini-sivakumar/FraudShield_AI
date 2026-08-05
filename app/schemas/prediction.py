from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    transaction_data: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: str
    fraud_probability: float
    risk_score: float
    risk_level: str
    applied_threshold: float
    model_name: str
    model_version: str
    dataset_source: str
    prediction_timestamp: datetime
    contributing_factors: List[str]
    recommendation: str
    detection_id: int

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_path: str
    features_count: int
    categorical_features: List[str]
    numeric_features: List[str]
    loaded_at: datetime

class DetectionRecordSchema(BaseModel):
    id: int
    transaction_id: str
    prediction_timestamp: datetime
    user_id: str
    amount: float
    merchant: str
    merchant_category: str
    payment_method: str
    payment_channel: str
    city: str
    state: str
    country: str
    device_type: str
    fraud_prediction: str
    fraud_probability: float
    risk_score: float
    risk_level: str
    applied_threshold: float
    model_name: str
    model_version: str
    dataset_source: str
    anomaly_factors: Any
    explanation: Optional[str] = None
    recommendation: Optional[str] = None
    investigation_status: str
    analyst_notes: Optional[str] = None
    prediction_latency_ms: float
    input_data: Any

    class Config:
        from_attributes = True

class InvestigationUpdate(BaseModel):
    investigation_status: str
    analyst_notes: str
