from kafka import KafkaConsumer
import json
import duckdb
import os

# Setup DuckDB
con = duckdb.connect('duckdb/churn_airflow.db')
con.execute("""
    CREATE TABLE IF NOT EXISTS customer_events (
        customer_id INTEGER,
        name VARCHAR,
        age INTEGER,
        tenure_months INTEGER,
        monthly_charges FLOAT,
        num_support_tickets INTEGER,
        last_login_days_ago INTEGER,
        num_products INTEGER,
        churned INTEGER,
        timestamp FLOAT
    )
""")

consumer = KafkaConsumer(
    'customer-events',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='churn-group'
)

print("Listening for customer events...")
for message in consumer:
    event = message.value
    con.execute("""
        INSERT INTO customer_events VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        event['customer_id'], event['name'], event['age'],
        event['tenure_months'], event['monthly_charges'],
        event['num_support_tickets'], event['last_login_days_ago'],
        event['num_products'], event['churned'], event['timestamp']
    ])
    print(f"Saved: Customer {event['customer_id']} to DuckDB")