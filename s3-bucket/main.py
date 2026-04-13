import boto3
from pathlib import Path

from core.settings import AppSettings

def get_s3_client():
    config = AppSettings()
    return boto3.client(
        's3',
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        region_name=config.region
    )


def list_all_files(prefix=None):
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        if prefix is not None:
            response = s3_client.list_objects_v2(Bucket=config.bucket_name, Prefix=prefix)
            print(f"Objects in bucket '{config.bucket_name}' under '{prefix}':")
        else:
            response = s3_client.list_objects_v2(Bucket=config.bucket_name)
            print(f"Objects in bucket '{config.bucket_name}':")
        objects = response.get('Contents', [])
        if not objects:
            print("  No objects found.")
        for obj in objects:
            print(f"  - {obj['Key']}")
            if obj['Key'].endswith('/') and obj['Key'] != (prefix or ''):
                list_all_files(prefix=obj['Key'])
    except Exception as e:
        print(f"Error listing objects in bucket: {e}")
        return []


def search_for_file(file_name):
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        # List all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=config.bucket_name)
        objects = response.get('Contents', [])
        matching_objects = [obj for obj in objects if obj['Key'].endswith(file_name)]
        print(f"Files named '{file_name}' in bucket '{config.bucket_name}':")
        if not matching_objects:
            print("  No matching files found.")
        for obj in matching_objects:
            print(f"  - {obj['Key']}")
        return [obj['Key'] for obj in matching_objects]
    except Exception as e:
        print(f"Error searching for files: {e}")
        return []


def read_file(key):
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        response = s3_client.get_object(Bucket=config.bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        print(f"Content of '{key}':")
        print(content)
        return content
    except Exception as e:
        print(f"Error reading file '{key}': {e}")
        return None


def download_file(key, local_path=None):
    if local_path is None:
        local_path = key.split('/')[-1]
    else:
        local_path = Path(local_path)
        if local_path.is_dir() or str(local_path).endswith('/'):
            file_name = key.split('/')[-1]
            local_path = local_path / file_name
        local_path = str(local_path)
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        s3_client.download_file(config.bucket_name, key, local_path)
        print(f"Downloaded '{key}' to '{local_path}'")
    except Exception as e:
        print(f"Error downloading file '{key}': {e}")


def delete_file(key):
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=config.bucket_name, Key=key)
        print(f"Deleted '{key}' from bucket '{config.bucket_name}'")
    except Exception as e:
        print(f"Error deleting file '{key}': {e}")

def upload_file(local_path, key):
    config = AppSettings()
    s3_client = get_s3_client()
    try:
        s3_client.upload_file(local_path, config.bucket_name, key)
        print(f"Uploaded '{local_path}' to bucket '{config.bucket_name}' as '{key}'")
    except Exception as e:
        print(f"Error uploading file '{local_path}': {e}")


if __name__ == "__main__":
    # Example usage
    list_all_files()
    upload_file("data/sample.txt", "test1/sample.txt")
    upload_file("data/sample.txt", "test2/sample.txt")
    search_for_file("sample.txt")
    read_file("test1/sample.txt")
    download_file("test1/sample.txt", "data/")
    # delete_file("test1/sample.txt")