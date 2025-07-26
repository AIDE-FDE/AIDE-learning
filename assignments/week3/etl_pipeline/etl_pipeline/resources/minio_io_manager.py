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
        path = context.asset_key.path
        layer, schema, table = path[0], path[1], path[-1]
        key = "/".join([layer, schema, table.replace(f"{layer}_", "")])

        # Tạo thư mục tmp trong dự án nếu chưa có
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

        file_name = "file-{}-{}.parquet".format(
            datetime.today().strftime('%Y%m%d%H%M%S'),
            "-".join(context.asset_key.path)
        )
        tmp_file_path = os.path.join(tmp_dir, file_name)

        if context.has_asset_partitions: # if the inputed asset is a partition asset
            partition_key = context.asset_partition_key
            key = f"{key}/{partition_key.replace('-', '')}.pq"
        else:
            key = f"{key}.pq"

        return key, tmp_file_path

    def handle_output(self, context: OutputContext, obj: pd.DataFrame):
        key_name, tmp_file_path = self._get_key_path (context)
        obj.to_parquet(tmp_file_path, index=False) # Save DataFrame to local parquet

        try:
            self.client.fput_object(
                bucket_name=self.bucket,
                object_name=key_name,
                file_path=tmp_file_path,
            )
            row_count = len (obj)
            context.add_output_metadata ({
                "path": key_name,
                "records": row_count,
                "tmp file": tmp_file_path
            })
            context.log.info(f"---- Uploaded asset to MinIO: {key_name}")
            os.remove(tmp_file_path)
        except Exception as e:
            raise e

    # def load_input(self, context: InputContext) -> pd.DataFrame:
    #     key_name, tmp_file_path = self._get_key_path (context)


    #     # Download file
    #     try:
    #         self.client.fget_object(
    #             bucket_name=self.bucket,
    #             object_name=key_name,
    #             file_path=tmp_file_path,
    #         )

    #         # Read to DataFrame
    #         df = pd.read_parquet(tmp_file_path)
    #         os.remove(tmp_file_path)

    #         context.log.info(f"Loaded asset from MinIO: {key_name}")
    #         return df
        
    #     except S3Error as e:
    #         raise FileNotFoundError(f"Can not find file {key_name} in bucket MinIO.") from e
    def load_input(self, context: InputContext) -> pd.DataFrame:
        path = context.asset_key.path
        layer, schema, table = path[0], path[1], path[-1]
        base_key = "/".join([layer, schema, table.replace(f"{layer}_", "")])
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        dfs = []

        if context.has_asset_partitions:
            for partition_key in context.asset_partition_keys:
                key_name = f"{base_key}/{partition_key.replace('-', '')}.pq"
                tmp_file_path = os.path.join(tmp_dir, f"{table}_{partition_key}.pq")

                try:
                    self.client.fget_object(
                        bucket_name=self.bucket,
                        object_name=key_name,
                        file_path=tmp_file_path,
                    )
                    df = pd.read_parquet(tmp_file_path)
                    dfs.append(df)
                    os.remove(tmp_file_path)
                    context.log.info(f"Loaded partition {partition_key} from MinIO")
                except S3Error as e:
                    raise FileNotFoundError(
                        f"Partition {partition_key} not found in MinIO at {key_name}"
                    ) from e
            return pd.concat(dfs, ignore_index=True)

        else:
            key_name = f"{base_key}.pq"
            tmp_file_path = os.path.join(tmp_dir, f"{table}.pq")

            try:
                self.client.fget_object(
                    bucket_name=self.bucket,
                    object_name=key_name,
                    file_path=tmp_file_path,
                )
                df = pd.read_parquet(tmp_file_path)
                os.remove(tmp_file_path)
                context.log.info(f"Loaded non-partitioned asset from MinIO")
                return df
            except S3Error as e:
                raise


