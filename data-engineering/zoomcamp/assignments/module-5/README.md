# Module 5 Homework - Data Platforms with Bruin

## Assignment Overview

Build a complete data pipeline with Bruin, from ingestion to reporting, using NYC taxi data and DuckDB.

## How to Complete

### 1. Install Bruin CLI

```bash
curl -LsSf https://getbruin.com/install/cli | sh
```

### 2. Initialize the zoomcamp template

```bash
bruin init zoomcamp my-pipeline
```

### 3. Configure your `.bruin.yml` with a DuckDB connection

### 4. Follow the tutorial in the [main module README](../../../05-data-platforms/)

After completing the setup, you should have a working NYC taxi data pipeline.

---

## Quiz Answers

### Question 1
**In a Bruin project, what are the required files/directories?**

**Answer: `.bruin.yml` and `pipeline.yml` (assets can be anywhere)**

> A Bruin project needs a `.bruin.yml` (project-level config with connections) and each pipeline needs a `pipeline.yml`. Assets can live anywhere inside the pipeline folder — they don't have to be in an `assets/` directory specifically.

---

### Question 2
**You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which materialization strategy should you use for the staging layer that deduplicates and cleans the data?**

**Answer: `time_interval` - incremental based on a time column**

> The `time_interval` strategy is designed for incrementally loading time-based data. It deletes existing records within the specified time interval and inserts new ones, which handles deduplication within each time window.

---

### Question 3
**You have an array variable `taxi_types` defined in `pipeline.yml` with default `["yellow", "green"]`. How do you override this when running the pipeline to only process yellow taxis?**

**Answer: `bruin run --var 'taxi_types=["yellow"]'`**

> Variables are overridden with `--var`. Since `taxi_types` is an array type, you need to pass it as a JSON array string.

---

### Question 4
**You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?**

**Answer: `bruin run ingestion/trips.py --downstream`**

> The `--downstream` flag runs the specified asset plus all assets that depend on it.

---

### Question 5
**You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?**

**Answer: `not_null: true`**

> The `not_null` check verifies that none of the values of the checked column are null. The syntax in the asset definition uses `checks: - name: not_null`.

---

### Question 6
**After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?**

**Answer: `bruin lineage`**

> The `bruin lineage` command shows upstream and downstream dependencies for assets, visualizing the dependency graph.
```bash
$ bruin lineage zoomcamp/pipeline/assets/staging/trips.sql

Lineage: 'staging.trips'

Upstream Dependencies
========================
- ingestion.trips (assets/ingestion/trips.py)
- ingestion.payment_lookup (assets/ingestion/payment_lookup.asset.yml)

Total: 2


Downstream Dependencies
========================
- reports.trips_report (assets/reports/trips_report.sql)

Total: 1
```

---

### Question 7
**You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?**

**Answer: `--full-refresh`**

> The `--full-refresh` flag truncates tables before running and ensures a clean state by dropping and recreating tables.

---