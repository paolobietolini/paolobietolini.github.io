# Module 7 Homework - Streaming with Kafka and PyFlink

## Assignment Overview

Practice streaming with Kafka (Redpanda) and PyFlink using Green Taxi Trip data from October 2025.

## Setup

### 1. Install Python dependencies

```bash
uv sync
```

### 2. Build and start all services

```bash
docker compose build    # first time: builds the PyFlink image (~5 min)
docker compose up -d
```

This gives us:
- Redpanda (Kafka-compatible broker) on `localhost:9092`
- Flink Job Manager at http://localhost:8081
- Flink Task Manager
- PostgreSQL on `localhost:5433` (user: `postgres`, password: `postgres`) — port 5433 to avoid conflicts with local PostgreSQL

Clean start if needed:
```bash
docker compose down -v
docker compose build
docker compose up -d
```

### 3. Create the Kafka topic and PostgreSQL tables

```bash
docker exec -it module-7-redpanda-1 rpk topic create green-trips
docker exec -i module-7-postgres-1 psql -U postgres -d postgres < init.sql
```

> Container names use the directory name as prefix. If you renamed the
> directory, adjust accordingly (check with `docker compose ps`).

### 4. Run the producer (Q2) and consumer (Q3)

```bash
uv run python src/producers/producer.py    # sends all green taxi data (~60s)
uv run python src/consumers/consumer.py    # counts trips with distance > 5 km
```

### 5. Run the Flink jobs (Q4-Q6)

Submit each job, let it run for 1-2 minutes, then query results in PostgreSQL.
Cancel running jobs from the Flink UI at http://localhost:8081 before submitting the next one.

```bash
# Q4: 5-minute tumbling window by PULocationID
docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q4_tumbling_pickup.py

# Q5: session window with 5-minute gap
docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q5_session_pickup.py

# Q6: 1-hour tumbling window for tip amounts
docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q6_hourly_tips.py
```

Query results (via pgcli, DBeaver, or docker exec):
```bash
docker exec -it module-7-postgres-1 psql -U postgres -d postgres
```

```sql
-- Q4
SELECT PULocationID, num_trips FROM tumbling_pickup ORDER BY num_trips DESC LIMIT 3;

-- Q5
SELECT PULocationID, num_trips, session_start, session_end FROM session_pickup ORDER BY num_trips DESC LIMIT 3;

-- Q6
SELECT window_start, total_tips FROM hourly_tips ORDER BY total_tips DESC LIMIT 3;
```

### Makefile shortcuts

```bash
make up             # build + start all services
make create-topic   # create green-trips topic
make init-db        # create PostgreSQL tables
make produce        # run the producer
make consume        # run the consumer
make q4 / q5 / q6   # submit Flink jobs
make clean          # stop + remove volumes
```

### Data

- [green_tripdata_2025-10.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet)

### Work through the questions in the [notebook](module-7-assignment.ipynb)

---

## Quiz Answers

### Question 1
**Run `rpk version` inside the Redpanda container. What version of Redpanda are you running?**

```bash
docker exec -it module-7-redpanda-1 rpk version
```

**Answer: `v25.3.9`**

---

### Question 2
**Create a topic called `green-trips`, produce all green taxi data, and measure how long it takes.**

**Answer: 10 seconds**

> Sending the full October 2025 green taxi dataset (49,416 rows, 8 columns) with `producer.flush()` takes approximately 4 seconds. The closest option is 10 seconds.

---

### Question 3
**Write a Kafka consumer that reads all messages from `green-trips`. How many trips have `trip_distance` > 5?**

**Answer: 8506**

---

### Question 4
**Create a Flink job with a 5-minute tumbling window to count trips per `PULocationID`. Which `PULocationID` had the most trips in a single 5-minute window?**

**Answer: 74**

---

### Question 5
**Create a Flink job with a session window (5-minute gap) on `PULocationID`. How many trips were in the longest session?**

**Answer: 81**

> The longest session had 72 trips at PULocationID 74. The closest multiple-choice option is 81.

---

### Question 6
**Create a Flink job with a 1-hour tumbling window to compute total `tip_amount` per hour. Which hour had the highest total tip amount?**

**Answer: 2025-10-16 18:00:00**

---
