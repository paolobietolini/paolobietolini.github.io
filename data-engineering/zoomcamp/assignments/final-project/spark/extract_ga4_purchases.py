"""
Spark job: read raw GA4 purchases parquet from GCS,
standardize columns, write cleaned parquet back to GCS.
"""

import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, DecimalType

BUCKET = "zmcp-final-reconciliation-datalake"
INPUT_PATH = f"gs://{BUCKET}/raw/ga4_purchases/"
OUTPUT_PATH = f"gs://{BUCKET}/cleaned/ga4_purchases/"

GCS_CONNECTOR_JAR = "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar"


def main():
    builder = (
        SparkSession.builder
        .appName("clean_ga4_purchases")
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
        .select(
            F.col("transaction_id"),
            F.to_date(F.col("event_date"), "yyyyMMdd").cast(DateType()).alias("event_date"),
            F.col("event_timestamp"),
            F.col("purchase_revenue").cast(DecimalType(10, 2)).alias("revenue"),
            F.col("user_pseudo_id").alias("user_id"),
            F.col("item_count").cast("int"),
        )
        .filter(F.col("transaction_id").isNotNull())
        .dropDuplicates(["transaction_id"])
    )

    cleaned.write.mode("overwrite").parquet(OUTPUT_PATH)

    print(f"Wrote {cleaned.count()} cleaned GA4 purchases to {OUTPUT_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()
