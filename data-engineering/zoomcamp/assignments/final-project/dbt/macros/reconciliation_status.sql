{%- macro reconciliation_status(order_tid, ga4_tid, order_revenue, ga4_revenue) -%}
    CASE
        WHEN {{ order_tid }} IS NOT NULL AND {{ ga4_tid }} IS NOT NULL
             AND ABS(CAST({{ order_revenue }} AS FLOAT64) - CAST({{ ga4_revenue }} AS FLOAT64)) < 0.01
            THEN 'matched'
        WHEN {{ order_tid }} IS NOT NULL AND {{ ga4_tid }} IS NOT NULL
            THEN 'revenue_mismatch'
        WHEN {{ order_tid }} IS NOT NULL AND {{ ga4_tid }} IS NULL
            THEN 'missing_in_ga4'
        WHEN {{ order_tid }} IS NULL AND {{ ga4_tid }} IS NOT NULL
            THEN 'ghost_order'
    END
{%- endmacro -%}
