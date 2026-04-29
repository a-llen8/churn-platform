from kafka import KafkaProducer
import json
import time
import random
from faker import Faker

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_customer_event():
    return {
        "customer_id": random.randint(1, 1000),
        "name": fake.name(),
        "age": random.randint(18, 70),
        "tenure_months": random.randint(1, 60),
        "monthly_charges": round(random.uniform(20, 120), 2),
        "num_support_tickets": random.randint(0, 10),
        "last_login_days_ago": random.randint(0, 90),
        "num_products": random.randint(1, 5),
        "churned": random.choice([0, 1]),
        "timestamp": time.time()
    }

print("Starting to send customer events...")
while True:
    event = generate_customer_event()
    producer.send('customer-events', value=event)
    print(f"Sent: Customer {event['customer_id']} | Churned: {event['churned']}")
    time.sleep(1)