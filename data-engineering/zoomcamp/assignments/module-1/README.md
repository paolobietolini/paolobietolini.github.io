# Module 1 Homework: Docker & SQL

## Question 1. Understanding Docker images
**Answer: 25.3**

```bash
docker run -it --entrypoint=bash python:3.13
pip -V
```

## Question 2. Understanding Docker networking
**Answer: db:5432**

In Docker Compose, services communicate using the service name as hostname within the internal network.

## Question 3. Counting short trips
**Answer: 8,007**

```sql
SELECT count(*) as TRIPS
FROM "green_tripdata_2025-11"
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

## Question 4. Longest trip for each day
**Answer: 2025-11-14**

```sql
SELECT date(lpep_pickup_datetime), trip_distance
FROM "green_tripdata_2025-11"
WHERE trip_distance < 100.00
ORDER BY trip_distance DESC
LIMIT 1;
```

## Question 5. Biggest pickup zone
**Answer: East Harlem North**

```sql
SELECT
    taxi_zones."Zone",
    SUM(green_trips."total_amount") AS total_amount
FROM "green_tripdata_2025-11" AS green_trips
JOIN taxi_zone_lookup AS taxi_zones
    ON green_trips."PULocationID" = taxi_zones."LocationID"
WHERE green_trips."lpep_pickup_datetime" >= '2025-11-18'
  AND green_trips."lpep_pickup_datetime" < '2025-11-19'
GROUP BY taxi_zones."Zone"
ORDER BY total_amount DESC
LIMIT 1;
```

## Question 6. Largest tip
**Answer: Yorkville West**

```sql
SELECT
    dropoff_zones."Zone" as dropoff_zone,
    green_trips.tip_amount
FROM "green_tripdata_2025-11" as green_trips
JOIN taxi_zone_lookup AS pickup_zones
    ON green_trips."PULocationID" = pickup_zones."LocationID"
JOIN taxi_zone_lookup AS dropoff_zones
    ON green_trips."DOLocationID" = dropoff_zones."LocationID"
WHERE pickup_zones."Zone" = 'East Harlem North'
    AND green_trips.lpep_pickup_datetime >= '2025-11-01'
    AND green_trips.lpep_pickup_datetime < '2025-12-01'
ORDER BY green_trips.tip_amount DESC
LIMIT 1;
```

## Question 7. Terraform Workflow
**Answer: terraform init, terraform apply -auto-approve, terraform destroy**
