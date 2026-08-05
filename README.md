# 🛡️ FraudShield AI

**FraudShield AI** is an open-source, locally runnable, end-to-end AI-powered fraud detection and risk analysis platform.

## Features
- **FastAPI Backend** — Real-time fraud prediction REST API
- **Streamlit Dashboard** — Interactive analytics with Plotly charts
- **Dual ML Models** — XGBoost + RandomForest with automatic comparison
- **SMOTE Balancing** — Handles class imbalance via oversampling
- **AI Chatbot** — OpenRouter-powered assistant (restricted to fraud/security topics)
- **Dataset Inspector** — Automatic column profiling, leakage detection
- **Auto-versioned Models** — Timestamp-based model saving with training reports
- **PostgreSQL Support** — Optional database for prediction logging

## Project Structure
```
FraudShield_AI/
├── app/                        # FastAPI backend
│   ├── api/                    # API endpoints (predict, health)
│   ├── core/                   # Config, logger, dataset inspector
│   ├── db/                     # SQLAlchemy models & session
│   ├── models/                 # ML pipeline & trainer
│   ├── schemas/                # Pydantic request/response models
│   └── main.py                 # FastAPI entry point
├── frontend/                   # Streamlit frontend
│   ├── pages/                  # Dashboard, predict, train, chatbot, reports
│   └── streamlit_app.py        # Main Streamlit entry point
├── scripts/                    # CLI tools
│   └── train.py                # Command-line training script
├── tests/                      # Unit tests
│   ├── test_inspector.py
│   └── test_predict_api.py
├── trained_models/             # Saved model artifacts (.joblib)
├── reports/                    # Training reports (JSON)
├── datasets/                   # Additional datasets
├── historical_transactions.csv # Primary training dataset
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Quick Start

### 1. Install Dependencies
```bash
cd FraudShield_AI
pip install -r requirements.txt
```

### 2. Train Models (CLI)
```bash
python -m scripts.train --csv_path historical_transactions.csv --target Fraud_Label
```

### 3. Start FastAPI Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Launch Streamlit Dashboard
```bash
streamlit run frontend/streamlit_app.py
```
Dashboard: [http://localhost:8501](http://localhost:8501)

### 5. Run Tests
```bash
pytest tests/ -v
```

## Environment Variables (Optional)
Copy `.env.example` to `.env` and fill in values:
```
OPENROUTER_API_KEY=your_key_here    # Required for AI Chatbot
POSTGRES_USER=postgres              # Required for DB logging
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fraudshield
```

## Dataset
The system is pre-configured for the `historical_transactions.csv` dataset with these key columns:
- **Target:** `Fraud_Label` (0 = Genuine, 1 = Fraud)
- **Features:** Amount, Age, Merchant info, Payment method, Device details, Risk scores, etc.
- **Binary flags:** Is_New_Device, Is_New_Location, Outside_Normal_Hours (Yes/No → 1/0)

## Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| ML Models | XGBoost, RandomForest, Scikit-learn |
| Balancing | imbalanced-learn (SMOTE) |
| Database | PostgreSQL + SQLAlchemy |
| AI Chatbot | OpenRouter (Gemini 2.0 Flash) |

## License
MIT License — free for personal and commercial use.
