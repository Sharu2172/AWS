# ---- Base ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Install uv ----
RUN pip install --no-cache-dir uv

# ---- Copy dependency files first (cache optimization) ----
COPY pyproject.toml uv.lock ./

# ---- Install deps ----
RUN uv pip install --system -e .

# ---- Copy source ----
COPY src ./src

# ---- Entrypoint ----
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]