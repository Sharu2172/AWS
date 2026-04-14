import click
import asyncio
from .service import S3BucketManager


@click.group()
def s3():
    pass


def run_async(awaitable):
    return asyncio.run(awaitable)


@s3.command()
@click.option("--bucket", required=False)
def list(bucket):
    manager = S3BucketManager(bucket)
    files = run_async(manager.list_all_files())

    for f in files:
        click.echo(f)


@s3.command()
@click.option("--bucket", required=False)
@click.option("--key", required=True)
def read(bucket, key):
    manager = S3BucketManager(bucket)

    async def _run():
        async for chunk in manager.stream_file(key):
            print(chunk.decode("utf-8"), end="")

    run_async(_run())


@s3.command()
@click.option("--bucket", required=False)
@click.option("--file", required=True)
@click.option("--key", required=True)
def upload(bucket, file, key):
    manager = S3BucketManager(bucket)
    run_async(manager.upload_file(file, key))
    click.echo("Upload successful")


@s3.command()
@click.option("--bucket", required=False)
@click.option("--key", required=True)
def delete(bucket, key):
    manager = S3BucketManager(bucket)
    run_async(manager.delete_file(key))
    click.echo("Deleted successfully")


@s3.command()
@click.option("--bucket", required=False)
@click.option("--files", multiple=True, help="local:key")
def upload_many(bucket, files):
    manager = S3BucketManager(bucket)

    parsed = []
    for item in files:
        local_path, separator, object_key = item.partition(":")
        if not separator or not local_path or not object_key:
            raise click.UsageError("Each --files entry must use the format local:key")
        parsed.append((local_path, object_key))

    run_async(manager.upload_files_parallel(parsed))
    click.echo("Parallel upload complete")


@s3.command()
@click.option("--bucket", required=False)
@click.option("--keys", multiple=True)
@click.option("--dest", default=".")
def download_many(bucket, keys, dest):
    manager = S3BucketManager(bucket)

    run_async(manager.download_files_parallel(list(keys), dest))
    click.echo("Parallel download complete")

@s3.command()
@click.option("--bucket", required=False)
@click.option("--prefix", required=True)
def search(bucket, prefix):
    manager = S3BucketManager(bucket)
    files = run_async(manager.search_for_file(prefix))

    for f in files:
        click.echo(f)


if __name__ == "__main__":
    s3()
