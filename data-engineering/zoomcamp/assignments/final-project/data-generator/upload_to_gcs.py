"""
Uploads locally generated parquet files to the GCS data lake bucket.
"""

import os
from pathlib import Path

from google.cloud import storage

BUCKET_NAME = os.environ.get("GCS_BUCKET", "zmcp-final-reconciliation-datalake")
OUTPUT_DIR = Path(__file__).parent / "output"

UPLOADS = {
    "orders.parquet": "raw/orders/orders.parquet",
    "ga4_purchases.parquet": "raw/ga4_purchases/ga4_purchases.parquet",
}


def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    for local_name, gcs_path in UPLOADS.items():
        local_file = OUTPUT_DIR / local_name
        if not local_file.exists():
            print(f"  SKIP {local_name} — not found. Run generate_orders.py first.")
            continue

        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(str(local_file))
        print(f"  Uploaded {local_name} -> gs://{BUCKET_NAME}/{gcs_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
