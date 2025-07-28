from dagster import Definitions, load_assets_from_modules, define_asset_job

from etl_pipeline.assets import testing, bronze_layer #, silver_layer #, gold_layer, warehouse # noqa: TID252

from etl_pipeline.resources.mysql_io_manager import MySQLIOManager
from etl_pipeline.resources.minio_io_manager import MinIOIOManager
from etl_pipeline.resources.psql_io_manager import PostgreSQLIOManager

from etl_pipeline.config.io_manager_config import *
from etl_pipeline.config.assets_config import daily_partition_def


daily_job = define_asset_job(
    name="daily_pipeline_job",
    selection="*",  
    partitions_def=daily_partition_def, 
)


all_assets = load_assets_from_modules([testing, bronze_layer]) # 

defs = Definitions(
    assets=all_assets,
    jobs=[
        daily_job
    ],
    resources={
        "mysql_io_manager": MySQLIOManager(MYSQL_CONFIG),
        'minio_io_manager': MinIOIOManager(MINIO_CONFIG),
        'psql_io_manager': PostgreSQLIOManager (PSQL_CONFIG)

    }
)
