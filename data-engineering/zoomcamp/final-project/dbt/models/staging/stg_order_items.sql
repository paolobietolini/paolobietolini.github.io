-- stg_order_items.sql

with source as (
    select * from {{ source('raw_backend', 'order_items') }}
),

cleaned as (
    select
        case
            when transaction_id = '(not set)' then null
            else cast(transaction_id as string)
        end as transaction_id,
        cast(item_id as string) as item_id,
        cast(item_name as string) as item_name,
        cast(item_category as string) as item_category,
        cast(price as numeric) as price,
        coalesce(cast(quantity as numeric), 0) as quantity,
        row_number() over (order by transaction_id, item_id) as row_num
    from source
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['transaction_id', 'item_id','row_num']) }} as order_item_id,
        transaction_id,
        item_id,
        item_name,
        item_category,
        price,
        quantity
    from cleaned
)

select * from final