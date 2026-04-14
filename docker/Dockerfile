FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv pip install --system --no-cache .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
