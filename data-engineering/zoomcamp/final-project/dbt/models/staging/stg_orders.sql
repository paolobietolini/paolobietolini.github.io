-- stg_orders.sql

with source as (
  select * from {{ source ('raw_backend', 'orders')}}
),

cleaned as (
  select
    coalesce(
      cast(order_id as string),
      concat('ORDER_', row_number() over (order by created_at))
    ) as order_id,
    case
        when transaction_id = '(not set)' then null
        else cast(transaction_id as string)
    end as transaction_id,
    cast(purchase_revenue as numeric) as purchase_revenue,
    cast(shipping_value as numeric) as shipping_value,
    cast(total_item_quantity as numeric) as total_item_quantity,
    coalesce(                                                                                                
      cast(user_id as string),                              
      concat('UNKNOWN_', row_number() over (order by created_at))                                      
    ) as user_id,
    cast(status as string) as order_status,
    parse_date('%Y%m%d', created_at) as created_at
  from source
)


select * from cleaned