from dagster import asset, Output, AssetIn, AssetKey, AssetExecutionContext
import pandas as pd


@asset(
    ins={
        "bronze_olist_products_dataset": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_olist_products_dataset"])),
        "bronze_product_category_name_translation": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_product_category_name_translation"])),
    },
    io_manager_key="minio_io_manager",
    group_name="silver_layer",
    key_prefix=["silver", "ecom"],
    compute_kind="MinIO"
)
def dim_products(
    context: AssetExecutionContext,
    bronze_olist_products_dataset: pd.DataFrame,
    bronze_product_category_name_translation: pd.DataFrame,
) -> Output[pd.DataFrame]:
    df = bronze_olist_products_dataset.merge(
        bronze_product_category_name_translation,
        how="left",
        on="product_category_name",
    )
    df["product_category_name_english"] = df["product_category_name_english"].fillna("Unknown")

    df = df[["product_id", "product_category_name_english"]]

    context.log.info(df.head(10).to_string())

    return Output(
        df,
        metadata={"records": len(df), "columns": df.columns.tolist()},
    )


@asset(
    ins={
        "bronze_olist_order_items_dataset": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_olist_order_items_dataset"])),
        "bronze_olist_orders_dataset": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_olist_orders_dataset"])),
        "bronze_olist_order_payments_dataset": AssetIn(key=AssetKey(["bronze", "ecom", "bronze_olist_order_payments_dataset"])),
    },
    io_manager_key="minio_io_manager",
    group_name="silver_layer",
    key_prefix=["silver", "ecom"],
    compute_kind="MinIO"
)
def fact_sales(
    context: AssetExecutionContext,
    bronze_olist_order_items_dataset: pd.DataFrame,
    bronze_olist_orders_dataset: pd.DataFrame,
    bronze_olist_order_payments_dataset: pd.DataFrame,
) -> Output[pd.DataFrame]:
    df = bronze_olist_orders_dataset.merge(
        bronze_olist_order_items_dataset, on="order_id", how="inner"
    ).merge(
        bronze_olist_order_payments_dataset, on="order_id", how="inner"
    )

    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce").fillna(0)

    df = df[df["order_status"] == "delivered"]

    df = df[[
        "order_id",
        "customer_id",
        "order_purchase_timestamp",
        "product_id",
        "payment_value",
        "order_status",
    ]]

    context.log.info(df.head(10).to_string())

    return Output(
        df,
        metadata={"records": len(df), "columns": df.columns.tolist()},
    )
