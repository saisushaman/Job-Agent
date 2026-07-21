"""Shared pytest fixtures.

Tests run against an isolated SQLite file and upload dir (set via env BEFORE the app is
imported, so ``Settings`` picks them up) — the dev database is never touched.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_job_agent.db"
os.environ["UPLOAD_DIR"] = "test_uploads"

# Start each test session from a clean database file.
_db_file = Path("test_job_agent.db")
if _db_file.exists():
    _db_file.unlink()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.database.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Resume  # noqa: E402
from app.resume_tracks import DEFAULT_TRACKS  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """Create tables and seed the default resume tracks."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = set(db.scalars(select(Resume.kind)).all())
        for kind, name in DEFAULT_TRACKS:
            if kind not in existing:
                db.add(Resume(kind=kind, name=name))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
