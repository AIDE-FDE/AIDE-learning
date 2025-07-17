import os
from contextlib import contextmanager
from shlex import join
import pandas as pd
from datetime import datetime
from typing import Union
from dagster import IOManager, OutputContext, InputContext
from minio import Minio
from minio.error import S3Error

@contextmanager
def connect_minio (config):
    client = Minio (
        endpoint=config.get ("endpoint_url"),
        access_key=config.get ("aws_access_key_id"),
        secret_key=config.get ("aws_secret_access_key"),
        secure=False
    )

    try:
        yield client
    except Exception:
        raise S3Error

class MinIOIOManager(IOManager):
    def __init__(self, config):
        self._config = config
        self.bucket = config["bucket"]

        with connect_minio(config) as client:
            self.client = client
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)

    def _get_key_path(self, context: Union[InputContext, OutputContext]):
        # e.g. warehouse/bronze/ecom/orders_dataset.parquet
        layer, schema, table = context.asset_key.path
        key = "/".join ([layer, schema, table.replace (f"{layer}_", "")])
        tmp_file_path = "/tmp/file-{}-{}.parquet".format (datetime.today ().strftime ('%Y%m%d%H%M%S'),
                                                          "-".join (context.asset_key.path))
        
        return f"{key}.pq", tmp_file_path

    def handle_output(self, context: OutputContext, obj: pd.DataFrame):
        key_name, tmp_file_path = self._get_key_path (context)
        obj.to_parquet(tmp_file_path, index=False) # Save DataFrame to local parquet

        try:
            self.client.fput_object(
                bucket_name=self.bucket,
                object_name=key_name,
                file_path=tmp_file_path,
            )
            context.log.info(f"---- Uploaded asset to MinIO: {key_name}")
            os.remove(tmp_file_path)
        except Exception as e:
            raise e

    def load_input(self, context: InputContext) -> pd.DataFrame:
        key_name, tmp_file_path = self._get_key_path (context)


        # Download file
        try:
            self.client.fget_object(
                bucket_name=self.bucket,
                object_name=key_name,
                file_path=tmp_file_path,
            )

            # Read to DataFrame
            df = pd.read_parquet(tmp_file_path)
            os.remove(tmp_file_path)

            context.log.info(f"Loaded asset from MinIO: {key_name}")
            return df
        
        except S3Error as e:
            raise FileNotFoundError(f"Can not find file {key_name} in bucket MinIO.") from e


