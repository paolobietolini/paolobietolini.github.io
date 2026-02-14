---
layout: default
title: "Analytics Engineering & dbt"
permalink: /data-engineering/zoomcamp/analytics-engineering
---

## Table of Contents

- [Analytics Engineering](#analytics-engineering)
  - [The Data Team Roles](#the-data-team-roles)
  - [Tooling](#tooling)
- [Data Modelling Concepts](#data-modelling-concepts)
  - [ETL vs ELT](#etl-vs-elt)
  - [Dimensional Modelling (Kimball)](#dimensional-modelling-kimball)
- [What is dbt?](#what-is-dbt)
  - [How dbt Works](#how-dbt-works)
  - [dbt Core vs dbt Cloud](#dbt-core-vs-dbt-cloud)
- [dbt Project Structure](#dbt-project-structure)
  - [Models](#models)
  - [Sources](#sources)
  - [Seeds](#seeds)
  - [Macros](#macros)
  - [Packages](#packages)
  - [Tests](#tests)
  - [Documentation](#documentation)
- [Building a dbt Project](#building-a-dbt-project)
  - [Materialisation Strategies](#materialisation-strategies)
  - [The Staging Layer](#the-staging-layer)
  - [The Core Layer](#the-core-layer)
  - [Variables](#variables)
- [dbt Commands](#dbt-commands)
- [Deployment](#deployment)
  - [Development vs Production](#development-vs-production)
  - [CI/CD with dbt](#cicd-with-dbt)
- [SQL Refresher](#sql-refresher)
  - [Window Functions](#window-functions)
  - [Common Table Expressions (CTEs)](#common-table-expressions-ctes)
- [Resources](#resources)

---

# Analytics Engineering

Analytics engineering sits at the intersection of data engineering and data analytics. It emerged because modern data tools (cloud warehouses, self-service BI, ELT pipelines) created a gap between the people who load data and the people who analyse it.

## The Data Team Roles

| Role | Focus |
|------|-------|
| **Data Engineer** | Prepares and maintains the data infrastructure. Builds pipelines (ingestion, orchestration), manages warehouses, ensures data availability. Strong software engineering skills |
| **Data Analyst** | Uses data to answer business questions. Builds dashboards, reports, ad-hoc queries. Strong SQL and BI tool skills, limited programming |
| **Analytics Engineer** | Bridges the gap. Introduces software engineering practices (version control, CI/CD, testing, documentation) to the data transformation layer. Takes raw data and builds clean, tested, documented datasets that analysts can trust |

The analytics engineer owns the **transformation layer** — the T in ELT. They write the SQL that turns raw loaded data into analytical models.

## Tooling

The analytics engineering workflow typically involves:

- **Data loading**: Fivetran, Airbyte, Stitch (managed EL tools)
- **Data storing**: BigQuery, Snowflake, Redshift (cloud warehouses)
- **Data transforming**: dbt, Dataform (SQL-based transformation frameworks)
- **Data visualisation**: Looker, Tableau, Power BI, Metabase

---

# Data Modelling Concepts

## ETL vs ELT

| | ETL | ELT |
|---|-----|-----|
| **Stands for** | Extract, Transform, Load | Extract, Load, Transform |
| **When transforms happen** | Before loading into the warehouse | After loading into the warehouse |
| **Compute** | Transformations run on a separate processing system | Transformations run inside the warehouse itself |
| **Schema approach** | Schema-on-write (define schema before loading) | Schema-on-read (store raw, define structure at query time) |
| **Cost** | Higher upfront compute costs | Higher storage costs (raw data stored first) |
| **Flexibility** | Less flexible — changes require rebuilding the pipeline | More flexible — raw data is always available to re-transform |

Modern cloud warehouses (BigQuery, Snowflake) are cheap to store data in and powerful enough to run transformations at scale, making ELT the dominant approach today. dbt is an ELT tool — it assumes the data is already loaded and focuses entirely on the T.

## Dimensional Modelling (Kimball)

**Ralph Kimball's dimensional modelling** is the most widely used approach for structuring analytical data. The goal is to make data easy to understand and fast to query for business users.

**Core principles:**
- Prioritise **user understandability** and **query performance** over strict normalisation
- Trade storage efficiency for simpler, faster queries
- Structure data around business processes

**Two types of tables:**

- **Fact tables**: Record business events (measurements, metrics). Each row is an event — a sale, a trip, a click. Contains foreign keys to dimension tables and numeric measures (amount, quantity, duration). Tall and narrow.
- **Dimension tables**: Describe the context of events (the who, what, where, when). Each row is an entity — a customer, a product, a location. Contains descriptive attributes. Short and wide.

```
  Fact Table: trips                Dimension: zones
 ┌────────────────────────┐      ┌─────────────────────────┐
 │ trip_id                │      │ location_id             │
 │ pickup_location_id  ───┼─────>│ borough                 │
 │ dropoff_location_id ───┼─────>│ zone_name               │
 │ pickup_datetime        │      │ service_zone            │
 │ fare_amount            │      └─────────────────────────┘
 │ trip_distance          │
 └────────────────────────┘       Dimension: vendors
                          │      ┌─────────────────────────┐
                          └─────>│ vendor_id               │
                                 │ vendor_name             │
                                 └─────────────────────────┘
```

**Other approaches:**
- **Bill Inmon** advocates a more normalised, enterprise-wide data warehouse (3NF) with data marts derived from it. More engineering effort, but eliminates redundancy.
- **Data Vault** (Dan Linstedt) uses hubs, links, and satellites for maximum flexibility and auditability. Common in highly regulated industries.

---

# What is dbt?

**dbt (data build tool)** is a transformation framework that lets you write SQL `SELECT` statements and turns them into tables and views in your warehouse. It brings software engineering best practices to SQL-based data transformation.

You write models (SQL files), and dbt handles:
- Compiling the SQL (resolving references, injecting macros)
- Determining execution order from dependencies (building a DAG)
- Running the SQL against your warehouse
- Testing the results
- Generating documentation

## How dbt Works

```
                    dbt
 ┌─────────────────────────────────────┐
 │                                     │
 │  .sql model files                   │
 │       │                             │
 │       v                             │
 │  Compile (resolve refs, macros)     │
 │       │                             │
 │       v                             │
 │  Build DAG (dependency order)       │
 │       │                             │
 │       v                             │
 │  Execute SQL against warehouse  ────┼──> BigQuery / Snowflake / DuckDB
 │       │                             │
 │       v                             │
 │  Test & Document                    │
 │                                     │
 └─────────────────────────────────────┘
```

dbt does **not** extract or load data. It only transforms data that is already in your warehouse. The modelling layer sits between raw loaded data and the final tables that analysts query.

## dbt Core vs dbt Cloud

| | dbt Core | dbt Cloud |
|---|---------|-----------|
| **What it is** | Open-source CLI tool | Managed SaaS platform built on dbt Core |
| **Interface** | Command line | Web-based IDE + CLI |
| **Execution** | Runs locally or on your own infrastructure | Runs on dbt Labs' infrastructure |
| **Scheduling** | You manage scheduling (cron, Airflow, etc.) | Built-in job scheduler |
| **Cost** | Free | Free tier available, paid plans for teams |
| **Version control** | You set up Git integration | Built-in Git integration |
| **Documentation** | `dbt docs generate` + self-host | Hosted documentation site |

For this course, both options work. The local setup uses **dbt Core + DuckDB** (free, no cloud needed). The cloud setup uses **dbt Cloud + BigQuery**.

---

# dbt Project Structure

A typical dbt project looks like this:

```
my_dbt_project/
├── dbt_project.yml          # Project configuration
├── models/
│   ├── staging/             # Staging models (1:1 with sources)
│   │   ├── schema.yml       # Source definitions + tests
│   │   ├── stg_green_tripdata.sql
│   │   └── stg_yellow_tripdata.sql
│   └── core/                # Core business models
│       ├── schema.yml
│       ├── dim_zones.sql
│       └── fact_trips.sql
├── macros/                  # Reusable SQL snippets (Jinja)
│   └── get_payment_type_description.sql
├── seeds/                   # Static CSV data
│   └── taxi_zone_lookup.csv
├── tests/                   # Custom data tests
├── packages.yml             # External package dependencies
└── profiles.yml             # Connection configuration (dbt Core only)
```

## Models

Models are the core of dbt. Each model is a `.sql` file containing a single `SELECT` statement. dbt compiles and runs these statements to create tables or views in your warehouse.

```sql
-- models/staging/stg_green_tripdata.sql
SELECT
    vendorid,
    lpep_pickup_datetime as pickup_datetime,
    lpep_dropoff_datetime as dropoff_datetime,
    passenger_count,
    trip_distance,
    payment_type,
    fare_amount,
    total_amount
FROM {{ source('staging', 'green_tripdata') }}
```

The `{{ source() }}` function references a declared data source (defined in a YAML file). The `{{ ref() }}` function references another dbt model, which tells dbt about the dependency so it can build the DAG.

**Key principle:** Models only contain `SELECT` statements. You never write `CREATE TABLE` or `INSERT INTO` — dbt generates that DDL/DML based on the materialisation strategy.

## Sources

Sources represent the raw data already loaded into your warehouse. You define them in YAML files:

```yaml
# models/staging/schema.yml
sources:
  - name: staging
    database: my_project       # BigQuery project / DuckDB database
    schema: trips_data_all     # Dataset / schema name
    tables:
      - name: green_tripdata
      - name: yellow_tripdata
```

Benefits of defining sources:
- **Abstraction**: If the source table name or location changes, you update it in one place
- **Documentation**: Sources appear in the generated docs and DAG
- **Freshness checks**: dbt can verify that source data is up-to-date (`dbt source freshness`)

## Seeds

Seeds are small CSV files that dbt loads into your warehouse as tables. Use them for static reference data that rarely changes:

```csv
-- seeds/taxi_zone_lookup.csv
locationid,borough,zone,service_zone
1,EWR,Newark Airport,EWR
2,Queens,Jamaica Bay,Boro Zone
3,Bronx,Allerton/Pelham Gardens,Boro Zone
```

Run `dbt seed` to load them. They are version-controlled alongside your models. Do not use seeds for large or frequently changing data — use proper data loading tools for that.

## Macros

Macros are reusable snippets written in **Jinja** (a Python templating language). They work like functions in programming — they accept arguments and return SQL.

```sql
-- macros/get_payment_type_description.sql
{% macro get_payment_type_description(payment_type) %}
    CASE {{ payment_type }}
        WHEN 1 THEN 'Credit card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided trip'
        ELSE 'EMPTY'
    END
{% endmacro %}
```

Use it in a model:

```sql
SELECT
    payment_type,
    {{ get_payment_type_description('payment_type') }} as payment_type_description
FROM {{ source('staging', 'green_tripdata') }}
```

dbt also includes built-in macros and you can install third-party macros via packages.

## Packages

Packages are reusable dbt projects that you can import. They provide macros, models, and tests written by the community.

```yaml
-- packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: dbt-labs/codegen
    version: 0.12.1
```

Run `dbt deps` to install them. Popular packages:
- **dbt_utils**: Generic tests, SQL helpers, cross-database macros
- **codegen**: Auto-generates model and source YAML from your warehouse schema

## Tests

dbt tests are assertions about your data. There are two types:

**Generic tests** (declared in YAML):

```yaml
# models/staging/schema.yml
models:
  - name: stg_green_tripdata
    columns:
      - name: tripid
        tests:
          - unique
          - not_null
      - name: payment_type
        tests:
          - accepted_values:
              values: [1, 2, 3, 4, 5, 6]
```

Built-in generic tests:
- `unique`: No duplicate values
- `not_null`: No null values
- `accepted_values`: Only specified values exist
- `relationships`: Foreign key integrity (values exist in another model)

**Singular tests** (custom SQL in the `tests/` directory):

```sql
-- tests/assert_positive_fare.sql
SELECT *
FROM {{ ref('fact_trips') }}
WHERE fare_amount < 0
```

A test passes if the query returns **zero rows**. Any rows returned are failures.

Run tests with `dbt test`.

## Documentation

dbt can auto-generate a documentation website from your project:

```yaml
# models/staging/schema.yml
models:
  - name: stg_green_tripdata
    description: "Cleaned and standardised green taxi trip data"
    columns:
      - name: tripid
        description: "Unique trip identifier (surrogate key)"
      - name: pickup_datetime
        description: "Timestamp when the meter was engaged"
```

Generate and serve docs:

```bash
dbt docs generate
dbt docs serve     # Opens a local web server with the documentation site
```

The docs site includes:
- Model descriptions and column-level documentation
- The full DAG (lineage graph) showing how models depend on each other
- Source definitions and freshness information

---

# Building a dbt Project

## Materialisation Strategies

Materialisation controls **how** dbt persists a model in the warehouse:

| Strategy | What it creates | When to use |
|----------|----------------|-------------|
| **View** | A SQL view (`CREATE VIEW`) | Lightweight models, not queried directly by end users. Default materialisation |
| **Table** | A physical table (`CREATE TABLE`) | Models queried frequently by BI tools or analysts. Faster reads, more storage |
| **Incremental** | Appends/merges new rows to an existing table | Large datasets where rebuilding the full table is too expensive. Only processes new or changed data |
| **Ephemeral** | Nothing — inlined as a CTE | Intermediate logic you don't want to persist. Used only as a dependency by other models |

Set materialisation in the model file or in `dbt_project.yml`:

```sql
-- In the model file
{{ config(materialized='table') }}

SELECT ...
```

```yaml
# In dbt_project.yml (applies to all models in the path)
models:
  my_project:
    staging:
      materialized: view
    core:
      materialized: table
```

## The Staging Layer

Staging models sit between raw sources and business logic. They:

- Map **1:1** with source tables (one staging model per source table)
- Perform light transformations: renaming columns, casting types, basic filtering
- Are materialised as **views** (they're lightweight wrappers)
- Use the naming convention `stg_<source>_<table>`

```sql
-- models/staging/stg_green_tripdata.sql
{{ config(materialized='view') }}

SELECT
    -- identifiers
    {{ dbt_utils.generate_surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as tripid,
    CAST(vendorid AS INTEGER) as vendorid,
    CAST(ratecodeid AS INTEGER) as ratecodeid,
    CAST(pulocationid AS INTEGER) as pickup_locationid,
    CAST(dolocationid AS INTEGER) as dropoff_locationid,

    -- timestamps
    CAST(lpep_pickup_datetime AS TIMESTAMP) as pickup_datetime,
    CAST(lpep_dropoff_datetime AS TIMESTAMP) as dropoff_datetime,

    -- trip info
    passenger_count,
    trip_distance,
    trip_type,

    -- payment
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    CAST(payment_type AS INTEGER) as payment_type,
    {{ get_payment_type_description('payment_type') }} as payment_type_description

FROM {{ source('staging', 'green_tripdata') }}
WHERE vendorid IS NOT NULL
```

## The Core Layer

Core models contain the actual business logic and produce the final tables that analysts query. They reference staging models (and other core models) using `{{ ref() }}`.

```sql
-- models/core/fact_trips.sql
{{ config(materialized='table') }}

WITH green_data AS (
    SELECT *, 'Green' as service_type
    FROM {{ ref('stg_green_tripdata') }}
),
yellow_data AS (
    SELECT *, 'Yellow' as service_type
    FROM {{ ref('stg_yellow_tripdata') }}
),
trips_unioned AS (
    SELECT * FROM green_data
    UNION ALL
    SELECT * FROM yellow_data
)
SELECT
    t.tripid,
    t.vendorid,
    t.service_type,
    t.pickup_locationid,
    t.dropoff_locationid,
    t.pickup_datetime,
    t.dropoff_datetime,
    t.passenger_count,
    t.trip_distance,
    t.fare_amount,
    t.total_amount,
    t.payment_type_description,
    z_pickup.borough as pickup_borough,
    z_pickup.zone as pickup_zone,
    z_dropoff.borough as dropoff_borough,
    z_dropoff.zone as dropoff_zone
FROM trips_unioned t
INNER JOIN {{ ref('dim_zones') }} z_pickup
    ON t.pickup_locationid = z_pickup.locationid
INNER JOIN {{ ref('dim_zones') }} z_dropoff
    ON t.dropoff_locationid = z_dropoff.locationid
```

## Variables

Variables let you parameterise your dbt project. Define defaults in `dbt_project.yml` and override them at runtime:

```yaml
# dbt_project.yml
vars:
  is_test_run: true
```

Use in models:

```sql
{% if var('is_test_run', default=true) %}
    LIMIT 100
{% endif %}
```

Override at runtime:

```bash
dbt build --vars '{"is_test_run": false}'
```

This is useful for running quick test builds during development (with a row limit) and full builds in production.

---

# dbt Commands

| Command | Description |
|---------|-------------|
| `dbt init` | Initialise a new dbt project |
| `dbt deps` | Install packages from `packages.yml` |
| `dbt seed` | Load CSV seed files into the warehouse |
| `dbt run` | Execute all models |
| `dbt test` | Run all tests |
| `dbt build` | Run models, tests, seeds, and snapshots in DAG order |
| `dbt compile` | Compile models to SQL without executing |
| `dbt docs generate` | Generate documentation |
| `dbt docs serve` | Serve documentation locally |
| `dbt source freshness` | Check source data freshness |
| `dbt run --select model_name` | Run a specific model |
| `dbt run --select +model_name` | Run a model and all its upstream dependencies |
| `dbt run --select model_name+` | Run a model and all its downstream dependents |

---

# Deployment

## Development vs Production

dbt projects typically have two environments:

| | Development | Production |
|---|-------------|------------|
| **Who runs it** | Individual data engineers / analytics engineers | Automated scheduler (dbt Cloud, Airflow, cron) |
| **Frequency** | On-demand, during development | Scheduled (e.g., daily, hourly) |
| **Target schema** | Personal dev schema (e.g., `dbt_paolo`) | Production schema (e.g., `production`) |
| **Data** | Often a subset (using `LIMIT` via variables) | Full dataset |
| **Branch** | Feature branches | Main branch |

In dbt Cloud, you configure a **production environment** that runs on a schedule against the main branch. Development happens in the IDE against a personal schema so you don't break production models while iterating.

## CI/CD with dbt

dbt Cloud supports **Continuous Integration** by running builds on pull requests:

1. Developer opens a PR with model changes
2. dbt Cloud automatically triggers a build of the changed models (and downstream dependents) into a temporary schema
3. All tests run against the temporary schema
4. If tests pass, the PR can be merged
5. Merging to main triggers the production build

This ensures that model changes are tested before they affect production data.

---

# SQL Refresher

## Window Functions

Window functions perform calculations across a set of rows related to the current row, without collapsing rows like aggregate functions do.

**Syntax:**
```sql
FUNCTION() OVER (PARTITION BY column ORDER BY column)
```

- `PARTITION BY`: Divides rows into groups (optional)
- `ORDER BY`: Defines the order of rows within each partition

### ROW_NUMBER, RANK, DENSE_RANK

These functions assign a ranking to each row:

```sql
SELECT
    total_amount,
    ROW_NUMBER() OVER (ORDER BY total_amount DESC) as row_num,
    RANK()       OVER (ORDER BY total_amount DESC) as rank,
    DENSE_RANK() OVER (ORDER BY total_amount DESC) as dense_rank
FROM green_tripdata
```

How they differ with ties (e.g., two rows tied for 2nd place):

| Function | Result |
|----------|--------|
| `ROW_NUMBER()` | 1, 2, 3, 4 (always unique, arbitrary tiebreak) |
| `RANK()` | 1, 2, 2, 4 (ties get same rank, next rank skipped) |
| `DENSE_RANK()` | 1, 2, 2, 3 (ties get same rank, no gap) |

### LAG and LEAD

Retrieve values from previous or subsequent rows without a self-join:

```sql
SELECT
    lpep_pickup_datetime,
    total_amount,
    LAG(total_amount)  OVER (ORDER BY lpep_pickup_datetime) as prev_amount,
    LEAD(total_amount) OVER (ORDER BY lpep_pickup_datetime) as next_amount
FROM green_tripdata
```

### PERCENTILE_CONT

Computes a percentile value with linear interpolation:

```sql
SELECT
    PULocationID,
    total_amount,
    PERCENTILE_CONT(total_amount, 0.9) OVER (PARTITION BY PULocationID) as p90
FROM green_tripdata
```

This returns the 90th percentile of `total_amount` for each pickup location.

## Common Table Expressions (CTEs)

CTEs create temporary named result sets using `WITH`. They make complex queries more readable and reusable:

```sql
WITH ranked_trips AS (
    SELECT
        lpep_pickup_datetime,
        total_amount,
        RANK() OVER (ORDER BY total_amount DESC) as rank
    FROM green_tripdata
)
SELECT *
FROM ranked_trips
WHERE rank = 2
```

CTEs are heavily used in dbt models to break down transformations into logical steps:

```sql
WITH trip_duration AS (
    SELECT *,
        TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) as duration_seconds
    FROM {{ source('staging', 'fhv_trips') }}
),
with_percentiles AS (
    SELECT
        PULocationID,
        duration_seconds,
        PERCENTILE_CONT(duration_seconds, 0.90) OVER (PARTITION BY PULocationID) as p90
    FROM trip_duration
)
SELECT * FROM with_percentiles
```

**Note:** In BigQuery, CTEs are inlined at execution time — they are not cached. If a CTE is referenced multiple times, it executes multiple times. For reusable intermediate results, materialise them as separate dbt models instead.

---

# Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Fundamentals Course](https://learn.getdbt.com/courses/dbt-fundamentals)
- [dbt Discord Community](https://www.getdbt.com/community/join-the-community)
- [Kimball Group - Dimensional Modelling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Course GitHub - Module 4](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering)
- [SQL Refresher - Window Functions & CTEs](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/refreshers/SQL.md)
