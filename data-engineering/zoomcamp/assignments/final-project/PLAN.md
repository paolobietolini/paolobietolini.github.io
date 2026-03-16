# Final Project: E-Commerce Order Reconciliation Pipeline

## Problem Statement

An e-commerce store (Google Merchandise Store) tracks purchases via GA4 (client-side analytics) and records orders in an internal database (PostgreSQL). These two systems inevitably diverge:

- **Ghost orders**: GA4 tracks a purchase event but no matching order exists in the DB (e.g. user had JS errors, payment failed after tracking fired)
- **Tracking failures**: Order exists in the DB but GA4 never recorded it (e.g. ad blocker, consent denial, tag misconfiguration)
- **Revenue discrepancies**: Both systems recorded the order but amounts differ (e.g. post-purchase adjustments, currency rounding)

This pipeline reconciles both sources daily, surfaces discrepancies, and presents match rates and revenue gaps on a dashboard.

---

## Architecture

```
                         ┌───────────────────┐
                         │    Terraform      │
                         │  (all GCP infra)  │
                         └───────────────────┘

┌─────────────┐     ┌──────────────────┐
│ PostgreSQL  │     │  GA4 Public      │
│ (Docker)    │     │  Dataset (BQ)    │
│ fake orders │     │  bigquery-public │
└──────┬──────┘     └──────┬───────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────────┐
│           GCS Data Lake              │
│  gs://bucket/raw/orders/             │
│  gs://bucket/raw/ga4_purchases/      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│        Spark (Dataproc)              │
│  - standardize schemas              │
│  - write cleaned parquet to GCS     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│       BigQuery (Data Warehouse)      │
│  - external tables on GCS parquet   │
│  - dbt staging + fact models        │
│  - partitioned & clustered          │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│        dbt (Transformations)         │
│  - stg_orders                        │
│  - stg_ga4_purchases                 │
│  - fct_reconciliation                │
│  - metrics_daily_summary             │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    Looker Studio (Dashboard)         │
│  Tile 1: Match rate over time (line) │
│  Tile 2: Discrepancy categories (bar)│
└──────────────────────────────────────┘

Orchestration: Airflow (Docker Compose, locally)
```

---

## Tech Stack

| Layer               | Tool                                          |
|---------------------|-----------------------------------------------|
| Cloud               | GCP                                           |
| IaC                 | Terraform                                     |
| Data Lake           | Google Cloud Storage (GCS)                    |
| Data Warehouse      | BigQuery                                      |
| Batch Processing    | PySpark on Dataproc (or local for dev)        |
| Transformations     | dbt-core with dbt-bigquery adapter            |
| Orchestration       | Airflow (Docker Compose)                      |
| Dashboard           | Looker Studio                                 |
| Fake Data Generator | Python (Faker + pandas)                       |
| Containerization    | Docker / Docker Compose                       |

---

## Data Sources

### 1. GA4 Public Dataset (BigQuery)

- **Location**: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
- **Date range**: 2020-11-01 to 2021-01-31
- **Key fields for purchases**:
  - `event_name = 'purchase'`
  - `event_date` (YYYYMMDD string)
  - `event_timestamp` (microseconds)
  - `user_pseudo_id`
  - `ecommerce.transaction_id`
  - `ecommerce.purchase_revenue`
  - `items[]` (array of purchased items with item_id, item_name, price, quantity)

### 2. Fake Orders Database (PostgreSQL in Docker)

Generated Python script creates orders that:
- ~80% match a real GA4 transaction_id (happy path)
- ~10% exist only in DB (simulates GA4 tracking failure)
- ~10% have a matching transaction_id but different revenue (simulates discrepancy)
- GA4 will also have ~10% purchase events with no DB match (ghost orders)

**Schema: `orders` table**

| Column           | Type        | Description                          |
|------------------|-------------|--------------------------------------|
| order_id         | VARCHAR(36) | UUID, primary key                    |
| transaction_id   | VARCHAR(50) | Maps to GA4 ecommerce.transaction_id |
| order_date       | DATE        | Order date                           |
| customer_id      | VARCHAR(36) | Internal customer ID                 |
| total_amount     | DECIMAL     | Order total in USD                   |
| item_count       | INTEGER     | Number of items                      |
| status           | VARCHAR(20) | completed / refunded / cancelled     |
| created_at       | TIMESTAMP   | Record creation time                 |

