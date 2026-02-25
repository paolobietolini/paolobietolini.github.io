-- int_ga4_sessions.sql

with events as (
  select * from {{ ref('stg_events') }}
  where ga_session_id is not null
),

sessions as (
  select
    user_pseudo_id,
    ga_session_id,
    min(event_timestamp) as session_start,
    max(event_timestamp) as session_end,

    -- landing page: First page_location in the session
    array_agg(page_location order by event_timestamp asc limit 1)[safe_offset(0)] as landing_page,

    -- campaign: first non null value
    array_agg(campaign ignore nulls order by event_timestamp asc limit 1)[safe_offset(0)] as campaign,

    count(*) as event_count,

    -- purchase
    countif(event_name = 'purchase') > 0 as has_purchase,

    -- revenue
    sum(if(event_name = 'purchase', purchase_revenue, 0)) as purchase_revenue,

    -- transaction_id:
    array_agg(transaction_id ignore nulls order by event_timestamp asc limit 1)[safe_offset(0)] as transaction_id

  from events
  group by user_pseudo_id, ga_session_id
)

select * from sessions