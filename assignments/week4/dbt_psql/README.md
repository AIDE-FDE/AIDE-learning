# Quy trình thực hiện
## Khởi tạo `docker-compose.yml` và các thiết lập liên quan:
- `docker-compose.yml`:
    ```yml
    version: "3.9"
    services:
        de_psql:
        image: postgres:15
        container_name: de_psql
        volumes:
            - ./postgresql:/var/lib/postgresql/data
        ports:
            - "5433:5432"
        env_file:
            - .env
    networks:
    de_network:
        driver: bridge
        name: de_network
    ```
- `.env`:
    ```
    # PostgreSQL
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=brazillian_ecommerce
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=admin123
    POSTGRES_HOST_AUTH_METHOD=trust
    ```
- `Makefile`:
    ```makefile
    up:
        docker-compose up -d

    down:
        docker-compose down

    create_table:
        docker exec de_psql psql postgres://admin:admin123@localhost:5432/brazillian_ecommerce -f /tmp/psql_schemas.sql

    to_psql:
        docker exec -ti de_psql psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

    dbt_build:
        dbt build --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom

    dbt_run:	
        dbt run --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom

    dbt_docs:
        dbt docs generate --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom && dbt docs serve --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom

    dbt_seed:
        dbt seed --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom --full-refresh

    ```
- Chuẩn bị folder dữ liệu `brazillian-ecommerce`:
    ```
    📦brazilian-ecommerce
        ┣ 📜olist_customers_dataset.csv
        ┣ 📜olist_geolocation_dataset.csv
        ┣ 📜olist_orders_dataset.csv
        ┣ 📜olist_order_items_dataset.csv
        ┣ 📜olist_order_payments_dataset.csv
        ┣ 📜olist_order_reviews_dataset.csv
        ┣ 📜olist_products_dataset.csv
        ┣ 📜olist_sellers_dataset.csv
        ┗ 📜product_category_name_translation.csv
    ```

- tạo folder với file để tạo table trong postgresql: `scripts/psql_schemas.sql`:
    ```sql
    DROP TABLE IF EXISTS olist_products_dataset CASCADE;
    CREATE TABLE olist_products_dataset (
        product_id varchar(32),
        product_category_name varchar(64),
        product_name_lenght int4,
        product_description_lenght int4,
        product_photos_qty int4,
        product_weight_g int4,
        product_length_cm int4,
        product_height_cm int4,
        product_width_cm int4,
        PRIMARY KEY (product_id)
    );

    DROP TABLE IF EXISTS olist_orders_dataset CASCADE;
    CREATE TABLE olist_orders_dataset (
        order_id varchar(32),
        customer_id varchar(32),
        order_status varchar(16),
        order_purchase_timestamp varchar(32),
        order_approved_at varchar(32),
        order_delivered_carrier_date varchar(32),
        order_delivered_customer_date varchar(32),
        order_estimated_delivery_date varchar(32),
        PRIMARY KEY (order_id, customer_id)
    );

    DROP TABLE IF EXISTS olist_order_items_dataset CASCADE;
    CREATE TABLE olist_order_items_dataset (
        order_id varchar(32),
        order_item_id int4,
        product_id varchar(32),
        seller_id varchar(32),
        shipping_limit_date varchar(32),
        price float4,
        freight_value float4,
        PRIMARY KEY (order_id, order_item_id, product_id, seller_id)
    );

    DROP TABLE IF EXISTS olist_order_payments_dataset CASCADE;
    CREATE TABLE olist_order_payments_dataset (
        order_id varchar(32),
        payment_sequential int4,
        payment_type varchar(16),
        payment_installments int4,
        payment_value float4,
        PRIMARY KEY (order_id, payment_sequential)
    );
    ```

- Thiết lập PostgreSQL server hỗ trợ nạp dữ liệu từ file CSV (folder brazilian-ecommerce/ là Kaggle CSV files sau khi download):
    ```bash
    # copy CSV data to psql container
    docker cp brazilian-ecommerce/ de_psql:/tmp/
    # copy SQL script data to psql container
    docker cp scripts/psql_schemas.sql de_psql:/tmp/
    # run commands to create tables
    docker exec de_psql psql postgres://admin:admin123@localhost:5432 brazillian_ecommerce -f /tmp/psql_schemas.sql
    # run commands to load data into tables
    docker exec -ti de_psql psql postgres://admin:admin123@localhost:5432/brazillian_ecommerce


    COPY olist_order_items_dataset FROM '/tmp/brazilian-ecommerce/olist_order_items_dataset.csv' DELIMITER ',' CSV HEADER;

    COPY olist_order_payments_dataset FROM '/tmp/brazilian-ecommerce/olist_order_payments_dataset.csv' DELIMITER ',' CSV HEADER;

    COPY olist_orders_dataset FROM '/tmp/brazilian-ecommerce/olist_orders_dataset.csv' DELIMITER ',' CSV HEADER;

    COPY olist_products_dataset FROM '/tmp/brazilian-ecommerce/olist_products_dataset.csv' DELIMITER ',' CSV HEADER;


    # check records of tables
    SELECT * FROM olist_order_items_dataset LIMIT 10;
    SELECT * FROM olist_order_payments_dataset LIMIT 10;
    SELECT * FROM olist_orders_dataset LIMIT 10;
    SELECT * FROM olist_products_dataset LIMIT 10;
    ```
