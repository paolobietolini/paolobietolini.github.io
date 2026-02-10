import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, bigquery
from google.api_core.exceptions import NotFound, Forbidden
import pyarrow.parquet as pq
import pyarrow as pa
import time


BUCKET_NAME = "de_hw4_2026"
CREDENTIALS_FILE = "secrets/keys.json"
storage_client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bq_client = bigquery.Client.from_service_account_json(CREDENTIALS_FILE)

BQ_DATASET = "elt-demo-de.nytaxi"

DATA_TYPES = ["green", "yellow"]
YEARS = ["2019", "2020"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = storage_client.bucket(BUCKET_NAME)


# Explicit schema for green_tripdata.
# ehail_fee has inconsistent types across parquet files (double in some, null in others).
# We normalize the parquet files before upload, then declare everything as FLOAT64.
GREEN_SCHEMA = [
    bigquery.SchemaField("VendorID", "INT64"),
    bigquery.SchemaField("lpep_pickup_datetime", "TIMESTAMP"),
    bigquery.SchemaField("lpep_dropoff_datetime", "TIMESTAMP"),
    bigquery.SchemaField("store_and_fwd_flag", "STRING"),
    bigquery.SchemaField("RatecodeID", "FLOAT64"),
    bigquery.SchemaField("PULocationID", "INT64"),
    bigquery.SchemaField("DOLocationID", "INT64"),
    bigquery.SchemaField("passenger_count", "FLOAT64"),
    bigquery.SchemaField("trip_distance", "FLOAT64"),
    bigquery.SchemaField("fare_amount", "FLOAT64"),
    bigquery.SchemaField("extra", "FLOAT64"),
    bigquery.SchemaField("mta_tax", "FLOAT64"),
    bigquery.SchemaField("tip_amount", "FLOAT64"),
    bigquery.SchemaField("tolls_amount", "FLOAT64"),
    bigquery.SchemaField("ehail_fee", "FLOAT64"),
    bigquery.SchemaField("improvement_surcharge", "FLOAT64"),
    bigquery.SchemaField("total_amount", "FLOAT64"),
    bigquery.SchemaField("payment_type", "FLOAT64"),
    bigquery.SchemaField("trip_type", "FLOAT64"),
    bigquery.SchemaField("congestion_surcharge", "FLOAT64"),
]


def create_bucket(bucket_name):
    try:
        storage_client.get_bucket(bucket_name)
        project_bucket_ids = [bckt.id for bckt in storage_client.list_buckets()]
        if bucket_name in project_bucket_ids:
            print(
                f"Bucket '{bucket_name}' exists and belongs to your project. Proceeding..."
            )
        else:
            print(f"Bucket '{bucket_name}' exists but does not belong to your project.")
            sys.exit(1)
    except NotFound:
        storage_client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    except Forbidden:
        print(
            f"Bucket '{bucket_name}' exists but is not accessible. Try a different name."
        )
        sys.exit(1)


def file_exists_in_gcs(filename):
    return storage.Blob(bucket=bucket, name=filename).exists(storage_client)


def normalize_parquet_schema(file_path):
    """Fix type inconsistencies in parquet files before uploading to GCS.
    Specifically casts ehail_fee to float64 (double) to ensure all green files
    have a consistent schema for BigQuery external tables."""
    try:
        table = pq.read_table(file_path)
        if "ehail_fee" in table.schema.names:
            col_type = table.schema.field("ehail_fee").type
            if col_type != pa.float64():
                print(f"  Fixing ehail_fee type in {file_path}: {col_type} -> float64")
                idx = table.schema.get_field_index("ehail_fee")
                table = table.set_column(
                    idx,
                    pa.field("ehail_fee", pa.float64()),
                    table.column("ehail_fee").cast(pa.float64()),
                )
                pq.write_table(table, file_path)
        else:
            # If ehail_fee column is missing entirely, add it as null float64
            print(f"  Adding missing ehail_fee column to {file_path}")
            null_col = pa.nulls(len(table), type=pa.float64())
            table = table.append_column(pa.field("ehail_fee", pa.float64()), null_col)
            pq.write_table(table, file_path)
    except Exception as e:
        print(f"Failed to normalize schema for {file_path}: {e}")


def download_file(data_type, year, month):
    filename = f"{data_type}_tripdata_{year}-{month}.parquet"
    url = f"{BASE_URL}/{filename}"
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def upload_to_gcs(file_path, max_retries=3):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if storage.Blob(bucket=bucket, name=blob_name).exists(storage_client):
                print(f"Verification successful for {blob_name}")
                return True
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")
        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")
    return False


def process_file(data_type, year, month):
    """Download, normalize schema if needed, upload to GCS."""
    filename = f"{data_type}_tripdata_{year}-{month}.parquet"

    if file_exists_in_gcs(filename):
        print(f"Skipping upload for {filename}, already in GCS.")
        return filename

    file_path = download_file(data_type, year, month)
    if file_path:
        if data_type == "green":
            normalize_parquet_schema(file_path)
        if upload_to_gcs(file_path):
            return filename
    return None


def create_external_table(data_type):
    """Create one external table per data type, pointing at all parquet files in GCS."""
    table_id = f"{BQ_DATASET}.{data_type}_tripdata"
    uris = [
        f"gs://{BUCKET_NAME}/{data_type}_tripdata_{year}-*.parquet" for year in YEARS
    ]

    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = uris

    if data_type == "green":
        external_config.autodetect = False
        external_config.schema = GREEN_SCHEMA
        print(f"Using explicit schema for {table_id}")
    else:
        external_config.autodetect = True

    table = bigquery.Table(table_id)
    table.external_data_configuration = external_config

    try:
        bq_client.delete_table(table_id, not_found_ok=True)
        bq_client.create_table(table)
        print(f"Created external table: {table_id}")
    except Exception as e:
        print(f"Failed to create external table {table_id}: {e}")


def cleanup_local_files():
    """Remove all downloaded parquet files."""
    count = 0
    for data_type in DATA_TYPES:
        for year in YEARS:
            for month in MONTHS:
                filename = f"{data_type}_tripdata_{year}-{month}.parquet"
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    count += 1
    print(f"Cleaned up {count} local parquet files.")


if __name__ == "__main__":
    create_bucket(BUCKET_NAME)

    tasks = [
        (data_type, year, month)
        for data_type in DATA_TYPES
        for year in YEARS
        for month in MONTHS
    ]

    # Download, normalize, and upload to GCS
    with ThreadPoolExecutor(max_workers=4) as executor:
        gcs_filenames = list(executor.map(lambda args: process_file(*args), tasks))

    valid_filenames = [f for f in gcs_filenames if f is not None]
    print(f"\nAll files uploaded. {len(valid_filenames)}/{len(tasks)} succeeded.")

    # Create external tables (one per data type)
    print("\n--- Creating external tables in BigQuery ---")
    for data_type in DATA_TYPES:
        create_external_table(data_type)

    print("Done. External tables created.")

    # Cleanup
    cleanup_local_files()
