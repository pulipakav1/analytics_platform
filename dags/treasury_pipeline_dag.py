"""Airflow DAG — daily treasury cashflow pipeline with SLA enforcement."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "sla": timedelta(hours=2),
}


def _ingest_and_validate(**context: dict) -> dict:
    import sys
    sys.path.insert(0, "/opt/airflow/treasury-analytics-platform")
    from app.core.config import get_config
    from app.data.loader import load_raw_data
    from app.data.schema import RAW_SCHEMA
    from app.data.validator import clean_and_validate

    config = get_config()
    raw = load_raw_data(config)
    RAW_SCHEMA.validate(raw)
    validated = clean_and_validate(raw)
    context["ti"].xcom_push(key="raw_count", value=len(raw))
    context["ti"].xcom_push(key="validated_count", value=len(validated))
    return {"raw_count": len(raw), "validated_count": len(validated)}


def _transform_features(**context: dict) -> dict:
    import sys
    sys.path.insert(0, "/opt/airflow/treasury-analytics-platform")
    import pandas as pd

    from app.core.config import get_config
    from app.data.schema import CURATED_SCHEMA
    from app.services.pipeline_service import run_pipeline

    result = run_pipeline()
    config = get_config()
    curated = pd.read_csv(config.data.curated_path, parse_dates=["date"])
    CURATED_SCHEMA.validate(curated)
    context["ti"].xcom_push(key="curated_count", value=result["curated_records"])
    return result


def _train_and_forecast(**context: dict) -> dict:
    import sys
    sys.path.insert(0, "/opt/airflow/treasury-analytics-platform")
    from app.models.arima_forecast import ArimaForecaster
    from app.services.pipeline_service import load_curated

    curated = load_curated()
    series = curated.set_index("date")["net_cash_flow"].dropna()
    split = int(len(series) * 0.8)

    forecaster = ArimaForecaster(order=(2, 1, 2))
    metrics = forecaster.evaluate(series.iloc[:split], series.iloc[split:])
    forecaster.forecast_future(series, horizon=14)
    forecaster.save("data/models/arima_net_flow.joblib")
    return {"metrics": metrics, "horizon_days": 14}


with DAG(
    dag_id="treasury_analytics_pipeline",
    description="Daily treasury cashflow ingestion, schema validation, feature engineering, and ARIMA forecasting",
    default_args=default_args,
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["treasury", "finance", "forecasting", "mlflow"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_and_validate",
        python_callable=_ingest_and_validate,
        provide_context=True,
    )

    transform_task = PythonOperator(
        task_id="transform_features",
        python_callable=_transform_features,
        provide_context=True,
    )

    forecast_task = PythonOperator(
        task_id="train_and_forecast",
        python_callable=_train_and_forecast,
        provide_context=True,
    )

    ingest_task >> transform_task >> forecast_task
