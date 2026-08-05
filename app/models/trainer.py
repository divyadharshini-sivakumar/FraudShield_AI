import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, csv_path: str, target: str = 'Fraud_Label', test_size: float = 0.2):
        self.csv_path = csv_path
        self.target = target
        self.test_size = test_size
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trained_models")
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        self.categorical_features = [
            'Gender', 'Occupation', 'Merchant_Name', 'Merchant_Category', 'Transaction_Type',
            'Payment_Method', 'Payment_Channel', 'Currency', 'City', 'State', 'Country',
            'Device_Type', 'Operating_System', 'Browser', 'Network_Type'
        ]
        self.numeric_features = [
            'Age', 'Account_Age_Months', 'Amount',
            'Is_New_Device', 'Is_New_Location', 'Outside_Normal_Hours', 'Amount_Deviation',
            'Previous_Transactions_24H', 'Transactions_Last_10_Min', 'Merchant_Previously_Used'
        ]
        self.drop_features = [
            'Transaction_ID', 'Timestamp', 'User_ID', 'User_Name', 'Fraud_Label', 'Fraud_Type',
            'AI_Explanation', 'Recommendation', 'Investigation_Status', 'Prediction', 'Merchant_ID',
            'Risk_Score', 'Confidence_Score'  # leakage: derived from target
        ]
        
    def load_data(self):
        logger.info(f"Loading data from {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        return df
        
    def preprocess_data(self, df: pd.DataFrame):
        # Convert Yes/No strings to 1/0
        binary_cols = ['Is_New_Device', 'Is_New_Location', 'Outside_Normal_Hours', 'Merchant_Previously_Used']
        for col in binary_cols:
            if col in df.columns:
                df[col] = df[col].map({'Yes': 1, 'No': 0, 1: 1, 0: 0})
        
        # Drop excluded columns
        cols_to_drop = [c for c in self.drop_features if c in df.columns]
        X = df.drop(columns=cols_to_drop)
        y = df[self.target]
        
        # Ensure only specified features are present
        features = self.categorical_features + self.numeric_features
        X = X[[c for c in features if c in X.columns]]
        
        return X, y
        
    def build_pipeline(self, classifier):
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])
            
        pipeline = ImbPipeline(steps=[
            ('preprocessor', preprocessor),
            ('smote', SMOTE(random_state=42)),
            ('classifier', classifier)
        ])
        
        return pipeline

    def train_and_evaluate(self):
        df = self.load_data()
        X, y = self.preprocess_data(df)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, stratify=y, random_state=42)
        
        models = {
            'RandomForest': RandomForestClassifier(random_state=42, class_weight='balanced'),
            'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
        }
        
        best_model = None
        best_f1 = -1
        best_name = ""
        results = {}
        
        for name, clf in models.items():
            logger.info(f"Training {name}...")
            pipeline = self.build_pipeline(clf)
            pipeline.fit(X_train, y_train)
            
            y_pred = pipeline.predict(X_test)
            y_pred_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else y_pred
            
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred)
            rec = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            results[name] = {
                'accuracy': acc,
                'precision': prec,
                'recall': rec,
                'f1_score': f1,
                'roc_auc': roc_auc
            }
            logger.info(f"{name} metrics: {results[name]}")
            
            if f1 > best_f1:
                best_f1 = f1
                best_model = pipeline
                best_name = name
                
        # Save best model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{best_name.lower()}_{timestamp}.joblib"
        model_path = os.path.join(self.models_dir, model_filename)
        joblib.dump(best_model, model_path)
        logger.info(f"Best model ({best_name}) saved to {model_path}")
        
        # Save report
        report_filename = f"training_report_{timestamp}.json"
        report_path = os.path.join(self.reports_dir, report_filename)
        report_data = {
            'timestamp': timestamp,
            'best_model': best_name,
            'results': results,
            'features': {
                'categorical': self.categorical_features,
                'numeric': self.numeric_features
            }
        }
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
            
        return results, best_name

class ModelRegistry:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trained_models")
        
    def list_models(self):
        if not os.path.exists(self.models_dir):
            return []
        return [f for f in os.listdir(self.models_dir) if f.endswith(".joblib")]
        
    def load_model(self, model_name: str):
        path = os.path.join(self.models_dir, model_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model {model_name} not found")
        return joblib.load(path)
