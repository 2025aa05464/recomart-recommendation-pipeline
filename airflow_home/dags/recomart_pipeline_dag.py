from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

PROJECT_DIR = "/workspaces/recomart-recommendation-pipeline"

default_args = {
    "owner": "recomart_data_team",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="recomart_recommendation_pipeline",
    default_args=default_args,
    description="End-to-end data pipeline for RecoMart recommendation system",
    schedule=None,
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["recomart", "recommendation-system", "assignment"],
) as dag:

    ingest_task = BashOperator(
        task_id="ingest_data",
        bash_command=f"cd {PROJECT_DIR} && source venv/bin/activate && python scripts/ingest_data.py",
    )

    validate_task = BashOperator(
        task_id="validate_data",
        bash_command=f"cd {PROJECT_DIR} && source venv/bin/activate && python scripts/validate_data.py",
    )

    feature_store_task = BashOperator(
        task_id="feature_store_demo",
        bash_command=f"cd {PROJECT_DIR} && source venv/bin/activate && python scripts/feature_store_demo.py",
    )

    train_task = BashOperator(
        task_id="train_model",
        bash_command=f"cd {PROJECT_DIR} && source venv/bin/activate && python scripts/train_model.py",
    )

    ingest_task >> validate_task >> feature_store_task >> train_task