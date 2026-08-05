import csv
import glob
import io
import os
import time
from datetime import datetime
from typing import List, Optional

import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.models import DetectionRecord
from app.db.session import engine, get_db
from app.schemas.prediction import (
    DetectionRecordSchema,
    InvestigationUpdate,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)


router = APIRouter()


# ============================================================
# MODEL GLOBALS
# ============================================================

model_pipeline = None
model_loaded_at = None
model_name_info = "Not loaded"
model_version_info = "1.0.0"
model_path_info = ""


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

MODELS_DIR = os.path.join(
    PROJECT_ROOT,
    "trained_models",
)


# ============================================================
# MODEL FEATURES
# ============================================================

CATEGORICAL_FEATURES = [
    "Gender",
    "Occupation",
    "Merchant_Name",
    "Merchant_Category",
    "Transaction_Type",
    "Payment_Method",
    "Payment_Channel",
    "Currency",
    "City",
    "State",
    "Country",
    "Device_Type",
    "Operating_System",
    "Browser",
    "Network_Type",
]

NUMERIC_FEATURES = [
    "Age",
    "Account_Age_Months",
    "Amount",
    "Is_New_Device",
    "Is_New_Location",
    "Outside_Normal_Hours",
    "Amount_Deviation",
    "Previous_Transactions_24H",
    "Transactions_Last_10_Min",
    "Merchant_Previously_Used",
]


# ============================================================
# MODEL LOADING
# ============================================================

def find_latest_model() -> Optional[str]:
    """
    Return the newest .joblib model file from trained_models.
    """

    if not os.path.exists(MODELS_DIR):
        print(
            f"Model directory does not exist: {MODELS_DIR}"
        )
        return None

    joblib_files = glob.glob(
        os.path.join(
            MODELS_DIR,
            "*.joblib",
        )
    )

    if not joblib_files:
        print(
            f"No .joblib files found in: {MODELS_DIR}"
        )
        return None

    return max(
        joblib_files,
        key=os.path.getmtime,
    )


def load_latest_model() -> None:
    """
    Load the newest trained model when the API starts.
    """

    global model_pipeline
    global model_loaded_at
    global model_name_info
    global model_path_info

    latest_model = find_latest_model()

    if latest_model is None:
        model_pipeline = None
        model_loaded_at = None
        model_name_info = "Not loaded"
        model_path_info = ""
        return

    try:
        model_pipeline = joblib.load(
            latest_model
        )

        model_loaded_at = datetime.utcnow()
        model_name_info = os.path.basename(
            latest_model
        )
        model_path_info = latest_model

        print(
            f"Loaded model: {model_name_info}"
        )
        print(
            f"Model path: {model_path_info}"
        )

    except Exception as exc:
        model_pipeline = None
        model_loaded_at = None
        model_name_info = "Not loaded"
        model_path_info = ""

        print(
            f"Failed to load model: {exc}"
        )


def refresh_model_if_needed() -> None:
    """
    Reload the model if a newer .joblib file is available.
    """

    global model_pipeline
    global model_loaded_at
    global model_name_info
    global model_path_info

    latest_model = find_latest_model()

    if latest_model is None:
        return

    latest_model = os.path.abspath(
        latest_model
    )

    current_model = (
        os.path.abspath(model_path_info)
        if model_path_info
        else ""
    )

    if (
        model_pipeline is not None
        and latest_model == current_model
    ):
        return

    try:
        model_pipeline = joblib.load(
            latest_model
        )

        model_loaded_at = datetime.utcnow()
        model_name_info = os.path.basename(
            latest_model
        )
        model_path_info = latest_model

        print(
            f"Reloaded latest model: "
            f"{model_name_info}"
        )

    except Exception as exc:
        print(
            f"Failed to reload model: {exc}"
        )


