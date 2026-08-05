"""Utility to inspect a CSV dataset and produce a JSON schema.
The inspector reads the CSV with pandas, computes column types, missing
values, duplicate rows, class balance, categorical/numerical identification
and simple leakage checks (high correlation with the target).
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

class DatasetInspector:
    def __init__(self, csv_path: Path, target_column: str):
        self.csv_path = csv_path
        self.target_column = target_column
        self.df: pd.DataFrame | None = None
        self.schema: Dict[str, Any] = {}

    def load(self) -> None:
        self.df = pd.read_csv(self.csv_path)

    def analyze(self) -> Dict[str, Any]:
        if self.df is None:
            raise RuntimeError("Dataset not loaded")
        df = self.df
        # Basic stats
        cols = df.columns.tolist()
        dtypes = {c: str(df[c].dtype) for c in cols}
        missing = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        # Target distribution (binary assumed)
        if self.target_column in df.columns:
            target_counts = df[self.target_column].value_counts().to_dict()
        else:
            target_counts = {}
        # Identify categorical vs numeric (simple heuristic)
        categorical = [c for c, t in dtypes.items() if t == "object"]
        numeric = [c for c, t in dtypes.items() if t in ("int64", "float64")]
        # Simple leakage: high correlation (>0.9) with target for numeric columns
        leakage = []
        if self.target_column in df.columns:
            for col in numeric:
                if col == self.target_column:
                    continue
                try:
                    corr = df[col].corr(df[self.target_column])
                    if abs(corr) > 0.9:
                        leakage.append({"column": col, "correlation": corr})
                except Exception:
                    pass
        self.schema = {
            "columns": cols,
            "dtypes": dtypes,
            "missing_counts": missing,
            "duplicate_rows": duplicates,
            "target_distribution": target_counts,
            "categorical_columns": categorical,
            "numeric_columns": numeric,
            "potential_leakage": leakage,
        }
        return self.schema

    def save_schema(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(self.schema, f, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inspect CSV dataset")
    parser.add_argument("csv_path", type=Path, help="Path to CSV file")
    parser.add_argument("target", type=str, help="Target column name")
    parser.add_argument("--out", type=Path, default=None, help="Where to write schema JSON")
    args = parser.parse_args()
    inspector = DatasetInspector(args.csv_path, args.target)
    inspector.load()
    schema = inspector.analyze()
    out = args.out or args.csv_path.with_name(args.csv_path.stem + "_schema.json")
    inspector.save_schema(out)
    print(f"Schema saved to {out}")
