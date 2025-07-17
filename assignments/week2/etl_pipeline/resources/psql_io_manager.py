from contextlib import contextmanager

import pandas as pd
from dagster import IOManager, OutputContext, InputContext
from sqlalchemy import create_engine
from tomlkit import table


@contextmanager
def connect_psql(config):
    conn_info = (
        f"postgresql+psycopg2://{config['user']}:{config['password']}" 
        + f"@{config['host']}:{config['port']}"
        + f"/{config['database']}"
    )

    db_conn = create_engine(conn_info)
    try:
        yield db_conn
    except Exception:
        raise Exception
    

class PostgreSQLIOManager(IOManager):
    def __init__(self, config):
        self._config = config

    def load_input (self, context: InputContext) -> pd.DataFrame:
        schema, table = context.asset_key.path[0], context.asset_key.path[-1]
        query = f'SELECT * FROM "{schema}"."{table}"'

        with connect_psql(self._config) as engine:
            try:
                df = pd.read_sql_query(query, engine)
                context.log.info(f"Loaded table from PostgreSQL: {schema}.{table} ({len(df)} rows)")
                return df
            except Exception as e:
                raise RuntimeError(f"Failed to load table {schema}.{table} from PostgreSQL: {e}") from e


    def handle_output (self, context: OutputContext, obj: pd.DataFrame):
        schema, table = context.asset_key.path[0], context.asset_key.path[-1]

        with connect_psql(self._config) as engine:
            try:
                obj.to_sql(
                    name=table,
                    con=engine,
                    schema=schema,
                    if_exists="append", 
                    index=False,
                )
                context.log.info(f"Wrote DataFrame to PostgreSQL table: {schema}.{table}")
            except Exception as e:
                context.log.error(f"Failed to write to PostgreSQL: {e}")
                raise
