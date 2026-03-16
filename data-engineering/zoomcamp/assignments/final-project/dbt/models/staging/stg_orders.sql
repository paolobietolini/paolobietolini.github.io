SELECT
    transaction_id,
    order_date,
    total_amount AS order_revenue,
    item_count   AS order_item_count,
    customer_id
FROM {{ source('reconciliation', 'ext_orders') }}
WHERE transaction_id IS NOT NULL
