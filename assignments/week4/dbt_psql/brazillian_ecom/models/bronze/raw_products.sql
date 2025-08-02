SELECT *
FROM {{ source('olist_dataset', 'olist_products_dataset')}}
