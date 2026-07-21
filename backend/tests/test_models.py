"""Smoke tests for the ORM models and a real round-trip insert/query."""

from __future__ import annotations

from app.database.session import SessionLocal
from app.models import Application, Job


def test_table_names() -> None:
    assert Job.__tablename__ == "jobs"
    assert Application.__tablename__ == "applications"


def test_job_application_roundtrip() -> None:
    db = SessionLocal()
    try:
        job = Job(
            title="AI Engineer",
            company="Example Corp",
            country="USA",
            city="Austin",
            url="https://example.com/jobs/1",
            description="Build local-first AI systems.",
        )
        db.add(job)
        db.flush()  # assigns job.id without committing

        app_row = Application(job_id=job.id, status="DISCOVERED")
        db.add(app_row)
        db.flush()

        assert job.id is not None
        assert app_row.id is not None
        assert app_row.job.company == "Example Corp"
        assert job.applications[0].status == "DISCOVERED"
    finally:
        db.rollback()  # keep the test database clean
        db.close()
