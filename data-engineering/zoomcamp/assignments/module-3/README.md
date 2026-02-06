# Module 3 Homework - Data Warehousing & BigQuery

## Assignment Overview

Practice working with BigQuery and Google Cloud Storage using Yellow Taxi Trip Records (Jan-Jun 2024).

## How to Complete

### 1. Load data into GCS

Use the `load_yellow_taxi_data.py` script to download Yellow Taxi parquet files (Jan-Jun 2024) and upload them to your GCS bucket `de_hw3_2026`.

### 2. Create an External Table in BigQuery

```sql
CREATE OR REPLACE EXTERNAL TABLE `your_project.your_dataset.yellow_taxi_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://de_hw3_2026/yellow_tripdata_2024-*.parquet']
);
```

### 3. Create a materialized table (no partitioning or clustering)

```sql
CREATE OR REPLACE TABLE `your_project.your_dataset.yellow_taxi_materialized` AS
SELECT * FROM `your_project.your_dataset.yellow_taxi_external`;
```

---

## Quiz Answers

### Question 1
**What is count of records for the 2024 Yellow Taxi Data?**

**Answer: 20,332,093**

Available in the Details tab or by running:
```sql
SELECT COUNT(*) FROM `elt-demo-de.zoomcamp.yellow_taxi_materialized`;
```

<img src="img/m3-q1.png" alt="Question 1" height="400">

---

### Question 2
**Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables. What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?**

**Answer: 0 MB for the External Table and 155.12 MB for the Materialized Table**

```sql
SELECT COUNT(DISTINCT PULocationID) FROM `elt-demo-de.zoomcamp.yellow_taxi_external`;

SELECT COUNT(DISTINCT PULocationID) FROM `elt-demo-de.zoomcamp.yellow_taxi_materialized`;
```

---

### Question 3
**Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?**

**Answer: BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.**

---

### Question 4
**How many records have a fare_amount of 0?**

**Answer: 8,333**

```sql
SELECT COUNT(*) FROM `elt-demo-de.zoomcamp.yellow_taxi_materialized` WHERE fare_amount = 0;
```

<img src="img/m3-q4.png" alt="Question 4" height="400">

---

### Question 5
**What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)**

**Answer: Partition by tpep_dropoff_datetime and Cluster on VendorID**

```sql
CREATE OR REPLACE TABLE elt-demo-de.zoomcamp.yellow_taxi_partitioned
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT * FROM elt-demo-de.zoomcamp.yellow_taxi_materialized;
```

<img src="img/m3-q5.png" alt="Question 5" height="400">

---

### Question 6
**Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive). Use the materialized table and the partitioned table. What are the estimated bytes processed?**

**Answer: 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table**

```sql
-- Materialized
SELECT DISTINCT VendorID
FROM elt-demo-de.zoomcamp.yellow_taxi_materialized
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';

-- Partitioned
SELECT DISTINCT VendorID
FROM elt-demo-de.zoomcamp.yellow_taxi_partitioned
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

---

### Question 7
**Where is the data stored in the External Table you created?**

**Answer: GCP Bucket**

> External tables don't store data in BigQuery, the data stays in the GCP Bucket.

---

### Question 8
**It is best practice in Big Query to always cluster your data:**

**Answer: False**

> Clustering isn't always beneficial (e.g., small tables, or queries that don't filter/sort on the clustered columns).

---

### Question 9
**No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?**

**Answer: 0 bytes**, BigQuery stores row count in table metadata and doesn't need to scan any data.

