import pandas as pd
from dagster import (
    asset,
    multi_asset,
    AssetIn,
    AssetOut,
    Output,
    DailyPartitionsDefinition,
    OutputContext,
)

@multi_asset(
    ins={
        "upstream": AssetIn(
            key=["bronze", "ecom", "bronze_olist_orders_dataset"],
        )
    },
    outs={
        "olist_orders_dataset": AssetOut(
            io_manager_key="psql_io_manager",
            key_prefix=["warehouse", "public"],
            metadata={
                "primary_keys": ["order_id", "customer_id"],
                "columns": [
                    "order_id",
                    "customer_id",
                    "order_status",
                    "order_purchase_timestamp",
                    "order_approved_at",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                    "order_estimated_delivery_date",
                ],
            },
        )
    },
    compute_kind="PostgreSQL",
    name="olist_orders_dataset",
    partitions_def=DailyPartitionsDefinition(start_date="2017-01-01"),
    group_name="warehouse"
)
def dwh_olist_orders_dataset(context, upstream: pd.DataFrame) -> Output[pd.DataFrame]:
    context.log.info("Transforming bronze → warehouse layer")
    return Output(
        upstream,
        metadata={
            "schema": "public",
            "record_count": len(upstream),
        },
    )




def create_warehouse_asset(name: str):
    bronze_asset_name = f"bronze_{name}"

    @asset(
        name=f"gold_{name}",
        key_prefix=["warehouse", "public"],
        io_manager_key="psql_io_manager",
        compute_kind="PostgreSQL",
        group_name="warehouse",
        ins={
            bronze_asset_name: AssetIn(
                key=["bronze", "ecom", bronze_asset_name],
            )
        },
    )
    def gold_asset(context, **kwargs) -> Output[pd.DataFrame]:
        df = kwargs[bronze_asset_name]
        context.log.info(f"[LOAD] {bronze_asset_name} → warehouse_{name}, shape={df.shape}")
        context.log.info (df.head (10))
        return Output(df, metadata={"records": len(df)})

    return gold_asset


# Non-partitioned gold assets
gold_olist_order_items_dataset = create_warehouse_asset("olist_order_items_dataset")
gold_olist_order_payments_dataset = create_warehouse_asset("olist_order_payments_dataset")
gold_olist_products_dataset = create_warehouse_asset("olist_products_dataset")
