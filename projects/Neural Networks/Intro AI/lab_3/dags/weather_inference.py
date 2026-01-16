import json
import logging
import os
from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator

POSTGRES_CONN_ID = "weather_postgres"
DATA_DIR = "/opt/airflow/data/weather"
LATEST_META_PATH = os.path.join(DATA_DIR, "latest_meta.json")


def run_inference(**context):
    if not os.path.exists(LATEST_META_PATH):
        raise AirflowSkipException(f"Pointer file not found: {LATEST_META_PATH}")

    with open(LATEST_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    transformed_path = meta.get("transformed_file")
    if not transformed_path or not os.path.exists(transformed_path):
        raise AirflowSkipException(f"Transformed file not found: {transformed_path}")

    with open(transformed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    city = data.get("city")
    observed_time_raw = data.get("observed_time")
    if not city or not observed_time_raw:
        raise AirflowSkipException("Transformed JSON missing city/observed_time")

    try:
        observed_time = datetime.fromisoformat(observed_time_raw)
    except ValueError:
        raise AirflowSkipException(f"Invalid observed_time: {observed_time_raw}")

    t = float(data["temperature_2m"])
    wind = float(data["wind_speed_10m"])
    gusts = float(data["wind_gusts_10m"])
    precip = float(data["precipitation_mm"])
    hum = int(data["relative_humidity"])
    is_day = int(data["is_day"])

    if precip > 0:
        condition = "precipitation"
        severity = 2
    elif gusts >= 20 or wind >= 15:
        condition = "windy"
        severity = 2
    elif t <= -20:
        condition = "very_cold"
        severity = 2
    elif t <= -10:
        condition = "cold"
        severity = 1
    elif t >= 30:
        condition = "hot"
        severity = 2
    else:
        condition = "normal"
        severity = 0

    tags = []
    if is_day == 0:
        tags.append("night")
    if hum >= 85:
        tags.append("high_humidity")

    inference_payload = {
        "city": city,
        "observed_time": observed_time_raw,
        "rule_version": "if_v1",
        "inputs": {
            "temperature_2m": t,
            "wind_speed_10m": wind,
            "wind_gusts_10m": gusts,
            "precipitation_mm": precip,
            "relative_humidity": hum,
            "is_day": is_day,
        },
        "output": {
            "condition": condition,
            "severity": severity,
            "tags": tags,
        },
        "created_at_utc": datetime.utcnow().isoformat(timespec="seconds"),
    }

    safe_city = city.strip().replace(" ", "_")
    ts = observed_time.strftime("%Y%m%dT%H%M%S")
    forecast_path = os.path.join(DATA_DIR, f"{safe_city}__{ts}__forecast.json")

    with open(forecast_path, "w", encoding="utf-8") as f:
        json.dump(inference_payload, f, ensure_ascii=False)

    meta["forecast_file"] = forecast_path
    meta["rule_version"] = "if_v1"
    meta["forecast_at_utc"] = datetime.utcnow().isoformat(timespec="seconds")

    with open(LATEST_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    logging.info("Inference file saved: %s", forecast_path)


def persist_inference(**context):
    if not os.path.exists(LATEST_META_PATH):
        raise AirflowSkipException(f"Pointer file not found: {LATEST_META_PATH}")

    with open(LATEST_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    forecast_path = meta.get("forecast_file")
    if not forecast_path or not os.path.exists(forecast_path):
        raise AirflowSkipException(f"Forecast file not found: {forecast_path}")

    with open(forecast_path, "r", encoding="utf-8") as f:
        forecast = json.load(f)

    city = forecast.get("city")
    observed_time_raw = forecast.get("observed_time")
    rule_version = forecast.get("rule_version", "if_v1")
    output = forecast.get("output") or {}

    if not city or not observed_time_raw:
        raise AirflowSkipException("Forecast JSON missing city/observed_time")

    try:
        observed_time = datetime.fromisoformat(observed_time_raw)
    except ValueError:
        raise AirflowSkipException(f"Invalid observed_time: {observed_time_raw}")

    condition = output.get("condition")
    severity = output.get("severity")
    tags = output.get("tags", [])

    if condition is None or severity is None:
        raise AirflowSkipException("Forecast JSON missing output.condition/output.severity")

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    hook.run(
        """
        INSERT INTO weather_inference (city,
                                       observed_time,
                                       rule_version,
                                       condition,
                                       severity,
                                       tags,
                                       payload)
        VALUES (%(city)s,
                %(observed_time)s,
                %(rule_version)s,
                %(condition)s,
                %(severity)s,
                %(tags)s::jsonb,
                %(payload)s::jsonb) ON CONFLICT (city, observed_time, rule_version) DO NOTHING;
        """,
        parameters={
            "city": city,
            "observed_time": observed_time,
            "rule_version": rule_version,
            "condition": condition,
            "severity": int(severity),
            "tags": json.dumps(tags, ensure_ascii=False),
            "payload": json.dumps(forecast, ensure_ascii=False),
        },
    )

    logging.info("Inference persisted for city=%s observed_time=%s", city, observed_time_raw)


def assess_inference(**context):
    if not os.path.exists(LATEST_META_PATH):
        raise AirflowSkipException(f"Pointer file not found: {LATEST_META_PATH}")

    with open(LATEST_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    city = meta.get("city")
    observed_time_raw = meta.get("observed_time")
    rule_version = meta.get("rule_version", "if_v1")

    if not city or not observed_time_raw:
        raise AirflowSkipException("Meta missing city/observed_time")

    try:
        observed_time = datetime.fromisoformat(observed_time_raw)
    except ValueError:
        raise AirflowSkipException(f"Invalid observed_time: {observed_time_raw}")

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    row = hook.get_first(
        """
        SELECT condition, severity, tags
        FROM weather_inference
        WHERE city = %(city)s
          AND observed_time = %(observed_time)s
          AND rule_version = %(rule_version)s LIMIT 1;
        """,
        parameters={
            "city": city,
            "observed_time": observed_time,
            "rule_version": rule_version,
        },
    )

    if row is None:
        raise AirflowSkipException("No inference row found to evaluate")

    condition, severity, tags_jsonb = row

    ok = condition in {"normal", "cold", "very_cold", "hot", "windy", "precipitation"} and int(severity) in {0, 1, 2}

    hook.run(
        """
        INSERT INTO weather_inference_metrics (city,
                                               observed_time,
                                               rule_version,
                                               calculated_at,
                                               ok,
                                               condition,
                                               severity,
                                               tags)
        VALUES (%(city)s,
                %(observed_time)s,
                %(rule_version)s,
                %(calculated_at)s,
                %(ok)s,
                %(condition)s,
                %(severity)s,
                %(tags)s::jsonb) ON CONFLICT (city, observed_time, rule_version) DO NOTHING;
        """,
        parameters={
            "city": city,
            "observed_time": observed_time,
            "rule_version": rule_version,
            "calculated_at": datetime.utcnow(),
            "ok": bool(ok),
            "condition": condition,
            "severity": int(severity),
            "tags": json.dumps(tags_jsonb if isinstance(tags_jsonb, list) else [], ensure_ascii=False),
        },
    )

    logging.info("Inference assessed for city=%s observed_time=%s, condition=%s ok=%s", city, observed_time_raw,
                 condition, ok)


with DAG(
        dag_id="weather_inference_dag",
        schedule=None,
        start_date=datetime(2026, 1, 7),
        catchup=False,
        max_active_runs=1,
) as dag:
    run_inference_task = PythonOperator(
        task_id="run_inference",
        python_callable=run_inference,
    )

    persist_inference_task = PythonOperator(
        task_id="persist_inference",
        python_callable=persist_inference,
    )

    assess_inference_task = PythonOperator(
        task_id="assess_inference",
        python_callable=assess_inference,
    )

    run_inference_task >> persist_inference_task >> assess_inference_task
