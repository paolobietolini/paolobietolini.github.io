---
layout: default
title: "Batch Processing with Spark"
permalink: /data-engineering/zoomcamp/batch-processing
---
{% raw %}

## Table of Contents

- [What is Batch Processing?](#what-is-batch-processing)
  - [Batch vs Streaming](#batch-vs-streaming)
  - [When to Use Batch](#when-to-use-batch)
- [Introduction to Spark](#introduction-to-spark)
  - [Where Spark Fits In](#where-spark-fits-in)
- [Installation](#installation)
  - [Java](#java)
  - [PySpark](#pyspark)
- [Spark SQL and DataFrames](#spark-sql-and-dataframes)
  - [Creating a SparkSession](#creating-a-sparksession)
  - [Reading Data](#reading-data)
  - [Schema Definition](#schema-definition)
  - [Partitioning and Parquet](#partitioning-and-parquet)
  - [Column Operations and UDFs](#column-operations-and-udfs)
  - [SQL Queries](#sql-queries)
- [Spark Internals](#spark-internals)
  - [Anatomy of a Spark Cluster](#anatomy-of-a-spark-cluster)
  - [GroupBy in Spark](#groupby-in-spark)
  - [Joins in Spark](#joins-in-spark)
- [Resilient Distributed Datasets (RDDs)](#resilient-distributed-datasets-rdds)
  - [RDD Operations](#rdd-operations)
  - [mapPartitions](#mappartitions)
- [Running Spark in the Cloud](#running-spark-in-the-cloud)
  - [Connecting to Google Cloud Storage](#connecting-to-google-cloud-storage)
  - [Local Spark Cluster and spark-submit](#local-spark-cluster-and-spark-submit)
  - [Dataproc](#dataproc)
  - [Connecting Spark to BigQuery](#connecting-spark-to-bigquery)
- [Resources](#resources)

---

# What is Batch Processing?

Batch processing is the execution of a series of jobs on a set of data that has been collected over a period. Unlike streaming (real-time, event-by-event), batch processes run on a schedule — hourly, daily, weekly — and operate on bounded datasets.

## Batch vs Streaming

| | Batch | Streaming |
|---|---|---|
| **Data** | Bounded, collected over time | Unbounded, continuous flow |
| **Latency** | Minutes to hours | Seconds to milliseconds |
| **Complexity** | Simpler to build and maintain | More complex (state, ordering, late data) |
| **Error handling** | Easier — rerun the job | Harder — need checkpointing, replay |
| **Tools** | Spark, Hive, Presto | Flink, Kafka Streams, Spark Streaming |

## When to Use Batch

Most data engineering workloads are batch. Use batch when:
- A human is the consumer (dashboards, reports) — they don't need sub-second latency
- The data naturally arrives in chunks (daily files, hourly exports)
- You can tolerate latency of minutes to hours
- You want simpler operations and easier debugging

---

# Introduction to Spark

**Apache Spark** is a multi-language engine for large-scale data processing. It's the industry standard for batch processing and also supports streaming (micro-batch).

Key characteristics:
- **Distributed** — splits work across a cluster of machines
- **In-memory** — processes data in RAM, much faster than disk-based MapReduce
- **Multi-language** — Python (PySpark), Scala, Java, R, SQL
- **Lazy evaluation** — builds an execution plan, only computes when you trigger an action (`.show()`, `.write()`, `.count()`)

## Where Spark Fits In

Spark is the processing engine. It reads data from a source (local files, GCS, S3, HDFS), transforms it, and writes results to a destination.

```
Data Lake (GCS/S3)  →  Spark  →  Data Warehouse (BigQuery)
                    →  Spark  →  Parquet files
                    →  Spark  →  Another data lake
```

When to use Spark vs SQL (dbt, BigQuery):
- **SQL is enough** for most transformations — joins, aggregations, window functions
- **Spark is needed** when you need custom logic that's hard in SQL (ML models, complex UDFs, graph processing), or when your data is too large for a single warehouse query

---

# Installation

Spark 4.x requires **Java 17 or 21**.

## Java

```bash
sudo apt update
sudo apt install default-jdk
java --version
```

Set `JAVA_HOME` (add to `.bashrc` or `.zshrc`):

```bash
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH="${JAVA_HOME}/bin:${PATH}"
```

## PySpark

Using `uv` (recommended):

```bash
uv init
uv add pyspark
```

Or with pip:

```bash
pip install pyspark
```

Both approaches install PySpark with a bundled Spark distribution — no separate Spark download needed.

Test it:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

print(f"Spark version: {spark.version}")
df = spark.range(10)
df.show()
spark.stop()
```

---

# Spark SQL and DataFrames

## Creating a SparkSession

The entry point for all Spark functionality:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

- `local[*]` — run locally using all available CPU cores
- In a cluster, `master` would point to the Spark master URL

## Reading Data

Read a CSV file:

```python
df = spark.read \
    .option("header", "true") \
    .csv('fhvhv_tripdata_2021-01.csv')
```

Without a schema, Spark infers all columns as strings. The `inferSchema` option can auto-detect types but reads the entire file twice.

Read Parquet (preserves schema automatically):

```python
df = spark.read.parquet('data/pq/green/*/*')
```

Glob patterns (`*`) let you read multiple partitions at once.

## Schema Definition

Define an explicit schema for type safety and performance:

```python
from pyspark.sql import types

schema = types.StructType([
    types.StructField('hvfhs_license_num', types.StringType(), True),
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)
])

df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv('fhvhv_tripdata_2021-01.csv')
```

Common types:
- `StringType()`, `IntegerType()` (4 bytes), `LongType()` (8 bytes)
- `FloatType()`, `DoubleType()`, `TimestampType()`, `DateType()`

A quick way to derive the schema: read a small sample with pandas, then convert:

```python
import pandas as pd
df_pandas = pd.read_csv('head.csv')
spark.createDataFrame(df_pandas).schema
```

## Partitioning and Parquet

**Repartition** controls how many files/partitions Spark uses. More partitions = more parallelism but more file overhead:

```python
df = df.repartition(24)
df.write.parquet('fhvhv/2021/01/')
```

**Coalesce** reduces partitions without a full shuffle (more efficient than repartition when reducing):

```python
df_result.coalesce(1).write.parquet('data/report/revenue/', mode='overwrite')
```

Parquet is the preferred format because:
- Columnar storage — reads only the columns you need
- Built-in compression
- Preserves schema (types are embedded in the file)
- Splittable — Spark can read partitions in parallel

## Column Operations and UDFs

Use `pyspark.sql.functions` for column transformations:

```python
from pyspark.sql import functions as F

df.withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
  .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
  .select('pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
  .show()
```

**Filtering:**

```python
df.filter(df.hvfhs_license_num == 'HV0003')
```

**Adding literal columns:**

```python
df_green_sel = df_green \
    .select(common_columns) \
    .withColumn('service_type', F.lit('green'))
```

**User-Defined Functions (UDFs)** for custom logic:

```python
def crazy_stuff(base_num):
    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'

crazy_stuff_udf = F.udf(crazy_stuff, returnType=types.StringType())

df.withColumn('base_id', crazy_stuff_udf(df.dispatching_base_num))
```

UDFs are powerful but slower than built-in functions — they can't be optimized by Spark's Catalyst optimizer. Prefer built-in functions when possible.

## SQL Queries

Register a DataFrame as a temp table, then use SQL:

```python
df_trips_data.registerTempTable('trips_data')

spark.sql("""
SELECT
    service_type,
    count(1)
FROM
    trips_data
GROUP BY
    service_type
""").show()
```

A more complex revenue report:

```python
df_result = spark.sql("""
SELECT
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month,
    service_type,

    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    AVG(passenger_count) AS avg_monthly_passenger_count,
    AVG(trip_distance) AS avg_monthly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")
```

**Combining DataFrames:** Use `unionAll` to stack DataFrames with the same schema. First rename columns to match:

```python
df_green = df_green.withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime')
df_yellow = df_yellow.withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime')

# Find common columns
common_columns = [col for col in df_green.columns if col in set(df_yellow.columns)]

df_trips = df_green.select(common_columns).withColumn('service_type', F.lit('green')) \
    .unionAll(df_yellow.select(common_columns).withColumn('service_type', F.lit('yellow')))
```

---

# Spark Internals

## Anatomy of a Spark Cluster

```
                    ┌──────────────┐
                    │   Driver     │
                    │  (SparkSession)│
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │ Cluster Mgr  │
                    │(YARN/Standalone)│
                    └──┬───┬───┬───┘
                       │   │   │
              ┌────────┘   │   └────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴─────┐ ┌────┴─────┐
        │ Executor 1 │ │Executor 2│ │Executor 3│
        │ (Worker)   │ │(Worker)  │ │(Worker)  │
        └────────────┘ └─────────┘ └──────────┘
```

| Component | Role |
|---|---|
| **Driver** | The program that creates the SparkSession. Builds the execution plan, sends tasks to executors |
| **Cluster Manager** | Allocates resources (YARN, Standalone, Kubernetes, Mesos) |
| **Executors** | Worker processes that run tasks. Each has CPU cores and memory |

**Execution flow:**
1. Your code defines transformations (lazy — nothing happens yet)
2. An action (`.show()`, `.write()`, `.count()`) triggers execution
3. Spark builds a **DAG** (Directed Acyclic Graph) of stages
4. The DAG is split into **stages** at shuffle boundaries
5. Each stage is split into **tasks** (one per partition)
6. Tasks are sent to executors for parallel execution

## GroupBy in Spark

GroupBy requires a **shuffle** — redistributing data across executors so all records with the same key end up on the same executor.

```python
df_green_revenue = spark.sql("""
SELECT
    date_trunc('hour', lpep_pickup_datetime) AS hour,
    PULocationID AS zone,
    SUM(total_amount) AS amount,
    COUNT(1) AS number_records
FROM green
WHERE lpep_pickup_datetime >= '2020-01-01 00:00:00'
GROUP BY 1, 2
""")
```

How Spark executes this:

1. **Stage 1 (Map)**: Each executor reads its partitions, computes partial aggregates locally (a "combine" step)
2. **Shuffle**: Partial results are redistributed by key (`hour`, `zone`) across the network
3. **Stage 2 (Reduce)**: Each executor merges the partial aggregates into final results

The shuffle is the expensive part — data moves across the network. Reducing the amount of data before the shuffle (via partial aggregates) is key to performance.

## Joins in Spark

Joins also require shuffles. Spark supports several join strategies:

**Sort-Merge Join** (default for large-large joins):
1. Both DataFrames are shuffled by the join key
2. Each partition is sorted
3. Sorted partitions are merged

```python
df_join = df_green_revenue_tmp.join(df_yellow_revenue_tmp, on=['hour', 'zone'], how='outer')
```

**Broadcast Join** (when one DataFrame is small):
- The small DataFrame is sent to every executor
- No shuffle needed for the large DataFrame
- Spark does this automatically when one side is below `spark.sql.autoBroadcastJoinThreshold` (default 10MB)

**Joining with a lookup table:**

```python
df_zones = spark.read.parquet('zones/')
df_result = df_join.join(df_zones, df_join.zone == df_zones.LocationID)
df_result.drop('LocationID', 'zone').write.parquet('tmp/revenue-zones')
```

Renaming columns before joins avoids ambiguity:

```python
df_green_revenue_tmp = df_green_revenue \
    .withColumnRenamed('amount', 'green_amount') \
    .withColumnRenamed('number_records', 'green_number_records')
```

---

# Resilient Distributed Datasets (RDDs)

RDDs are Spark's low-level API. DataFrames and SQL are built on top of RDDs. You rarely need RDDs directly, but they're useful for:
- Operations that can't be expressed in SQL/DataFrame API
- Applying ML models per partition
- Fine-grained control over processing

## RDD Operations

Convert a DataFrame to an RDD:

```python
rdd = df_green \
    .select('lpep_pickup_datetime', 'PULocationID', 'total_amount') \
    .rdd
```

**filter** — keep rows matching a condition:

```python
from datetime import datetime
start = datetime(year=2020, month=1, day=1)

def filter_outliers(row):
    return row.lpep_pickup_datetime >= start

rdd = rdd.filter(filter_outliers)
```

**map** — transform each row:

```python
def prepare_for_grouping(row):
    hour = row.lpep_pickup_datetime.replace(minute=0, second=0, microsecond=0)
    zone = row.PULocationID
    key = (hour, zone)
    value = (row.total_amount, 1)
    return (key, value)

rdd = rdd.map(prepare_for_grouping)
```

**reduceByKey** — aggregate by key (like GroupBy):

```python
def calculate_revenue(left_value, right_value):
    left_amount, left_count = left_value
    right_amount, right_count = right_value
    return (left_amount + right_amount, left_count + right_count)

rdd = rdd.reduceByKey(calculate_revenue)
```

**Convert back to DataFrame:**

```python
from collections import namedtuple

RevenueRow = namedtuple('RevenueRow', ['hour', 'zone', 'revenue', 'count'])

def unwrap(row):
    return RevenueRow(hour=row[0][0], zone=row[0][1],
                      revenue=row[1][0], count=row[1][1])

result_schema = types.StructType([
    types.StructField('hour', types.TimestampType(), True),
    types.StructField('zone', types.IntegerType(), True),
    types.StructField('revenue', types.DoubleType(), True),
    types.StructField('count', types.IntegerType(), True)
])

df_result = rdd.map(unwrap).toDF(result_schema)
```

## mapPartitions

`mapPartitions` processes an entire partition at once instead of row-by-row. This is useful when you need to load a model or create a batch for predictions:

```python
columns = ['VendorID', 'lpep_pickup_datetime', 'PULocationID',
           'DOLocationID', 'trip_distance']

def apply_model_in_batch(rows):
    df = pd.DataFrame(rows, columns=columns)
    predictions = model_predict(df)  # your ML model
    df['predicted_duration'] = predictions
    for row in df.itertuples():
        yield row

df_predicts = duration_rdd \
    .mapPartitions(apply_model_in_batch) \
    .toDF() \
    .drop('Index')
```

Why `mapPartitions` over `map`:
- Amortize expensive setup (loading ML models, opening DB connections) across many rows
- Work with pandas DataFrames for batch operations
- `yield` lets you produce output incrementally (memory-efficient)

---

# Running Spark in the Cloud

## Connecting to Google Cloud Storage

Upload data to GCS:

```bash
gsutil -m cp -r pq/ gs://dtc_data_lake_de-zoomcamp/pq
```

Download the GCS connector JAR:

```bash
gsutil cp gs://hadoop-lib/gcs/gcs-connector-hadoop3-2.2.5.jar ./lib/
```

Then configure Spark to use GCS credentials (see `09_spark_gcs.ipynb` in the course repo).

## Local Spark Cluster and spark-submit

Create a standalone cluster:

```bash
# Start master
./sbin/start-master.sh

# Start worker (get URL from master's web UI)
URL="spark://your-hostname:7077"
./sbin/start-worker.sh ${URL}
```

Convert a notebook to a script and submit:

```bash
jupyter nbconvert --to=script 06_spark_sql.ipynb

spark-submit \
    --master="${URL}" \
    06_spark_sql.py \
        --input_green=data/pq/green/2021/*/ \
        --input_yellow=data/pq/yellow/2021/*/ \
        --output=data/report-2021
```

`spark-submit` sends the job to the cluster. The cluster manager distributes tasks to workers.

## Dataproc

**Google Cloud Dataproc** is a managed Spark/Hadoop service. It handles cluster creation, scaling, and teardown.

Upload your script to GCS, then submit:

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=europe-west6 \
    gs://your-bucket/code/06_spark_sql.py \
    -- \
        --input_green=gs://your-bucket/pq/green/2020/*/ \
        --input_yellow=gs://your-bucket/pq/yellow/2020/*/ \
        --output=gs://your-bucket/report-2020
```

Advantages over self-managed Spark:
- No cluster setup — create/destroy in minutes
- Autoscaling
- Integrates with GCS and BigQuery natively
- Pay only for compute time

## Connecting Spark to BigQuery

Submit a job that writes directly to BigQuery:

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=europe-west6 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar \
    gs://your-bucket/code/06_spark_sql_big_query.py \
    -- \
        --input_green=gs://your-bucket/pq/green/2020/*/ \
        --input_yellow=gs://your-bucket/pq/yellow/2020/*/ \
        --output=trips_data_all.reports-2020
```

> Dataproc 2.1+ images pre-install the Spark BigQuery connector — no need to include the JAR.

---

# Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [Course Module 6 Code](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch/code)
- [Spark Installation Guides](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch/setup)
- [Cloud Storage Connector for Hadoop](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage)
- [Spark BigQuery Connector](https://github.com/GoogleCloudDataproc/spark-bigquery-connector)
{% endraw %}
