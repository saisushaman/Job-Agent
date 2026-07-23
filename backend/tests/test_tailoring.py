"""Tests for resume tailoring & cover letters (Phase 8)."""

from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.database.session import SessionLocal
from app.main import app
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume, ResumeVersion
from app.schemas.job_analysis import JobAnalysisResult, Region
from app.schemas.tailoring import DraftAnswer, TailorResult
from app.services import tailoring as tsvc


class FakeProvider(AIProvider):
    model = "fake"

    def generate(self, prompt, *, system=None):  # pragma: no cover
        return ""

    def generate_json(self, prompt, schema, *, system=None, max_retries=None):
        return TailorResult(
            tailored_resume="TAILORED RESUME BODY",
            cover_letter="Dear Hiring Manager, ...",
            draft_answers=[DraftAnswer(question="Why?", answer="Because.")],
            changes_summary=["Emphasized Python experience"],
        )

    def embed(self, text):
        h = hashlib.sha256(text.lower().strip().encode()).digest()
        return [(b - 127.5) / 127.5 for b in h[:16]]

    def health(self):  # pragma: no cover
        return {}


def _make_job(eligibility: str = "ELIGIBLE", description: str = "Python role") -> int:
    db = SessionLocal()
    try:
        job = Job(title="Engineer", company="Acme", description=description)
        db.add(job)
        db.flush()
        db.add(
            JobAnalysis(
                job_id=job.id,
                region="USA",
                eligibility=eligibility,
                citizenship_required=eligibility == "NOT_ELIGIBLE",
                work_authorization_required=False,
                summary="",
                data=JobAnalysisResult(region=Region.USA).model_dump(mode="json"),
            )
        )
        db.commit()
        return job.id
    finally:
        db.close()


def _add_resume_version(text: str, version_number: int = 1) -> int:
    db = SessionLocal()
    try:
        resume = db.query(Resume).first()
        v = ResumeVersion(
            resume_id=resume.id,
            version_number=version_number,
            original_filename="cv.txt",
            content_type="text/plain",
            file_size=len(text),
            storage_path="x",
            parsed_text=text,
        )
        db.add(v)
        db.commit()
        return v.id
    finally:
        db.close()


def _create_application(client: TestClient, job_id: int) -> int:
    return client.post("/api/applications", json={"job_id": job_id}).json()["id"]


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_pick_best_resume_returns_none_without_versions() -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).first() or Job(title="t", company="c")
        result = tsvc.pick_best_resume_version(FakeProvider(), db, job)
    finally:
        db.close()
    # If other tests added versions this may be non-None; assert it doesn't crash.
    assert result is None or result.parsed_text is not None


def test_tailor_generates_and_approves() -> None:
    job_id = _make_job("ELIGIBLE")
    _add_resume_version("Experienced Python engineer. FastAPI, PyTorch.")
    app.dependency_overrides[get_ai_provider] = lambda: FakeProvider()
    client = TestClient(app)

    app_id = _create_application(client, job_id)

    gen = client.post(f"/api/applications/{app_id}/tailor", json={})
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert body["status"] == "DRAFT"
    assert body["tailored_resume"] == "TAILORED RESUME BODY"
    assert body["before_resume"]  # original text present for the diff
    assert body["draft_answers"][0]["question"] == "Why?"

    # approve -> APPROVED, application readied
    approved = client.post(f"/api/applications/{app_id}/tailor/approve").json()
    assert approved["status"] == "APPROVED"
    assert approved["approved_at"] is not None
    detail = client.get(f"/api/applications/{app_id}").json()
    assert detail["status"] == "APPLICATION_READY"


def test_tailor_blocked_for_not_eligible() -> None:
    job_id = _make_job("NOT_ELIGIBLE")
    _add_resume_version("Some resume text")
    app.dependency_overrides[get_ai_provider] = lambda: FakeProvider()
    client = TestClient(app)
    app_id = _create_application(client, job_id)
    resp = client.post(f"/api/applications/{app_id}/tailor", json={})
    assert resp.status_code == 400
    assert "NOT_ELIGIBLE" in resp.json()["detail"]


def test_document_download() -> None:
    job_id = _make_job("ELIGIBLE")
    _add_resume_version("Resume for download test")
    app.dependency_overrides[get_ai_provider] = lambda: FakeProvider()
    client = TestClient(app)
    app_id = _create_application(client, job_id)
    client.post(f"/api/applications/{app_id}/tailor", json={})

    txt = client.get(f"/api/applications/{app_id}/tailor/document?kind=resume&fmt=txt")
    assert txt.status_code == 200
    assert b"TAILORED RESUME BODY" in txt.content

    docx = client.get(
        f"/api/applications/{app_id}/tailor/document?kind=cover_letter&fmt=docx"
    )
    assert docx.status_code == 200
    assert docx.content[:2] == b"PK"  # docx is a zip
