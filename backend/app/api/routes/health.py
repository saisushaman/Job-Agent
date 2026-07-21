"""Health check route — reports app info and database connectivity."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    database_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - any DB error means "unavailable"
        database_ok = False

    return HealthResponse(
        status="ok" if database_ok else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database="connected" if database_ok else "unavailable",
        time=datetime.now(timezone.utc),
    )
