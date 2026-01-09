FROM apache/airflow:3.1.5-python3.11

USER root

# Системные пакеты (по минимуму; добавляй только реально нужное)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY r.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER airflow
