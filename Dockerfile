FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock alembic.ini README.md LICENSE ./
COPY migrations ./migrations
COPY src ./src

RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