---

## Directory Structure

```
final-project/
├── PLAN.md                          # This file
├── README.md                        # Project overview for submission
├── Makefile                         # One-command setup & run
│
├── terraform/
│   ├── main.tf                      # Provider, GCS bucket, BQ dataset
│   ├── variables.tf                 # Project ID, region, bucket name
│   ├── outputs.tf                   # Bucket URL, dataset ID
│   └── terraform.tfvars.example     # Example variables (not real creds)
│
├── data-generator/
│   ├── generate_orders.py           # Reads GA4 purchases, creates fake orders
│   ├── upload_to_gcs.py             # Exports orders to parquet, uploads to GCS
│   ├── requirements.txt             # faker, pandas, google-cloud-bigquery, etc.
│   └── Dockerfile                   # Containerized generator
│
├── spark/
│   ├── extract_ga4_purchases.py     # Extract purchase events from BQ -> GCS parquet
│   ├── clean_orders.py              # Standardize order data
│   ├── reconcile.py                 # Join + reconcile both sources
│   └── Dockerfile                   # Spark job container (if running local)
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml.example
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_orders.sql               # Clean orders from GCS/BQ
│   │   │   ├── stg_ga4_purchases.sql        # Clean GA4 purchase events
│   │   │   └── schema.yml                   # Tests & docs
│   │   └── marts/
│   │       ├── fct_reconciliation.sql       # Full outer join, match logic
│   │       ├── metrics_daily_summary.sql    # Daily match rates & revenue gaps
│   │       └── schema.yml
│   └── macros/
│       └── reconciliation_status.sql        # Macro: matched/ghost/missing/mismatch
│
├── airflow/
│   ├── docker-compose.yml           # Airflow + Postgres metadata DB
│   ├── Dockerfile                   # Custom Airflow image with providers
│   ├── requirements.txt             # apache-airflow-providers-google, dbt-core, etc.
│   └── dags/
│       └── reconciliation_dag.py    # Full pipeline DAG (see below)
│
├── dashboard/
│   └── screenshots/                 # Dashboard screenshots for README
│
└── .gitignore
```

---

## Phase-by-Phase Implementation Plan

### Phase 1: Terraform (GCP Infrastructure)

**Goal**: Provision all cloud resources with `terraform apply`.

**Resources to create**:
- GCS bucket: `{project_id}-reconciliation-datalake`
  - Folders: `raw/orders/`, `raw/ga4_purchases/`, `cleaned/`
- BigQuery dataset: `reconciliation`
  - Location: `US` (same as public dataset)
- Service account: `reconciliation-sa` with roles:
  - `roles/bigquery.admin`
  - `roles/storage.admin`
- Service account key (JSON) for Airflow

**Files**:
- `terraform/main.tf` — all resources
- `terraform/variables.tf` — project_id, region, bucket_name
- `terraform/outputs.tf` — bucket name, dataset id, SA email

**Done when**: `terraform apply` creates all resources, `terraform output` shows values.

---

### Phase 2: Data Generator (Fake Orders)

**Goal**: Python script that queries GA4 purchase events and generates a realistic but imperfect orders table.

**Logic**:
1. Query GA4 for all `purchase` events:
   ```sql
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
   ```
2. For each GA4 purchase, decide:
   - **80% chance**: Create matching order (same transaction_id, same amount)
   - **5% chance**: Create order with slightly different amount (revenue mismatch)
   - **5% chance**: Skip (this GA4 event becomes a "ghost order")
   - **10% chance**: Create an extra order with no GA4 match (tracking failure)
3. Output: `orders.parquet` uploaded to `gs://bucket/raw/orders/`
4. Also export GA4 purchases to `gs://bucket/raw/ga4_purchases/` as parquet

**Done when**: Both parquet files exist in GCS.

---

### Phase 3: Spark Processing

**Goal**: Clean, standardize, and prepare data for BigQuery.

