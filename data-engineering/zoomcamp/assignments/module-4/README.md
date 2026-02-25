# Module 4 Homework - Analytics Engineering with dbt

## Assignment Overview

Practice analytics engineering with dbt, building staging models, fact tables, and revenue aggregations using NYC taxi trip data (Green, Yellow, and FHV).

## How to Complete

### 1. Load Green and Yellow taxi data into GCS and BigQuery

Use the `load_taxi_data.py` script to download Green and Yellow parquet files (2019-2020) and upload them to your GCS bucket `de_hw4_2026`.

### 2. Load FHV data into GCS and BigQuery

Use the `load_fhv_data.py` script to download FHV csv.gz files (2019) and upload them to your GCS bucket.

### 3. Build dbt models

Run `dbt build` to create staging, intermediate, and fact models in BigQuery.

---

## Quiz Answers

### Question 1
**If you run `dbt run --select int_trips_unioned`, what models will be built?**

**Answer: Any model with upstream and downstream dependencies to `int_trips_unioned`**

---

### Question 2
**Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data. What happens when you run `dbt test --select fct_trips`?**

**Answer: dbt will fail the test, returning a non-zero exit code**

> `accepted_values` is a strict test by default. If a value appears that isn't in the list, the test fails ([docs](https://docs.getdbt.com/reference/resource-properties/data-tests#accepted_values)). It doesn't warn — it returns rows that violate the condition, and any rows returned means failure.
>
> For it to warn instead of fail, you'd need to explicitly configure the severity:
> ```yaml
> - accepted_values:
>     values: [1, 2, 3, 4, 5]
>     config:
>       severity: warn
> ```
> Without that, the default severity is `error`, which means a non-zero exit code.

---

### Question 3
**What is the count of records in the `fct_monthly_zone_revenue` model?**

**Answer: 12,184**

```sql
SELECT COUNT(*)
FROM `elt-demo-de`.`dbt_prod`.`fct_monthly_zone_revenue`;
```

---

### Question 4
**Using the `fct_monthly_zone_revenue` table, find the pickup zone with the highest total revenue (`revenue_monthly_total_amount`) for Green taxi trips in 2020. Which zone had the highest revenue?**

**Answer: East Harlem North**

```sql
SELECT
  pickup_zone,
  SUM(revenue_monthly_total_amount) AS total_revenue
FROM `elt-demo-de`.`dbt_prod`.`fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1;
```

---

### Question 5
**Using the `fct_monthly_zone_revenue` table, what is the total number of trips (`total_monthly_trips`) for Green taxis in October 2019?**

**Answer: 384,624**

```sql
SELECT
  SUM(total_monthly_trips) AS total_trips
FROM `elt-demo-de`.`dbt_prod`.`fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND EXTRACT(MONTH FROM revenue_month) = 10
  AND EXTRACT(YEAR FROM revenue_month) = 2019;
```

---

### Question 6
**Create a staging model `stg_fhv_tripdata` for the FHV trip data (2019). Filter out records where `dispatching_base_num IS NULL` and rename fields to match naming conventions. What is the count of records in `stg_fhv_tripdata`?**

**Answer: 43,244,693**

```sql
SELECT COUNT(*) AS records
FROM `elt-demo-de`.`dbt_prod`.`stg_fhv_tripdata`;
```

---
