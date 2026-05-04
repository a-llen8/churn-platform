import duckdb
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import shap
import mlflow
import mlflow.xgboost
import matplotlib.pyplot as plt
import os

# ── 1. Load features from DuckDB ──────────────────────────────
print("Loading data from DuckDB...")
con = duckdb.connect('duckdb/churn_airflow.db')
df = con.execute("SELECT * FROM churn_features").df()
con.close()

print(f"Loaded {len(df)} customers")
print(df.head())

# ── 2. Prepare features ───────────────────────────────────────
feature_cols = [
    'avg_monthly_charges',
    'avg_tenure_months',
    'avg_support_tickets',
    'avg_last_login_days',
    'avg_num_products',
    'total_events'
]

X = df[feature_cols]
y = df['is_high_risk']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

# ── 3. Train with MLflow tracking ─────────────────────────────
mlflow.set_experiment("churn-prediction")

with mlflow.start_run():

    # Model parameters
    params = {
        "n_estimators": 100,
        "max_depth": 4,
        "learning_rate": 0.1,
        "random_state": 42
    }

    # Train model
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)

    print(f"\n✅ AUC-ROC: {auc:.4f}")
    print(classification_report(y_test, y_pred))

    # Log to MLflow
    mlflow.log_params(params)
    mlflow.log_metric("auc_roc", auc)
    mlflow.xgboost.log_model(model, "churn_model")

    # ── 4. SHAP Explainability ─────────────────────────────
    print("\nComputing SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # Save SHAP plot
    os.makedirs("models/plots", exist_ok=True)
    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    plt.savefig("models/plots/shap_summary.png")
    plt.close()

    # Log SHAP plot to MLflow
    mlflow.log_artifact("models/plots/shap_summary.png")

    print("✅ Model trained and logged to MLflow!")
    print(f"✅ SHAP plot saved to models/plots/shap_summary.png")