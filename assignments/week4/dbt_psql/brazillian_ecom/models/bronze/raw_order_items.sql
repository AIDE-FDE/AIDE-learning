SELECT *
FROM {{ source('olist_dataset', 'olist_order_items_dataset')}}
