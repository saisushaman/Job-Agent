"""Tests for the application tracker (Phase 7)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.schemas.job_analysis import JobAnalysisResult, Region, SponsorshipUS


def _make_job(eligibility: str = "ELIGIBLE") -> int:
    db = SessionLocal()
    try:
        job = Job(title=f"Job {eligibility}", company="Acme")
        db.add(job)
        db.flush()
        result = JobAnalysisResult(region=Region.USA)
        db.add(
            JobAnalysis(
                job_id=job.id,
                region="USA",
                sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT.value,
                eligibility=eligibility,
                citizenship_required=eligibility == "NOT_ELIGIBLE",
                work_authorization_required=False,
                summary="",
                data=result.model_dump(mode="json"),
            )
        )
        db.commit()
        return job.id
    finally:
        db.close()


def test_create_default_status_eligible(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    resp = client.post("/api/applications", json={"job_id": job_id})
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "DISCOVERED"
    # a CREATED event was recorded
    assert any(e["event_type"] == "CREATED" for e in body["events"])


def test_create_default_status_not_eligible(client: TestClient) -> None:
    job_id = _make_job("NOT_ELIGIBLE")
    body = client.post("/api/applications", json={"job_id": job_id}).json()
    assert body["status"] == "NOT_ELIGIBLE"


def test_duplicate_application_conflict(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    assert client.post("/api/applications", json={"job_id": job_id}).status_code == 201
    assert client.post("/api/applications", json={"job_id": job_id}).status_code == 409


def test_status_transition_logs_event(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    app_id = client.post("/api/applications", json={"job_id": job_id}).json()["id"]

    resp = client.patch(f"/api/applications/{app_id}", json={"status": "APPLIED"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "APPLIED"
    assert body["applied_at"] is not None  # auto-stamped
    changes = [e for e in body["events"] if e["event_type"] == "STATUS_CHANGE"]
    assert changes and changes[-1]["to_status"] == "APPLIED"


def test_not_eligible_guard_blocks_apply(client: TestClient) -> None:
    job_id = _make_job("NOT_ELIGIBLE")
    app_id = client.post("/api/applications", json={"job_id": job_id}).json()["id"]
    # Cannot move a NOT_ELIGIBLE job into an apply column.
    resp = client.patch(f"/api/applications/{app_id}", json={"status": "APPLYING"})
    assert resp.status_code == 400
    # But a non-apply status like ON_HOLD is fine.
    assert client.patch(
        f"/api/applications/{app_id}", json={"status": "ON_HOLD"}
    ).status_code == 200


def test_unknown_status_rejected(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    app_id = client.post("/api/applications", json={"job_id": job_id}).json()["id"]
    assert client.patch(
        f"/api/applications/{app_id}", json={"status": "BOGUS"}
    ).status_code == 422


def test_update_fields_and_detail(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    app_id = client.post("/api/applications", json={"job_id": job_id}).json()["id"]
    client.patch(
        f"/api/applications/{app_id}",
        json={"recruiter_name": "Jane", "notes": "Referred internally"},
    )
    detail = client.get(f"/api/applications/{app_id}").json()
    assert detail["recruiter_name"] == "Jane"
    assert detail["notes"] == "Referred internally"


def test_pipeline_stats_reflect_applications(client: TestClient) -> None:
    job_id = _make_job("ELIGIBLE")
    app_id = client.post("/api/applications", json={"job_id": job_id}).json()["id"]
    client.patch(f"/api/applications/{app_id}", json={"status": "INTERVIEW"})
    stats = client.get("/api/dashboard/stats").json()
    assert stats["pipeline"]["INTERVIEW"] >= 1
