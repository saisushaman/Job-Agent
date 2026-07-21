"""Health check response schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str          # "ok" | "degraded"
    app: str
    version: str
    environment: str
    database: str        # "connected" | "unavailable"
    time: datetime
