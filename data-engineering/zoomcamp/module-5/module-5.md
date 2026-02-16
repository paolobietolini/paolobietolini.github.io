---
layout: default
title: "Data Platforms with Bruin"
permalink: /data-engineering/zoomcamp/data-platforms
---
{% raw %}

## Table of Contents

- [What is a Data Platform?](#what-is-a-data-platform)
  - [The Modern Data Stack](#the-modern-data-stack)
  - [Where Bruin Fits In](#where-bruin-fits-in)
- [Bruin Core Concepts](#bruin-core-concepts)
  - [Assets](#assets)
  - [Pipelines](#pipelines)
  - [Environments and Connections](#environments-and-connections)
- [Project Structure](#project-structure)
  - [`.bruin.yml`](#bruinyml)
  - [`pipeline.yml`](#pipelineyml)
  - [Asset Files](#asset-files)
- [Asset Types](#asset-types)
  - [Python Assets](#python-assets)
  - [SQL Assets](#sql-assets)
  - [Seed Assets](#seed-assets)
- [Materialization Strategies](#materialization-strategies)
- [Pipeline Variables](#pipeline-variables)
- [Data Quality Checks](#data-quality-checks)
  - [Column Checks](#column-checks)
  - [Custom Checks](#custom-checks)
- [Building an ELT Pipeline](#building-an-elt-pipeline)
  - [Ingestion Layer](#ingestion-layer)
  - [Staging Layer](#staging-layer)
  - [Reports Layer](#reports-layer)
- [Bruin Commands](#bruin-commands)
- [Deployment](#deployment)
  - [Local to Cloud (BigQuery)](#local-to-cloud-bigquery)
  - [Bruin Cloud](#bruin-cloud)
- [Resources](#resources)

---

# What is a Data Platform?

A data platform is the full stack of tools and infrastructure that moves data from sources into a warehouse, transforms it into analytical models, and ensures its quality. Traditionally, each concern (ingestion, transformation, orchestration, quality) required a separate tool — Airbyte for extraction, Airflow for orchestration, dbt for transformation, Great Expectations for quality. A unified data platform collapses these into a single workflow.

## The Modern Data Stack

| Component | Purpose | Typical Tools |
|-----------|---------|---------------|
| **Ingestion** | Extract data from sources into your warehouse | Airbyte, Fivetran, Stitch |
| **Transformation** | Clean, model, aggregate data (the T in ELT) | dbt, Dataform |
| **Orchestration** | Schedule runs, manage dependencies, retries | Airflow, Dagster, Prefect |
| **Quality** | Validate data, run checks, alert on failures | Great Expectations, Soda |
| **Metadata** | Track lineage, ownership, documentation | DataHub, OpenMetadata |

## Where Bruin Fits In

**Bruin** is an open-source (Apache-licensed) CLI tool that combines ingestion, transformation, orchestration, and quality into a single binary. It replaces the need for separate tools for each concern.

Key characteristics:
- **Multi-language assets**: SQL, Python, and R in the same pipeline
- **Built-in ingestion**: Python assets can fetch data from APIs, files, databases
- **Built-in quality**: Column-level and custom checks run automatically after each asset
- **Dependency resolution**: Assets declare dependencies and Bruin builds a DAG
- **No vendor lock-in**: Runs locally, on VMs, or in CI/CD — everything is version-controlled text files
- **Multi-platform**: Supports DuckDB, BigQuery, Snowflake, Postgres, Redshift, Databricks, and more

```
 Traditional Stack                     Bruin
┌──────────────────┐              ┌──────────────────┐
│ Airbyte          │  ingestion   │                  │
├──────────────────┤              │                  │
│ Airflow          │  orchestrate │   bruin CLI      │
├──────────────────┤              │                  │
│ dbt              │  transform   │   (single tool)  │
├──────────────────┤              │                  │
│ Great Expectations│  quality    │                  │
└──────────────────┘              └──────────────────┘
```

---

# Bruin Core Concepts

## Assets

An **asset** is any data artifact that carries value — a table, a view, a file, an ML model. Assets are the building blocks of a Bruin pipeline. Each asset is a single file (`.sql`, `.py`, or `.asset.yml`) that contains:

- **Metadata** (name, type, connection, materialization, columns, quality checks)
- **Logic** (a SQL query or Python function)

Assets declare their dependencies on other assets. Bruin uses these declarations to build a DAG and execute assets in the correct order.

## Pipelines

A **pipeline** is a group of assets executed together in dependency order. It is defined by a `pipeline.yml` file. All asset files that live in the `assets/` directory next to `pipeline.yml` belong to that pipeline.

A pipeline has:
- A **name** (appears in logs and environment variables)
- A **schedule** (`daily`, `hourly`, `weekly`, `monthly`, or a cron expression)
- A **start date** (earliest date for backfills)
- **Default connections** (so assets don't have to specify them individually)
- **Variables** (parameterise the pipeline, overridable at runtime)

## Environments and Connections

An **environment** is a named set of connection configurations. The same pipeline can run locally against DuckDB and in production against BigQuery — only the environment changes.

A **connection** holds the credentials to authenticate with a data source or destination. Connections are defined in `.bruin.yml` and referenced by name in `pipeline.yml` or individual assets.

```yaml
# .bruin.yml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: ./db/mydata.db
  production:
    connections:
      google_cloud_platform:
        - name: gcp-default
          project_id: my-gcp-project
          use_application_default_credentials: true
```

---

# Project Structure

A Bruin project has two required files: `.bruin.yml` at the project root and `pipeline.yml` inside a pipeline directory. Assets live in an `assets/` folder next to `pipeline.yml`.

```
my-project/
├── .bruin.yml                        # Project-level config (environments, connections)
└── pipeline/
    ├── pipeline.yml                  # Pipeline config (name, schedule, variables)
    └── assets/
        ├── ingestion/
        │   ├── trips.py              # Python asset (data ingestion)
        │   ├── requirements.txt      # Python dependencies
        │   ├── payment_lookup.asset.yml  # Seed asset definition
        │   └── payment_lookup.csv    # Seed data (static CSV)
        ├── staging/
        │   └── trips.sql             # SQL asset (clean, deduplicate, enrich)
        └── reports/
            └── trips_report.sql      # SQL asset (aggregate for analytics)
```

## `.bruin.yml`

The project-level configuration file. Lives at the project root. Defines environments and their connections.

- **Must be gitignored** — it contains credentials and secrets
- `bruin init` auto-adds it to `.gitignore`
- Bruin uses git to detect the project root, so the project must be in a git repository

## `pipeline.yml`

The pipeline configuration file. Defines the pipeline's identity and behaviour.

```yaml
name: nyctrips
schedule: daily
start_date: "2022-01-01"

default_connections:
  duckdb: duckdb-default

variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

Key fields:

| Field | Purpose |
|-------|---------|
| `name` | Pipeline identifier — appears in logs and as `BRUIN_PIPELINE` env var |
| `schedule` | When to run: `daily`, `hourly`, `weekly`, `monthly`, or a cron string |
| `start_date` | Earliest date the pipeline should consider for backfills |
| `default_connections` | Maps platform names to connection names (e.g., `duckdb: duckdb-default`) |
| `variables` | User-defined variables with JSON Schema types and defaults |

## Asset Files

Assets are identified by a metadata block embedded in the file. The format depends on the file type:

- **SQL assets**: Metadata in a `/* @bruin ... @bruin */` comment block at the top
- **Python assets**: Metadata in a `"""@bruin ... @bruin"""` docstring at the top
- **YAML assets** (seeds, ingestr): The entire file is YAML metadata

---

# Asset Types

## Python Assets

Python assets run arbitrary Python code. They're used primarily for data ingestion — fetching data from APIs, files, or databases. A Python asset must define a `materialize()` function that returns a pandas DataFrame.

```python
"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
  - name: fare_amount
    type: float
  - name: taxi_type
    type: string

@bruin"""

import os
import json
import pandas as pd

def materialize():
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]

    # Fetch data, return a DataFrame
    # Bruin inserts the DataFrame into the target table
    return df
```

Key points:
- Python assets receive pipeline context via environment variables: `BRUIN_START_DATE`, `BRUIN_END_DATE`, `BRUIN_VARS`, `BRUIN_PIPELINE`
- Dependencies go in a `requirements.txt` next to the asset
- The returned DataFrame is automatically inserted into the target table using the specified materialization strategy
- Python assets run in an isolated Docker container (specified by the `image` field)

## SQL Assets

SQL assets contain a single query that Bruin wraps with the appropriate DDL/DML based on the materialization strategy. You write `SELECT` — Bruin handles `CREATE TABLE`, `INSERT`, `DELETE`, etc.

```sql
/* @bruin
name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp

columns:
  - name: pickup_datetime
    type: timestamp
    primary_key: true
    checks:
      - name: not_null

@bruin */

SELECT
    t.pickup_datetime,
    t.dropoff_datetime,
    t.fare_amount,
    t.taxi_type,
    p.payment_type_name
FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup p
    ON t.payment_type = p.payment_type_id
WHERE t.pickup_datetime >= '{{ start_datetime }}'
  AND t.pickup_datetime < '{{ end_datetime }}'
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY t.pickup_datetime, t.dropoff_datetime, t.fare_amount
    ORDER BY t.pickup_datetime
) = 1
```

Key points:
- `depends` declares upstream dependencies — Bruin runs those assets first
- `type` specifies the SQL dialect (e.g., `duckdb.sql`, `bq.sql`, `sf.sql`)
- Jinja templates are available: `{{ start_datetime }}`, `{{ end_datetime }}`, `{{ var.my_variable }}`
- The `QUALIFY` clause (DuckDB) filters window function results inline, useful for deduplication

## Seed Assets

Seeds are small, static CSV files loaded into your warehouse as tables. They're defined with a `.asset.yml` file that references the CSV.

```yaml
# payment_lookup.asset.yml
name: ingestion.payment_lookup
type: duckdb.seed
parameters:
  path: payment_lookup.csv
columns:
  - name: payment_type_id
    type: integer
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: payment_type_name
    type: string
    checks:
      - name: not_null
```

Use seeds for reference data that rarely changes (lookup tables, code mappings). Do not use seeds for large or frequently changing data.

---

# Materialization Strategies

Materialization controls how Bruin persists the results of an asset query into a table or view. The `type` is either `table` or `view`, and the `strategy` determines the insert/update behaviour.

| Strategy | What it Does | When to Use |
|----------|-------------|-------------|
| **`create+replace`** | Drops and recreates the table each run | Small tables, full refresh every run (default when no strategy is set) |
| **`append`** | Inserts new rows without touching existing data | Raw ingestion, event logs, immutable data |
| **`delete+insert`** | Deletes rows matching the `incremental_key`, then inserts new rows | Incremental updates keyed on a non-time column |
| **`truncate+insert`** | Truncates the entire table, then inserts | Full refresh without DROP/CREATE (preserves schema/permissions) |
| **`merge`** | Upserts: updates existing rows, inserts new ones (requires `primary_key`) | Dimension tables, slowly changing data |
| **`time_interval`** | Deletes rows within a time window, then inserts | Time-series data with incremental loads |
| **`scd2_by_column`** | Tracks historical changes by detecting column value differences | Slowly Changing Dimensions (Type 2) |
| **`scd2_by_time`** | Tracks historical changes based on a time-based incremental key | SCD2 with reliable source timestamps |
| **`DDL`** | Creates an empty table from column definitions (no query needed) | Schema-only assets, staging tables |

**For an ELT pipeline like the NYC Taxi project:**
- **Ingestion**: `append` — raw data arrives and duplicates are handled downstream
- **Staging**: `time_interval` — re-process specific date ranges without a full refresh
- **Reports**: `time_interval` — same reasoning, keeps consistency across layers

### `time_interval` in Detail

The `time_interval` strategy is the most important for incremental pipelines. It requires:

- `incremental_key`: The column used for time-based filtering
- `time_granularity`: Either `date` or `timestamp`

```yaml
materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp
```

How it works:
1. Begin a transaction
2. Delete existing records where `incremental_key` falls within the run's time window
3. Insert new records from the asset query
4. Commit

The time window is controlled by `--start-date` and `--end-date` flags (defaults to yesterday). In SQL assets, use `{{ start_datetime }}` and `{{ end_datetime }}` to filter your query to the same window.

---

# Pipeline Variables

Variables let you parameterise your pipeline. Define them in `pipeline.yml` using JSON Schema, and override them at runtime with `--var`.

```yaml
# pipeline.yml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

**Accessing variables:**
- In SQL assets: `{{ var.taxi_types }}`
- In Python assets: `json.loads(os.environ["BRUIN_VARS"])["taxi_types"]`

**Overriding at runtime:**

```bash
# Override a string variable
bruin run --var env=prod

# Override an array variable (must be valid JSON)
bruin run --var 'taxi_types=["yellow"]'
```

Variables must always have a `default` so assets can render without `--var`.

---

# Data Quality Checks

Bruin treats quality as a first-class citizen. Checks run automatically after each asset completes. If a check fails, the pipeline reports the failure.

## Column Checks

Column checks are declared in the asset metadata under `columns[].checks`:

```yaml
columns:
  - name: pickup_datetime
    type: timestamp
    checks:
      - name: not_null
  - name: fare_amount
    type: float
    checks:
      - name: non_negative
  - name: payment_type_id
    type: integer
    checks:
      - name: unique
      - name: accepted_values
        value: [0, 1, 2, 3, 4, 5, 6]
```

Available built-in checks:

| Check | What it Validates |
|-------|-------------------|
| `not_null` | No null values in the column |
| `unique` | No duplicate values |
| `positive` | All values greater than zero |
| `non_negative` | All values greater than or equal to zero |
| `negative` | All values less than zero |
| `accepted_values` | Values are in the specified list |
| `pattern` | Values match a regex pattern |
| `min` | All values >= specified minimum |
| `max` | All values <= specified maximum |

## Custom Checks

For business-specific invariants, use `custom_checks` with arbitrary SQL:

```yaml
custom_checks:
  - name: row_count_greater_than_zero
    query: |
      SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END
      FROM staging.trips
    value: 1
```

A custom check passes when the query result matches `value`. This lets you express any invariant that can be written as a SQL query.

---

# Building an ELT Pipeline

A typical Bruin ELT pipeline has three layers, each in its own subdirectory under `assets/`:

```
 Ingestion          Staging              Reports
┌──────────┐      ┌──────────────┐      ┌────────────────┐
│ trips.py │─────>│ trips.sql    │─────>│ trips_report.sql│
│ (append) │      │(time_interval)│     │ (time_interval) │
└──────────┘      └──────────────┘      └────────────────┘
┌──────────────┐        │
│payment_lookup│────────┘
│  (seed CSV)  │
└──────────────┘
```

## Ingestion Layer

The ingestion layer extracts raw data from external sources and loads it into your warehouse with minimal transformation. Design principles:

- Use `append` strategy — never overwrite raw data
- Normalise column names across sources (e.g., `tpep_pickup_datetime` and `lpep_pickup_datetime` both become `pickup_datetime`)
- Add metadata columns like `extracted_at` for debugging and lineage
- Handle duplicates downstream in the staging layer, not here

## Staging Layer

The staging layer cleans, deduplicates, and enriches raw data. Design principles:

- Use `time_interval` strategy for incremental processing
- Declare dependencies on upstream ingestion assets with `depends`
- Filter the query to the run's time window using `{{ start_datetime }}` and `{{ end_datetime }}`
- Deduplicate using `ROW_NUMBER()` with a composite key (since taxi data has no unique ID)
- Join with lookup tables (seeds) to enrich the data
- Add quality checks on key columns (`not_null`, `unique`, etc.)

## Reports Layer

The reports layer aggregates staging data into analytics-ready tables. Design principles:

- Use `time_interval` strategy with a date-granularity incremental key
- Aggregate by business dimensions (date, taxi type, payment type)
- Add quality checks on metrics (`non_negative` for counts and amounts)

---

# Bruin Commands

| Command | Purpose |
|---------|---------|
| `bruin init <template> <folder>` | Initialise a new project from a template |
| `bruin validate <path>` | Check syntax, schemas, and dependencies without running |
| `bruin run <path>` | Execute a pipeline or a single asset |
| `bruin run <path> --downstream` | Run an asset and all downstream dependents |
| `bruin run --full-refresh` | Drop and recreate tables from scratch |
| `bruin run --start-date <date> --end-date <date>` | Set the time window for the run |
| `bruin run --var 'key=value'` | Override a pipeline variable |
| `bruin lineage <path>` | Show upstream and downstream dependencies |
| `bruin query --connection <name> --query "..."` | Execute an ad-hoc SQL query |
| `bruin render <path>` | Show the rendered template output (Jinja resolved) |
| `bruin connections list` | List all configured connections |
| `bruin connections ping <name>` | Test a connection |

**Running the NYC Taxi pipeline:**

```bash
# Validate before running (fast, catches errors early)
bruin validate ./pipeline/pipeline.yml

# First-time run: create tables from scratch with a small date range
bruin run ./pipeline/pipeline.yml \
  --full-refresh \
  --start-date 2022-01-01 \
  --end-date 2022-02-01

# Subsequent incremental runs
bruin run ./pipeline/pipeline.yml \
  --start-date 2022-02-01 \
  --end-date 2022-03-01

# Run a single asset and everything downstream
bruin run ./pipeline/assets/ingestion/trips.py --downstream

# Query results
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM staging.trips"
```

---

# Deployment

## Local to Cloud (BigQuery)

To move from local DuckDB to BigQuery:

1. **Create BigQuery datasets** matching your asset schemas (`ingestion`, `staging`, `reports`)
2. **Add a GCP connection** to `.bruin.yml`:

```yaml
environments:
  production:
    connections:
      google_cloud_platform:
        - name: gcp-default
          project_id: my-gcp-project
          location: US
          use_application_default_credentials: true
```

3. **Update asset types**: `duckdb.sql` to `bq.sql`, `duckdb.seed` to `bq.seed`
4. **Update default connections**: `duckdb: duckdb-default` to `bigquery: gcp-default`
5. **Fix SQL dialect differences**: data types, function names, and quoting may differ between DuckDB and BigQuery

## Bruin Cloud

Bruin Cloud provides managed infrastructure to schedule and run pipelines automatically:

1. Sign up at [getbruin.com](https://getbruin.com) (free tier, no credit card required)
2. Connect your GitHub repository
3. Enable your pipeline and create a run

Bruin Cloud handles scheduling, retries, and monitoring. Your pipeline code stays in Git — the same version-controlled text files you develop locally.

---

# Resources

- [Bruin Documentation](https://getbruin.com/docs/)
- [Bruin GitHub Repository](https://github.com/bruin-data/bruin)
- [Bruin MCP Setup](https://getbruin.com/docs/bruin/getting-started/bruin-mcp)
- [Materialization Strategies](https://getbruin.com/docs/bruin/assets/materialization)
- [Quality Checks Reference](https://getbruin.com/docs/bruin/quality/available_checks)
- [Pipeline Variables](https://getbruin.com/docs/bruin/getting-started/pipeline-variables)
- [Course GitHub - Module 5](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-data-platforms)
{% endraw %}
