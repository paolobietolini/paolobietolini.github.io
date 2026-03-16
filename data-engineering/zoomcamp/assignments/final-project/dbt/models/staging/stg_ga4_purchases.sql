SELECT
    transaction_id,
    event_date   AS purchase_date,
    revenue      AS ga4_revenue,
    item_count   AS ga4_item_count,
    user_id      AS ga4_user_id
FROM {{ source('reconciliation', 'ext_ga4_purchases') }}
WHERE transaction_id IS NOT NULL
