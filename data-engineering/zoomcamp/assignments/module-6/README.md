# Module 6 Homework - Batch Processing with Spark

## Assignment Overview

Use Apache Spark and PySpark to process and analyze NYC Yellow Taxi data from November 2025.

## How to Complete

### 1. Install Spark and PySpark

Follow the [setup guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/06-batch/setup/).

### 2. Download the data

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

### 3. Work through the questions in the [notebook](module-6-assignment.ipynb)

---

## Quiz Answers

### Question 1
**Execute `spark.version`. What's the output?**

**Answer: `4.1.1`**

---

### Question 2
**Repartition the Dataframe to 4 partitions and save it to parquet. What is the average size of the Parquet files that were created (in MB)?**

**Answer: 25MB**

> After repartitioning to 4 partitions and saving to parquet, each file is approximately 25MB.

---

### Question 3
**How many taxi trips were there on the 15th of November?**

**Answer: 162,604**

> Filtering on `tpep_pickup_datetime` for November 15th returns 162,604 trips.

---

### Question 4
**What is the length of the longest trip in the dataset in hours?**

**Answer: 90.6**

> Using `DATEDIFF(second, ...) / 3600` to get precise fractional hours. `DATEDIFF(hour, ...)` only counts whole hour boundaries and would return 90.

---

### Question 5
**Spark's User Interface which shows the application's dashboard runs on which local port?**

**Answer: 4040**

> The Spark UI is available at `http://localhost:4040` by default.

---

### Question 6
**Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?**

**Answer: Governor's Island/Ellis Island/Liberty Island** (also Arden Heights — both have 1 trip)

> Joining on `PULocationID = LocationID`, grouping by Zone and sorting ascending shows both Governor's Island/Ellis Island/Liberty Island and Arden Heights tied with 1 trip each. The question says "if multiple answers are correct, select any."

---
