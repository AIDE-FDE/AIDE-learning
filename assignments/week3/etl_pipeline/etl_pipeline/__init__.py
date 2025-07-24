from dagster import Definitions
from .assets import my_first_asset

defs = Definitions(
    assets=[my_first_asset],
)

