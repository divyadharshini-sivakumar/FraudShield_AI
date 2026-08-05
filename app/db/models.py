from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime
from datetime import datetime
from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)

class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    amount = Column(Float)
    merchant = Column(String)
    merchant_category = Column(String)
    payment_method = Column(String)
    payment_channel = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    device_type = Column(String)
    fraud_prediction = Column(String)
    fraud_probability = Column(Float)
    risk_score = Column(Float)
    risk_level = Column(String)
    applied_threshold = Column(Float)
    model_name = Column(String)
    model_version = Column(String)
    dataset_source = Column(String)
    anomaly_factors = Column(JSON)
    explanation = Column(String)
    recommendation = Column(String)
    investigation_status = Column(String, default="Pending")
    analyst_notes = Column(Text)
    prediction_latency_ms = Column(Float)
    input_data = Column(JSON)
