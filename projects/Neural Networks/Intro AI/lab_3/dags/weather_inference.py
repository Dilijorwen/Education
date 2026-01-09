import json
from datetime import datetime

import requests

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator


DAG_ID = "weather_inference"

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


def get_data(**context) -> dict:
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


def inference(**context) -> dict:
    """
    Заглушка инференса.
    Здесь подключаешь свою модель: загрузка артефакта, подготовка фичей, predict.
    """
    ti = context["ti"]
    payload = ti.xcom_pull(task_ids="get_data")

    hourly = payload["hourly"]
    times = hourly["time"]

    # Пример: прогноз = температура_2m (как заглушка)
    temps = hourly.get("temperature_2m", [])
    preds = []
    for i, t in enumerate(times):
        preds.append({"time": t, "prediction": temps[i] if i < len(temps) else None})

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "n": len(preds),
        "preds": preds,
    }


def save(**context) -> str:
    """
    Сохранение результатов. Для простоты пишем в Variable.
    Для реального проекта: Postgres/S3/файлы/витрина.
    """
    ti = context["ti"]
    result = ti.xcom_pull(task_ids="inference")
    Variable.set("weather_inference_last_result", json.dumps(result, ensure_ascii=False))
    return "ok"


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2025, 12, 23),
    schedule=None,
    catchup=False,
    tags=["weather", "inference"],
) as dag:
    start = EmptyOperator(task_id="start")

    get_data_task = PythonOperator(
        task_id="get_data",
        python_callable=get_data,
    )

    inference_task = PythonOperator(
        task_id="inference",
        python_callable=inference,
    )

    save_task = PythonOperator(
        task_id="save",
        python_callable=save,
    )

    finish = EmptyOperator(task_id="finish")

    start >> get_data_task >> inference_task >> save_task >> finish
