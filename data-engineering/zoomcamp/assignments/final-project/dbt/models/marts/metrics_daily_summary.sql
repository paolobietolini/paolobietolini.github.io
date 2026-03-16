SELECT
    report_date,
    reconciliation_status,
    COUNT(*)          AS transaction_count,
    SUM(revenue_diff) AS total_revenue_gap,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
        PARTITION BY report_date
    ) AS pct_of_daily_total
FROM {{ ref('fct_reconciliation') }}
GROUP BY 1, 2
