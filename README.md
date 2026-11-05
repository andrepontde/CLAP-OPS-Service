# CLAP OPS Service

## Local setup

1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD`, `DATABASE_URL`, and
   `JWT_SECRET_KEY`.
2. Start PostgreSQL:

   ```sh
   docker compose up -d db
   ```

3. Create or update the schema:

   ```sh
   uv run alembic upgrade head
   ```

4. Create an administrator:

   ```sh
   uv run create-admin
   ```

### Alembic bootstrap (new project only)

If starting from an empty project, the one-time setup is:

```sh
uv add alembic
uv run alembic init migrations
```

Then configure `alembic.ini`, replace `migrations/env.py` with the project's
database URL and `Base.metadata` setup, and import every SQLAlchemy model in
that `env.py`. This repository has already completed those steps, so do not
run `alembic init migrations` again.

Generate a migration after adding or changing SQLAlchemy models:

```sh
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

Only models imported by `migrations/env.py` are included in autogeneration.
Add each new model there before generating its first migration.