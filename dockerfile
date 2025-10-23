# syntax=docker/dockerfile:1.4

# -------------------------
# Base image
# -------------------------
FROM python:3.13-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:$PATH"

RUN apk add --no-cache \
    netcat-openbsd \
    build-base \
    libpq \
    libpq-dev \
    postgresql-dev \
    bash

WORKDIR /app

# -------------------------
# Builder
# -------------------------
FROM base AS builder

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# -------------------------
# Final image
# -------------------------
FROM base AS final

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . .

COPY entrypoint.sh wait-for-db.sh ./
RUN chmod +x entrypoint.sh wait-for-db.sh

RUN adduser -D appuser && chown -R appuser /app
USER appuser

CMD ["sh", "entrypoint.sh"]
