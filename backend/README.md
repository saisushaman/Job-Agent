# Job-Agent backend

FastAPI service. See the repo root [`README.md`](../README.md) for full setup.

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

- `app/config.py` — env-driven settings (Pydantic Settings)
- `app/database/` — engine/session, `DATABASE_URL`-driven (SQLite dev / Postgres prod)
- `app/models/` — SQLAlchemy models (`Job`, `Application`)
- `app/schemas/` — Pydantic response models
- `app/api/routes/` — routers (health)
- `alembic/` — migrations
- `tests/` — pytest
