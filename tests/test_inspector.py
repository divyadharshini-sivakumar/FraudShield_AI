import pandas as pd
from app.core.dataset_inspector import DatasetInspector

def test_inspector_with_synthetic_data():
    data = {
        'Age': [25, 30, 35],
        'Amount': [100.5, 200.0, 50.2],
        'Fraud_Label': [0, 1, 0]
    }
    df = pd.DataFrame(data)
    
    inspector = DatasetInspector(df)
    assert inspector is not None
