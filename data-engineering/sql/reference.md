---
layout: default
title: "SQL Reference for Data Engineering"
permalink: /data-engineering/sql/reference
---
{% raw %}

## Table of Contents

- [Type Casting](#type-casting)
- [NULL Handling](#null-handling)
  - [COALESCE](#coalesce)
  - [NULLIF](#nullif)
  - [IS NULL / IS NOT NULL](#is-null--is-not-null)
  - [IFNULL and IF](#ifnull-and-if)
- [CASE Expressions](#case-expressions)
- [Filtering](#filtering)
  - [WHERE](#where)
  - [HAVING](#having)
  - [IN and NOT IN](#in-and-not-in)
  - [BETWEEN](#between)
  - [LIKE](#like)
- [Aggregations](#aggregations)
  - [Basic Aggregates](#basic-aggregates)
  - [GROUP BY](#group-by)
  - [COUNTIF and SUMIF](#countif-and-sumif)
- [Joins](#joins)
  - [INNER JOIN](#inner-join)
  - [LEFT JOIN](#left-join)
  - [FULL OUTER JOIN](#full-outer-join)
  - [CROSS JOIN](#cross-join)
  - [Self Join](#self-join)
- [UNION and UNION ALL](#union-and-union-all)
- [Common Table Expressions (CTEs)](#common-table-expressions-ctes)
  - [Basic CTE](#basic-cte)
  - [Chaining CTEs](#chaining-ctes)
  - [dbt CTE Pattern](#dbt-cte-pattern)
- [Subqueries](#subqueries)
- [Window Functions](#window-functions)
  - [ROW_NUMBER](#row_number)
  - [RANK and DENSE_RANK](#rank-and-dense_rank)
  - [LAG and LEAD](#lag-and-lead)
  - [Running Totals and Averages](#running-totals-and-averages)
  - [PERCENTILE_CONT](#percentile_cont)
  - [FIRST_VALUE and LAST_VALUE](#first_value-and-last_value)
- [Date and Timestamp Functions](#date-and-timestamp-functions)
  - [Parsing and Formatting](#parsing-and-formatting)
  - [Date Arithmetic](#date-arithmetic)
  - [Extracting Parts](#extracting-parts)
  - [Truncating](#truncating)
  - [Timezone Conversion](#timezone-conversion)
- [String Functions](#string-functions)
- [Array and Struct Functions (BigQuery)](#array-and-struct-functions-bigquery)
  - [UNNEST](#unnest)
  - [ARRAY_AGG](#array_agg)
  - [Accessing Nested Fields](#accessing-nested-fields)
- [Surrogate Keys](#surrogate-keys)
- [Deduplication](#deduplication)
- [Incremental Patterns](#incremental-patterns)
- [Pivot and Unpivot](#pivot-and-unpivot)

---

# Type Casting

Convert values between types. Essential in staging models where raw data often arrives as strings.

```sql
CAST(user_id AS STRING)
CAST(price AS NUMERIC)
CAST(created_at AS TIMESTAMP)
CAST(quantity AS INT64)
```

**Safe cast** returns NULL instead of erroring on invalid input:

```sql
SAFE_CAST('not_a_number' AS INT64)   -- Returns NULL
CAST('not_a_number' AS INT64)         -- Errors
```

In staging models, cast everything explicitly:

```sql
SELECT
    CAST(order_id AS STRING) AS order_id,
    CAST(purchase_revenue AS NUMERIC) AS purchase_revenue,
    CAST(status AS STRING) AS order_status
FROM {{ source('raw', 'orders') }}
```

---

# NULL Handling

## COALESCE

Returns the first non-NULL value. Use it for fallback values:

```sql
-- Fallback to a generated ID when user_id is missing
COALESCE(
    CAST(user_id AS STRING),
    CONCAT('UNKNOWN_', ROW_NUMBER() OVER (ORDER BY created_at))
) AS user_id
```

Can chain multiple fallbacks:

```sql
COALESCE(preferred_name, first_name, email, 'Anonymous') AS display_name
```

## NULLIF

Returns NULL if the two values are equal. Useful for cleaning sentinel values:

```sql
-- Turn '(not set)' into actual NULL
NULLIF(transaction_id, '(not set)') AS transaction_id
```

Equivalent to the CASE pattern:

```sql
CASE WHEN transaction_id = '(not set)' THEN NULL ELSE transaction_id END
```

## IS NULL / IS NOT NULL

```sql
WHERE user_id IS NOT NULL           -- Keep only rows with a user_id
WHERE transaction_id IS NULL        -- Find rows missing a transaction
```

Use in boolean columns:

```sql
SELECT
    user_id IS NULL AS is_user_id_missing
FROM source
```

## IFNULL and IF

```sql
IFNULL(quantity, 0) AS quantity     -- Replace NULL with 0
IF(event_name = 'purchase', revenue, 0) AS purchase_revenue
```

---

# CASE Expressions

Conditional logic. Two forms:

**Simple CASE** (matching a single value):

```sql
CASE payment_type
    WHEN 1 THEN 'Credit card'
    WHEN 2 THEN 'Cash'
    WHEN 3 THEN 'No charge'
    ELSE 'Unknown'
END AS payment_description
```

**Searched CASE** (arbitrary conditions):

```sql
CASE
    WHEN total_amount > 100 THEN 'high'
    WHEN total_amount > 20 THEN 'medium'
    ELSE 'low'
END AS spend_tier
```

Cleaning sentinel values in staging:

```sql
CASE
    WHEN transaction_id = '(not set)' THEN NULL
    ELSE CAST(transaction_id AS STRING)
END AS transaction_id
```

---

# Filtering

## WHERE

Filters rows **before** aggregation:

```sql
SELECT * FROM orders
WHERE order_status = 'completed'
  AND created_at >= '2024-01-01'
  AND purchase_revenue > 0
```

## HAVING

Filters **after** aggregation (use with GROUP BY):

```sql
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5    -- Only users with more than 5 orders
```

## IN and NOT IN

```sql
WHERE event_name IN ('purchase', 'add_to_cart', 'begin_checkout')
WHERE platform NOT IN ('internal', 'test')
```

With a subquery:

```sql
WHERE user_id IN (
    SELECT user_id FROM orders WHERE purchase_revenue > 100
)
```

## BETWEEN

Inclusive on both ends:

```sql
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
WHERE price BETWEEN 10 AND 50
```

## LIKE

Pattern matching. `%` matches any characters, `_` matches one character:

```sql
WHERE page_location LIKE '%/checkout%'     -- Contains /checkout
WHERE email LIKE '%@gmail.com'             -- Ends with @gmail.com
WHERE item_name LIKE 'T-shirt%'            -- Starts with T-shirt
```

---

# Aggregations

## Basic Aggregates

```sql
COUNT(*)                    -- Total rows
COUNT(DISTINCT user_id)     -- Unique users
SUM(purchase_revenue)       -- Total revenue
AVG(price)                  -- Average price
MIN(created_at)             -- Earliest date
MAX(created_at)             -- Latest date
```

## GROUP BY

Group rows to compute aggregates per group:

```sql
SELECT
    item_category,
    COUNT(*) AS item_count,
    SUM(price * quantity) AS total_revenue,
    AVG(price) AS avg_price
FROM order_items
GROUP BY item_category
ORDER BY total_revenue DESC
```

## COUNTIF and SUMIF

BigQuery shortcuts for conditional aggregation:

```sql
SELECT
    user_pseudo_id,
    COUNT(*) AS total_events,
    COUNTIF(event_name = 'purchase') AS purchase_count,
    COUNTIF(event_name = 'page_view') AS pageview_count,
    SUM(IF(event_name = 'purchase', purchase_revenue, 0)) AS total_revenue
FROM events
GROUP BY user_pseudo_id
```

Standard SQL equivalent (works everywhere):

```sql
SUM(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS purchase_count
```

---

# Joins

```
  orders              users
 ┌──────────┐      ┌──────────┐
 │ order_id │      │ user_id  │
 │ user_id  │──┐   │ name     │
 │ amount   │  └──>│ email    │
 └──────────┘      └──────────┘
```

## INNER JOIN

Returns only rows that match in **both** tables:

```sql
SELECT o.order_id, o.amount, u.name
FROM orders o
INNER JOIN users u ON o.user_id = u.user_id
```

## LEFT JOIN

Returns **all** rows from the left table, NULLs where no match on the right:

```sql
-- All orders, even if the user doesn't exist
SELECT o.order_id, o.amount, u.name
FROM orders o
LEFT JOIN users u ON o.user_id = u.user_id
```

Find orphan rows (left table rows with no match):

```sql
SELECT o.*
FROM orders o
LEFT JOIN users u ON o.user_id = u.user_id
WHERE u.user_id IS NULL    -- Orders with no matching user
```

## FULL OUTER JOIN

Returns all rows from **both** tables, NULLs where no match on either side:

```sql
SELECT
    COALESCE(ga.transaction_id, be.transaction_id) AS transaction_id,
    ga.session_revenue,
    be.order_revenue
FROM ga_sessions ga
FULL OUTER JOIN backend_orders be ON ga.transaction_id = be.transaction_id
```

Useful for **reconciliation** — finding mismatches between two data sources.

## CROSS JOIN

Every row from the left paired with every row from the right. Rarely used, but useful for generating combinations:

```sql
SELECT d.date, c.category
FROM date_spine d
CROSS JOIN categories c
```

## Self Join

A table joined to itself. Useful for comparing rows within the same table:

```sql
-- Find orders placed by the same user on the same day
SELECT a.order_id, b.order_id, a.user_id, a.created_at
FROM orders a
INNER JOIN orders b
    ON a.user_id = b.user_id
    AND a.created_at = b.created_at
    AND a.order_id < b.order_id   -- Avoid duplicating pairs
```

---

# UNION and UNION ALL

Combine rows from multiple queries with the same columns:

```sql
-- UNION ALL keeps all rows (including duplicates) — faster
SELECT *, 'green' AS service_type FROM green_trips
UNION ALL
SELECT *, 'yellow' AS service_type FROM yellow_trips
```

`UNION` (without ALL) removes duplicates — slower, rarely needed.

**Rule:** Always use `UNION ALL` unless you specifically need deduplication.

---

# Common Table Expressions (CTEs)

## Basic CTE

A named temporary result set using `WITH`:

```sql
WITH active_users AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY user_id
)
SELECT * FROM active_users WHERE order_count > 5
```

## Chaining CTEs

Multiple CTEs separated by commas, each can reference the previous:

```sql
WITH events AS (
    SELECT * FROM {{ ref('stg_events') }}
    WHERE ga_session_id IS NOT NULL
),

sessions AS (
    SELECT
        user_pseudo_id,
        ga_session_id,
        MIN(event_timestamp) AS session_start,
        MAX(event_timestamp) AS session_end,
        COUNT(*) AS event_count,
        COUNTIF(event_name = 'purchase') > 0 AS has_purchase
    FROM events
    GROUP BY user_pseudo_id, ga_session_id
)

SELECT * FROM sessions
```

## dbt CTE Pattern

The standard dbt pattern: **import CTEs** at the top, then **logic CTEs**, then a **final SELECT**:

```sql
-- 1. Import CTEs (one per ref/source)
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

-- 2. Logic CTEs
orders_with_items AS (
    SELECT
        o.order_id,
        o.user_id,
        o.purchase_revenue,
        o.created_at,
        COUNT(oi.order_item_id) AS item_count,
        SUM(oi.price * oi.quantity) AS items_total
    FROM orders o
    LEFT JOIN order_items oi ON o.transaction_id = oi.transaction_id
    GROUP BY o.order_id, o.user_id, o.purchase_revenue, o.created_at
),

-- 3. Final SELECT
final AS (
    SELECT
        owi.*,
        u.user_name,
        u.user_email
    FROM orders_with_items owi
    LEFT JOIN users u ON owi.user_id = u.user_id
)

SELECT * FROM final
```

**Note:** BigQuery inlines CTEs — if referenced multiple times, they execute multiple times. Materialise as separate dbt models instead.

---

# Subqueries

A query nested inside another. CTEs are usually clearer, but subqueries work well for simple cases:

**In WHERE:**

```sql
SELECT * FROM orders
WHERE user_id IN (SELECT user_id FROM vip_users)
```

**Correlated subquery** (references the outer query — runs once per row):

```sql
SELECT *
FROM orders o
WHERE purchase_revenue > (
    SELECT AVG(purchase_revenue) FROM orders WHERE user_id = o.user_id
)
```

**In SELECT (scalar subquery):**

```sql
SELECT
    order_id,
    purchase_revenue,
    (SELECT AVG(purchase_revenue) FROM orders) AS avg_revenue
FROM orders
```

---

# Window Functions

Compute values across a set of rows **without collapsing** them. The `OVER()` clause defines the window.

```sql
FUNCTION() OVER (
    PARTITION BY group_column     -- Optional: split into groups
    ORDER BY sort_column          -- Optional: define row order
    ROWS BETWEEN ... AND ...      -- Optional: define frame
)
```

## ROW_NUMBER

Assigns a unique sequential number within each partition. The most-used window function in data engineering — essential for deduplication.

```sql
SELECT *,
    ROW_NUMBER() OVER (
        PARTITION BY user_id
        ORDER BY created_at DESC
    ) AS row_num
FROM users
```

Keep only the latest row per user:

```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM users
)
SELECT * FROM ranked WHERE rn = 1
```

Generate fallback IDs:

```sql
COALESCE(
    CAST(user_id AS STRING),
    CONCAT('UNKNOWN_', ROW_NUMBER() OVER (ORDER BY created_at))
) AS user_id
```

## RANK and DENSE_RANK

Like ROW_NUMBER but handle ties differently:

| Input values | ROW_NUMBER | RANK | DENSE_RANK |
|-------------|-----------|------|------------|
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 80 | 4 | 4 | 3 |

- `ROW_NUMBER`: Always unique (arbitrary tiebreak)
- `RANK`: Ties get same rank, next rank skipped
- `DENSE_RANK`: Ties get same rank, no gap

## LAG and LEAD

Access previous/next row values without a self-join:

```sql
SELECT
    event_date,
    purchase_revenue,
    LAG(purchase_revenue) OVER (ORDER BY event_date) AS prev_day_revenue,
    LEAD(purchase_revenue) OVER (ORDER BY event_date) AS next_day_revenue,
    purchase_revenue - LAG(purchase_revenue) OVER (ORDER BY event_date) AS day_over_day_change
FROM daily_revenue
```

With offset and default:

```sql
LAG(value, 2, 0) OVER (...)   -- 2 rows back, default 0 if no row exists
```

## Running Totals and Averages

```sql
SELECT
    event_date,
    daily_revenue,
    SUM(daily_revenue) OVER (ORDER BY event_date) AS running_total,
    AVG(daily_revenue) OVER (
        ORDER BY event_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS seven_day_avg
FROM daily_revenue
```

## PERCENTILE_CONT

Computes a percentile with linear interpolation:

```sql
SELECT
    item_category,
    price,
    PERCENTILE_CONT(price, 0.5) OVER (PARTITION BY item_category) AS median_price,
    PERCENTILE_CONT(price, 0.9) OVER (PARTITION BY item_category) AS p90_price
FROM order_items
```

## FIRST_VALUE and LAST_VALUE

```sql
SELECT
    user_pseudo_id,
    ga_session_id,
    event_name,
    FIRST_VALUE(page_location) OVER (
        PARTITION BY user_pseudo_id, ga_session_id
        ORDER BY event_timestamp
    ) AS landing_page,
    LAST_VALUE(page_location) OVER (
        PARTITION BY user_pseudo_id, ga_session_id
        ORDER BY event_timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS exit_page
FROM events
```

**Warning:** `LAST_VALUE` requires an explicit frame (`ROWS BETWEEN ... AND UNBOUNDED FOLLOWING`), otherwise it defaults to the current row.

---

# Date and Timestamp Functions

## Parsing and Formatting

```sql
-- String → Date
PARSE_DATE('%Y%m%d', '20240115')                -- 2024-01-15
PARSE_DATE('%d/%m/%Y', '15/01/2024')            -- 2024-01-15

-- String → Timestamp
PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', '2024-01-15 14:30:00')

-- Microseconds → Timestamp (GA4 stores timestamps this way)
TIMESTAMP_MICROS(1705312200000000)

-- Date/Timestamp → String
FORMAT_DATE('%Y-%m', order_date)                -- '2024-01'
FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', event_ts)    -- '2024-01-15 14:30'
```

## Date Arithmetic

```sql
DATE_ADD(order_date, INTERVAL 30 DAY)           -- 30 days later
DATE_SUB(order_date, INTERVAL 1 MONTH)          -- 1 month earlier
DATE_DIFF(end_date, start_date, DAY)            -- Days between
TIMESTAMP_DIFF(session_end, session_start, SECOND)  -- Seconds between
```

## Extracting Parts

```sql
EXTRACT(YEAR FROM order_date)         -- 2024
EXTRACT(MONTH FROM order_date)        -- 1
EXTRACT(DAY FROM order_date)          -- 15
EXTRACT(DAYOFWEEK FROM order_date)    -- 1 (Sunday) to 7 (Saturday)
EXTRACT(HOUR FROM event_timestamp)    -- 14
```

## Truncating

Round down to a boundary:

```sql
DATE_TRUNC(order_date, MONTH)         -- 2024-01-01 (first of month)
DATE_TRUNC(order_date, WEEK)          -- Start of the week
TIMESTAMP_TRUNC(event_ts, HOUR)       -- Round to the hour
```

Useful for grouping by time period:

```sql
SELECT
    DATE_TRUNC(created_at, MONTH) AS month,
    COUNT(*) AS order_count,
    SUM(purchase_revenue) AS revenue
FROM orders
GROUP BY month
ORDER BY month
```

## Timezone Conversion

```sql
DATETIME(CAST(created_at AS TIMESTAMP), 'Europe/Rome') AS created_at_rome
DATETIME(event_timestamp, 'Europe/Warsaw') AS event_time_local
```

---

# String Functions

```sql
CONCAT('user_', user_id)                -- Concatenation
LOWER(email)                            -- Lowercase
UPPER(name)                             -- Uppercase
TRIM(name)                              -- Remove leading/trailing whitespace
LTRIM(value, '0')                       -- Remove leading zeros
REPLACE(url, 'http://', 'https://')     -- Replace substring
SUBSTR(phone, 1, 3)                     -- First 3 characters
LENGTH(name)                            -- Character count
SPLIT(page_path, '/')[OFFSET(1)]        -- Split and access element
REGEXP_EXTRACT(url, r'/product/(\d+)')  -- Regex capture group
STARTS_WITH(url, 'https://')            -- Boolean check
ENDS_WITH(email, '@gmail.com')          -- Boolean check
```

---

# Array and Struct Functions (BigQuery)

GA4 data heavily uses nested/repeated fields. These functions are essential for working with it.

## UNNEST

Flattens an array into rows. Required to access BigQuery repeated fields:

```sql
-- GA4 event_params is an array of key-value structs
SELECT
    event_name,
    param.key,
    param.value.string_value,
    param.value.int_value
FROM events,
UNNEST(event_params) AS param
```

Extract a specific parameter (correlated subquery pattern — very common in GA4):

```sql
SELECT
    event_name,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') AS page_location,
    (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'campaign') AS campaign
FROM events
```

## ARRAY_AGG

Aggregate rows back into an array. Useful for picking first/last values in a group:

```sql
-- First non-null campaign in a session
ARRAY_AGG(campaign IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS first_campaign

-- Landing page (first page_location)
ARRAY_AGG(page_location ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS landing_page
```

`SAFE_OFFSET(0)` returns NULL if the array is empty instead of erroring.

## Accessing Nested Fields

BigQuery structs use dot notation:

```sql
SELECT
    ecommerce.transaction_id,
    ecommerce.purchase_revenue,
    ecommerce.total_item_quantity
FROM events
```

---

# Surrogate Keys

Generate deterministic unique keys from multiple columns. Essential in dbt for creating primary keys where none exist:

```sql
-- Using dbt_utils (MD5 hash of concatenated columns)
{{ dbt_utils.generate_surrogate_key(['transaction_id', 'item_id', 'row_num']) }} AS order_item_id
```

Manual equivalent (BigQuery):

```sql
TO_HEX(MD5(CONCAT(
    COALESCE(CAST(transaction_id AS STRING), ''),
    '|',
    COALESCE(CAST(item_id AS STRING), ''),
    '|',
    CAST(row_num AS STRING)
))) AS order_item_id
```

Use surrogate keys when:
- The source has no natural primary key
- The primary key spans multiple columns
- You need a single-column key for joins

---

# Deduplication

Remove duplicate rows. The most common pattern uses ROW_NUMBER:

```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id, event_date
            ORDER BY event_timestamp DESC     -- Keep the latest
        ) AS rn
    FROM events
)
SELECT * FROM ranked WHERE rn = 1
```

BigQuery also has `QUALIFY` (shorthand — avoids the CTE):

```sql
SELECT *
FROM events
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY user_id, event_date
    ORDER BY event_timestamp DESC
) = 1
```

---

# Incremental Patterns

In dbt, incremental models only process new/changed rows:

```sql
{{ config(materialized='incremental', unique_key='event_id') }}

SELECT *
FROM {{ source('raw', 'events') }}

{% if is_incremental() %}
    WHERE event_date >= (SELECT MAX(event_date) FROM {{ this }})
{% endif %}
```

`{{ this }}` refers to the existing table. On the first run, the WHERE clause is skipped (full load). On subsequent runs, only new data is processed.

---

# Pivot and Unpivot

**Pivot** (rows → columns):

```sql
SELECT
    user_id,
    COUNTIF(event_name = 'page_view') AS page_views,
    COUNTIF(event_name = 'add_to_cart') AS add_to_carts,
    COUNTIF(event_name = 'purchase') AS purchases
FROM events
GROUP BY user_id
```

**Unpivot** (columns → rows):

```sql
SELECT user_id, metric_name, metric_value
FROM user_metrics
UNPIVOT (metric_value FOR metric_name IN (page_views, add_to_carts, purchases))
```
{% endraw %}
