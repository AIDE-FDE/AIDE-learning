# etl_pipeline/assets/bronze_layer.py

import pandas as pd
from dagster import asset, Output

TABLES = [
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_orders_dataset",
    "olist_products_dataset",
    "product_category_name_translation",
]

def create_bronze_asset(table_name):
    @asset(
        name=f"bronze_{table_name}",
        key_prefix=["bronze", "ecom"],  
        io_manager_key="minio_io_manager",
        required_resource_keys={"mysql_io_manager"},
        compute_kind="MySQL",
        group_name="bronze_layer"
    )
    def bronze_asset(context) -> Output[pd.DataFrame]:
        sql = f"SELECT * FROM {table_name}"
        df = context.resources.mysql_io_manager.extract_data(sql)
        context.log.info(f"Extracted {len(df)} rows from MySQL table: {table_name}")
        context.log.info (df.head (10))
        return Output(
            df,
            metadata={
                "source_table": table_name,
                "records": len(df),
            }
        )
    return bronze_asset

# Generate all bronze assets
bronze_olist_order_items_dataset = create_bronze_asset("olist_order_items_dataset")
bronze_olist_order_payments_dataset = create_bronze_asset("olist_order_payments_dataset")
bronze_olist_orders_dataset = create_bronze_asset("olist_orders_dataset")
bronze_olist_products_dataset = create_bronze_asset("olist_products_dataset")
bronze_product_category_name_translation = create_bronze_asset("product_category_name_translation")
