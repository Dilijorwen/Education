FROM apache/airflow:3.1.5-python3.13

USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
USER airflow

COPY r.txt /r.txt
RUN pip install --no-cache-dir -r /r.txt
