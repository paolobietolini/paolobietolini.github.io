{{
    config(
        partition_by={
            "field": "report_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["reconciliation_status"]
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

ga4 AS (
    SELECT * FROM {{ ref('stg_ga4_purchases') }}
),

reconciled AS (
    SELECT
        COALESCE(o.transaction_id, g.transaction_id) AS transaction_id,
        COALESCE(o.order_date, g.purchase_date)      AS report_date,
        o.order_date,
        g.purchase_date,
        o.order_revenue,
        g.ga4_revenue,
        ABS(
            COALESCE(CAST(o.order_revenue AS FLOAT64), 0)
          - COALESCE(CAST(g.ga4_revenue   AS FLOAT64), 0)
        ) AS revenue_diff,
        {{ reconciliation_status('o.transaction_id', 'g.transaction_id', 'o.order_revenue', 'g.ga4_revenue') }} AS reconciliation_status
    FROM orders o
    FULL OUTER JOIN ga4 g ON o.transaction_id = g.transaction_id
)

SELECT * FROM reconciled
