SELECT *
FROM {{ source('olist_dataset', 'olist_order_payments_dataset')}}
