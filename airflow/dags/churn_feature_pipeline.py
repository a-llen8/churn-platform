from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import duckdb
import pandas as pd
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def compute_churn_features():
    con = duckdb.connect('/opt/airflow/duckdb/churn_airflow.db')
    
    df = con.execute("""
        SELECT
            customer_id,
            COUNT(*) as total_events,
            AVG(monthly_charges) as avg_monthly_charges,
            AVG(tenure_months) as avg_tenure_months,
            AVG(num_support_tickets) as avg_support_tickets,
            AVG(last_login_days_ago) as avg_last_login_days,
            AVG(num_products) as avg_num_products,
            SUM(churned) as churn_count,
            MAX(timestamp) as last_seen
        FROM customer_events
        GROUP BY customer_id
    """).df()
    
    df['churn_rate'] = df['churn_count'] / df['total_events']
    df['is_high_risk'] = (df['churn_rate'] > 0.5).astype(int)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS churn_features AS 
        SELECT * FROM df
    """)
    
    con.execute("DELETE FROM churn_features")
    con.execute("INSERT INTO churn_features SELECT * FROM df")
    
    print(f"✅ Computed features for {len(df)} customers")
    print(df.head())
    con.close()

with DAG(
    dag_id='churn_feature_pipeline',
    default_args=default_args,
    description='Daily churn feature computation',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    compute_features = PythonOperator(
        task_id='compute_churn_features',
        python_callable=compute_churn_features
    )

    compute_features