# Load the model when this module is imported.
load_latest_model()


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health_check():
    db_backend = (
        "postgres"
        if "postgres" in str(engine.url).lower()
        else "sqlite"
    )

    return {
        "status": "ok",
        "db_backend": db_backend,
        "model_loaded": model_pipeline is not None,
        "model_name": model_name_info,
        "model_path": model_path_info,
        "models_directory": MODELS_DIR,
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
)
def model_info():
    refresh_model_if_needed()

    if model_pipeline is None:
        raise HTTPException(
            status_code=404,
            detail="Model not loaded",
        )

    return {
        "model_name": model_name_info,
        "model_version": model_version_info,
        "model_path": model_path_info,
        "features_count": (
            len(CATEGORICAL_FEATURES)
            + len(NUMERIC_FEATURES)
        ),
        "categorical_features": (
            CATEGORICAL_FEATURES
        ),
        "numeric_features": NUMERIC_FEATURES,
        "loaded_at": (
            model_loaded_at
            or datetime.utcnow()
        ),
    }


# ============================================================
# PREDICTION
# ============================================================

@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db),
):
    start_time = time.time()

    refresh_model_if_needed()

    if model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not initialized",
        )

    data = request.transaction_data.copy()

    binary_columns = [
        "Is_New_Device",
        "Is_New_Location",
        "Outside_Normal_Hours",
        "Merchant_Previously_Used",
    ]

    for column in binary_columns:
        value = data.get(column)

        if isinstance(value, str):
            data[column] = (
                1
                if value.strip().lower() == "yes"
                else 0
            )
        elif isinstance(value, bool):
            data[column] = int(value)
        elif value is None:
            data[column] = 0
        else:
            data[column] = int(value)

    row = {}

    for column in CATEGORICAL_FEATURES:
        value = data.get(column)

        row[column] = (
            str(value)
            if value not in (None, "")
            else "Unknown"
        )

    for column in NUMERIC_FEATURES:
        value = data.get(column)

        if value in (None, ""):
            row[column] = 0
        else:
            try:
                row[column] = float(value)
            except (TypeError, ValueError):
                row[column] = 0

    dataframe = pd.DataFrame(
        [row]
    )

    try:
        probabilities = (
            model_pipeline.predict_proba(
                dataframe
            )[0]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Model prediction failed: "
                f"{exc}"
            ),
        ) from exc

    fraud_probability = (
        float(probabilities[1])
        if len(probabilities) > 1
        else 0.0
    )

    if fraud_probability >= 0.85:
        risk_level = "Critical"

    elif fraud_probability >= 0.60:
        risk_level = "High"

    elif fraud_probability >= 0.30:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    prediction_label = (
        "Fraud"
        if fraud_probability >= 0.50
        else "Legitimate"
    )

    factors = []

    amount = float(
        data.get("Amount", 0) or 0
    )

    if amount > 1000:
        factors.append(
            f"High transaction amount: {amount}"
        )

    if data.get("Is_New_Device", 0) == 1:
        factors.append(
            "New device detected"
        )

    if data.get("Is_New_Location", 0) == 1:
        factors.append(
            "New location detected"
        )

    if (
        data.get(
            "Outside_Normal_Hours",
            0,
        )
        == 1
    ):
        factors.append(
            "Transaction outside normal hours"
        )

    if (
        float(
            data.get(
                "Transactions_Last_10_Min",
                0,
            )
            or 0
        )
        >= 5
    ):
        factors.append(
            "High transaction frequency"
        )

    latency_ms = (
        time.time() - start_time
    ) * 1000

    record = DetectionRecord(
        transaction_id=str(
            data.get(
                "Transaction_ID",
                "UNKNOWN",
            )
        ),
        user_id=str(
            data.get(
                "User_ID",
                "UNKNOWN",
            )
        ),
        amount=amount,
        merchant=str(
            data.get(
                "Merchant_Name",
                "UNKNOWN",
            )
        ),
        merchant_category=str(
            data.get(
                "Merchant_Category",
                "UNKNOWN",
            )
        ),
        payment_method=str(
            data.get(
                "Payment_Method",
                "UNKNOWN",
            )
        ),
        payment_channel=str(
            data.get(
                "Payment_Channel",
                "UNKNOWN",
            )
        ),
        city=str(
            data.get(
                "City",
                "UNKNOWN",
            )
        ),
        state=str(
            data.get(
                "State",
                "UNKNOWN",
            )
        ),
        country=str(
            data.get(
                "Country",
                "UNKNOWN",
            )
        ),
        device_type=str(
            data.get(
                "Device_Type",
                "UNKNOWN",
            )
        ),
        fraud_prediction=prediction_label,
        fraud_probability=fraud_probability,
        risk_score=fraud_probability * 100,
        risk_level=risk_level,
        applied_threshold=0.50,
        model_name=model_name_info,
        model_version=model_version_info,
        dataset_source="API",
        anomaly_factors=factors,
        recommendation=(
            "Investigate"
            if risk_level in [
                "High",
                "Critical",
            ]
            else "Approve"
        ),
        prediction_latency_ms=latency_ms,
        input_data=request.transaction_data,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction succeeded, but "
                "saving the detection failed: "
                f"{exc}"
            ),
        ) from exc

    return PredictionResponse(
        prediction=prediction_label,
        fraud_probability=fraud_probability,
        risk_score=fraud_probability * 100,
        risk_level=risk_level,
        applied_threshold=0.50,
        model_name=model_name_info,
        model_version=model_version_info,
        dataset_source="API",
        prediction_timestamp=(
            record.prediction_timestamp
        ),
        contributing_factors=factors,
        recommendation=record.recommendation,
        detection_id=record.id,
    )


