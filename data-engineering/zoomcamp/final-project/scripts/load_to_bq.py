import os
import pandas as pd
from sqlalchemy import create_engine
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, WriteDisposition

bq_client = bigquery.Client()

password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
db = os.environ["DB_NAME"]
port = os.environ.get("DB_PORT", "5432")
user = os.environ["DB_USER"]


engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
tables = ["users", "orders", "order_items"]
PROJECT_ID = "zmcp-final"
DATASET_ID = "raw_backend"
for t in tables:
    df = pd.read_sql(f"SELECT * FROM {t}", engine)
    job_config = LoadJobConfig(write_disposition=WriteDisposition.WRITE_TRUNCATE)
    bq_client.load_table_from_dataframe(
        df, f"{PROJECT_ID}.{DATASET_ID}.{t}", job_config=job_config
    )
