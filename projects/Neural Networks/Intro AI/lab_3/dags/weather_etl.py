import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from geopy.geocoders import Nominatim
from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.sdk import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

POSTGRES_CONN_ID = "weather_postgres"
TABLE_NAME = "weather_current"

DATA_DIR = "/opt/airflow/data/weather"
LATEST_META_PATH = os.path.join(DATA_DIR, "latest_meta.json")


def _atomic_write_json(path: str, obj: dict) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp_path, path)


def extract_weather_data(**context):
    api_url = Variable.get("api_url")
    city = "Vladivostok"

    g = Nominatim(user_agent="pp")
    location = g.geocode("Vladivostok")

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "is_day", "precipitation", "wind_speed_10m",
                    "wind_direction_10m", "wind_gusts_10m"],
        "timezone": "Asia/Vladivostok",
    }

    logging.info("Request URL: %s", api_url)
    logging.info("Request params: %s", params)
    logging.info("City (external): %s", city)

    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise AirflowSkipException(f"Request failed: {e}")

    payload = response.json()

    try:
        observed_time_raw = payload["current"]["time"]
    except Exception:
        raise AirflowSkipException("Payload missing required field: current.time")

    try:
        observed_time = datetime.fromisoformat(observed_time_raw)
    except ValueError:
        raise AirflowSkipException(f"Invalid observed_time format: {observed_time_raw}")

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    exists_sql = f"""
        SELECT 1
        FROM {TABLE_NAME}
        WHERE city = %(city)s
          AND observed_time = %(observed_time)s
        LIMIT 1;
    """
    rec = hook.get_first(
        exists_sql,
        parameters={"city": city, "observed_time": observed_time},
    )
    if rec:
        raise AirflowSkipException(
            f"Duplicate detected for city={city}, observed_time={observed_time_raw}"
        )

    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    safe_city = city.strip().replace(" ", "_")
    ts = observed_time.strftime("%Y%m%dT%H%M%S")

    raw_path = os.path.join(DATA_DIR, f"{safe_city}__{ts}__raw.json")
    meta_path = os.path.join(DATA_DIR, f"{safe_city}__{ts}__meta.json")

    _atomic_write_json(raw_path, payload)

    meta = {
        "city": city,
        "observed_time": observed_time_raw,
        "request_params": params,
        "raw_file": raw_path,
        "meta_file": meta_path,
        "created_at_utc": datetime.utcnow().isoformat(timespec="seconds"),
    }
    _atomic_write_json(meta_path, meta)

    _atomic_write_json(LATEST_META_PATH, meta)

    logging.info("Saved raw payload: %s", raw_path)
    logging.info("Saved meta: %s", meta_path)
    logging.info("Updated pointer: %s", LATEST_META_PATH)

