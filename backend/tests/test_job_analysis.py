"""Tests for job analysis: eligibility rule, service, and endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.main import app
from app.models.job import Job
from app.schemas.job_analysis import (
    Eligibility,
    JobAnalysisResult,
    Region,
    SponsorshipUS,
    VisaSupportEU,
    compute_eligibility,
)
from app.services.job_analysis import analyze_job


# --- deterministic eligibility rule ----------------------------------------


def test_citizenship_forces_not_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.USA,
        sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT,  # even if sponsorship looks great
        citizenship_required=True,
    )
    assert compute_eligibility(r) is Eligibility.NOT_ELIGIBLE


def test_security_clearance_forces_not_eligible() -> None:
    r = JobAnalysisResult(region=Region.USA, security_clearance_required=True)
    assert compute_eligibility(r) is Eligibility.NOT_ELIGIBLE


def test_no_sponsorship_not_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.USA, sponsorship_us=SponsorshipUS.NO_SPONSORSHIP
    )
    assert compute_eligibility(r) is Eligibility.NOT_ELIGIBLE


def test_work_auth_required_us_not_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.USA, sponsorship_us=SponsorshipUS.WORK_AUTH_REQUIRED
    )
    assert compute_eligibility(r) is Eligibility.NOT_ELIGIBLE


def test_explicit_sponsorship_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.USA, sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT
    )
    assert compute_eligibility(r) is Eligibility.ELIGIBLE


def test_eu_visa_support_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.EUROPE, visa_support_eu=VisaSupportEU.VISA_SUPPORT_LIKELY
    )
    assert compute_eligibility(r) is Eligibility.ELIGIBLE


def test_eu_no_visa_not_eligible() -> None:
    r = JobAnalysisResult(
        region=Region.EUROPE, visa_support_eu=VisaSupportEU.NO_VISA_SUPPORT
    )
    assert compute_eligibility(r) is Eligibility.NOT_ELIGIBLE


def test_unclear_is_review() -> None:
    r = JobAnalysisResult(
        region=Region.USA, sponsorship_us=SponsorshipUS.SPONSORSHIP_UNCLEAR
    )
    assert compute_eligibility(r) is Eligibility.REVIEW


# --- service applies the rule regardless of model output --------------------


class _FakeProvider(AIProvider):
    model = "fake"

    def __init__(self, result: JobAnalysisResult) -> None:
        self._result = result

    def generate(self, prompt, *, system=None):  # pragma: no cover
        return ""

    def generate_json(self, prompt, schema, *, system=None, max_retries=None):
        return self._result

    def embed(self, text):  # pragma: no cover
        return []

    def health(self):  # pragma: no cover
        return {}


def test_service_overrides_model_eligibility() -> None:
    # Model wrongly claims ELIGIBLE despite citizenship requirement.
    model_result = JobAnalysisResult(
        region=Region.USA,
        sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT,
        citizenship_required=True,
        citizenship_evidence="Must be a U.S. citizen.",
        eligibility=Eligibility.ELIGIBLE,
    )
    job = Job(title="Engineer", company="GovContractor")
    out = analyze_job(_FakeProvider(model_result), job)
    assert out.eligibility is Eligibility.NOT_ELIGIBLE
    assert any("citizenship" in c.lower() for c in out.concerns)


# --- endpoints --------------------------------------------------------------


def _override_provider(result: JobAnalysisResult) -> None:
    app.dependency_overrides[get_ai_provider] = lambda: _FakeProvider(result)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_job_create_analyze_flow(client: TestClient) -> None:
    created = client.post(
        "/api/jobs",
        json={
            "title": "AI Engineer",
            "company": "SponsorCo",
            "country": "USA",
            "city": "Austin",
            "description": "We sponsor H-1B visas. Python, FastAPI.",
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]

    _override_provider(
        JobAnalysisResult(
            region=Region.USA,
            sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT,
            technical_skills=["Python", "FastAPI"],
            sponsorship_evidence=["We sponsor H-1B visas."],
            summary="Sponsorship-friendly AI role.",
        )
    )
    analyzed = client.post(f"/api/jobs/{job_id}/analyze")
    assert analyzed.status_code == 200, analyzed.text
    body = analyzed.json()
    assert body["eligibility"] == "ELIGIBLE"
    assert body["result"]["technical_skills"] == ["Python", "FastAPI"]

    # Persisted and retrievable
    fetched = client.get(f"/api/jobs/{job_id}/analysis")
    assert fetched.status_code == 200
    assert fetched.json()["eligibility"] == "ELIGIBLE"


def test_analyze_citizenship_job_not_eligible(client: TestClient) -> None:
    job_id = client.post(
        "/api/jobs",
        json={
            "title": "Defense SWE",
            "company": "GovCorp",
            "country": "USA",
            "description": "Must be a U.S. citizen. Active clearance required.",
        },
    ).json()["id"]

    _override_provider(
        JobAnalysisResult(
            region=Region.USA,
            sponsorship_us=SponsorshipUS.NO_SPONSORSHIP,
            citizenship_required=True,
            citizenship_evidence="Must be a U.S. citizen.",
            security_clearance_required=True,
        )
    )
    body = client.post(f"/api/jobs/{job_id}/analyze").json()
    assert body["eligibility"] == "NOT_ELIGIBLE"
    assert body["citizenship_required"] is True


def test_analyze_missing_job_404(client: TestClient) -> None:
    _override_provider(JobAnalysisResult())
    assert client.post("/api/jobs/999999/analyze").status_code == 404
