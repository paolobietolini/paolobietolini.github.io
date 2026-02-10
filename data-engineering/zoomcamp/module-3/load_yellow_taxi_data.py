import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time


BUCKET_NAME = "de_hw3_2026"
CREDENTIALS_FILE = "secrets/keys.json"
client = storage.Client.from_service_account_json(CREDENTIALS_FILE)

DATA_TYPES = ["green", "yellow"]
YEARS = ["2019", "2020"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = client.bucket(BUCKET_NAME)


def download_file(data_type, year, month):
    filename = f"{data_type}_tripdata_{year}-{month}.parquet"
    url = f"{BASE_URL}/{filename}"
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    print(file_path)
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def create_bucket(bucket_name):
    try:
        bucket = client.get_bucket(bucket_name)
        project_bucket_ids = [bckt.id for bckt in client.list_buckets()]
        if bucket_name in project_bucket_ids:
            print(f"Bucket '{bucket_name}' exists and belongs to your project. Proceeding...")
        else:
            print(f"Bucket '{bucket_name}' exists but does not belong to your project.")
            sys.exit(1)
    except NotFound:
        bucket = client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    except Forbidden:
        print(f"Bucket '{bucket_name}' exists but is not accessible. Try a different name.")
        sys.exit(1)


def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)


def upload_to_gcs(file_path, max_retries=3):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if verify_gcs_upload(blob_name):
                print(f"Verification successful for {blob_name}")
                return
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")

        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")


if __name__ == "__main__":
    create_bucket(BUCKET_NAME)

    tasks = [
        (data_type, year, month)
        for data_type in DATA_TYPES
        for year in YEARS
        for month in MONTHS
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        file_paths = list(executor.map(lambda args: download_file(*args), tasks))

    valid_paths = [p for p in file_paths if p is not None]

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, valid_paths)

    print(f"All files processed. {len(valid_paths)}/{len(tasks)} succeeded.")