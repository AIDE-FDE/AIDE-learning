DROP TABLE IF EXISTS public.product_category_name_translation;
CREATE TABLE public.product_category_name_translation (
    product_category_name VARCHAR(64),
    product_category_name_english VARCHAR(64),
    PRIMARY KEY (product_category_name)
);

DROP TABLE IF EXISTS public.olist_products_dataset;
CREATE TABLE public.olist_products_dataset (
    product_id VARCHAR(32),
    product_category_name VARCHAR(64),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER,
    PRIMARY KEY (product_id)
);

DROP TABLE IF EXISTS public.olist_orders_dataset;
CREATE TABLE public.olist_orders_dataset (
    order_id VARCHAR(32),
    customer_id VARCHAR(32),
    order_status VARCHAR(16),
    order_purchase_timestamp VARCHAR(32),
    order_approved_at VARCHAR(32),
    order_delivered_carrier_date VARCHAR(32),
    order_delivered_customer_date VARCHAR(32),
    order_estimated_delivery_date VARCHAR(32),
    PRIMARY KEY (order_id)
);

DROP TABLE IF EXISTS public.olist_order_items_dataset;
CREATE TABLE public.olist_order_items_dataset (
    order_id VARCHAR(32),
    order_item_id INTEGER,
    product_id VARCHAR(32),
    seller_id VARCHAR(32),
    shipping_limit_date VARCHAR(32),
    price REAL,
    freight_value REAL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (order_id, order_item_id, product_id, seller_id),
    FOREIGN KEY (order_id) REFERENCES public.olist_orders_dataset(order_id),
    FOREIGN KEY (product_id) REFERENCES public.olist_products_dataset(product_id)
);

DROP TABLE IF EXISTS public.olist_order_payments_dataset;
CREATE TABLE public.olist_order_payments_dataset (
    order_id VARCHAR(32),
    payment_sequential INTEGER,
    payment_type VARCHAR(16),
    payment_installments INTEGER,
    payment_value REAL,
    PRIMARY KEY (order_id, payment_sequential)
);
