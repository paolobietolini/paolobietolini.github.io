from google.cloud import bigquery
import polars as pl
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta
import random
import os

PROJECT_ID = "zmcp-final"
DATASET_ID = "raw_ga4"
TABLE_ID = "events"
CREDENTIALS_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
# CREDENTIALS_FILE = "secrets/secret_zcmp-final.json"
BACKEND_DIR = "scripts/data/raw_backend"

random.seed(42)
Faker.seed(42)
fake = Faker()

QUERY_ECOMMERCE = f"""SELECT DISTINCT
      event_date,
      user_pseudo_id,
      ecommerce.transaction_id,
      ecommerce.total_item_quantity,
      ecommerce.purchase_revenue,
      ecommerce.shipping_value
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    WHERE ecommerce.transaction_id IS NOT NULL
"""

QUERY_ITEMS = f"""
    SELECT
      ecommerce.transaction_id,
      items.item_id,
      items.item_name,
      items.item_category,
      items.price,
      items.quantity
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`,
    UNNEST(items) AS items
    WHERE ecommerce.transaction_id IS NOT NULL
"""


def query_bq(query):
    try:
        print("Querying BigQuery...")
        bq_client = bigquery.Client()
        query_job = bq_client.query(query)
        df = pl.from_pandas(query_job.to_dataframe())
        print("BigQuery, done.")
        return df
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


def generate_users_table(df):
    """
    Deduplicates user_pseudo_id and creates a users table
    with a synthetic user_id, email, name, and created_at.
    """
    users = df.select("user_pseudo_id", "event_date").unique(
        subset="user_pseudo_id", keep="first", maintain_order=True
    )

    first_event_dates = df.group_by("user_pseudo_id").agg(
        pl.col("event_date").min().alias("first_event_date")
    )
    users = users.drop("event_date").join(first_event_dates, on="user_pseudo_id")

    n = len(users)
    users = users.with_columns(
        [
            pl.Series("user_id", list(range(1, n + 1))),
            pl.Series("email", [fake.email() for _ in range(n)]),
            pl.Series("name", [fake.name() for _ in range(n)]),
            pl.Series(
                "created_at",
                [
                    datetime.strptime(d, "%Y%m%d")
                    - timedelta(days=random.randint(1, 90))
                    for d in users["first_event_date"].to_list()
                ],
            ),
        ]
    ).drop("first_event_date")

    return users


def generate_orders_table(df, users):
    """
    Builds an orders table by joining ecommerce data with users,
    then drops ~15-20% of rows to simulate data gaps.
    """
    orders = df.select(
        "transaction_id",
        "user_pseudo_id",
        "purchase_revenue",
        "shipping_value",
        "total_item_quantity",
        "event_date",
    ).unique(subset="transaction_id", keep="first", maintain_order=True)

    orders = orders.join(users.select("user_pseudo_id", "user_id"), on="user_pseudo_id")

    n = len(orders)
    orders = orders.with_columns(
        [
            pl.Series("order_id", list(range(1, n + 1))),
            pl.Series(
                "status",
                [
                    random.choice(
                        ["completed", "completed", "completed", "refunded", "pending"]
                    )
                    for _ in range(n)
                ],
            ),
            pl.col("event_date").alias("created_at"),
        ]
    ).drop("event_date", "user_pseudo_id")

    # Drop ~15-20% of rows to simulate data gaps
    keep_mask = [random.random() > 0.17 for _ in range(n)]
    orders = orders.filter(pl.Series(keep_mask))

    return orders


def generate_order_items_table(items_df, orders):
    """
    Filters items to only kept transaction_ids from orders table.
    """
    kept_ids = orders.select("transaction_id")
    order_items = items_df.join(kept_ids, on="transaction_id")
    return order_items


def main():
    Path(BACKEND_DIR).mkdir(parents=True, exist_ok=True)
    ecommerce_path = f"{BACKEND_DIR}/raw_ecommerce_query.parquet"
    items_path = f"{BACKEND_DIR}/raw_items_query.parquet"

    # Load or query ecommerce data
    if Path(ecommerce_path).is_file():
        df = pl.read_parquet(ecommerce_path)
    else:
        df = query_bq(QUERY_ECOMMERCE)
        if df is not None:
            df.write_parquet(ecommerce_path)

    # Load or query items data
    if Path(items_path).is_file():
        items_df = pl.read_parquet(items_path)
    else:
        items_df = query_bq(QUERY_ITEMS)
        if items_df is not None:
            items_df.write_parquet(items_path)

    if df is None or items_df is None:
        print("Failed to load data.")
        return

    # Generate tables
    users = generate_users_table(df)
    orders = generate_orders_table(df, users)
    order_items = generate_order_items_table(items_df, orders)

    # Save as parquet
    users.write_parquet(f"{BACKEND_DIR}/users.parquet")
    orders.write_parquet(f"{BACKEND_DIR}/orders.parquet")
    order_items.write_parquet(f"{BACKEND_DIR}/order_items.parquet")

    print(f"Users: {len(users)} rows")
    print(f"Orders: {len(orders)} rows (with ~17% dropped)")
    print(f"Order items: {len(order_items)} rows")
    print(f"Saved to {BACKEND_DIR}/")

    print(pl.read_parquet(f"{BACKEND_DIR}/orders.parquet"))


if __name__ == "__main__":
    main()
