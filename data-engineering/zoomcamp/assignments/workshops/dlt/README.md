# Workshop Homework: dlt Pipeline

## Overview

Built a dlt pipeline ingesting NYC Yellow Taxi trip data from a custom paginated API into DuckDB.

- **Source:** `https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api`
- **Pagination:** 1,000 records/page; stops on empty response body
- **Total records loaded:** 10,000 (10 pages)
- **Pipeline file:** `workshops/dlt-pipeline/taxi_pipeline.py`

## Question 1: What is the start date and end date of the dataset?

**Answer: 2009-06-01 to 2009-07-01**

```sql
SELECT MIN(trip_pickup_date_time) AS start_date, MAX(trip_dropoff_date_time) AS end_date
FROM rides;
-- 2009-06-01T11:33:00Z  |  2009-07-01T00:03:00Z
```

## Question 2: What proportion of trips are paid with credit card?

**Answer: 26.66%**

```sql
SELECT payment_type,
       COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM rides
GROUP BY payment_type
ORDER BY cnt DESC;
-- Credit: 2666 / 10000 = 26.66%
```

## Question 3: What is the total amount of money generated in tips?

**Answer: $6,063.41**

```sql
SELECT ROUND(SUM(tip_amt), 2) AS total_tips
FROM rides;
-- 6063.41
```
