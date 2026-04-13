# S3 Bucket Manager

A Python application for managing AWS S3 bucket operations, including listing, searching, reading, downloading, uploading, and deleting files.

## Features

- **List Files**: Recursively list all files and folders in the S3 bucket.
- **Search Files**: Search for files by name across the entire bucket, including subfolders.
- **Read Files**: Read and display the content of text files from S3.
- **Download Files**: Download files from S3 to local storage, with support for directory paths.
- **Upload Files**: Upload local files to the S3 bucket.
- **Delete Files**: Delete files from the S3 bucket.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd s3-bucket
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

3. Copy the example environment file and configure it:
   ```bash
   cp example.env .env
   ```

4. Edit `.env` with your AWS credentials and bucket details:
   ```
   AccessKey = YOUR_AWS_ACCESS_KEY
   SecretKey = YOUR_AWS_SECRET_KEY
   Region = YOUR_AWS_REGION
   BucketName = YOUR_S3_BUCKET_NAME
   ```

## Usage

Run the application:
```bash
uv run main.py
```

### Available Functions

- `list_all_files(prefix=None)`: Lists all files in the bucket, optionally under a prefix.
- `search_for_file(file_name)`: Searches for files with the exact name in the bucket.
- `read_file(key)`: Reads and prints the content of a file.
- `download_file(key, local_path=None)`: Downloads a file to the specified local path.
- `upload_file(local_path, key)`: Uploads a local file to the S3 bucket.
- `delete_file(key)`: Deletes a file from the S3 bucket.

### Examples

```python
from main import list_all_files, upload_file, search_for_file, read_file, download_file, delete_file

# List all files
list_all_files()

# Upload a file
upload_file("/path/to/local/file.txt", "folder/file.txt")

# Search for a file
search_for_file("file.txt")

# Read a file
read_file("folder/file.txt")

# Download a file
download_file("folder/file.txt", "/path/to/download/")

# Delete a file
delete_file("folder/file.txt")
```

## Configuration

The application uses Pydantic settings loaded from a `.env` file. Ensure the following variables are set:

- `AccessKey`: Your AWS access key.
- `SecretKey`: Your AWS secret key.
- `Region`: The AWS region of your S3 bucket.
- `BucketName`: The name of your S3 bucket.

## Requirements

- Python >= 3.11
- boto3 >= 1.42.88
- pydantic-settings >= 2.13.1

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License.