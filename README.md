# 🔄 Customer Churn Prevention Platform

An enterprise-grade, end-to-end MLOps platform that predicts customer churn in real-time and automatically triggers targeted interventions — built with the same architecture used by companies like Airtel, Swiggy, and HDFC.

---

## 🎯 Problem Statement

Every month, telecom and SaaS companies lose thousands of customers silently. By the time the business notices, it's too late. This platform solves that by:
- Capturing customer behavior in real-time
- Predicting churn risk automatically every day
- Identifying which customers will actually respond to an intervention
- Serving predictions via API to any downstream application
- Monitoring model health and alerting on data drift

---

## 🏗️ Architecture

```
Customer Events
      ↓
Kafka (Real-time Streaming)
      ↓
DuckDB (Local Data Warehouse)
      ↓
Airflow (Daily Feature Pipeline)
      ↓
XGBoost + SHAP (Churn Prediction)
      ↓
CausalML (Uplift Modeling)
      ↓
MLflow (Experiment Tracking)
      ↓
FastAPI + Docker (Model Serving)
      ↓
Evidently + Slack (Monitoring)
      ↓
Streamlit (Business Dashboard)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Streaming | Apache Kafka | Real-time customer event ingestion |
| Storage | DuckDB | Local analytical data warehouse |
| Orchestration | Apache Airflow | Automated daily feature pipeline |
| ML Modeling | XGBoost | Churn prediction |
| Explainability | SHAP | Model interpretability |
| Causal ML | CausalML (Uber) | Uplift modeling |
| Experiment Tracking | MLflow | Model versioning & comparison |
| Model Serving | FastAPI + Docker | REST API for predictions |
| Monitoring | Evidently AI | Data drift detection |
| Alerting | Slack API | Real-time drift alerts |
| Dashboard | Streamlit | Business-facing UI |

---

## 📦 Modules

### ✅ Module 1 — Real-Time Data Pipeline
Simulates customer behavioral events (logins, support tickets, payments) using a Kafka producer. A consumer picks up events and stores them in DuckDB — the same pattern used in production data platforms.

### ✅ Module 2 — Feature Engineering Pipeline
An Airflow DAG runs daily and computes churn features from raw events — RFM scores, average charges, support ticket frequency, login recency, and churn rate per customer.

### 🔄 Module 3 — Churn Prediction Model *(In Progress)*
XGBoost model trained on computed features. SHAP values explain every prediction. MLflow tracks all experiments — parameters, metrics, and model artifacts.

### ⏳ Module 4 — Uplift Modeling
CausalML identifies customers where intervention actually makes a difference — not just who will churn, but who will respond to a retention offer.

### ⏳ Module 5 — Model Serving
FastAPI wraps the trained model into a REST endpoint. Dockerized for easy deployment anywhere.

### ⏳ Module 6 — Monitoring & Alerting
Evidently monitors feature distributions weekly. If data drift is detected, a Slack alert fires automatically.

### ⏳ Module 7 — Business Dashboard
Streamlit dashboard shows churn risk by customer segment, intervention recommendations, and model performance over time.

---

## 🚀 How to Run

### Prerequisites
- Python 3.12+
- Docker Desktop
- Git

### Setup
```bash
# Clone the repo
git clone https://github.com/yourusername/churn-platform.git
cd churn-platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install kafka-python duckdb pandas

# Start all services
docker-compose up -d

# Run data pipeline (open two terminals)
python kafka/consumer.py   # Terminal 1
python kafka/producer.py   # Terminal 2
```

### Access Airflow
```
URL: http://localhost:8080
Username: admin
Password: admin123
```

---

## 💡 Key Interview Talking Points

- *"I built an end-to-end MLOps pipeline, not just a model"*
- *"Airflow automates daily feature recomputation — no manual intervention needed"*
- *"SHAP explains every prediction so business teams can trust the model"*
- *"CausalML targets only customers where intervention makes a difference — saving marketing budget"*
- *"Evidently monitors for data drift — if customer behavior shifts, we catch it before the business feels it"*

---

## 📊 Dataset
IBM Telco Customer Churn dataset replayed through Kafka to simulate real-time streaming.

---

## 👤 Author
Built as a portfolio project to demonstrate enterprise-grade Data Science and MLOps skills.
