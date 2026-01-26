import pandas as pd
import click
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import re
import pyarrow.parquet as pq


def read_parquet_in_batches(filepath, batch_size=10000):
    """Generator to read parquet file in batches"""
    parquet_file = pq.ParquetFile(filepath)
    for batch in parquet_file.iter_batches(batch_size=batch_size):
        yield batch.to_pandas()


def create_table(iterator, filename, engine):
    pattern = r"\.[^.]+$"
    TABLE_NAME = re.sub(pattern, "", filename)
    first = True
    for chunk in tqdm(iterator):
        if first:
            chunk.head(0).to_sql(
                name=TABLE_NAME, con=engine, if_exists="replace", index=False
            )
            first = False
            print(f"Table {TABLE_NAME} Created")
        chunk.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
        )
        print("Inserted:", len(chunk))


@click.command()
@click.option("--user", default="root", help="PostgreSQL user")
@click.option("--password", default="root", help="PostgreSQL password")
@click.option("--host", default="localhost", help="PostgreSQL host")
@click.option("--port", default=9868, type=int, help="PostgreSQL port")
@click.option("--db", default="ny_taxi", help="PostgreSQL database name")
def ingest_data(user, password, host, port, db):
    FILENM_TAXI_TRIPS = "green_tripdata_2025-11.parquet"
    FILENM_TAXI_ZONES = "taxi_zone_lookup.csv"
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    csv_dtype = {
        "LocationID": "Int64",
        "Borough": "string",
        "Zone": "string",
        "service_zone": "string",
    }

    csv_iter = pd.read_csv(
        FILENM_TAXI_ZONES, iterator=True, chunksize=10000, dtype=csv_dtype
    )

    parquet_iter = read_parquet_in_batches(FILENM_TAXI_TRIPS, batch_size=10000)

    create_table(parquet_iter, FILENM_TAXI_TRIPS, engine)
    create_table(csv_iter, FILENM_TAXI_ZONES, engine)


if __name__ == "__main__":
    ingest_data()