- Cài đặt các thư viện cần thiết
    ```bash
    pip install dbt-core dbt-postgres pytz
    ```

- Khởi tạo project:
    ```bash
    dbt init --profiles-dir ./
    # sau đó điền các thông tin liên qua: chú ý tên project là brazillian_ecom
    ```


## Thiết lập dbt:
***Xem các thiết lập ở hai file `brazillian_ecom/dbt_project.yml` và file `brazillian_ecom/profiles.yml`***

## Tạo các model
***Xem ở thư mục `brazillian_ecom/models`***

## Định nghĩa các source
***Xem ở thư mục `brazillian_ecom/models/_olist_bronze_source.yml`***

## Tạo seed data
copy file `product_category_name_translation.csv` vào `brazillian_ecom/seeds`

và sau đó chạy lệnh:
```bash
make dbt_seed
# or
dbt seed --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom --full-refresh
```

## Tiến hành kiểm tra kết quả:
- build các models:
```bash
dbt build --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom
# or
make dbt_build
```

- run các model và source
```bash
dbt run --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom
# or
make dbt_run
```

- tiến hành kiểm tra trong DBeaver, và xem docs của DBT:
```bash
dbt docs generate --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom && dbt docs serve --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom
# or
make dbt_docs
```

## Tạo pivot table cho `sales_values_by_category.sql` (OPTIONAL)
- tạo `brazillian_ecom/packages.yml`:
```yml
packages:
  - package: dbt-labs/dbt_utils
    version: 0.9.2
```

- chạy `cd brazillian && dbt deps` để cài các packages

- Tạo `sales_values_by_category_pivot.sql` trong `brazillian_ecom/models/gold`:
```sql
WITH base AS (
    SELECT 
        category,
        monthly,
        total_bills
    FROM {{ ref('sales_values_by_category') }}
),

pivoted AS (
    SELECT 
        category,
        {% set pivoted_cols = dbt_utils.pivot(
            column='monthly',
            values=[
                '2018-08', '2018-07', '2018-06', '2018-05', '2018-04',
                '2018-03', '2018-02', '2018-01', '2017-12', '2017-11',
                '2017-10', '2017-09', '2017-08', '2017-07', '2017-06',
                '2017-05', '2017-04', '2017-03', '2017-02', '2017-01',
                '2016-12', '2016-10'
            ],  
            agg='sum',
            then_value='total_bills'
        ) %}
        {{ pivoted_cols }}
    FROM base
    GROUP BY category
)

SELECT * FROM pivoted
```
> để lấy được danh sách các tháng, chạy scripts `get_month.sql` trong thư mục scripts


## Tạo macros phân loại bill cho cho `sales_values_by_category.sql` (OPTIONAL):
- trong `brazillian_ecom/macros` tạo file `classify_bill.sql`:
```sql
{% macro classify_bills(column_name) %}
    CASE
        WHEN {{ column_name }} < 100 THEN 'D'
        WHEN {{ column_name }} >= 100 AND {{ column_name }} < 200 THEN 'C'
        WHEN {{ column_name }} >= 200 AND {{ column_name }} < 300 THEN 'B'
        ELSE 'A'
    END
{% endmacro %}
```

- Tạo `sales_values_by_category_classify_bill.sql` trong `brazillian_ecom/models/gold` để dùng macro đã tạo:
```sql
select
    *
    , {{ classify_bills ('total_bills')}} as class
from {{ ref ("sales_values_by_category")}}
```

- Tiến hành build và chạy lại docs, đồng thời kiếm tra trong postresql

> các kết quả thực hiện nằm ở phần tiếp theo KẾT QUẢ THỰC HIỆN

# Kết quả thực hiện
![alt text](../images/image_54.png)
![alt text](../images/image_55.png)
![alt text](../images/image_56.png)
![alt text](../images/image_57.png)
