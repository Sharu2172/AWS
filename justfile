set shell := ["bash", "-cu"]

project := "aws-cli-lite:test"
compose := "docker compose -f docker/docker-compose.yml"
uv := "UV_CACHE_DIR=/tmp/uv-cache uv"

default:
  @just --list

sync:
  {{uv}} sync
  {{uv}} sync --extra dev

test:
  {{uv}} run pytest

test-venv:
  .venv/bin/pytest

check:
  python -m compileall src tests
  {{uv}} run pytest

cli-help:
  {{uv}} run aws --help

s3-help:
  {{uv}} run aws s3 --help

s3-list bucket='':
  if [ -n "{{bucket}}" ]; then {{uv}} run aws s3 list --bucket "{{bucket}}"; else {{uv}} run aws s3 list; fi

s3-read key:
  {{uv}} run aws s3 read --key "{{key}}"

s3-search prefix:
  {{uv}} run aws s3 search --prefix "{{prefix}}"

s3-upload file key:
  {{uv}} run aws s3 upload --file "{{file}}" --key "{{key}}"

s3-delete key:
  {{uv}} run aws s3 delete --key "{{key}}"

s3-download-many dest='.' *keys:
  {{uv}} run aws s3 download-many {{keys}} --dest "{{dest}}"

docker-build:
  docker build -f docker/Dockerfile -t {{project}} .

docker-help:
  docker run --rm --env-file .env.dev {{project}} --help

docker-s3-list:
  docker run --rm --env-file .env.dev -v ~/.aws:/root/.aws:ro {{project}} s3 list

compose-config:
  {{compose}} config

compose-help:
  {{compose}} run --rm aws-cli-lite --help

compose-s3-list:
  {{compose}} run --rm aws-cli-lite s3 list

compose-s3-read key:
  {{compose}} run --rm aws-cli-lite s3 read --key "{{key}}"

clean:
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
  find . -type f -name '*.pyc' -delete

clean-all:
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
  find . -type f -name '*.pyc' -delete
  rm -rf .pytest_cache .ruff_cache build dist
