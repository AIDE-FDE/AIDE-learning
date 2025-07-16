import pandas as pd
from dagster import asset, Output, Definitions
from resources.mysql_io_manager import MySQLIOManager


@asset(
    required_resource_keys={"mysql_io_manager"},
    key_prefix=["bronze", "ecom"],
    compute_kind="MySQL"
)
def bronze_olist_orders_dataset(context) -> Output[pd.DataFrame]:
    sql_stm = "SELECT * FROM olist_orders_dataset"
    pd_data = context.resources.mysql_io_manager.extract_data(sql_stm)

    return Output(
        pd_data,
        metadata={
            "table": "olist_orders_dataset",
            "records count": len(pd_data),
        },
    )


MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "brazillian_ecommerce",
    "user": "admin",
    "password": "admin123",
}

defs = Definitions(
    assets=[bronze_olist_orders_dataset],
    resources={
        "mysql_io_manager": MySQLIOManager(MYSQL_CONFIG),
    },
)