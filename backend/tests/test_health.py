"""Tests for the health check and root endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"]
    assert body["version"]
    assert body["health"] == "/api/health"


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert body["version"]
    assert body["environment"]
    assert "time" in body
