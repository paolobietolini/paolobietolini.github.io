# E-Commerce Order Reconciliation Pipeline

## Problem Description

An e-commerce store (Google Merchandise Store) tracks purchases through two independent systems:

- **GA4 (Google Analytics 4)** — client-side analytics tracking purchase events
- **Internal order database** — server-side record of completed orders

These systems inevitably diverge. Without reconciliation, the business has no visibility into how much revenue is being lost to tracking gaps or how reliable its analytics data actually is. Marketing teams make budget decisions based on GA4 attribution data — if 10-15% of conversions are never tracked, those campaigns appear to underperform and get underfunded.

This pipeline reconciles both sources daily and surfaces discrepancies:

| Discrepancy | Meaning | Business Impact |
|---|---|---|
| **Ghost order** | GA4 recorded a purchase but no matching order exists in the DB (JS error, payment failed after tracking) | Inflates reported revenue, distorts conversion metrics |
| **Missing in GA4** | Order exists in the DB but GA4 never recorded it (ad blocker, consent denial, tag misconfiguration) | Under-reports campaign performance, leads to misallocated ad spend |
| **Revenue mismatch** | Both systems have the order but amounts differ (post-purchase adjustments, currency rounding) | Creates discrepancies between finance and marketing reporting |

The pipeline produces a daily reconciliation fact table and a dashboard showing match rates and revenue gaps over time, enabling data and marketing teams to quantify tracking quality and prioritize fixes.

## Architecture

```
┌─────────────┐     ┌──────────────────┐
│ Fake Orders │     │  GA4 Public      │
│ (generated) │     │  Dataset (BQ)    │
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
│        Spark (local / Dataproc)      │
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
│    Looker Studio (Dashboard)         │
│  - Match rate over time              │
│  - Discrepancy breakdown             │
└──────────────────────────────────────┘

Orchestration: Apache Airflow (Docker Compose) or make run-local
IaC: Terraform
```

## Tech Stack

| Layer | Tool |
|---|---|
| Cloud | GCP |
| IaC | Terraform |
| Data Lake | Google Cloud Storage |
| Data Warehouse | BigQuery |
| Batch Processing | PySpark (local / Dataproc) |
| Transformations | dbt-core + dbt-bigquery |
| Orchestration | Apache Airflow (Docker Compose) |
| Dashboard | Looker Studio |
| Containerization | Docker / Docker Compose |

## Data Sources

**GA4 Public Dataset** — `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` (Nov 2020 – Jan 2021). Purchase events with `transaction_id`, `purchase_revenue`, and item details.

**Fake Orders** — generated Python script that creates orders with controlled discrepancies: ~80% matched, ~5% revenue mismatch, ~5% ghost (GA4-only), ~10% DB-only.

## BigQuery Optimization

- `fct_reconciliation` is **partitioned by `report_date`** (daily granularity) — queries filtering by date scan only relevant partitions, reducing cost and improving performance.
- **Clustered by `reconciliation_status`** — queries filtering or grouping by status (e.g. dashboard tiles) benefit from co-located storage.

## Prerequisites

- GCP account with billing enabled
- GCP service account with **BigQuery Admin** and **Storage Admin** roles
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- Python 3.11+
- Java 11+ (for PySpark)
- (Optional) [Docker](https://docs.docker.com/get-docker/) — only needed if running via Airflow

> **Tip**: [GCP Cloud Shell](https://shell.cloud.google.com) has all of the above pre-installed except dbt/pyspark, which `make setup` handles.

## How to Run

### 0. Clone the repository

```bash
git clone --filter=blob:none --sparse https://github.com/paolobietolini/paolobietolini.github.io.git
cd paolobietolini.github.io
git sparse-checkout set data-engineering/zoomcamp/assignments/final-project
cd data-engineering/zoomcamp/assignments/final-project
```

### 1. Configure credentials

```bash
# Set the path to your GCP service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Copy and edit Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your project ID and credentials path

# Copy and edit dbt profile
cp dbt/profiles.yml.example dbt/profiles.yml
# Edit dbt/profiles.yml with your keyfile path if different
```

### 2. Install dependencies

```bash
make setup
```

### 3. Provision infrastructure

```bash
make infra
```

Verify: `terraform -chdir=terraform output` should show your bucket name and dataset ID.

### 4. Run the full pipeline

**Option A — Without Docker (recommended for Cloud Shell):**

```bash
make run-local
```

This runs all steps sequentially:
1. Generate fake orders from GA4 data
2. Upload raw parquet to GCS
3. Spark: clean and standardize both sources
4. Create BigQuery external tables
5. dbt: build staging views and fact tables
6. dbt: run tests

**Option B — With Airflow (requires Docker):**

```bash
make airflow-up
# Airflow UI: http://localhost:8080 (admin / admin)
make run-all
```

### 5. View the dashboard

Open the Looker Studio dashboard (link + screenshots below).

### 6. Tear down

```bash
# If using Airflow:
make airflow-down

# Destroy GCP resources
make destroy
```

### Available Makefile targets

```
make help          # Show all targets
make setup         # Install Python dependencies
make infra         # Provision GCP resources with Terraform
make generate      # Generate fake order data
make upload        # Upload parquet files to GCS
make spark-clean   # Run Spark cleaning jobs
make create-tables # Create BigQuery external tables
make dbt-run       # Run dbt models
make dbt-test      # Run dbt tests
make run-local     # Run full pipeline (no Docker)
make destroy       # Tear down GCP resources
```

## Dashboard

<!-- TODO: Add Looker Studio link and screenshots -->

## What I'd Improve With More Time

- Parameterize date range for incremental processing
- Deploy Spark jobs to Dataproc instead of local execution
- Add data quality checks with Great Expectations
- Set up alerting on reconciliation anomalies
