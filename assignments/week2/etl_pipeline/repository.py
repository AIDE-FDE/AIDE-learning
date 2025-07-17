from dagster import Definitions
from resources.mysql_io_manager import MySQLIOManager
from resources.minio_io_manager import MinIOIOManager
from resources.psql_io_manager import PostgreSQLIOManager
from config import *
from assets.bronze_layer import *
from assets.silver_layer import *
from assets.gold_layer import *
from assets.warehouse import *


defs = Definitions(
    assets=[
        bronze_olist_order_items_dataset,
        bronze_olist_order_payments_dataset,
        bronze_olist_orders_dataset,
        bronze_olist_products_dataset,
        bronze_product_category_name_translation,
        dim_products,
        fact_sales,
        gold_sales_by_category,
        sales_values_by_category
    ],
    resources={
        "mysql_io_manager": MySQLIOManager(MYSQL_CONFIG),
        'minio_io_manager': MinIOIOManager(MINIO_CONFIG),
        'psql_io_manager': PostgreSQLIOManager (PSQL_CONFIG)
    },
)