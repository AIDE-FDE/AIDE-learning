import pandas as pd
from dagster import asset, AssetExecutionContext, Output, AssetIn, AssetKey


@asset(
    ins={
        "fact_sales": AssetIn(key=AssetKey(["silver", "ecom", "fact_sales"])),
        "dim_products": AssetIn(key=AssetKey(["silver", "ecom", "dim_products"])),
    },
    io_manager_key="minio_io_manager",
    group_name="gold_layer",
    key_prefix=["gold", "ecom"],
    compute_kind="MinIO"
)
def gold_sales_by_category(
    context: AssetExecutionContext,
    fact_sales: pd.DataFrame,
    dim_products: pd.DataFrame,
) -> Output[pd.DataFrame]:
    df = fact_sales.copy()
    df["daily"] = df["order_purchase_timestamp"].dt.date

    daily_sales = (
        df.groupby(["daily", "product_id"])
        .agg(
            sales=pd.NamedAgg(column="payment_value", aggfunc="sum"),
            bills=pd.NamedAgg(column="order_id", aggfunc="nunique"),
        )
        .reset_index()
    )

    enriched = daily_sales.merge(dim_products, on="product_id", how="left")
    enriched["product_category_name_english"] = enriched["product_category_name_english"].fillna("Unknown")

    enriched["monthly"] = pd.to_datetime(enriched["daily"]).dt.to_period("M").astype(str)
    enriched["values_per_bills"] = enriched["sales"] / enriched["bills"]

    result = (
        enriched.groupby(["monthly", "product_category_name_english"])
        .agg(
            total_sales=pd.NamedAgg(column="sales", aggfunc="sum"),
            total_bills=pd.NamedAgg(column="bills", aggfunc="sum"),
        )
        .reset_index()
    )

    result["values_per_bills"] = result["total_sales"] / result["total_bills"]
    result = result.rename(columns={"product_category_name_english": "category"})

    context.log.info(result.head(10).to_string())

    return Output(
        result,
        metadata={"records": len(result), "columns": result.columns.tolist()},
    )