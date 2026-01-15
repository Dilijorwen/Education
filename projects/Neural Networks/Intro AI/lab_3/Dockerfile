FROM apache/airflow:3.1.5

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

USER airflow

COPY r.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt