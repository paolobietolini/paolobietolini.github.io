"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.13.7

columns:
  - name: VendorID
    type: integer
    description: TPEP/LPEP provider code (1=Creative Mobile, 2=VeriFone)
  - name: pickup_datetime
    type: timestamp
    description: Pickup date and time (normalized from tpep/lpep prefix)
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff date and time (normalized from tpep/lpep prefix)
  - name: passenger_count
    type: float
    description: Number of passengers
  - name: trip_distance
    type: float
    description: Trip distance in miles
  - name: RatecodeID
    type: float
    description: Rate code (1=Standard, 2=JFK, 3=Newark, etc.)
  - name: store_and_fwd_flag
    type: string
    description: Whether trip was held in memory before sending (Y/N)
  - name: PULocationID
    type: integer
    description: TLC Taxi Zone pickup location ID
  - name: DOLocationID
    type: integer
    description: TLC Taxi Zone dropoff location ID
  - name: payment_type
    type: integer
    description: Payment type code (1=Credit card, 2=Cash, etc.)
  - name: fare_amount
    type: float
    description: Time-and-distance fare in USD
  - name: extra
    type: float
    description: Miscellaneous extras and surcharges
  - name: mta_tax
    type: float
    description: MTA tax
  - name: tip_amount
    type: float
    description: Tip amount (credit card tips only)
  - name: tolls_amount
    type: float
    description: Total tolls paid
  - name: improvement_surcharge
    type: float
    description: Improvement surcharge
  - name: total_amount
    type: float
    description: Total amount charged to passenger
  - name: congestion_surcharge
    type: float
    description: Congestion surcharge
  - name: airport_fee
    type: float
    description: Airport fee
  - name: taxi_type
    type: string
    description: 'Taxi type: yellow or green'
  - name: extracted_at
    type: timestamp
    description: Timestamp when this record was extracted

@bruin"""

# TODO: Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python

import io
import os
import json
from urllib.request import Request, urlopen

import pandas as pd


def materialize():
    """
    Design TODOs (keep logic minimal, focus on architecture):
    - Use start/end dates + `taxi_types` to generate a list of source endpoints for the run window.
    - Fetch data for each endpoint, parse into DataFrames, and concatenate.
    - Add a column like `extracted_at` for lineage/debugging (timestamp of extraction).
    - Prefer append-only in ingestion; handle duplicates in staging.
    """
    dfs = []
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    months = pd.date_range(start=start, end=end, freq="MS")

    for taxi_type in taxi_types:
        for month in months:
            year = month.year
            month_str = f"{month.month:02d}"
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month_str}.parquet"

            print(f"Fetching {url}")
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req) as resp:
                    df = pd.read_parquet(io.BytesIO(resp.read()))
            except Exception as e:
                print(f"Skipping {url}: {e}")
                continue
            # Normalize column names: yellow uses tpep_ prefix, green uses lpep_
            prefix = "tpep" if taxi_type == "yellow" else "lpep"
            df = df.rename(
                columns={
                    f"{prefix}_pickup_datetime": "pickup_datetime",
                    f"{prefix}_dropoff_datetime": "dropoff_datetime",
                }
            )
            df["taxi_type"] = taxi_type
            df["extracted_at"] = pd.Timestamp.utcnow()

            dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)
