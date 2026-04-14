import logging
import asyncio
import click
from pathlib import Path

from core.aws.session import get_s3_session
from core.config.loader import get_settings

try:
    from botocore.exceptions import ClientError
except ModuleNotFoundError:
    class ClientError(Exception):
        pass

logger = logging.getLogger(__name__)


class S3BucketManager:
    def __init__(self, bucket_name: str = None):
        self.config = get_settings()
        self.bucket_name = bucket_name or self.config.aws.bucket_name
        if not self.bucket_name:
            raise click.UsageError(
                "Missing bucket. Use --bucket or set AWS_BUCKET_NAME"
            )
        self.session = get_s3_session()

    # ✅ LIST (async + pagination)
    async def list_all_files(self, prefix=None):
        keys = []

        try:
            async with self.session.client("s3") as s3:
                continuation_token = None

                while True:
                    kwargs = {"Bucket": self.bucket_name}
                    if prefix:
                        kwargs["Prefix"] = prefix
                    if continuation_token:
                        kwargs["ContinuationToken"] = continuation_token

                    response = await s3.list_objects_v2(**kwargs)

                    contents = response.get("Contents", [])
                    keys.extend([obj["Key"] for obj in contents])

                    if not response.get("IsTruncated"):
                        break

                    continuation_token = response.get("NextContinuationToken")

            logger.info(f"Listed {len(keys)} objects from {self.bucket_name}")
            return keys

        except ClientError as e:
            logger.error(f"List failed: {e}")
            raise

    # ✅ SEARCH
    async def search_for_file(self, file_name):
        files = await self.list_all_files()
        result = [f for f in files if f.endswith(file_name)]

        logger.info(f"Found {len(result)} matches for {file_name}")
        return result

    # ✅ STREAM READ
    async def stream_file(self, key, chunk_size=1024 * 1024):
        """
        Stream file in chunks (1MB default)
        """
        async with self.session.client("s3") as s3:
            response = await s3.get_object(
                Bucket=self.bucket_name, Key=key
            )

            stream = response["Body"]

            while True:
                chunk = await stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    # ✅ DOWNLOAD
    async def download_file(self, key, local_path=None):
        try:
            if local_path is None:
                local_path = key.split("/")[-1]
            else:
                local_path = Path(local_path)
                if local_path.is_dir():
                    local_path = local_path / key.split("/")[-1]

            async with self.session.client("s3") as s3:
                await s3.download_file(
                    self.bucket_name, key, str(local_path)
                )

            logger.info(f"Downloaded {key} -> {local_path}")
            return str(local_path)

        except ClientError as e:
            logger.error(f"Download failed: {e}")
            raise

    # ✅ DELETE
    async def delete_file(self, key):
        try:
            async with self.session.client("s3") as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name, Key=key
                )

            logger.info(f"Deleted {key}")
            return True

        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            raise

    # ✅ UPLOAD
    async def upload_file(self, local_path, key):
        try:
            async with self.session.client("s3") as s3:
                await s3.upload_file(
                    local_path, self.bucket_name, key
                )

            logger.info(f"Uploaded {local_path} -> {key}")
            return key

        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    # ✅ PARALLEL UPLOAD
    async def upload_files_parallel(self, files: list[tuple[str, str]]):
        """
        files = [(local_path, key), ...]
        """
        async def _upload(local_path, key):
            async with self.session.client("s3") as s3:
                await s3.upload_file(local_path, self.bucket_name, key)

        await asyncio.gather(*[_upload(lp, k) for lp, k in files])


    # ✅ PARALLEL DOWNLOAD
    async def download_files_parallel(self, keys: list[str], dest_dir="."):
        async def _download(key):
            path = f"{dest_dir}/{key.split('/')[-1]}"
            async with self.session.client("s3") as s3:
                await s3.download_file(self.bucket_name, key, path)

        await asyncio.gather(*[_download(k) for k in keys])
