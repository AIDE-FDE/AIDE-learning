from contextlib import contextmanager
from datetime import datetime
from operator import index
from os import name

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

        tmp_tbl = f"{table}_tmp_{datetime.now ().strftime ('%Y_%m_%d')}"

        with connect_psql(self._config) as engine:
            primary_keys = (context.metadata or {}).get ("primary_keys", {})
            ls_columns = (context.metadata or {}).get ("columns", {})

            with engine.connect () as cursor:
                # tmp file creattion
                cursor.execute (
                    f"CREATE TEMP TABLE IF NOT EXISTS {tmp_tbl} (LIKE {schema}.{table})"
                )

                # insert new data
                obj[ls_columns].to_sql (
                    name=tmp_tbl,
                    con=engine,
                    schema=schema,
                    if_exists="replace",
                    index=False,
                    chunksize=10000,
                    method="multi"
                )

            with engine.connect () as cursor:
                result = cursor.execute (f"SELECT COUNT (*) FROM {tmp_tbl}")
                for row in result:
                    print (f"temp table records: {row}")

                    if len (primary_keys) > 0:
                        conditions = " AND ".join ([
                            f"""
                            {schema}.{table}."{k}" = {tmp_tbl}."{k}"
                            """ for k in primary_keys
                        ])


                        command = f"""
                            BEGIN TRANSACTION
                            DELETE FROM {schema}.{table}
                            USING {tmp_tbl}
                            WHERE {conditions};

                            INSERT INTO {schema}.{table}
                            SELECT * FROM {tmp_tbl}

                            END TRANSACTION
                        """
                    else:
                        command = f"""
                            BEGIN TRANSACTION
                            TRUNCATE TABLE {schema}.{table};

                            INSERT INTO {schema}.{table}
                            SELECT * FROM {tmp_tbl}

                            END TRANSACTION
                        """

                    cursor.execute (command)
                    cursor.execute (f"DROP TABLE IF EXISTS {tmp_tbl}")