"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.database.session import engine
from app.main import app
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """Ensure tables exist for the test database."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
