"""ML pipeline for preprocessing and model handling.

The pipeline wraps a sklearn ColumnTransformer (one‑hot for categoricals,
standard scaling for numerics) and a trained model (XGBoost or RandomForest).
It provides `fit`, `predict_proba`, `save` and `load` methods.
"""
import joblib
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

class ModelPipeline:
    def __init__(self, categorical_cols: List[str], numeric_cols: List[str]):
        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), self.categorical_cols),
                ("num", StandardScaler(), self.numeric_cols),
            ]
        )
        self.model = None

    def fit(self, X: pd.DataFrame, y: pd.Series, model) -> None:
        """Fit preprocessing then the supplied model.
        `model` should already be instantiated (e.g. XGBClassifier()).
        """
        self.model = model
        X_pre = self.preprocessor.fit_transform(X)
        self.model.fit(X_pre, y)

    def predict_proba(self, X: pd.DataFrame) -> float:
        X_pre = self.preprocessor.transform(X)
        prob = self.model.predict_proba(X_pre)[:, 1]
        return float(prob[0]) if prob.size == 1 else prob.tolist()

    def predict(self, X: pd.DataFrame) -> int:
        X_pre = self.preprocessor.transform(X)
        return int(self.model.predict(X_pre)[0])

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.preprocessor, directory / "preprocessor.joblib")
        joblib.dump(self.model, directory / "model.joblib")

    @classmethod
    def load(cls, directory: Path, categorical_cols: List[str], numeric_cols: List[str]):
        pipeline = cls(categorical_cols, numeric_cols)
        pipeline.preprocessor = joblib.load(directory / "preprocessor.joblib")
        pipeline.model = joblib.load(directory / "model.joblib")
        return pipeline
