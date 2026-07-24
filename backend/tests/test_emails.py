"""Tests for email sync + classification (Phase 9), using mocked data."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.database.session import SessionLocal
from app.main import app
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.schemas.email import EmailClassificationResult, EmailCategory
from app.schemas.job_analysis import JobAnalysisResult, Region


class ScriptedClassifier(AIProvider):
    """Returns a classification based on keywords in the prompt (deterministic)."""

    model = "fake"

    def generate(self, prompt, *, system=None):  # pragma: no cover
        return ""

    def generate_json(self, prompt, schema, *, system=None, max_retries=None):
        p = prompt.lower()
        if "interview" in p:
            return EmailClassificationResult(
                category=EmailCategory.INTERVIEW, confidence=0.95, reason="invite"
            )
        if "received your application" in p or "we have received" in p:
            return EmailClassificationResult(
                category=EmailCategory.APPLICATION_CONFIRMATION,
                confidence=0.9,
                reason="ack",
            )
        if "assessment" in p:
            return EmailClassificationResult(
                category=EmailCategory.ASSESSMENT, confidence=0.88, reason="test"
            )
        # ambiguous newsletter -> low confidence
        return EmailClassificationResult(
            category=EmailCategory.OTHER, confidence=0.3, reason="unsure"
        )

    def embed(self, text):  # pragma: no cover
        return [0.0]

    def health(self):  # pragma: no cover
        return {}


def _make_globaltech_application(client: TestClient) -> int:
    db = SessionLocal()
    try:
        job = Job(title="AI Engineer", company="GlobalTech", description="Python")
        db.add(job)
        db.flush()
        db.add(
            JobAnalysis(
                job_id=job.id,
                region="USA",
                eligibility="ELIGIBLE",
                citizenship_required=False,
                work_authorization_required=False,
                summary="",
                data=JobAnalysisResult(region=Region.USA).model_dump(mode="json"),
            )
        )
        db.commit()
        job_id = job.id
    finally:
        db.close()
    return client.post("/api/applications", json={"job_id": job_id}).json()["id"]


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_status_is_mock(client: TestClient) -> None:
    body = client.get("/api/emails/status").json()
    assert body["provider"] == "mock"
    assert body["configured"] is True


def test_sync_stores_and_dedupes(client: TestClient) -> None:
    first = client.post("/api/emails/sync").json()
    assert first["new"] >= 1
    assert first["fetched"] >= first["new"]
    # second sync adds nothing new
    second = client.post("/api/emails/sync").json()
    assert second["new"] == 0


def test_classify_matches_and_updates_status(client: TestClient) -> None:
    app_id = _make_globaltech_application(client)
    client.post("/api/emails/sync")
    app.dependency_overrides[get_ai_provider] = lambda: ScriptedClassifier()

    result = client.post("/api/emails/classify").json()
    assert result["classified"] >= 1
    assert result["matched"] >= 1  # GlobalTech emails match the application
    assert result["needs_review"] >= 1  # the newsletter is low-confidence

    # The application advanced due to an interview/assessment/confirmation email.
    detail = client.get(f"/api/applications/{app_id}").json()
    assert detail["status"] in {"APPLIED", "INTERVIEW"}
    assert any(e["event_type"] == "EMAIL" for e in detail["events"])

    # A low-confidence email is flagged NEEDS_REVIEW.
    flagged = client.get("/api/emails", params={"needs_review": "true"}).json()
    assert len(flagged) >= 1


def test_manual_override(client: TestClient) -> None:
    client.post("/api/emails/sync")
    app.dependency_overrides[get_ai_provider] = lambda: ScriptedClassifier()
    client.post("/api/emails/classify")
    email_id = client.get("/api/emails").json()[0]["id"]
    resp = client.patch(
        f"/api/emails/{email_id}", json={"category": "OFFER", "needs_review": False}
    )
    assert resp.status_code == 200
    assert resp.json()["category"] == "OFFER"
    assert resp.json()["needs_review"] is False


def test_no_delete_endpoint(client: TestClient) -> None:
    client.post("/api/emails/sync")
    email_id = client.get("/api/emails").json()[0]["id"]
    # The app must never delete email — DELETE is not implemented.
    assert client.delete(f"/api/emails/{email_id}").status_code == 405
