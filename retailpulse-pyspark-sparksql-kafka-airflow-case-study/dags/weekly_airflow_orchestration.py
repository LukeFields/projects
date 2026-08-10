from datetime import datetime

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.databricks.hooks.databricks import DatabricksHook
from airflow.providers.standard.operators.python import PythonOperator
from pathlib import Path

from kafka_app.producer import publish_events
from kafka_app.consumer import consume_events

DATABRICKS_CONN_ID = "databricks_default"
VOLUME_FILE_PATH = "/Volumes/workspace/retail_fresher/retail_raw/kafka_events.jsonl"
LOCAL_DOWNLOAD_PATH = "/opt/airflow/data/kafka_events.jsonl"

NOTEBOOK_PATHS = {
    "notebook_1": "/Workspace/pyspark_bronze",
    "notebook_2": "/Workspace/pyspark_silver",
    "notebook_3": "/Workspace/pyspark_gold",
    "notebook_4": "/Workspace/kafka_gold_events",
}

def download_volume_file(**context):
    import os
    import requests
 
    hook = DatabricksHook(databricks_conn_id=DATABRICKS_CONN_ID)
    host = hook.host
    token = hook._get_token(raise_error=True)
 
    url = f"https://{host}/api/2.0/fs/files{VOLUME_FILE_PATH}"
    headers = {"Authorization": f"Bearer {token}"}
 
    os.makedirs(os.path.dirname(LOCAL_DOWNLOAD_PATH), exist_ok=True)
 
    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()
        with open(LOCAL_DOWNLOAD_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
 
    print(f"Downloaded {VOLUME_FILE_PATH} to {LOCAL_DOWNLOAD_PATH}")

def publish_to_kafka() -> None:
    publish_events(
        input_file=LOCAL_DOWNLOAD_PATH,
        bootstrap_servers="kafka:19092",
        topic="retail-sales-summary",
    )

def consume_from_kafka() -> None:
    consume_events(
        bootstrap_servers="kafka:19092",
        topic="retail-sales-summary",
        group_id="retailpulse-summary-consumer",
        output_file="/opt/airflow/data/consumed_events.jsonl",
        max_messages=5,
        timeout_seconds=30,
    )

with DAG(
    dag_id="retailpulse_weekly",
    description="Run Databricks notebooks via Airflow on Free Edition serverless compute",
    schedule="0 9 * * 3", 
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_tasks=1,
    tags=["databricks", "serverless"],
) as dag:

    run_notebooks = DatabricksSubmitRunOperator(
        task_id="run_databricks_notebook",
        databricks_conn_id=DATABRICKS_CONN_ID,
        run_name="bronze",
        tasks=[
            {
                "task_key": "run_notebook_1_task",
                "notebook_task": {
                    "notebook_path": NOTEBOOK_PATHS["notebook_1"],
                    "source": "WORKSPACE",

                },
            },
            {
                "task_key": "run_notebook_2_task",
                "notebook_task": {
                    "notebook_path": NOTEBOOK_PATHS["notebook_2"],
                    "source": "WORKSPACE", 

                },
            },
            {
                "task_key": "run_notebook_3_task",
                "notebook_task": {
                    "notebook_path": NOTEBOOK_PATHS["notebook_3"],
                    "source": "WORKSPACE",

                },
            },
            {
                "task_key": "run_notebook_4_task",
                "notebook_task": {
                    "notebook_path": NOTEBOOK_PATHS["notebook_4"],
                    "source": "WORKSPACE",

                },
            }
        ],
    )

    download_file = PythonOperator(
        task_id="download_kafka_events_jsonl",
        python_callable=download_volume_file,
    )

    publish_events_task = PythonOperator(
        task_id="publish_events_to_kafka",
        python_callable=publish_to_kafka,
    )

    consume_events_task = PythonOperator(
        task_id="consume_events_from_kafka",
        python_callable=consume_from_kafka,
    )

    run_notebooks >> download_file >> publish_events_task >> consume_events_task