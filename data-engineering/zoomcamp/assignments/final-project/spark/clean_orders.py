"""
Spark job: read raw orders parquet from GCS,
standardize columns, filter to completed orders,
write cleaned parquet back to GCS.
"""

import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, DecimalType

BUCKET = "zmcp-final-reconciliation-datalake"
INPUT_PATH = f"gs://{BUCKET}/raw/orders/"
OUTPUT_PATH = f"gs://{BUCKET}/cleaned/orders/"

GCS_CONNECTOR_JAR = "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar"


def main():
    builder = (
        SparkSession.builder
        .appName("clean_orders")
        .master("local[*]")
        .config("spark.jars", GCS_CONNECTOR_JAR)
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    )

    keyfile = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if keyfile:
        builder = builder.config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", keyfile)

    spark = builder.getOrCreate()

    df = spark.read.parquet(INPUT_PATH)

    cleaned = (
        df
        .filter(F.col("status") == "completed")
        .select(
            F.col("order_id"),
            F.col("transaction_id"),
            F.col("order_date").cast(DateType()),
            F.col("customer_id"),
            F.col("total_amount").cast(DecimalType(10, 2)),
            F.col("item_count").cast("int"),
            F.col("created_at"),
        )
        .filter(F.col("transaction_id").isNotNull())
        .dropDuplicates(["transaction_id"])
    )

    cleaned.write.mode("overwrite").parquet(OUTPUT_PATH)

    print(f"Wrote {cleaned.count()} cleaned orders to {OUTPUT_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()
