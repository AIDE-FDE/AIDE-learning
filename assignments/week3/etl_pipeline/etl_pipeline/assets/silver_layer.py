# etl_pipeline/assets/silver_layer.py

import pandas as pd
from dagster import asset, multi_asset, AssetKey, AssetIn, AssetOut, Output, AssetExecutionContext
from etl_pipeline.config.assets_config import daily_partition_def

asset_names = [
    "olist_products_dataset",
    "product_category_name_translation",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
]

ins = {
    name: AssetIn(key=AssetKey(["bronze", "ecom", f"bronze_{name}"]))
    for name in asset_names
}

outs = {
    name: AssetOut(
        io_manager_key="minio_io_manager",
        key_prefix=["silver", "ecom"],
        group_name="silver_layer",
        metadata={"compute_kind": "MinIO"},
        asset_key=AssetKey(["silver", "ecom", f"silver_{name}"])
    )
    for name in asset_names
}

@multi_asset(
    ins=ins,
    outs=outs,
    compute_kind="MinIO",
    group_name="silver_layer",
    key_prefix=["silver", "ecom"],
    io_manager_key="minio_io_manager",
)
def load_static_bronze_to_silver(context: AssetExecutionContext, **kwargs):
    for name, df in kwargs.items():
        silver_name = f"silver_{name}"
        context.log.info(f"Loading {silver_name} from bronze: shape={df.shape}")
        yield Output(df, output_name=name, metadata={"records": len(df)})




@asset(
    name="silver_olist_orders_dataset",  
    ins={"bronze_olist_orders_dataset": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_olist_orders_dataset"]))},
    partitions_def=daily_partition_def,
    io_manager_key="minio_io_manager",
    group_name="silver_layer",
    key_prefix=["silver", "ecom"],
    compute_kind="MinIO"
)
def silver_olist_orders_dataset(
    context: AssetExecutionContext,
    bronze_olist_orders_dataset: pd.DataFrame,
) -> Output[pd.DataFrame]:
    df = bronze_olist_orders_dataset
    context.log.info(f"Pass-through partitioned data: shape={df.shape}")
    return Output(df, metadata={"records": len(df), "columns": list(df.columns)})
