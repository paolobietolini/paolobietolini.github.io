---
layout: default
title: "Stream Processing with PyFlink"
permalink: /data-engineering/zoomcamp/stream-processing
---
{% raw %}

## Table of Contents

- [What is Stream Processing?](#what-is-stream-processing)
  - [When to Use Streaming](#when-to-use-streaming)
- [Kafka and Redpanda](#kafka-and-redpanda)
  - [Why Redpanda over Kafka?](#why-redpanda-over-kafka)
  - [Kafka Two-Step Connection](#kafka-two-step-connection)
- [Producing Messages](#producing-messages)
  - [Serialization](#serialization)
- [Consuming Messages](#consuming-messages)
  - [Deserialization](#deserialization)
  - [Consumer Groups and Offsets](#consumer-groups-and-offsets)
- [Saving Events to PostgreSQL](#saving-events-to-postgresql)
  - [Limitations of Plain Consumers](#limitations-of-plain-consumers)
- [Apache Flink](#apache-flink)
  - [Why Flink?](#why-flink)
  - [Architecture: JobManager and TaskManager](#architecture-jobmanager-and-taskmanager)
  - [Task Slots and Parallelism](#task-slots-and-parallelism)
- [PyFlink Jobs](#pyflink-jobs)
  - [The Custom Docker Image](#the-custom-docker-image)
  - [Source Tables (Kafka)](#source-tables-kafka)
  - [Sink Tables (PostgreSQL via JDBC)](#sink-tables-postgresql-via-jdbc)
  - [Pass-Through Job](#pass-through-job)
  - [Checkpointing](#checkpointing)
- [Offsets: earliest vs latest](#offsets-earliest-vs-latest)
- [Windowed Aggregation](#windowed-aggregation)
  - [Watermarks](#watermarks)
  - [Late Events and Upserts](#late-events-and-upserts)
- [Window Types](#window-types)
  - [Tumbling Windows](#tumbling-windows)
  - [Sliding Windows](#sliding-windows)
  - [Session Windows](#session-windows)
- [Flink in Production](#flink-in-production)
- [Kafka Theory (Optional)](#kafka-theory-optional)
- [Resources](#resources)

---

# What is Stream Processing?

Stream processing is the continuous, real-time processing of data as it arrives, as opposed to batch processing where data is collected first and processed later. A streaming pipeline reads events from a source (like Kafka), processes them (filters, aggregates, transforms), and writes results to a sink (like PostgreSQL or another Kafka topic).

The architecture we build in this module:

```
Producer (Python) -> Kafka (Redpanda) -> Flink -> PostgreSQL
```

## When to Use Streaming

The key question: **is something going to happen in real time on the other side?** If an automated process will change something based on the data, streaming is a great choice. If a human is just looking at data, real-time is usually unnecessary and micro-batch (hourly, every 15 minutes) is easier to maintain.

Genuine streaming use cases are rare. Examples from production:
- **Fraud detection** — 5 minutes of delay means 5 more minutes of a hacked account
- **Surge pricing** — supply and demand changes rapidly

The operational cost is significant: a streaming job runs 24/7. If it breaks at 3 AM, someone needs to fix it. Before committing to streaming, consider whether your entire team can support it on-call.

---

# Kafka and Redpanda

Before we can produce or consume messages, we need a **message broker** — a service that receives messages from producers, stores them, and delivers them to consumers.

**Apache Kafka** is the industry standard. We use **Redpanda**, a drop-in replacement that implements the same protocol. Any Kafka client library (like `kafka-python`) works with Redpanda unchanged.

## Why Redpanda over Kafka?

| | Kafka | Redpanda |
|---|---|---|
| **Runtime** | JVM (Java) — needs significant memory | C++ — starts in seconds, far less overhead |
| **Coordination** | Requires ZooKeeper (separate cluster) | Built-in Raft consensus — no extra service |
| **Deployment** | Multiple containers | Single binary, one container |

## Kafka Two-Step Connection

Kafka clients use a two-step connection process:

1. Client connects to a **bootstrap server** and asks for cluster metadata
2. Broker responds with **advertised addresses** — where the client should connect for data transfer

This is why Redpanda exposes two listeners:
- **Internal** (`redpanda:29092`) — for Docker containers (e.g., Flink)
- **External** (`localhost:9092`) — for your laptop (Python scripts)

If we used only one address, either Docker containers or your laptop wouldn't be able to connect.

Docker Compose config for Redpanda:

```yaml
services:
  redpanda:
    image: redpandadata/redpanda:v25.3.9
    command:
      - redpanda
      - start
      - --smp
      - '1'
      - --reserve-memory
      - 0M
      - --overprovisioned
      - --node-id
      - '1'
      - --kafka-addr
      - PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092
      - --advertise-kafka-addr
      - PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092
      - --pandaproxy-addr
      - PLAINTEXT://0.0.0.0:28082,OUTSIDE://0.0.0.0:8082
      - --advertise-pandaproxy-addr
      - PLAINTEXT://redpanda:28082,OUTSIDE://localhost:8082
      - --rpc-addr
      - 0.0.0.0:33145
      - --advertise-rpc-addr
      - redpanda:33145
    ports:
      - 8082:8082
      - 9092:9092
      - 28082:28082
      - 29092:29092
```

Resource parameters:

| Parameter | Purpose |
|---|---|
| `--smp 1` | Use 1 CPU core (built on [Seastar](http://seastar.io/) which pins threads to cores) |
| `--reserve-memory 0M` | Skip internal cache reservation (development only) |
| `--overprovisioned` | Don't pin threads to specific CPU cores |
| `--node-id 1` | Unique broker ID in the cluster |

---

# Producing Messages

Initialize a Python project and send NYC taxi trip data to Kafka:

```bash
uv init -p 3.12
uv add kafka-python pandas pyarrow
```

Define a data model:

```python
from dataclasses import dataclass

@dataclass
class Ride:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    tpep_pickup_datetime: int  # epoch milliseconds
```

Convert DataFrame rows to `Ride` objects:

```python
def ride_from_row(row):
    return Ride(
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
        tpep_pickup_datetime=int(row['tpep_pickup_datetime'].timestamp() * 1000),
    )
```

## Serialization

Kafka works with raw bytes. We need a serializer to convert Python objects to JSON bytes:

```python
import json
import dataclasses
from kafka import KafkaProducer

def ride_serializer(ride):
    return json.dumps(dataclasses.asdict(ride)).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=ride_serializer
)
```

Send all rows:

```python
import time

t0 = time.time()
for _, row in df.iterrows():
    ride = ride_from_row(row)
    producer.send('rides', value=ride)
producer.flush()
print(f'took {(time.time() - t0):.2f} seconds')
```

---

# Consuming Messages

## Deserialization

The consumer receives raw bytes. Write a deserializer that converts JSON bytes back to a `Ride`:

```python
def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)
```

## Consumer Groups and Offsets

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'rides',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    group_id='rides-console',
    value_deserializer=ride_deserializer
)
```

Key concepts:
- **`auto_offset_reset='earliest'`** — start reading from the beginning of the topic. Without this, new consumers default to `latest` and only see new messages.
- **`group_id`** — identifies this consumer group. Kafka tracks how far each group has read, so restarting with the same group ID continues where it left off.
- Each consumer group tracks offsets independently — the console consumer and the PostgreSQL consumer each read all messages.

---

# Saving Events to PostgreSQL

Add PostgreSQL to `docker-compose.yml`:

```yaml
postgres:
  image: postgres:18
  restart: on-failure
  environment:
    - POSTGRES_DB=postgres
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
  ports:
    - "5432:5432"
```

Create a table and write a consumer that inserts each message:

```python
import psycopg2
from datetime import datetime

conn = psycopg2.connect(host='localhost', port=5432, database='postgres',
                        user='postgres', password='postgres')
conn.autocommit = True
cur = conn.cursor()

for message in consumer:
    ride = message.value
    pickup_dt = datetime.fromtimestamp(ride.tpep_pickup_datetime / 1000)
    cur.execute(
        """INSERT INTO processed_events
           (PULocationID, DOLocationID, trip_distance, total_amount, pickup_datetime)
           VALUES (%s, %s, %s, %s, %s)""",
        (ride.PULocationID, ride.DOLocationID,
         ride.trip_distance, ride.total_amount, pickup_dt)
    )
```

## Limitations of Plain Consumers

This works for simple consume-and-write, but lacks:
- **Windowing** — time-based aggregations require custom logic
- **Fault tolerance** — manual offset tracking vs. automatic checkpointing
- **Parallelism** — distributed processing requires consumer group management
- **Sinks** — writing to different destinations needs connector code for each

---

# Apache Flink

## Why Flink?

Flink is a stream processing framework that handles all the hard parts:

| Capability | Plain Consumer | Flink |
|---|---|---|
| **Windowing** | Build it yourself | Built-in tumbling, sliding, session windows |
| **Checkpointing** | Manual offset tracking | Automatic state recovery after failures |
| **Parallelism** | Manage consumer instances | Distributed automatically |
| **Connectors** | Write code per destination | Built-in JDBC, Kafka, filesystem sinks |
| **Interface** | Python code | SQL queries |

The trade-off is infrastructure complexity — Flink requires JobManager and TaskManager containers. A streaming job is more like owning a server than running a batch pipeline — it runs 24/7 and needs monitoring.

## Architecture: JobManager and TaskManager

| Component | Role |
|---|---|
| **JobManager** | Coordinator — accepts jobs, manages checkpoints, assigns work. Web UI on port `8081`, RPC on port `6123` |
| **TaskManager** | Worker — executes actual data processing |

```yaml
jobmanager:
  build:
    context: .
    dockerfile: ./Dockerfile.flink
  image: pyflink-workshop
  pull_policy: never
  expose:
    - "6123"
  ports:
    - "8081:8081"
  volumes:
    - ./:/opt/flink/usrlib
    - ./src/:/opt/src
  command: jobmanager
  environment:
    - |
      FLINK_PROPERTIES=
      jobmanager.rpc.address: jobmanager
      jobmanager.memory.process.size: 1600m

taskmanager:
  image: pyflink-workshop
  pull_policy: never
  expose:
    - "6121"
    - "6122"
  volumes:
    - ./:/opt/flink/usrlib
    - ./src/:/opt/src
  depends_on:
    - jobmanager
  command: taskmanager --taskmanager.registration.timeout 5 min
  environment:
    - |
      FLINK_PROPERTIES=
      jobmanager.rpc.address: jobmanager
      taskmanager.memory.process.size: 1728m
      taskmanager.numberOfTaskSlots: 15
      parallelism.default: 3
```

## Task Slots and Parallelism

A **task slot** is a unit of resources (memory, CPU) that can run one parallel instance of a pipeline stage. Think of slots like lanes on a highway.

- If you submit a job with parallelism 3, it uses 3 slots
- With 15 slots available, you can run 5 such jobs simultaneously
- In production, multiple task managers across different machines each contribute slots

---

# PyFlink Jobs

## The Custom Docker Image

Flink doesn't include Python support out of the box. The custom `Dockerfile.flink`:
- Starts from `flink:2.2.0-scala_2.12-java17`
- Installs Python 3.12 and PyFlink via `uv`
- Downloads connector JARs (Kafka, JDBC, PostgreSQL driver)
- Applies custom Flink config to increase JVM metaspace

Build and start:

```bash
docker compose up --build -d
```

## Source Tables (Kafka)

Flink uses SQL DDL to define source tables. The Kafka connector reads JSON messages:

```python
def create_events_source_kafka(t_env):
    source_ddl = f"""
        CREATE TABLE events (
            PULocationID INTEGER,
            DOLocationID INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            tpep_pickup_datetime BIGINT
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'rides',
            'scan.startup.mode' = 'latest-offset',
            'properties.auto.offset.reset' = 'latest',
            'format' = 'json'
        );
    """
    t_env.execute_sql(source_ddl)
```

Note: `redpanda:29092` is the **internal** Docker address (not `localhost`).

## Sink Tables (PostgreSQL via JDBC)

No psycopg2 needed — just declare the table and Flink handles writes:

```python
def create_processed_events_sink_postgres(t_env):
    sink_ddl = f"""
        CREATE TABLE processed_events (
            PULocationID INTEGER,
            DOLocationID INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            pickup_datetime TIMESTAMP
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'processed_events',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
    """
    t_env.execute_sql(sink_ddl)
```

## Pass-Through Job

The simplest Flink job: read from Kafka, convert timestamp, write to PostgreSQL:

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def log_processing():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    create_events_source_kafka(t_env)
    create_processed_events_sink_postgres(t_env)

    t_env.execute_sql("""
        INSERT INTO processed_events
        SELECT PULocationID, DOLocationID, trip_distance, total_amount,
               TO_TIMESTAMP_LTZ(tpep_pickup_datetime, 3) as pickup_datetime
        FROM events
    """).wait()
```

Submit:

```bash
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/pass_through_job.py \
    --pyFiles /opt/src -d
```

## Checkpointing

`enable_checkpointing(10 * 1000)` tells Flink to snapshot the job's state every 10 seconds. A checkpoint captures:
- Kafka offsets (how far Flink has read)
- Any in-flight data and open windows

If the job crashes, it resumes from the last checkpoint. The trade-off: checkpoint too frequently = expensive (serialize entire state often), checkpoint too rarely = lose more progress on failure.

**Important**: checkpoints are scoped to a specific job instance. If you cancel and resubmit, it's a brand new job with no knowledge of previous checkpoints.

---

# Offsets: earliest vs latest

| Mode | Behavior |
|---|---|
| `latest-offset` | Only read messages arriving after the job starts |
| `earliest-offset` | Read everything from the beginning of the topic |
| `timestamp` | Start from a specific point in time |

- **`latest`** — common production setting for real-time processing
- **`earliest`** — used for backfilling or restating data
- **`timestamp`** — useful for recovering from a specific point after a failure

The offset setting only matters at startup. Once the job is running, checkpointing takes over and tracks progress.

**Common pattern (Lambda architecture)**: run your streaming job with `latest-offset` for real-time results, and if it goes down, use a separate batch job to backfill the gap.

---

# Windowed Aggregation

The real power of Flink — doing what plain consumers can't easily do.

PostgreSQL table for aggregated results (note the PRIMARY KEY for upserts):

```sql
CREATE TABLE processed_events_aggregated (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT,
    total_revenue DOUBLE PRECISION,
    PRIMARY KEY (window_start, PULocationID)
);
```

Flink aggregation job with 1-hour tumbling windows:

```python
def create_events_source_kafka(t_env):
    source_ddl = f"""
        CREATE TABLE events (
            PULocationID INTEGER,
            DOLocationID INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            tpep_pickup_datetime BIGINT,
            event_timestamp AS TO_TIMESTAMP_LTZ(tpep_pickup_datetime, 3),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'rides',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
    """
    t_env.execute_sql(source_ddl)
```

Two new lines compared to the pass-through:
- **`event_timestamp AS TO_TIMESTAMP_LTZ(...)`** — computed column converting epoch ms to a timestamp
- **`WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND`** — tells Flink when to publish window results

The aggregation query:

```sql
INSERT INTO processed_events_aggregated
SELECT
    window_start,
    PULocationID,
    COUNT(*) AS num_trips,
    SUM(total_amount) AS total_revenue
FROM TABLE(
    TUMBLE(TABLE events, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
)
GROUP BY window_start, PULocationID;
```

## Watermarks

Three pieces working together:

| Piece | Purpose |
|---|---|
| **Window** | What bucket to count into (e.g., 1 hour) |
| **Watermark** | When to publish the result (the trigger) |
| **Upsert (PRIMARY KEY)** | Safety net that corrects the result if something arrives after publishing |

The watermark is always N seconds behind the latest event timestamp Flink has seen. When the watermark passes the end of a window, Flink publishes that window's results. The N seconds is patience for stragglers — events that happened before the window ended but arrived a few seconds late.

The trade-off is **latency vs completeness**. A larger watermark = more patience for late events, but you wait longer before seeing results.

## Late Events and Upserts

If an event arrives **before** the watermark closes the window → it's counted normally.

If an event arrives **after** the watermark already closed the window → Flink sends a correction via the PRIMARY KEY (upsert). Without a PRIMARY KEY (append-only sink), the late event would be lost.

By default, allowed lateness is zero — events arriving after the watermark are discarded. You can set `ALLOWED LATENESS` to let Flink re-open closed windows, but this requires holding window state on disk for the tolerance duration.

---

# Window Types

## Tumbling Windows

Fixed-size, non-overlapping. Every event belongs to exactly one window. The most familiar if you come from batch processing — they just cut data into fixed segments.

```
|  Window 1  |  Window 2  |  Window 3  |
|  1 hour    |  1 hour    |  1 hour    |
```

```sql
TUMBLE(TABLE events, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
```

Use case: counting trips per hour, daily revenue summaries.

## Sliding Windows

Fixed-size, overlapping. An event can belong to multiple windows. Captures all possible windows of a given size at regular intervals.

```
|--- Window 1 (1 hour) ---|
      |--- Window 2 (1 hour) ---|
            |--- Window 3 (1 hour) ---|
      <- 15 min slide ->
```

```sql
HOP(TABLE events, DESCRIPTOR(event_timestamp), INTERVAL '15' MINUTE, INTERVAL '1' HOUR)
```

Use case: finding peaks and valleys, moving averages, surge detection.

## Session Windows

Dynamic windows based on **inactivity gaps**. The window doesn't close at a specified time — it closes after a specified amount of inactivity.

```
|--events--| gap |--events------| gap |--events--|
| Session 1|     |  Session 2   |     | Session 3|
```

Use case: grouping user behavior. A user logs in, clicks buttons, leaves for 2 minutes, comes back — still the same session. Set a session gap (e.g., 5 minutes of inactivity) and Flink groups all events within that session together.

---

# Flink in Production

Job submission depends on the deployment:

| Deployment | How Jobs Are Submitted |
|---|---|
| **Managed services** (AWS Kinesis Data Analytics, Google Cloud Dataflow) | Upload JAR or Python zip through web console or CLI |
| **Kubernetes** (self-hosted) | Bake job code into Docker image, or use Flink Kubernetes Operator to pull from S3/GCS |
| **Standalone cluster** | `flink run` CLI pointing to local file or HTTP/S3 URL |

Common pattern: code lives in git → CI builds artifact → pushes to registry/object store → triggers Flink cluster to pick it up.

### Spark Streaming vs Flink Streaming

| | Spark Streaming | Flink |
|---|---|---|
| **Architecture** | Micro-batch (pull) — pulses every 15-30 seconds | Continuous (push) — events flow as they arrive |
| **Latency** | Higher (startup alone ~1 minute) | Lower for truly real-time needs |
| **Sweet spot** | Hourly or every 15 minutes | Sub-second to seconds |

For most use cases the difference is negligible.

---

# Kafka Theory (Optional)

The theory section covers Kafka fundamentals with video lectures and Java examples:

**Stream Processing Basics:**
- Introduction to stream processing concepts
- Kafka fundamentals (architecture, topics, partitions)
- Confluent Cloud (managed Kafka)
- Producer-consumer patterns
- Configuration management

**Kafka Streams (advanced):**
- Stream basics
- Stream joins
- Stream testing
- Windowing
- ksqlDB and Connect
- Schema Registry

---

# Resources

- [Workshop Video](https://www.youtube.com/watch?v=YDUgFeHQzJU)
- [Workshop Code](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming/workshop)
- [Theory Section](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming/theory)
- [Apache Flink Documentation](https://flink.apache.org/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [kafka-python Library](https://kafka-python.readthedocs.io/)
{% endraw %}
