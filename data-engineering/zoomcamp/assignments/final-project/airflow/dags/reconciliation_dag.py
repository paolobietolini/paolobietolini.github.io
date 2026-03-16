"""
Reconciliation pipeline DAG.

generate_orders  ──► upload_to_gcs ──┐
                                     ├──► spark_clean_orders   ──┐
extract_ga4_to_gcs ──────────────────┘                           │
                                     spark_clean_ga4 ────────────┤
                                                                 ├──► create_external_tables ──► dbt_run ──► dbt_test
"""

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

GCS_BUCKET = os.environ.get("GCS_BUCKET", "zmcp-final-reconciliation-datalake")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "zmcp-final")
BQ_DATASET = os.environ.get("BQ_DATASET", "reconciliation")
CREDS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/opt/gcp/key.json")

CREATE_EXT_TABLES_SQL = f"""
CREATE OR REPLACE EXTERNAL TABLE `{GCP_PROJECT}.{BQ_DATASET}.ext_orders`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://{GCS_BUCKET}/cleaned/orders/*.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `{GCP_PROJECT}.{BQ_DATASET}.ext_ga4_purchases`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://{GCS_BUCKET}/cleaned/ga4_purchases/*.parquet']
);
"""

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="reconciliation_dag",
    default_args=default_args,
    description="E-commerce order reconciliation pipeline",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["reconciliation"],
) as dag:

    generate_orders = BashOperator(
        task_id="generate_orders",
        bash_command="cd /opt/airflow/data-generator && python generate_orders.py",
    )

    upload_to_gcs = BashOperator(
        task_id="upload_to_gcs",
        bash_command="cd /opt/airflow/data-generator && python upload_to_gcs.py",
    )

    extract_ga4_to_gcs = BashOperator(
        task_id="extract_ga4_to_gcs",
        bash_command=(
            "cd /opt/airflow/data-generator && "
            "python -c \""
            "from google.cloud import bigquery, storage; "
            "import pandas as pd; "
            "bq = bigquery.Client(); "
            "df = bq.query("
            "    'SELECT event_date, event_timestamp, user_pseudo_id, "
            "     ecommerce.transaction_id, ecommerce.purchase_revenue, "
            "     (SELECT COUNT(*) FROM UNNEST(items)) AS item_count "
            "     FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` "
            "     WHERE event_name = \\\"purchase\\\" "
            "     AND ecommerce.transaction_id IS NOT NULL'"
            ").to_dataframe(); "
            "df.to_parquet('/tmp/ga4_purchases.parquet', index=False); "
            "gcs = storage.Client(); "
            f"bucket = gcs.bucket('{GCS_BUCKET}'); "
            "blob = bucket.blob('raw/ga4_purchases/ga4_purchases.parquet'); "
            "blob.upload_from_filename('/tmp/ga4_purchases.parquet'); "
            "print(f'Uploaded {{len(df)}} GA4 purchases to GCS')"
            "\""
        ),
    )

    spark_clean_orders = BashOperator(
        task_id="spark_clean_orders",
        bash_command=(
            "spark-submit "
            "--master local[*] "
            "--jars https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar "
            f"--conf spark.hadoop.google.cloud.auth.service.account.json.keyfile={CREDS} "
            "/opt/airflow/spark/clean_orders.py"
        ),
    )

    spark_clean_ga4 = BashOperator(
        task_id="spark_clean_ga4",
        bash_command=(
            "spark-submit "
            "--master local[*] "
            "--jars https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar "
            f"--conf spark.hadoop.google.cloud.auth.service.account.json.keyfile={CREDS} "
            "/opt/airflow/spark/extract_ga4_purchases.py"
        ),
    )

    create_external_tables = BashOperator(
        task_id="create_external_tables",
        bash_command=(
            f"bq query --use_legacy_sql=false --project_id={GCP_PROJECT} "
            f"'{CREATE_EXT_TABLES_SQL}'"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
    )

    # Task dependencies
    generate_orders >> upload_to_gcs
    [upload_to_gcs, extract_ga4_to_gcs] >> spark_clean_orders
    [upload_to_gcs, extract_ga4_to_gcs] >> spark_clean_ga4
    [spark_clean_orders, spark_clean_ga4] >> create_external_tables
    create_external_tables >> dbt_run >> dbt_test