def transform_weather_data(**context):
    if not os.path.exists(LATEST_META_PATH):
        raise AirflowSkipException(f"Pointer file not found: {LATEST_META_PATH}")

    with open(LATEST_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    raw_path = meta.get("raw_file")
    if not raw_path or not os.path.exists(raw_path):
        raise AirflowSkipException(f"Raw file not found: {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    def req(obj: dict, path: str):
        cur = obj
        for key in path.split("."):
            if not isinstance(cur, dict) or key not in cur:
                raise AirflowSkipException(f"Missing required field: {path}")
            cur = cur[key]
        return cur

    observed_time_raw = meta.get("observed_time")
    city = meta.get("city")
    if not observed_time_raw or not city:
        raise AirflowSkipException("Meta missing required fields: city/observed_time")

    try:
        observed_time = datetime.fromisoformat(observed_time_raw)
    except ValueError:
        raise AirflowSkipException(f"Invalid observed_time in meta: {observed_time_raw}")

    transformed = {
        "observed_time": observed_time_raw,  # строкой
        "city": city,
        "timezone": req(payload, "timezone"),
        "utc_offset_seconds": int(req(payload, "utc_offset_seconds")),
        "elevation": float(req(payload, "elevation")),
        "temperature_2m": float(req(payload, "current.temperature_2m")),
        "relative_humidity": int(req(payload, "current.relative_humidity_2m")),
        "is_day": int(req(payload, "current.is_day")),
        "precipitation_mm": float(req(payload, "current.precipitation")),
        "wind_speed_10m": float(req(payload, "current.wind_speed_10m")),
        "wind_direction_deg": int(req(payload, "current.wind_direction_10m")),
        "wind_gusts_10m": float(req(payload, "current.wind_gusts_10m")),
        "payload": payload,
    }

    safe_city = city.strip().replace(" ", "_")
    ts = observed_time.strftime("%Y%m%dT%H%M%S")
    transformed_path = os.path.join(DATA_DIR, f"{safe_city}__{ts}__transformed.json")

    _atomic_write_json(transformed_path, transformed)

    meta["transformed_file"] = transformed_path
    meta["transformed_at_utc"] = datetime.utcnow().isoformat(timespec="seconds")
    _atomic_write_json(LATEST_META_PATH, meta)

    logging.info("Saved transformed payload: %s", transformed_path)
    logging.info("Updated pointer: %s", LATEST_META_PATH)


def load_weather_data(**context):
    if not os.path.exists(LATEST_META_PATH):
        raise AirflowSkipException(f"Pointer file not found: {LATEST_META_PATH}")

    with open(LATEST_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    transformed_path = meta.get("transformed_file")
    if not transformed_path or not os.path.exists(transformed_path):
        raise AirflowSkipException(f"Transformed file not found: {transformed_path}")

    with open(transformed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        observed_time = datetime.fromisoformat(data["observed_time"])
    except Exception:
        raise AirflowSkipException(f"Invalid observed_time: {data.get('observed_time')}")

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    insert_sql = f"""
        INSERT INTO {TABLE_NAME} (
          observed_time,
          city, timezone, utc_offset_seconds, elevation,
          temperature_2m, relative_humidity, is_day, precipitation_mm,
          wind_speed_10m, wind_direction_deg, wind_gusts_10m,
          payload
        ) VALUES (
          %(observed_time)s,
          %(city)s, %(timezone)s, %(utc_offset_seconds)s, %(elevation)s,
          %(temperature_2m)s, %(relative_humidity)s, %(is_day)s, %(precipitation_mm)s,
          %(wind_speed_10m)s, %(wind_direction_deg)s, %(wind_gusts_10m)s,
          %(payload)s::jsonb
        )
        ON CONFLICT (city, observed_time) DO NOTHING;
    """

    params = {
        "observed_time": observed_time,
        "city": data["city"],
        "timezone": data["timezone"],
        "utc_offset_seconds": data["utc_offset_seconds"],
        "elevation": data["elevation"],
        "temperature_2m": data["temperature_2m"],
        "relative_humidity": data["relative_humidity"],
        "is_day": data["is_day"],
        "precipitation_mm": data["precipitation_mm"],
        "wind_speed_10m": data["wind_speed_10m"],
        "wind_direction_deg": data["wind_direction_deg"],
        "wind_gusts_10m": data["wind_gusts_10m"],
        "payload": json.dumps(data["payload"], ensure_ascii=False),
    }

    hook.run(insert_sql, parameters=params)

    meta["loaded_at_utc"] = datetime.utcnow().isoformat(timespec="seconds")
    _atomic_write_json(LATEST_META_PATH, meta)

    logging.info("Data loaded (or skipped by ON CONFLICT). File: %s", transformed_path)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="weather_dag",
    default_args=default_args,
    schedule="*/10 * * * *",
    start_date=datetime(2025, 12, 30),
    max_active_runs=1,
    catchup=False,
) as dag:
    extract_weather = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather_data,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )

    transform_weather = PythonOperator(
        task_id="transform_weather",
        python_callable=transform_weather_data,
    )

    load_weather = PythonOperator(
        task_id="load_weather",
        python_callable=load_weather_data,
    )
    trigger_inference = TriggerDagRunOperator(
        task_id="trigger_inference",
        trigger_dag_id="weather_inference_dag",
        wait_for_completion=False,
    )


    extract_weather >> transform_weather >> load_weather >> trigger_inference
