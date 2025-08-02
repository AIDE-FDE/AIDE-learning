SELECT *
FROM {{ source('olist_dataset', 'olist_orders_dataset')}}
