select * from {{ ref ('stg_users')}}
select * from {{ ref ('stg_order_items')}}

with orders as (
  select * from {{ ref('stg_orders') }}
  
)
