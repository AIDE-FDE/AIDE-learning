from contextlib import contextmanager
from datetime import datetime
import pandas as pd
from dagster import IOManager, OutputContext, InputContext
from sqlalchemy import create_engine, text


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
        raise 


class PostgreSQLIOManager(IOManager):
    def __init__(self, config):
        self._config = config

    def load_input(self, context: InputContext) -> pd.DataFrame:
        pass

    def handle_output(self, context: OutputContext, obj: pd.DataFrame):
        schema, table = context.asset_key.path[0], context.asset_key.path[-1]
        tmp_tbl = f"{table}_tmp_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
        metadata = context.metadata or {}
        primary_keys = metadata.get("primary_keys", [])
        ls_columns = metadata.get("columns", obj.columns.tolist())

        with connect_psql(self._config) as engine:
            with engine.connect() as conn:
                # Create schema if not exists
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))

                # Check if table exists
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = :schema AND table_name = :table
                    );
                """), {"schema": schema, "table": table})
                table_exists = result.scalar()

                if not table_exists:
                    context.log.warning(f"Table {schema}.{table} does not exist. Creating new one.")
                    obj.to_sql(name=table, con=engine, schema=schema, index=False, if_exists="replace")
                    return

                # Create temp table based on existing structure
                conn.execute(text(f"""
                    CREATE TEMP TABLE {tmp_tbl} (LIKE {schema}.{table} INCLUDING ALL);
                """))

                # Insert data into temp table
                obj[ls_columns].to_sql(
                    name=tmp_tbl,
                    con=engine,
                    schema='public',  # Temp tables always go to 'pg_temp' or 'public'
                    if_exists='replace',
                    index=False,
                    chunksize=10000,
                    method="multi"
                )

            with engine.begin() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tmp_tbl}"))
                row_count = result.scalar()
                context.log.info(f"Temp table row count: {row_count}")

                if primary_keys:
                    join_condition = " AND ".join(
                        [f"{schema}.{table}.{k} = {tmp_tbl}.{k}" for k in primary_keys]
                    )
                    upsert_sql = f"""
                        DELETE FROM {schema}.{table}
                        USING {tmp_tbl}
                        WHERE {join_condition};

                        INSERT INTO {schema}.{table}
                        SELECT * FROM {tmp_tbl};
                    """
                else:
                    upsert_sql = f"""
                        TRUNCATE TABLE {schema}.{table};
                        INSERT INTO {schema}.{table}
                        SELECT * FROM {tmp_tbl};
                    """

                conn.execute(text(upsert_sql))
                conn.execute(text(f"DROP TABLE IF EXISTS {tmp_tbl}"))

