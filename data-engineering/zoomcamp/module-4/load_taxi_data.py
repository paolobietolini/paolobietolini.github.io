import os
import gzip
import sys
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, bigquery
from google.api_core.exceptions import NotFound, Forbidden
import time
import polars as pl

BUCKET_NAME = "de_hw4_2026"
CREDENTIALS_FILE = "secrets/keys.json"
storage_client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bq_client = bigquery.Client.from_service_account_json(CREDENTIALS_FILE)

BQ_DATASET = "elt-demo-de.nytaxi"

DATA_TYPES = ["green", "yellow"]
YEARS = ["2019", "2020"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download" #/yellow/yellow_tripdata_2019-01.csv.gz
DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = storage_client.bucket(BUCKET_NAME)


def create_bucket(bucket_name):
    try:
        storage_client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' exists. Proceeding...")
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




def download_file(data_type, year, month):
    gz_filename = f"{data_type}_tripdata_{year}-{month}.csv.gz"
    url = f"{BASE_URL}/{data_type}/{gz_filename}"
    file_path = os.path.join(DOWNLOAD_DIR, gz_filename)
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
def convert_gz_to_parquet(gz_path):
    """Decompress .csv.gz and convert to .parquet, return the parquet path."""
    # e.g. green_tripdata_2019-01.csv.gz -> green_tripdata_2019-01
    base = gz_path.removesuffix(".csv.gz")
    csv_path = base + ".csv"
    parquet_path = base + ".parquet"

    print(f"Decompressing {gz_path}...")
    with gzip.open(gz_path, 'rb') as f_in:
        with open(csv_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Converting {csv_path} to parquet...")
    pl.read_csv(csv_path, infer_schema_length=None).write_parquet(parquet_path)
    print(f"Created {parquet_path}")

    os.remove(gz_path)
    os.remove(csv_path)
    return parquet_path


def process_file(data_type, year, month):
    """Download csv.gz, convert to parquet, upload to GCS."""
    parquet_filename = f"{data_type}_tripdata_{year}-{month}.parquet"

    if file_exists_in_gcs(parquet_filename):
        print(f"Skipping {parquet_filename}, already in GCS.")
        return parquet_filename

    gz_path = download_file(data_type, year, month)
    if gz_path:
        parquet_path = convert_gz_to_parquet(gz_path)
        if upload_to_gcs(parquet_path):
            os.remove(parquet_path)
            return parquet_filename
    return None


def create_external_table(data_type):
    """Create one external table per data type, pointing at all parquet files in GCS."""
    table_id = f"{BQ_DATASET}.{data_type}_tripdata"
    uris = [
        f"gs://{BUCKET_NAME}/{data_type}_tripdata_{year}-*.parquet" for year in YEARS
    ]

    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = uris
    external_config.autodetect = True

    table = bigquery.Table(table_id)
    table.external_data_configuration = external_config

    try:
        bq_client.delete_table(table_id, not_found_ok=True)
        bq_client.create_table(table)
        print(f"Created external table: {table_id}")
    except Exception as e:
        print(f"Failed to create external table {table_id}: {e}")



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
