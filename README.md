# aws-cli-lite

A small Python CLI workspace for AWS-related packages. Right now it includes an `S3` package, and the README is structured so more packages can be added under their own sections later.

## Requirements

- Python `3.14`
- `uv`
- AWS credentials, either through `~/.aws` or environment variables

## Packages

### S3

Location:
`src/s3`

Purpose:
Manage S3 bucket objects from the CLI.

Features:
- List objects
- Search objects by suffix
- Read object contents
- Upload single files
- Upload multiple files
- Download multiple files
- Delete objects

CLI group:

```bash
aws_cli_lite s3
```

Future packages can be added in the same format:

- package name
- location
- purpose
- supported commands
- environment variables
- usage examples

## Environment Configuration

The app loads environment variables from `.env.<ENV>`.

By default:

```bash
ENV=dev
```

So local runs will load:

```bash
.env.dev
```

Create `.env.dev` from `example.env.dev` and set the values you need:

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-south-1
AWS_BUCKET_NAME=your-bucket
DEBUG=False
```

Supported AWS config values:

- `AWS_PROFILE`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_BUCKET_NAME`

## Install

Install runtime dependencies:

```bash
uv sync
```

Install dev dependencies too:

```bash
uv sync --extra dev
```

## Justfile

Common workflows are available through `just`.

List commands:

```bash
just
```

Examples:

```bash
just test
just docker-build
just compose-help
just s3-read test1/sample.txt
just s3-download-many test1/sample.txt test2/sample.txt
just clean
```

## Run Locally

Show CLI help:

```bash
uv run aws_cli_lite --help
```

Show package help:

```bash
uv run aws_cli_lite s3 --help
```

### Commands

List S3 objects:

```bash
uv run aws_cli_lite s3 list
```

Read an object:

```bash
uv run aws_cli_lite s3 read --key test1/sample.txt
```

Search by suffix:

```bash
uv run aws_cli_lite s3 search --prefix sample.txt
```

Upload a file:

```bash
uv run aws_cli_lite s3 upload --file ./local.txt --key uploads/local.txt
```

Delete a file:

```bash
uv run aws_cli_lite s3 delete --key uploads/local.txt
```

Override the configured bucket for a single command:

```bash
uv run aws_cli_lite s3 list --bucket another-bucket
```

Upload multiple files:

```bash
uv run aws_cli_lite s3 upload-many \
  --files ./a.txt:uploads/a.txt \
  --files ./b.txt:uploads/b.txt
```

Download multiple files:

```bash
uv run aws_cli_lite s3 download-many \
  --keys uploads/a.txt \
  --keys uploads/b.txt \
  --dest ./downloads
```

## Tests

Run tests with the project environment:

```bash
uv run pytest
```

If you already have the project virtualenv and want to use it directly:

```bash
.venv/bin/pytest
```

Current S3 test coverage includes:

- S3 service behavior
- Pagination handling
- Streaming reads
- Upload, download, and delete flows
- Parallel upload and download helpers
- CLI command behavior

## Docker

Build the image:

```bash
docker build -f docker/Dockerfile -t aws-cli-lite:test .
```

Run the CLI in a container:

```bash
docker run --rm --env-file .env.dev aws-cli-lite:test --help
```

Run an S3 command with local AWS credentials mounted:

```bash
docker run --rm \
  --env-file .env.dev \
  -v ~/.aws:/root/.aws:ro \
  aws-cli-lite:test s3 list
```

## Docker Compose

The Compose service automatically loads `../.env.dev` and mounts `~/.aws` read-only.

Show help:

```bash
docker compose -f docker/docker-compose.yml run --rm aws-cli-lite --help
```

List files:

```bash
docker compose -f docker/docker-compose.yml run --rm aws-cli-lite s3 list
```

Override a value for one run:

```bash
docker compose -f docker/docker-compose.yml run --rm \
  -e AWS_BUCKET_NAME=my-bucket \
  aws-cli-lite s3 list
```

Run an S3 read command:

```bash
docker compose -f docker/docker-compose.yml run --rm \
  aws-cli-lite s3 read --key test1/sample.txt
```

## CI

GitHub Actions runs the test suite on pushes to `main` and on pull requests.

## Notes

- Use `uv run pytest` instead of plain `pytest` if your shell is not already using the project virtualenv.
- `docker compose config` prints resolved environment values, so avoid sharing that output if your `.env.dev` contains real secrets.