**Job 1: `extract_ga4_purchases.py`**
- Read GA4 parquet from GCS
- Standardize columns: `transaction_id`, `event_date` (cast to DATE), `revenue` (cast to DECIMAL), `user_id`, `item_count`
- Write to `gs://bucket/cleaned/ga4_purchases/`

**Job 2: `clean_orders.py`**
- Read orders parquet from GCS
- Standardize columns to match GA4 schema naming
- Filter to `status = 'completed'` only
- Write to `gs://bucket/cleaned/orders/`

**Note on Spark execution**:
- For dev/submission: run locally via `spark-submit` (no Dataproc cost)
- Airflow DAG will call `SparkSubmitOperator` or `BashOperator`

**Done when**: Cleaned parquet files in `gs://bucket/cleaned/`.

---

### Phase 4: BigQuery + dbt

**Goal**: Load cleaned data into BQ, transform with dbt into reconciliation facts.

**Step 4a: External tables (or BQ load)**

Create BigQuery external tables pointing to cleaned GCS parquet:
```sql
CREATE OR REPLACE EXTERNAL TABLE reconciliation.ext_orders
OPTIONS (format = 'PARQUET', uris = ['gs://bucket/cleaned/orders/*.parquet']);

CREATE OR REPLACE EXTERNAL TABLE reconciliation.ext_ga4_purchases
OPTIONS (format = 'PARQUET', uris = ['gs://bucket/cleaned/ga4_purchases/*.parquet']);
```

**Step 4b: dbt models**

**`stg_orders.sql`** — clean staging from external table:
```sql
SELECT
    transaction_id,
    order_date,
    total_amount AS order_revenue,
    item_count AS order_item_count,
    customer_id
FROM {{ source('reconciliation', 'ext_orders') }}
WHERE transaction_id IS NOT NULL
```

**`stg_ga4_purchases.sql`** — clean staging from GA4:
```sql
SELECT
    transaction_id,
    event_date AS purchase_date,
    revenue AS ga4_revenue,
    item_count AS ga4_item_count,
    user_id AS ga4_user_id
FROM {{ source('reconciliation', 'ext_ga4_purchases') }}
WHERE transaction_id IS NOT NULL
```

**`fct_reconciliation.sql`** — the core model:
```sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
ga4 AS (
    SELECT * FROM {{ ref('stg_ga4_purchases') }}
),
reconciled AS (
    SELECT
        COALESCE(o.transaction_id, g.transaction_id) AS transaction_id,
        o.order_date,
        g.purchase_date,
        o.order_revenue,
        g.ga4_revenue,
        ABS(COALESCE(o.order_revenue, 0) - COALESCE(g.ga4_revenue, 0)) AS revenue_diff,
        CASE
            WHEN o.transaction_id IS NOT NULL AND g.transaction_id IS NOT NULL
                 AND ABS(o.order_revenue - g.ga4_revenue) < 0.01
                THEN 'matched'
            WHEN o.transaction_id IS NOT NULL AND g.transaction_id IS NOT NULL
                THEN 'revenue_mismatch'
            WHEN o.transaction_id IS NOT NULL AND g.transaction_id IS NULL
                THEN 'missing_in_ga4'
            WHEN o.transaction_id IS NULL AND g.transaction_id IS NOT NULL
                THEN 'ghost_order'
        END AS reconciliation_status
    FROM orders o
    FULL OUTER JOIN ga4 g ON o.transaction_id = g.transaction_id
)
SELECT * FROM reconciled
```

**`metrics_daily_summary.sql`** — aggregated for dashboard:
```sql
SELECT
    COALESCE(order_date, purchase_date) AS report_date,
    reconciliation_status,
    COUNT(*) AS transaction_count,
    SUM(revenue_diff) AS total_revenue_gap,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
        PARTITION BY COALESCE(order_date, purchase_date)
    ) AS pct_of_daily_total
FROM {{ ref('fct_reconciliation') }}
GROUP BY 1, 2
```

**BQ optimization**:
- `fct_reconciliation`: partitioned by `COALESCE(order_date, purchase_date)`, clustered by `reconciliation_status`
- Explain partitioning/clustering choice in README

**Done when**: `dbt run` succeeds, `dbt test` passes.

---

### Phase 5: Airflow DAG

