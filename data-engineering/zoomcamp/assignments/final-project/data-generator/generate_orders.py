"""
Queries GA4 public dataset for purchase events, then generates
a fake orders table with controlled discrepancies:
  - ~80% matched (same transaction_id + revenue)
  - ~5% revenue mismatch (same transaction_id, different amount)
  - ~5% skipped (becomes ghost order in GA4 with no DB match)
  - ~10% extra DB-only orders (no GA4 match)
"""

import random
import uuid
from pathlib import Path

import pandas as pd
from faker import Faker
from google.cloud import bigquery

OUTPUT_DIR = Path(__file__).parent / "output"

GA4_QUERY = """
SELECT
    event_date,
    event_timestamp,
    user_pseudo_id,
    ecommerce.transaction_id,
    ecommerce.purchase_revenue,
    (SELECT COUNT(*) FROM UNNEST(items)) AS item_count
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE event_name = 'purchase'
  AND ecommerce.transaction_id IS NOT NULL
"""

fake = Faker()
Faker.seed(42)
random.seed(42)


def fetch_ga4_purchases() -> pd.DataFrame:
    """Fetch purchase events from GA4 public dataset."""
    client = bigquery.Client()
    print("Querying GA4 public dataset for purchase events...")
    df = client.query(GA4_QUERY).to_dataframe()
    print(f"  Found {len(df)} purchase events")
    return df


def generate_orders(ga4_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate fake orders based on GA4 purchases.
    Returns (orders_df, ga4_purchases_df).
    """
    orders = []

    for _, row in ga4_df.iterrows():
        roll = random.random()

        if roll < 0.80:
            # Matched order — same transaction_id and revenue
            orders.append(_make_order(row, revenue_override=None))
        elif roll < 0.85:
            # Revenue mismatch — same transaction_id, tweaked amount
            offset = random.uniform(-5.0, 5.0)
            orders.append(_make_order(row, revenue_override=row["purchase_revenue"] + offset))
        elif roll < 0.90:
            # Ghost order — skip, GA4 event has no DB match
            continue
        else:
            # DB-only order — no GA4 match (tracking failure)
            orders.append(_make_order(row, revenue_override=None))
            orders.append(_make_extra_order(row))

    orders_df = pd.DataFrame(orders)
    print(f"  Generated {len(orders_df)} orders")

    return orders_df, ga4_df


def _make_order(ga4_row: pd.Series, revenue_override: float | None) -> dict:
    event_date = pd.to_datetime(ga4_row["event_date"], format="%Y%m%d").date()
    return {
        "order_id": str(uuid.uuid4()),
        "transaction_id": ga4_row["transaction_id"],
        "order_date": event_date,
        "customer_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, ga4_row["user_pseudo_id"])),
        "total_amount": round(float(revenue_override if revenue_override is not None else ga4_row["purchase_revenue"]), 2),
        "item_count": int(ga4_row["item_count"]),
        "status": random.choices(["completed", "refunded", "cancelled"], weights=[0.90, 0.05, 0.05])[0],
        "created_at": pd.Timestamp(event_date) + pd.Timedelta(seconds=random.randint(0, 86400)),
    }


def _make_extra_order(ga4_row: pd.Series) -> dict:
    """Create a DB-only order with no matching GA4 event."""
    event_date = pd.to_datetime(ga4_row["event_date"], format="%Y%m%d").date()
    return {
        "order_id": str(uuid.uuid4()),
        "transaction_id": f"DB-{uuid.uuid4().hex[:12]}",
        "order_date": event_date,
        "customer_id": str(uuid.uuid4()),
        "total_amount": round(random.uniform(5.0, 300.0), 2),
        "item_count": random.randint(1, 8),
        "status": "completed",
        "created_at": pd.Timestamp(event_date) + pd.Timedelta(seconds=random.randint(0, 86400)),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ga4_df = fetch_ga4_purchases()
    orders_df, ga4_purchases_df = generate_orders(ga4_df)

    orders_path = OUTPUT_DIR / "orders.parquet"
    ga4_path = OUTPUT_DIR / "ga4_purchases.parquet"

    orders_df.to_parquet(orders_path, index=False)
    ga4_purchases_df.to_parquet(ga4_path, index=False)

    print(f"\nSaved:")
    print(f"  {orders_path}  ({len(orders_df)} rows)")
    print(f"  {ga4_path}  ({len(ga4_purchases_df)} rows)")


if __name__ == "__main__":
    main()
