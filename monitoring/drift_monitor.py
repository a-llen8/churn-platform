import duckdb
import pandas as pd
import os
from evidently import Dataset, DataDefinition
from evidently.presets import DataDriftPreset
from evidently import Report

print("Loading data from DuckDB...")
con = duckdb.connect('duckdb/churn_airflow.db')
df = con.execute("SELECT * FROM churn_features").df()
con.close()

feature_cols = [
    'avg_monthly_charges',
    'avg_tenure_months', 
    'avg_support_tickets',
    'avg_last_login_days',
    'avg_num_products',
    'total_events'
]

split = int(len(df) * 0.5)
reference_data = df[feature_cols].iloc[:split]
current_data = df[feature_cols].iloc[split:]

print(f"Reference: {len(reference_data)} rows | Current: {len(current_data)} rows")

reference = Dataset.from_pandas(reference_data, data_definition=DataDefinition())
current = Dataset.from_pandas(current_data, data_definition=DataDefinition())

report = Report([DataDriftPreset()])
result = report.run(reference, current)

os.makedirs("monitoring/reports", exist_ok=True)
result.save_html("monitoring/reports/drift_report.html")
print("✅ Drift report saved!")
print(result.dict())