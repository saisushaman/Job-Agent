"""Tests for the matching engine: sub-scores, recommendation, technical match, endpoint."""

from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.main import app
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.schemas.job_analysis import (
    Eligibility,
    EnglishCompatibility,
    JobAnalysisResult,
    Region,
    Relocation,
    SponsorshipUS,
)
from app.schemas.matching import MatchScores, MatchWeights, Recommendation
from app.services import matching


def _profile(**kw) -> CandidateProfile:
    base = dict(
        skills=["Python", "FastAPI"],
        languages=["English"],
        preferred_regions=["USA", "EUROPE"],
        years_experience=5.0,
        needs_sponsorship=True,
        open_to_relocation=True,
        open_to_remote=True,
        headline="AI Engineer",
    )
    base.update(kw)
    return CandidateProfile(**base)


class DeterministicProvider(AIProvider):
    """Fake provider: identical strings embed identically; different strings differ."""

    model = "fake"

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        return "Deterministic reasoning."

    def generate_json(self, prompt, schema, *, system=None, max_retries=None):  # pragma: no cover
        raise NotImplementedError

    def embed(self, text: str) -> list[float]:
        # Center around 0 so distinct strings are near-orthogonal (like real embeddings);
        # identical strings still embed identically (cosine 1.0).
        h = hashlib.sha256(text.lower().strip().encode()).digest()
        return [(b - 127.5) / 127.5 for b in h[:16]]

    def health(self):  # pragma: no cover
        return {}


# --- sub-score unit tests ---------------------------------------------------


def test_experience_score() -> None:
    assert matching.experience_score(5, 3) == 100.0
    assert matching.experience_score(2, 3) == 85.0
    assert matching.experience_score(None, 3) == 50.0
    assert matching.experience_score(5, None) == 70.0


def test_sponsorship_score() -> None:
    explicit = JobAnalysisResult(
        region=Region.USA, sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT
    )
    assert matching.sponsorship_score(explicit) == 100.0
    citizen = JobAnalysisResult(region=Region.USA, citizenship_required=True)
    assert matching.sponsorship_score(citizen) == 0.0


def test_recommendation_mapping() -> None:
    assert matching.recommend(Eligibility.ELIGIBLE, 80) is Recommendation.APPLY
    assert matching.recommend(Eligibility.ELIGIBLE, 60) is Recommendation.REVIEW
    assert matching.recommend(Eligibility.ELIGIBLE, 40) is Recommendation.LOW_PRIORITY
    assert matching.recommend(Eligibility.ELIGIBLE, 10) is Recommendation.DO_NOT_APPLY
    # Hard rule: not eligible always DO_NOT_APPLY regardless of score
    assert matching.recommend(Eligibility.NOT_ELIGIBLE, 99) is Recommendation.DO_NOT_APPLY


def test_overall_weighting() -> None:
    scores = MatchScores(
        technical=100, experience=100, sponsorship=0, location=100,
        language=100, relocation=100,
    )
    # sponsorship weight 0.25 -> overall = 75
    assert matching.overall(scores, MatchWeights()) == 75.0


def test_technical_match_exact_and_missing() -> None:
    provider = DeterministicProvider()
    score, matched, missing = matching.technical_match(
        provider,
        candidate_skills=["Python", "FastAPI"],
        job_skills=["Python", "Kubernetes"],
        candidate_text="",
        job_text="",
    )
    assert "Python" in matched
    assert "Kubernetes" in missing
    assert 0 <= score <= 100


def test_match_job_not_eligible_is_do_not_apply() -> None:
    provider = DeterministicProvider()
    analysis = JobAnalysisResult(
        region=Region.USA,
        sponsorship_us=SponsorshipUS.NO_SPONSORSHIP,
        citizenship_required=True,
        technical_skills=["Python"],
    )
    job = Job(title="Defense Eng", company="GovCorp", description="x")
    result = matching.match_job(
        provider, _profile(), job, analysis, Eligibility.NOT_ELIGIBLE
    )
    assert result.recommendation is Recommendation.DO_NOT_APPLY
    assert result.scores.sponsorship == 0.0


def test_match_job_strong_fit_applies() -> None:
    provider = DeterministicProvider()
    analysis = JobAnalysisResult(
        region=Region.USA,
        sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT,
        english_compatibility=EnglishCompatibility.ENGLISH_OK,
        relocation=Relocation.REMOTE,
        technical_skills=["Python", "FastAPI"],
        experience_years_min=3,
    )
    job = Job(title="AI Engineer", company="SponsorCo", description="Python FastAPI")
    result = matching.match_job(
        provider, _profile(), job, analysis, Eligibility.ELIGIBLE
    )
    assert result.recommendation is Recommendation.APPLY
    assert result.overall_score >= 75


# --- endpoint tests ---------------------------------------------------------


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_profile_get_and_update(client: TestClient) -> None:
    got = client.get("/api/profile")
    assert got.status_code == 200
    assert "skills" in got.json()

    updated = client.put(
        "/api/profile",
        json={"full_name": "Sai", "skills": ["Python", "PyTorch"], "years_experience": 4},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["full_name"] == "Sai"
    assert body["skills"] == ["Python", "PyTorch"]


def test_match_requires_analysis_first(client: TestClient) -> None:
    app.dependency_overrides[get_ai_provider] = lambda: DeterministicProvider()
    job_id = client.post(
        "/api/jobs",
        json={"title": "X", "company": "Y", "description": "Python role"},
    ).json()["id"]
    resp = client.post(f"/api/jobs/{job_id}/match")
    assert resp.status_code == 400  # must analyze first


def test_full_match_flow(client: TestClient) -> None:
    provider = DeterministicProvider()

    # Seed an analysis directly (avoid depending on generate_json here).
    from app.models.job_analysis import JobAnalysis
    from app.database.session import SessionLocal

    job_id = client.post(
        "/api/jobs",
        json={"title": "AI Engineer", "company": "SponsorCo", "description": "Python FastAPI"},
    ).json()["id"]

    analysis = JobAnalysisResult(
        region=Region.USA,
        sponsorship_us=SponsorshipUS.SPONSORSHIP_EXPLICIT,
        english_compatibility=EnglishCompatibility.ENGLISH_OK,
        relocation=Relocation.REMOTE,
        technical_skills=["Python", "FastAPI"],
        experience_years_min=3,
        eligibility=Eligibility.ELIGIBLE,
    )
    db = SessionLocal()
    try:
        db.add(
            JobAnalysis(
                job_id=job_id,
                region="USA",
                sponsorship_us="SPONSORSHIP_EXPLICIT",
                eligibility="ELIGIBLE",
                citizenship_required=False,
                work_authorization_required=False,
                summary="",
                data=analysis.model_dump(mode="json"),
            )
        )
        db.commit()
    finally:
        db.close()

    client.put("/api/profile", json={"skills": ["Python", "FastAPI"], "years_experience": 5})

    app.dependency_overrides[get_ai_provider] = lambda: provider
    resp = client.post(f"/api/jobs/{job_id}/match")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["recommendation"] in {"APPLY", "REVIEW"}
    assert "Python" in body["result"]["matched_skills"]

    # persisted
    assert client.get(f"/api/jobs/{job_id}/match").status_code == 200
