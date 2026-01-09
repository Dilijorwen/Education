import json
from datetime import datetime, timedelta

import requests

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


DAG_ID = "weather_etl"
INFERENCE_DAG_ID = "weather_inference"

URL = "https://archive-api.open-meteo.com/v1/archive"

DEFAULT_PARAMS = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2025-12-23",
    "end_date": "2026-01-06",
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "snowfall",
        "snow_depth",
        "weather_code",
        "cloud_cover",
        "wind_speed_100m",
        "wind_direction_100m",
        "wind_gusts_10m",
        "soil_temperature_100_to_255cm",
        "soil_moisture_100_to_255cm",
    ],
}


def _get_params() -> dict:
    """
    Опционально позволяет переопределять параметры через Airflow Variable:
    key = open_meteo_params, value = JSON.
    """
    raw = Variable.get("open_meteo_params", default_var="")
    if not raw:
        return dict(DEFAULT_PARAMS)

    try:
        user_params = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError("Variable 'open_meteo_params' must be valid JSON") from e

    merged = dict(DEFAULT_PARAMS)
    merged.update(user_params)
    return merged


def should_run_etl(**context) -> str:
    """
    BO_1: есть ли новые данные?
    Локальная логика без сети: сравниваем end_date с последним загруженным.
    """
    params = _get_params()
    end_date = params["end_date"]

    last_end = Variable.get("meteo_archive_last_end_date", default_var="")
    if last_end == end_date:
        return "finish"

    return "extract"


def extract(**context) -> dict:
    """
    Extract: получить данные из Open-Meteo (requests).
    """
    params = _get_params()

    resp = requests.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    hourly = data.get("hourly")
    if not isinstance(hourly, dict):
        raise RuntimeError("Open-Meteo response does not contain valid 'hourly' object")

    times = hourly.get("time")
    if not isinstance(times, list) or len(times) == 0:
        raise RuntimeError("Open-Meteo returned empty hourly.time")

    return {
        "_request_params": params,
        "hourly": hourly,
    }


def data_is_valid(**context) -> str:
    """
    BO_2: данные есть и подходят для transform?
    """
    ti = context["ti"]
    payload = ti.xcom_pull(task_ids="extract")

    if not isinstance(payload, dict):
        return "finish"

    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        return "finish"

    times = hourly.get("time")
    if not isinstance(times, list) or len(times) == 0:
        return "finish"

    requested = payload.get("_request_params", {}).get("hourly", [])
    if not isinstance(requested, list) or len(requested) == 0:
        return "finish"

    for field in requested:
        values = hourly.get(field)
        if not isinstance(values, list) or len(values) != len(times):
            return "finish"

    return "transform"


def transform(**context) -> list[dict]:
    """
    Transform: wide -> rows (список dict по часам).
    """
    ti = context["ti"]
    payload = ti.xcom_pull(task_ids="extract")

    hourly = payload["hourly"]
    times = hourly["time"]
    keys = [k for k in hourly.keys() if k != "time"]

    rows: list[dict] = []
    for i, t in enumerate(times):
        row = {"time": t}
        for k in keys:
            row[k] = hourly[k][i]
        rows.append(row)

    return rows


def load(**context) -> dict:
    """
    Load: фиксируем, что end_date загружен (для BO_1 в будущих запусках),
    и возвращаем метаданные (можно использовать в инференсе через conf или XCom).
    """
    params = _get_params()
    Variable.set("meteo_archive_last_end_date", params["end_date"])
    return {"status": "ok", "end_date": params["end_date"], "dag_id": DAG_ID}


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2025, 12, 23),
    schedule="0 2 * * *",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
    tags=["weather", "etl"],
) as dag:
    start = EmptyOperator(task_id="start")

    bo_1 = BranchPythonOperator(
        task_id="BO_1_should_run_etl",
        python_callable=should_run_etl,
    )

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    bo_2 = BranchPythonOperator(
        task_id="BO_2_data_is_valid",
        python_callable=data_is_valid,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )

    trigger_inference = TriggerDagRunOperator(
        task_id="trigger_inference",
        trigger_dag_id=INFERENCE_DAG_ID,
        wait_for_completion=False,
        conf={
            "source_dag": DAG_ID,
            "params_var": "open_meteo_params",
            "last_end_var": "meteo_archive_last_end_date",
        },
    )

    finish = EmptyOperator(task_id="finish")

    start >> bo_1

    bo_1 >> extract_task >> bo_2
    bo_1 >> finish

    bo_2 >> transform_task >> load_task >> trigger_inference >> finish
    bo_2 >> finish