**Goal**: Wire everything into a single DAG that runs end-to-end.

**DAG: `reconciliation_dag.py`**

```
generate_fake_orders >> upload_to_gcs
                                       \
extract_ga4_to_gcs ────────────────────->> spark_clean_orders >> spark_clean_ga4
                                                                        \
                                                              create_external_tables >> dbt_run >> dbt_test
```

**Tasks**:
1. `generate_fake_orders` — BashOperator: run `generate_orders.py`
2. `upload_to_gcs` — BashOperator: run `upload_to_gcs.py`
3. `extract_ga4_to_gcs` — BigQueryToGCSOperator or BashOperator
4. `spark_clean_orders` — BashOperator: `spark-submit clean_orders.py`
5. `spark_clean_ga4` — BashOperator: `spark-submit extract_ga4_purchases.py`
6. `create_external_tables` — BigQueryInsertJobOperator
7. `dbt_run` — BashOperator: `dbt run`
8. `dbt_test` — BashOperator: `dbt test`

**Airflow setup**: Docker Compose with:
- Airflow webserver + scheduler + worker
- PostgreSQL (Airflow metadata)
- Volume mounts for DAGs, Spark jobs, dbt project
- GCP credentials via environment variable

**Done when**: Trigger DAG in Airflow UI, all tasks go green.

---

### Phase 6: Dashboard (Looker Studio)

**Goal**: 2+ tiles connected to BigQuery `metrics_daily_summary`.

**Tile 1 — Match Rate Over Time (Line Chart)**:
- X-axis: `report_date`
- Y-axis: % of transactions with `reconciliation_status = 'matched'`
- Shows trend of reconciliation health

**Tile 2 — Discrepancy Breakdown (Stacked Bar / Pie)**:
- Categories: `matched`, `ghost_order`, `missing_in_ga4`, `revenue_mismatch`
- Shows overall distribution of reconciliation outcomes

**Optional Tile 3 — Revenue Gap (KPI card)**:
- Total `revenue_diff` across all mismatched transactions

**Done when**: Dashboard is published with a shareable link, screenshots saved.

---

### Phase 7: Reproducibility & README

**Goal**: Anyone can clone and run the project.

**Makefile targets**:
```makefile
setup:           ## Install dependencies
    pip install -r data-generator/requirements.txt
    pip install -r dbt/requirements.txt

infra:           ## Create GCP resources
    cd terraform && terraform init && terraform apply -auto-approve

generate:        ## Generate fake order data
    cd data-generator && python generate_orders.py

airflow-up:      ## Start Airflow
    cd airflow && docker-compose up -d

airflow-down:    ## Stop Airflow
    cd airflow && docker-compose down

run-all:         ## Trigger the full DAG
    cd airflow && docker-compose exec airflow-webserver \
        airflow dags trigger reconciliation_dag

destroy:         ## Tear down GCP resources
    cd terraform && terraform destroy -auto-approve
```

**README sections**:
1. Problem description (business context)
2. Architecture diagram
3. Tech stack & rationale
4. Prerequisites (GCP account, Docker, Terraform)
5. How to run (step by step)
6. Dashboard (link + screenshots)
7. What I'd improve with more time

---

## Scoring Checklist

| Criteria            | Target | How                                             |
|---------------------|--------|--------------------------------------------------|
| Problem description | 4/4    | Clear README with business context + diagram     |
| Cloud               | 4/4    | GCP + Terraform for all infra                    |
| Data ingestion      | 4/4    | Airflow DAG with multiple tasks, data to GCS     |
| Data warehouse      | 4/4    | BQ tables partitioned + clustered (with explanation) |
| Transformations     | 4/4    | dbt models (staging + marts)                     |
| Dashboard           | 4/4    | 2+ tiles in Looker Studio                        |
| Reproducibility     | 4/4    | Makefile + README + Terraform + Docker Compose   |
| **Total**           | **28/28** |                                               |

---

## Extra Mile (Optional, Not Graded)

- [ ] Add dbt tests (unique, not_null, accepted_values on reconciliation_status)
- [ ] Add CI with GitHub Actions (lint + dbt compile)
- [ ] Add `make test` target
- [ ] Parameterize date range so pipeline can run incrementally
