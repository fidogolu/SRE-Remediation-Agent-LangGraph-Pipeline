# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Build stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

RUN pip install --no-cache-dir --upgrade uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py"]
