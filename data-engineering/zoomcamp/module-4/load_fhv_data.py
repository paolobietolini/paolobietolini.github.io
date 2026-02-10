import os
import sys
import gzip
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, bigquery
from google.api_core.exceptions import NotFound, Forbidden
import time

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/"
BASE_FILENAME = "fhv_tripdata_"
YEARS = ["2019"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]

BUCKET_NAME = "de_hw4_2026"
CREDENTIALS_FILE = "secrets/keys.json"
storage_client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bq_client = bigquery.Client.from_service_account_json(CREDENTIALS_FILE)

BQ_DATASET = "elt-demo-de.nytaxi"

DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = storage_client.bucket(BUCKET_NAME)


def create_bucket(bucket_name):
    try:
        storage_client.get_bucket(bucket_name)
        project_bucket_ids = [bckt.id for bckt in storage_client.list_buckets()]
        if bucket_name in project_bucket_ids:
            print(f"Bucket '{bucket_name}' exists and belongs to your project. Proceeding...")
        else:
            print(f"Bucket '{bucket_name}' exists but does not belong to your project.")
            sys.exit(1)
    except NotFound:
        storage_client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    except Forbidden:
        print(f"Bucket '{bucket_name}' exists but is not accessible. Try a different name.")
        sys.exit(1)


def file_exists_in_gcs(filename):
    return storage.Blob(bucket=bucket, name=filename).exists(storage_client)


def upload_to_gcs(file_path, max_retries=3):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")
            return True
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")
        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")
    return False


def process_file(year, month):
    """Download csv.gz, extract to csv, upload to GCS."""
    gz_filename = f"{BASE_FILENAME}{year}-{month}.csv.gz"
    csv_filename = gz_filename.replace(".csv.gz", ".csv")
    csv_path = os.path.join(DOWNLOAD_DIR, csv_filename)
    gz_path = os.path.join(DOWNLOAD_DIR, gz_filename)

    if file_exists_in_gcs(csv_filename):
        print(f"Skipping {csv_filename}, already in GCS.")
        return csv_filename

    url = f"{BASE_URL}{gz_filename}"
    try:
        # Download
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, gz_path)

        # Extract gz -> csv
        print(f"Extracting {gz_filename}...")
        with gzip.open(gz_path, "rb") as f_in:
            with open(csv_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(gz_path)

        # Upload csv to GCS
        if upload_to_gcs(csv_path):
            os.remove(csv_path)
            return csv_filename

    except Exception as e:
        print(f"Failed to process {gz_filename}: {e}")

    # Cleanup on failure
    for f in [gz_path, csv_path]:
        if os.path.exists(f):
            os.remove(f)
    return None


def create_external_table():
    """Create external table for FHV data."""
    table_id = f"{BQ_DATASET}.fhv_tripdata"
    uris = [
        f"gs://{BUCKET_NAME}/{BASE_FILENAME}{year}-*.csv"
        for year in YEARS
    ]

    external_config = bigquery.ExternalConfig("CSV")
    external_config.source_uris = uris
    external_config.autodetect = True
    external_config.options.skip_leading_rows = 1

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

    tasks = [(year, month) for year in YEARS for month in MONTHS]

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda args: process_file(*args), tasks))

    valid = [f for f in results if f is not None]
    print(f"\nUploaded {len(valid)}/{len(tasks)} files.")

    print("\n--- Creating external table in BigQuery ---")
    create_external_table()

    print("Done.")