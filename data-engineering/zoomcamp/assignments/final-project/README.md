# E-Commerce Order Reconciliation Pipeline

## Problem Description

An e-commerce store (Google Merchandise Store) tracks purchases through two independent systems:

- **GA4 (Google Analytics 4)** — client-side analytics tracking purchase events
- **Internal order database** — server-side record of completed orders

These systems inevitably diverge. This pipeline reconciles both sources daily and surfaces discrepancies:

| Discrepancy | Meaning |
|---|---|
| **Ghost order** | GA4 recorded a purchase but no matching order exists in the DB (JS error, payment failed after tracking) |
| **Missing in GA4** | Order exists in the DB but GA4 never recorded it (ad blocker, consent denial, tag misconfiguration) |
| **Revenue mismatch** | Both systems have the order but amounts differ (post-purchase adjustments, currency rounding) |

The pipeline produces a daily reconciliation fact table and a dashboard showing match rates and revenue gaps over time.

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

Orchestration: Apache Airflow (Docker Compose)
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
- [Terraform](https://developer.hashicorp.com/terraform/install) installed
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Python 3.11+
- GCP service account key with BigQuery Admin + Storage Admin roles

## How to Run

### 1. Provision infrastructure

```bash
# Set your GCP project and credentials in terraform/variables.tf, then:
make infra
```

### 2. Start Airflow

```bash
make airflow-up
# Airflow UI available at http://localhost:8080 (admin / admin)
```

### 3. Trigger the pipeline

Either via the Airflow UI or:

```bash
make run-all
```

This runs the full DAG:
1. Generate fake orders from GA4 data
2. Upload raw parquet to GCS
3. Spark: clean and standardize both sources
4. Create BigQuery external tables
5. dbt: build staging views and fact tables
6. dbt: run tests

### 4. View the dashboard

Open the Looker Studio dashboard (link + screenshots below).

### 5. Tear down

```bash
make airflow-down
make destroy
```

## Dashboard

<!-- TODO: Add Looker Studio link and screenshots -->

## What I'd Improve With More Time

- Parameterize date range for incremental processing
- Add CI with GitHub Actions (lint + dbt compile)
- Deploy Spark jobs to Dataproc instead of local execution
- Add data quality checks with Great Expectations
- Set up alerting on reconciliation anomalies
