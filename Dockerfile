FROM apache/airflow:2.8.1-python3.10
USER root
RUN apt-get update && apt-get install -y gcc g++
USER airflow
RUN pip install --no-cache-dir "duckdb==1.5.2" pandas