# ============================================================
# DETECTIONS
# ============================================================

@router.get(
    "/detections",
    response_model=List[
        DetectionRecordSchema
    ],
)
def list_detections(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(
        DetectionRecord
    )

    if status:
        query = query.filter(
            DetectionRecord.investigation_status
            == status
        )

    if risk_level:
        query = query.filter(
            DetectionRecord.risk_level
            == risk_level
        )

    return query.order_by(
        DetectionRecord.id.desc()
    ).all()


# ============================================================
# EXPORT CSV
# ============================================================

@router.get("/detections/export/csv")
def export_csv(
    db: Session = Depends(get_db),
):
    records = db.query(
        DetectionRecord
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        column.name
        for column
        in DetectionRecord.__table__.columns
    ]

    writer.writerow(headers)

    for record in records:
        row = []

        for header in headers:
            value = getattr(
                record,
                header,
            )

            if isinstance(
                value,
                datetime,
            ):
                value = value.isoformat()

            row.append(value)

        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=detections.csv"
            )
        },
    )


# ============================================================
# EXPORT JSON
# ============================================================

@router.get("/detections/export/json")
def export_json(
    db: Session = Depends(get_db),
):
    records = db.query(
        DetectionRecord
    ).all()

    output = []

    for record in records:
        record_data = {}

        for column in (
            DetectionRecord
            .__table__
            .columns
        ):
            value = getattr(
                record,
                column.name,
            )

            if isinstance(
                value,
                datetime,
            ):
                value = value.isoformat()

            record_data[
                column.name
            ] = value

        output.append(
            record_data
        )

    return output


# ============================================================
# GET ONE DETECTION
# ============================================================

@router.get(
    "/detections/{id}",
    response_model=DetectionRecordSchema,
)
def get_detection(
    id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(DetectionRecord)
        .filter(
            DetectionRecord.id == id
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Detection not found",
        )

    return record


# ============================================================
# INVESTIGATE DETECTION
# ============================================================

@router.put(
    "/detections/{id}/investigate",
    response_model=DetectionRecordSchema,
)
def investigate_detection(
    id: int,
    update: InvestigationUpdate,
    db: Session = Depends(get_db),
):
    record = (
        db.query(DetectionRecord)
        .filter(
            DetectionRecord.id == id
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Detection not found",
        )

    record.investigation_status = (
        update.investigation_status
    )
    record.analyst_notes = (
        update.analyst_notes
    )

    try:
        db.commit()
        db.refresh(record)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update investigation: "
                f"{exc}"
            ),
        ) from exc

    return record