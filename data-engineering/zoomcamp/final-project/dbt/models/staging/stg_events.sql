-- stg_events.sql

with source as (
  select * from {{ source('raw_ecommerce', 'events') }}
),

cleaned as (
  select
    parse_date('%Y%m%d', event_date) as event_date,
    timestamp_micros(event_timestamp) as event_timestamp,
    cast(event_name as string) as event_name,
    cast(user_pseudo_id as string) as user_pseudo_id,
    cast(platform as string) as platform,
    coalesce(
      cast(user_id as string),
      concat('UNKNOWN_', row_number() over (order by user_pseudo_id))
    ) as user_id,
    user_id is null as is_user_id_missing,
    case
        when ecommerce.transaction_id = '(not set)' then null
        else cast(ecommerce.transaction_id as string)
    end as transaction_id,
    ecommerce.purchase_revenue as purchase_revenue,
    ecommerce.total_item_quantity as total_item_quantity,
    (select value.string_value from unnest(event_params) where key = 'page_location') as page_location,
    (select value.int_value from unnest(event_params) where key = 'ga_session_id') as ga_session_id,
    (select value.string_value from unnest(event_params) where key = 'campaign') as campaign
  from source
)

select * from cleaned
