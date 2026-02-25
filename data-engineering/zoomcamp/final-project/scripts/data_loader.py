import os
from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path

BACKEND_DATA = Path("scripts/data/raw_backend")

user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
db = os.environ["DB_NAME"]
port = os.environ.get("DB_PORT", "5432")

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


def load_parquet_to_postgres(file_path: Path, engine):
    table_name = file_path.stem  # e.g. "users", "orders", "order_items"
    print(f"Loading {file_path} -> table '{table_name}'...")
    df = pd.read_parquet(file_path)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"  Loaded {len(df)} rows into '{table_name}'")


def main():
    parquet_files = sorted(BACKEND_DATA.glob("*.parquet"))

    # Skip the raw query caches, only load the generated tables
    skip = {"raw_ecommerce_query", "raw_items_query"}
    parquet_files = [f for f in parquet_files if f.stem not in skip]

    if not parquet_files:
        print(f"No parquet files found in {BACKEND_DATA}")
        return

    print(
        f"Found {len(parquet_files)} parquet files: {[f.name for f in parquet_files]}"
    )

    for f in parquet_files:
        load_parquet_to_postgres(f, engine)

    print("Done.")


if __name__ == "__main__":
    main()
