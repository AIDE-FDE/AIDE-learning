from dagster import Definitions
from resources.mysql_io_manager import MySQLIOManager
from resources.minio_io_manager import MinIOIOManager
from config import *
from assets.bronze_layer import *


defs = Definitions(
    assets=[bronze_olist_orders_dataset],
    resources={
        "mysql_io_manager": MySQLIOManager(MYSQL_CONFIG),
        'minio_io_manager': MinIOIOManager(MINIO_CONFIG)
    },
)