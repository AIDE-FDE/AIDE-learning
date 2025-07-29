import os
from contextlib import contextmanager
from datetime import datetime
from typing import Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from dagster import IOManager, OutputContext, InputContext
from minio import Minio


@contextmanager
def connect_minio(config):
    client = Minio(
        endpoint=config.get("endpoint_url"),
        access_key=config.get("aws_access_key_id"),
        secret_key=config.get("aws_secret_access_key"),
        secure=False,
    )
    try:
        yield client
    except Exception:
        raise  


class MinIOIOManager(IOManager):
    def __init__(self, config):
        self._config = config

    def _get_path(self, context: Union[InputContext, OutputContext]):
        layer, schema, table = context.asset_key.path
        base_key = "/".join([layer, schema, table.replace(f"{layer}_", "")])

        # Nếu có phân vùng
        if context.has_asset_partitions:
            partition_key = context.asset_partition_key
            key = f"{base_key}/partition={partition_key}/data.parquet"
        else:
            key = f"{base_key}.parquet"

        tmp_file_path = f"/tmp/{datetime.now().strftime('%Y%m%d%H%M%S')}_{table}.parquet"
        return key, tmp_file_path

    def handle_output(self, context: OutputContext, obj: pd.DataFrame):
        key_name, tmp_file_path = self._get_path(context)

        # Chuyển DataFrame -> Parquet
        table = pa.Table.from_pandas(obj)
        pq.write_table(table, tmp_file_path)

        bucket_name = self._config.get("bucket")

        try:
            with connect_minio(self._config) as client:
                # Tạo bucket nếu chưa có
                if not client.bucket_exists(bucket_name):
                    client.make_bucket(bucket_name)
                    context.log.info(f"Created bucket {bucket_name}")
                else:
                    context.log.debug(f"Bucket {bucket_name} already exists")

                # Upload lên MinIO
                client.fput_object(bucket_name, key_name, tmp_file_path)
                context.log.info(f"Uploaded {key_name} to bucket {bucket_name}")

                # Ghi metadata
                context.add_output_metadata({
                    "bucket": bucket_name,
                    "key": key_name,
                    "records": len(obj),
                    "tmp_path": tmp_file_path,
                })

        finally:
            # Xóa file tạm
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def load_input(self, context: InputContext) -> pd.DataFrame:
        key_name, tmp_file_path = self._get_path(context)
        bucket_name = self._config.get("bucket")

        try:
            with connect_minio(self._config) as client:
                if not client.bucket_exists(bucket_name):
                    raise FileNotFoundError(f"Bucket {bucket_name} does not exist.")

                # Download file về local
                client.fget_object(bucket_name, key_name, tmp_file_path)

                # Đọc thành pandas
                df = pd.read_parquet(tmp_file_path)
                return df

        finally:
            # Cleanup
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
