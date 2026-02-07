---
layout: default
title: "Data Warehouse & BigQuery"
permalink: /data-engineering/zoomcamp/data-warehouse
---

## Table of Contents

- [OLAP vs OLTP](#olap-vs-oltp)
  - [Star Schema and Snowflake Schema](#star-schema-and-snowflake-schema)
  - [Data Warehouse Architecture](#data-warehouse-architecture)
- [BigQuery](#bigquery)
  - [External Tables](#external-tables)
  - [Partitioning](#partitioning)
    - [Ingestion Time Partitioning](#ingestion-time-partitioning)
    - [Choosing Partition Granularity](#choosing-partition-granularity)
  - [Clustering](#clustering)
    - [Clustering vs Partitioning](#clustering-vs-partitioning)
    - [When to Use Clustering Over Partitioning](#when-to-use-clustering-over-partitioning)
    - [Automatic Reclustering](#automatic-reclustering)
  - [Best Practices](#best-practices)
    - [Cost Reduction](#cost-reduction)
    - [Query Performance](#query-performance)
  - [Internals of BigQuery](#internals-of-bigquery)
- [BigQuery Machine Learning](#bigquery-machine-learning)
  - [ML Workflow in BigQuery](#ml-workflow-in-bigquery)
  - [Creating a Model](#creating-a-model)
  - [Model Evaluation and Prediction](#model-evaluation-and-prediction)
  - [Model Deployment](#model-deployment)
  - [Resources](#resources)

---

# OLAP vs OLTP

There are two fundamental database approaches: **OLAP** and **OLTP**.

| | OLAP | OLTP |
|---|------|------|
| **Stands for** | Online Analytical Processing | Online Transaction Processing |
| **Purpose** | Analysing large data quantities | Processing real-time transactions |
| **Operations** | Optimised for read-only queries | Supports all CRUD operations (read, insert, update, delete) |
| **Query complexity** | Complex aggregations on large datasets | Simple, fast queries on individual records |
| **Users** | Data analysts, business intelligence | End users, applications |
| **Examples** | Data warehouses, reporting systems | Banking systems, e-commerce, CRMs |

OLAP is the foundational approach used in **Data Warehouses**. It is used by companies, universities, or any entity that needs to analyse their data at scale.

OLTP systems handle day-to-day operations. The term "transaction" has a dual meaning: a database transaction (an atomic change of state) and a business transaction (an exchange of economic entities). OLTP systems use the first type to record the second.

## Star Schema and Snowflake Schema

OLAP databases typically use a **star schema** or **snowflake schema** to organise data.

- **Measures** (metrics like `sale_amount`, `quantity`) live in the central **fact table**
- **Dimensions** (descriptive attributes like `time`, `product`, `location`) live in surrounding **dimension tables**

```
                              ┌──────────────────────┐
                              │   Time Dimension     │
                              ├──────────┬───────────┤
                              │ time_id  │ timestamp │
                       ┌─────>│ 1234     │ 2008-09-02│
                       │      └──────────┴───────────┘
  ┌────────────────────┤
  │   Sales Fact Table │      ┌──────────────────────────┐
  ├────────┬───────┬───┤      │   Product Dimension      │
  │ amount │time_id│prod_id   ├──────────┬───────────────┤
  │ 930.10 │ 1234  │ 42 ─────>│ prod_id  │ name          │
  │ 120.50 │ 1235  │ 17 │     │ 42       │ Widget Pro    │
  └────────┴───────┴────┘     └──────────┴───────────────┘
```

In a **star schema**, dimension tables connect directly to the fact table (forming a star shape). In a **snowflake schema**, dimension tables are further normalised into sub-dimensions (e.g., a `location` dimension split into `city`, `country` tables).

## Data Warehouse Architecture

A data warehouse collects data from many sources (OLTP databases, CRMs, flat files, APIs) and consolidates it for analytical queries.

```
  Data Sources          Staging Area         Data Warehouse         Data Marts
 ┌───────────┐        ┌────────────┐       ┌───────────────┐     ┌───────────┐
 │  OLTP DBs │───┐    │            │       │               │  ┌─>│ Marketing │
 ├───────────┤   ├───>│  Cleaning  │──────>│  Integrated   │──┤  ├───────────┤
 │   CRMs    │───┤    │  Validating│       │  Historical   │  ├─>│  Finance  │
 ├───────────┤   │    │  Conforming│       │  Read-Only    │  │  ├───────────┤
 │   Files   │───┘    │            │       │               │  └─>│   Sales   │
 └───────────┘        └────────────┘       └───────────────┘     └───────────┘
                                                                       │
                                                                       v
                                                                   End Users
                                                              (BI tools, reports)
```

- **Staging area**: A temporary holding zone where raw data is cleaned, validated, and conformed before entering the warehouse. It exists to prevent dirty or inconsistent data from polluting the warehouse. Transformations here include deduplication, format standardisation, and data type casting.
- **Data warehouse**: The central, integrated, read-only repository. It does not support arbitrary CRUD operations — data flows in through controlled ETL/ELT processes.
- **Data marts**: Subsets of the warehouse tailored for specific business departments (marketing, finance, sales). They provide a focused view so users don't have to query the entire warehouse.

Some users, such as data scientists, may prefer to consume raw data directly from the warehouse or even the staging area, bypassing data marts.

---

# BigQuery

BigQuery is a **serverless data warehouse** provided by Google Cloud. "Serverless" means the infrastructure (machines, databases, servers) is fully managed — you don't provision or maintain anything.

**Key features:**
- Built-in **Machine Learning**, **Geospatial Analysis**, and **Business Intelligence**
- **Separation of compute and storage**: the query engine scales independently from data storage, meaning the compute doesn't need to grow linearly with the data size
- Pay only for what you query (on-demand pricing) or reserve flat-rate slots

## External Tables

[Documentation](https://docs.cloud.google.com/bigquery/docs/external-tables)

An external table allows you to query data stored **outside** of BigQuery (e.g., in Google Cloud Storage) without loading it into BigQuery's own storage.

**Why use external tables?**
- **Cost efficiency**: Avoids duplicating storage costs — the data stays in GCS
- **Real-time access**: Query the latest data in GCS without running a load job
- **Flexibility**: Useful for ad-hoc queries on data that doesn't need to be permanently stored in BigQuery

**Creating an external table:**
```sql
CREATE OR REPLACE EXTERNAL TABLE my_dataset.my_external_table
OPTIONS (
  format = 'JSON',
  uris = ['gs://my_bucket/my_file.json']
);
```

This avoids defining a schema explicitly — BigQuery infers it from the data.

**Limitations of external tables:**
- BigQuery **cannot estimate** the number of rows or the query cost upfront, since the data lives elsewhere
- Query performance is slower than native tables because data must be read from GCS at query time
- No support for clustering or partitioning on the external data itself

---

## Partitioning

When queries frequently filter on a specific column (e.g., a date), we can **partition** the table on that column. Partitioning physically splits the table into segments based on the partition key, so queries that filter on that key only scan the relevant partitions instead of the entire table.

```
  Unpartitioned Table                  Partitioned by date
 ┌──────────────────────┐          ┌──────────────────────┐
 │ date       │ amount  │          │ 2024-01-01           │
 │ 2024-01-01 │  50.00  │          │  ┌────────┬────────┐ │
 │ 2024-01-02 │  75.00  │          │  │  50.00 │  20.00 │ │
 │ 2024-01-01 │  20.00  │   ──>    │  └────────┴────────┘ │
 │ 2024-01-03 │ 100.00  │          ├──────────────────────┤
 │ 2024-01-02 │  30.00  │          │ 2024-01-02           │
 │ 2024-01-03 │  60.00  │          │  ┌────────┬────────┐ │
 └──────────────────────┘          │  │  75.00 │  30.00 │ │
                                   │  └────────┴────────┘ │
  Query scans ALL rows             ├──────────────────────┤
                                   │ 2024-01-03           │
                                   │  ┌─────────┬───────┐ │
                                   │  │ 100.00  │ 60.00 │ │
                                   │  └─────────┴───────┘ │
                                   └──────────────────────┘

                                   Query for 2024-01-02
                                   scans ONLY that partition
```

**Key constraint:** A table can have a maximum of **4,000 partitions**.

You can partition by:
- **Time-unit column** (DATE, TIMESTAMP, DATETIME)
- **Ingestion time** (when the data was loaded)
- **Integer range** (e.g., customer ID ranges)

### Ingestion Time Partitioning

When you create a table partitioned by **ingestion time**, BigQuery automatically assigns rows to partitions based on **when BigQuery ingested the data**, not based on any column value in the data itself.

This is useful when:
- Your data doesn't have a reliable timestamp column
- You want to track *when data arrived* rather than when events occurred
- You're loading data in regular batches and want automatic time-based organisation

BigQuery creates a pseudocolumn called `_PARTITIONTIME` that stores the ingestion time, truncated to the partition boundary. For example, with hourly partitioning, data ingested at `14:23` gets a `_PARTITIONTIME` of `14:00`.

You can query it like a regular column:
```sql
SELECT *
FROM my_dataset.my_table
WHERE _PARTITIONTIME = '2024-01-15 14:00:00'
```

### Choosing Partition Granularity

| Granularity | Best for |
|-------------|----------|
| **Daily** (default) | Data spread over a wide date range, or continuously added over time |
| **Hourly** | High-volume data spanning a short date range (< 6 months). Watch the 4,000 partition limit |
| **Monthly / Yearly** | Small daily data volume but wide date range, or workflows that frequently update rows across many dates |

For monthly/yearly partitions, combine with **clustering** on the partition column for best performance.

---

## Clustering

[Documentation](https://docs.cloud.google.com/bigquery/docs/clustered-tables)

After partitioning, you can further organise data within each partition by **clustering**. Clustering sorts the data based on the values of one or more columns, so that rows with similar values are stored together in the same storage blocks.

When you query with a filter on a clustered column, BigQuery can skip entire blocks of data that don't match, dramatically reducing the amount of data scanned.

```sql
-- Creating a partitioned AND clustered table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```

**Rules for clustering:**
- You can specify up to **4** clustering columns
- Clustering columns must be **top-level** (not nested) and **non-repeating**
- The order of clustering columns matters — data is sorted by the first column, then the second within that, and so on
- Supported types: `INT64`, `FLOAT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `BYTES`, `BOOL`, `DATE`, `DATETIME`, `TIMESTAMP`, `GEOGRAPHY`

### Clustering vs Partitioning

| | Clustering | Partitioning |
|---|-----------|-------------|
| **Cost estimation** | Cost benefit unknown until query runs | Cost known upfront (partition pruning) |
| **Granularity** | Fine-grained, block-level pruning | Coarse-grained, partition-level pruning |
| **Management** | Automatic | Partition-level management possible (delete/expire partitions) |
| **Filter pattern** | Queries filter or aggregate on multiple columns | Queries filter on a single column |
| **Cardinality** | Works well with high-cardinality columns | Works best with low-to-medium cardinality |

### When to Use Clustering Over Partitioning

Prefer clustering (instead of or in addition to partitioning) when:

- **Partitions would be too small**: Each partition has less than ~1 GB of data, meaning the overhead of partition management outweighs the benefit
- **Too many partitions**: Your data would exceed the 4,000 partition limit (e.g., partitioning by hour over several years)
- **Frequent mutations across many partitions**: If your writes (inserts/updates) routinely touch most partitions, BigQuery must modify many partitions per operation, which is expensive. Clustering handles this more gracefully because the data is organised within fewer, larger units

### Automatic Reclustering

As new data is added to a clustered table, incoming rows may not be physically co-located with existing rows that share the same cluster values. Over time, this can degrade query performance.

BigQuery automatically performs **reclustering in the background** to re-sort and re-organise data blocks. For partitioned tables, reclustering is scoped to each individual partition. This is free of charge and requires no user action.

---

## Best Practices

### Cost Reduction

- **Avoid `SELECT *`**: BigQuery is columnar — it only reads the columns you reference. Selecting all columns forces a full-row scan
- **Price your queries before running them**: Use the query validator in the BigQuery console (top-right corner) to see estimated bytes processed
- **Use clustered or partitioned tables**: Reduces the amount of data scanned per query
- **Use streaming inserts with caution**: Streaming inserts are expensive compared to batch loads
- **Materialise query results in stages**: Break complex queries into intermediate tables. Instead of one massive query with many joins, create intermediate result tables and query those. This avoids recomputing expensive operations and makes debugging easier

### Query Performance

- **Filter on partitioned/clustered columns**: This enables partition pruning and block skipping
- **Denormalise the data**: Joins are expensive in distributed systems. Denormalised (flattened) tables reduce join overhead
- **Use nested or repeated columns**: BigQuery supports `STRUCT` and `ARRAY` types. Instead of joining a `users` table to an `orders` table, you can store orders as a nested repeated field inside users. This preserves relational structure without the cost of a join
- **Use external data sources appropriately**: External tables are slower; use native tables for frequently queried data
- **Reduce data before using a `JOIN`**: Filter and aggregate tables before joining them, not after
- **Avoid oversharding tables**: Don't split data into too many small tables (e.g., one table per day). Use partitioning instead — it achieves the same logical separation without the management overhead of thousands of tables
- **Do not treat `WITH` clauses as prepared statements**: CTEs (`WITH` clauses) are inlined at execution time, not cached. If a CTE is referenced multiple times, it gets executed multiple times. Materialise it into a temp table instead
- **Avoid JavaScript user-defined functions**: JS UDFs are significantly slower than native SQL functions. Use them only when absolutely necessary
- **Use approximate aggregation functions**: Functions like `APPROX_COUNT_DISTINCT` (using HyperLogLog++) are much faster than exact `COUNT(DISTINCT ...)` on large datasets, with minimal accuracy loss
- **Order last**: Apply `ORDER BY` only at the outermost query. Ordering intermediate results wastes compute
- **Optimise `JOIN` patterns**: Place the **largest table first** in the `FROM` clause, followed by smaller tables in decreasing size. BigQuery uses the first table as the base for the join, and distributes the smaller tables to each processing node

---

## Internals of BigQuery

[Video: BigQuery Internals](https://www.youtube.com/watch?v=eduHi1inM4s)

BigQuery is built on top of several Google technologies:

- **Dremel**: The query execution engine. It uses a tree-like architecture where a root server receives the query, breaks it into smaller sub-queries, and distributes them to intermediate servers (mixers) and leaf nodes. Leaf nodes read data from storage and return results upward through the tree
- **Colossus**: Google's distributed file system (successor to GFS). It stores BigQuery data in a columnar format called **Capacitor**
- **Jupiter**: Google's petabit-scale network that connects Dremel and Colossus, enabling the separation of compute and storage
- **Borg**: Google's cluster management system that allocates compute resources for Dremel jobs

```
  Query
    │
    v
 ┌──────┐
 │ Root │  Dremel execution tree
 └──┬───┘
   ┌┴─────────┐
   v           v
┌──────┐  ┌──────┐
│Mixer │  │Mixer │  Intermediate servers
└──┬───┘  └──┬───┘
  ┌┴──┐     ┌┴──┐
  v   v     v   v
┌───┐┌───┐┌───┐┌───┐
│Leaf││Leaf││Leaf││Leaf│  Read from Colossus (columnar storage)
└───┘└───┘└───┘└───┘
```

The columnar storage format is key to performance: when you query only a few columns, BigQuery reads only those columns from disk, skipping all others entirely. This is fundamentally different from row-oriented databases that must read entire rows.

**Further reading:**
- [Dremel: Interactive Analysis of Web-Scale Datasets](https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets-2/)
- [BigQuery Documentation](https://docs.cloud.google.com/bigquery/docs/introduction)
- [BigQuery Architecture Overview](https://panoply.io/data-warehouse-guide/bigquery-architecture/)
- [A Look at Dremel](https://www.goldsborough.me/distributed-systems/2019/05/18//21-09-00-a_look_at_dremel/)

---

# BigQuery Machine Learning

[Video: BigQuery ML](https://www.youtube.com/watch?v=B-WtpB0PuG4&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=28)

BigQuery ML lets you create and execute machine learning models directly in BigQuery using **SQL**. This removes the need to export data to a separate ML framework (Python/TensorFlow/scikit-learn), which saves time and avoids data movement overhead.

## ML Workflow in BigQuery

The traditional ML workflow requires moving data out of the warehouse:

```
Traditional:  BigQuery → Export → Python/Jupyter → Train → Deploy → Serve

BigQuery ML:  BigQuery → CREATE MODEL → EVALUATE → PREDICT → EXPORT (optional)
```

With BigQuery ML, the entire workflow stays inside BigQuery. This is particularly valuable when:
- Your data is already in BigQuery and is too large to export easily
- You want quick baseline models without setting up a full ML pipeline
- Your team is SQL-fluent but not necessarily Python-fluent

**Supported model types:**
- Linear regression
- Logistic regression (binary/multiclass)
- K-means clustering
- Matrix factorisation (recommendations)
- Time series forecasting (ARIMA+)
- Deep neural networks (via TensorFlow integration)
- Boosted trees (XGBoost)
- Imported TensorFlow and ONNX models

## Creating a Model

```sql
-- Example: Predict tip amount based on trip features
CREATE OR REPLACE MODEL `taxi-rides-ny.nytaxi.tip_model`
OPTIONS (
  model_type = 'linear_reg',
  input_label_cols = ['tip_amount'],
  data_split_method = 'auto_split'
) AS
SELECT
  passenger_count,
  trip_distance,
  PULocationID,
  DOLocationID,
  payment_type,
  fare_amount,
  tolls_amount,
  tip_amount
FROM
  `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned`
WHERE
  tip_amount IS NOT NULL;
```

- `model_type`: The algorithm to use
- `input_label_cols`: The column(s) to predict (the target/label)
- `data_split_method`: How to split data into training/evaluation sets (`auto_split` lets BigQuery handle it)

## Model Evaluation and Prediction

**Evaluate the model:**
```sql
SELECT *
FROM ML.EVALUATE(
  MODEL `taxi-rides-ny.nytaxi.tip_model`,
  (
    SELECT passenger_count, trip_distance, PULocationID,
           DOLocationID, payment_type, fare_amount,
           tolls_amount, tip_amount
    FROM `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned`
    WHERE tip_amount IS NOT NULL
  )
);
```

This returns metrics such as `mean_absolute_error`, `mean_squared_error`, `r2_score`, and `explained_variance`.

**Make predictions:**
```sql
SELECT *
FROM ML.PREDICT(
  MODEL `taxi-rides-ny.nytaxi.tip_model`,
  (
    SELECT passenger_count, trip_distance, PULocationID,
           DOLocationID, payment_type, fare_amount,
           tolls_amount
    FROM `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned`
    LIMIT 10
  )
);
```

The result includes a `predicted_tip_amount` column alongside the input features.

## Model Deployment

BigQuery ML models can be exported and deployed to external serving infrastructure:

**Step 1: Export the model to GCS**
```bash
bq extract -m taxi-rides-ny:nytaxi.tip_model gs://my-bucket/tip_model
```

**Step 2: Download the model locally**
```bash
mkdir /tmp/model
gsutil cp -r gs://my-bucket/tip_model /tmp/model
```

**Step 3: Serve with a Docker container (TensorFlow Serving)**
```bash
docker pull tensorflow/serving

docker run -p 8501:8501 \
  --mount type=bind,source=/tmp/model/tip_model,target=/models/tip_model \
  -e MODEL_NAME=tip_model \
  -t tensorflow/serving
```

**Step 4: Send prediction requests**
```bash
curl -d '{"instances": [{"passenger_count": 1, "trip_distance": 3.5, ...}]}' \
  -X POST http://localhost:8501/v1/models/tip_model:predict
```

This workflow lets you train models with SQL in BigQuery and deploy them as REST APIs for real-time inference.

---

## Resources

- [BigQuery Documentation](https://docs.cloud.google.com/bigquery/docs/introduction)
- [BigQuery ML Documentation](https://cloud.google.com/bigquery/docs/bqml-introduction)
- [Partitioned Tables](https://docs.cloud.google.com/bigquery/docs/partitioned-tables)
- [Clustered Tables](https://docs.cloud.google.com/bigquery/docs/clustered-tables)
- [External Tables](https://docs.cloud.google.com/bigquery/docs/external-tables)
- [Dremel Paper](https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets-2/)
