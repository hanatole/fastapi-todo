FROM python:3.12-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /bin/

COPY pyproject.toml uv.lock ./

RUN python -m venv .venv \
    && uv sync --no-group dev

FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY --from=builder /app/.venv /app/.venv
COPY *.py ./

CMD ["/app/.venv/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
