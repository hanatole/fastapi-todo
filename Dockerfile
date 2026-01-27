FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN python -m venv .venv \
    && uv sync --no-group dev

FROM python:3.12-alpine3.23
LABEL author=ahagbes89@gmail.com
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY --from=builder /app/.venv /app/.venv
COPY *.py ./
EXPOSE 8000

ENTRYPOINT ["/app/.venv/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]