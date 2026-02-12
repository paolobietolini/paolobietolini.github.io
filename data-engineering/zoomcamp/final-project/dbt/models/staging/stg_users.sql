-- stg_users.sql


with source as (
  select * from {{ source ('raw_backend', 'users')}}
),


cleaned as (
  select
    coalesce(                                                                                                
        cast(user_id as string),                              
        concat('UNKNOWN_', row_number() over (order by user_pseudo_id))                                      
    ) as user_id,                                             
    user_id is null as is_user_id_missing,
    cast(user_pseudo_id as string) as user_pseudo_id,
    cast(email as string) as user_email,
    cast(name as string) as user_name,
    datetime(cast(created_at as timestamp), 'Europe/Rome') as created_at
  from source
)

select * from cleaned