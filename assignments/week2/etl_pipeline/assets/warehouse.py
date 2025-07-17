import pandas as pd
from dagster import asset, AssetIn, AssetKey, AssetExecutionContext, Output

@asset(
    ins={"gold_sales_by_category": AssetIn(key=AssetKey(["gold", "ecom", "gold_sales_by_category"]))},
    io_manager_key="psql_io_manager",
    group_name="report_layer",
    key_prefix=["gold", "ecom"],
    compute_kind="PostgreSQL"
)
def sales_values_by_category(
    context: AssetExecutionContext,
    gold_sales_by_category: pd.DataFrame,
) -> Output[pd.DataFrame]:
    df = gold_sales_by_category.rename(columns={
        "total_sales": "sales",
        "total_bills": "bills",
        "values_per_bills": "values_per_bill",
    })

    context.log.info(f"Saving {len(df)} rows to PostgreSQL table gold.sales_values_by_category")

    return Output(
        df,
        metadata={
            "rows": len(df),
            "columns": list(df.columns),
        },
    )
