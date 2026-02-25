# Customer Journey Unification Pipeline

## Overview
Integrate frontend analytics (GA4) with backend transactional data (PostgreSQL) to build a unified customer journey view, with data quality reconciliation.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                    │
│                                                     │
│  ┌──────────┐   ┌────────────┐   ┌───────────────┐  │
│  │ Airflow  │   │ PostgreSQL │   │ Python scripts│  │
│  └────┬─────┘   └─────┬──────┘   └───────┬───────┘  │
│       │               │                  │          │
└───────┼───────────────┼──────────────────┼──────────┘
        │               │                  │
        ▼               ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│                    BigQuery                         │
│  raw_ga4.events           raw_backend.orders        │
│                           raw_backend.users         │
│                           raw_backend.order_items   │
│       │                        │                    │
│       ▼────────► dbt ◄────────▼                     │
│                   │                                 │
│        staging_ga4.stg_events                       │
│        staging_backend.stg_orders                   │
│        staging_backend.stg_users                    │
│                   │                                 │
│                   ▼                                 │
│        marts.fct_user_journeys                      │
│        marts.fct_reconciliation                     │
│        marts.dim_users                              │
│                   │                                 │
└───────────────────┼─────────────────────────────────┘
                    ▼
             Looker Studio
```

## Data Sources

### Source A — Frontend (GA4)
- Dataset: `bigquery-public-data.ga4_obfuscated_sample_ecommerce`
- URL: https://console.cloud.google.com/bigquery?ws=!1m4!1m3!3m2!1sbigquery-public-data!2sga4_obfuscated_sample_ecommerce
- Date range: 20201101 – 20201231
- Load into own BQ project as raw table

### Source B — Backend (Synthetic → PostgreSQL)
- Python script queries GA4 data to extract real `transaction_id` and `user_pseudo_id` values
- Generates `users`, `orders`, `order_items` tables with intentional data gaps (~15-20%)
- Loaded into PostgreSQL (Docker), then ingested into BigQuery

## Stack

| Layer           | Tool                                      |
|-----------------|-------------------------------------------|
| Infrastructure  | Docker Compose (PostgreSQL + Airflow)     |
| Ingestion A     | BigQuery dataset copy / scheduled query   |
| Ingestion B     | Python: generate synthetic data → PostgreSQL → BigQuery |
| Orchestration   | Airflow                                   |
| Transformation  | dbt (BigQuery)                            |
| Visualization   | Looker Studio                             |

## Airflow DAG

```
generate_synthetic_data
        │
        ▼
┌───────────────────┬──────────────────────┐
│                   │                      │
▼                   ▼                      ▼
load_ga4_to_bq    load_users_to_bq    load_orders_to_bq
│                   │                      │
└───────────────────┴──────────────────────┘
                    │
                    ▼
              run_dbt_models
                    │
                    ▼
            dbt_test (data quality)
```

## dbt Models

### Staging
- Clean column names, cast types, filter test data

### Intermediate
- Sessionize GA4 events
- Map `user_pseudo_id` to backend `user_id`

### Marts
- `fct_user_journeys` — full funnel: first visit → engagement → purchase
- `fct_reconciliation` — GA4 transactions vs backend orders (match rate, revenue delta)
- `dim_users` — unified user profile

## Looker Studio Dashboard
- Funnel visualization (sessions → add_to_cart → purchase)
- Reconciliation metrics (match rate %, revenue discrepancy)
- User journey timeline

## Repo Structure

```
final-project/
├── docker-compose.yml
├── dags/
│   └── pipeline_dag.py
├── scripts/
│   ├── generate_synthetic_data.py
│   └── load_to_bq.py
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── dbt_project.yml
├── README.md
└── IDEAS.md
```

## Build Order
1. Get GA4 sample data loaded into own BQ project
2. Write the synthetic data generator
3. Get Docker Compose running with PostgreSQL + Airflow
4. Build the DAG
5. Write dbt models
6. Connect Looker Studio



<! -- Notes -->
● Good plan. Here's what you still need to build out:

  Generate the tables from the query result:
  - users — deduplicate user_pseudo_id, add fake columns (email,
  name, created_at) using something like faker
  - orders — map transaction_id to a user_id (from your users
  table), add status, created_at. Drop ~15-20% randomly to create
  data gaps
  - order_items — second query with UNNEST(items) filtered to the
  kept transaction_ids, add price, quantity

  File format:
  - Parquet is better than CSV (types are preserved, smaller files)
  — good instinct

  Load into PostgreSQL:
  - Use sqlalchemy + pandas.to_sql() or psycopg2 with COPY
  - Create the tables/schema first (or let pandas create them)
  - Connection string pointing to your Docker PostgreSQL

  Things easy to forget:
  - Add a user_id (integer PK) to users — don't use user_pseudo_id
  directly as the PK, keep it as a separate column. This simulates a
   real backend where the frontend ID and backend ID are different
  - Timestamps — make created_at dates realistic relative to
  event_date
  - Set a random seed (random.seed(42)) so results are reproducible

