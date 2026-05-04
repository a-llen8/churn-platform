import duckdb
import pandas as pd
import numpy as np
from causalml.inference.tree import UpliftTreeClassifier
from causalml.metrics import plot_gain
import mlflow
import matplotlib.pyplot as plt
import os

# ── 1. Load features from DuckDB ──────────────────────────────
print("Loading data from DuckDB...")
con = duckdb.connect('duckdb/churn_airflow.db')
df = con.execute("SELECT * FROM churn_features").df()
con.close()

print(f"Loaded {len(df)} customers")

# ── 2. Simulate treatment (who received retention offer) ───────
np.random.seed(42)
df['treatment'] = np.random.choice(['treatment', 'control'], size=len(df))

# Simulate response — treated high risk customers more likely to respond
df['response'] = 0
df.loc[(df['treatment'] == 'treatment') & (df['is_high_risk'] == 1), 'response'] = \
    np.random.binomial(1, 0.4, sum((df['treatment'] == 'treatment') & (df['is_high_risk'] == 1)))
df.loc[(df['treatment'] == 'control') & (df['is_high_risk'] == 1), 'response'] = \
    np.random.binomial(1, 0.1, sum((df['treatment'] == 'control') & (df['is_high_risk'] == 1)))

# ── 3. Prepare features ───────────────────────────────────────
feature_cols = [
    'avg_monthly_charges',
    'avg_tenure_months',
    'avg_support_tickets',
    'avg_last_login_days',
    'avg_num_products',
    'total_events'
]

X = df[feature_cols].values
treatment = df['treatment'].values
y = df['response'].values

# ── 4. Train Uplift Model ─────────────────────────────────────
print("\nTraining Uplift Model...")
uplift_model = UpliftTreeClassifier(
    control_name='control',
    max_depth=4,
    min_samples_leaf=10,
    min_samples_treatment=5,
    n_reg=100
)

uplift_model.fit(X, treatment=treatment, y=y)

# ── 5. Predict uplift scores ──────────────────────────────────
uplift_scores = uplift_model.predict(X)
df['uplift_score'] = uplift_scores[:, 0]

# ── 6. Segment customers ──────────────────────────────────────
df['intervention_recommendation'] = pd.cut(
    df['uplift_score'],
    bins=[-np.inf, 0.05, 0.15, np.inf],
    labels=['Do Not Contact', 'Low Priority', 'High Priority']
)

print("\n✅ Uplift Score Distribution:")
print(df['intervention_recommendation'].value_counts())

# ── 7. Log to MLflow ──────────────────────────────────────────
mlflow.set_experiment("churn-prediction")

with mlflow.start_run(run_name="uplift-model"):
    mlflow.log_param("model_type", "UpliftTreeClassifier")
    mlflow.log_param("max_depth", 4)
    mlflow.log_metric("avg_uplift_score", float(df['uplift_score'].mean()))
    mlflow.log_metric("high_priority_customers", 
                      int((df['intervention_recommendation'] == 'High Priority').sum()))

    # Save recommendations
    os.makedirs("models/outputs", exist_ok=True)
    df[['customer_id', 'uplift_score', 'intervention_recommendation', 'is_high_risk']]\
        .to_csv("models/outputs/intervention_recommendations.csv", index=False)
    mlflow.log_artifact("models/outputs/intervention_recommendations.csv")

    print("\n✅ Uplift model logged to MLflow!")
    print("✅ Intervention recommendations saved!")

print("\n📊 Sample Recommendations:")
print(df[['customer_id', 'uplift_score', 'intervention_recommendation']].head(10))