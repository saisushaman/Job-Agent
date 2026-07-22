"""Tests for dashboard stats and job search/filter (Phase 6)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.job_match import JobMatch
from app.schemas.job_analysis import JobAnalysisResult, Region, SponsorshipUS
from app.schemas.matching import (
    MatchResult,
    MatchScores,
    MatchWeights,
    Recommendation,
)


def _seed_job(
    title: str,
    company: str,
    *,
    region: Region,
    sponsorship: SponsorshipUS | None,
    eligibility: str,
    recommendation: str | None,
    score: float | None,
    remote: bool = False,
    country: str | None = None,
) -> int:
    db = SessionLocal()
    try:
        job = Job(title=title, company=company, country=country)
        db.add(job)
        db.flush()

        analysis_result = JobAnalysisResult(
            region=region,
            sponsorship_us=sponsorship,
            technical_skills=["Python"],
            relocation="REMOTE" if remote else "NOT_MENTIONED",
        )
        db.add(
            JobAnalysis(
                job_id=job.id,
                region=region.value,
                sponsorship_us=sponsorship.value if sponsorship else None,
                eligibility=eligibility,
                citizenship_required=False,
                work_authorization_required=False,
                summary="",
                data=analysis_result.model_dump(mode="json"),
            )
        )
        if recommendation is not None and score is not None:
            result = MatchResult(
                scores=MatchScores(
                    technical=score, experience=score, sponsorship=score,
                    location=score, language=score, relocation=score,
                ),
                overall_score=score,
                recommendation=Recommendation(recommendation),
                reasoning="",
                weights=MatchWeights(),
            )
            db.add(
                JobMatch(
                    job_id=job.id,
                    overall_score=score,
                    recommendation=recommendation,
                    data=result.model_dump(mode="json"),
                )
            )
        db.commit()
        return job.id
    finally:
        db.close()


def test_dashboard_stats(client: TestClient) -> None:
    _seed_job(
        "AI Engineer", "SponsorCo", region=Region.USA,
        sponsorship=SponsorshipUS.SPONSORSHIP_EXPLICIT, eligibility="ELIGIBLE",
        recommendation="APPLY", score=95.0, remote=True, country="USA",
    )
    _seed_job(
        "Defense SWE", "GovCorp", region=Region.USA,
        sponsorship=SponsorshipUS.NO_SPONSORSHIP, eligibility="NOT_ELIGIBLE",
        recommendation="DO_NOT_APPLY", score=40.0, country="USA",
    )
    _seed_job(
        "Backend Dev", "EuroTech", region=Region.EUROPE,
        sponsorship=None, eligibility="REVIEW", recommendation=None, score=None,
        country="Germany",
    )

    stats = client.get("/api/dashboard/stats").json()
    assert stats["total_jobs"] >= 3
    assert stats["analyzed"] >= 3
    assert stats["regions"].get("USA", 0) >= 2
    assert stats["regions"].get("EUROPE", 0) >= 1
    assert stats["usa_total"] >= 2
    assert stats["recommendations"]["APPLY"] >= 1
    assert stats["recommendations"]["DO_NOT_APPLY"] >= 1
    assert stats["eligibility"].get("NOT_ELIGIBLE", 0) >= 1
    # top matches exclude DO_NOT_APPLY
    titles = [m["title"] for m in stats["top_matches"]]
    assert "Defense SWE" not in titles
    assert "AI Engineer" in titles
    # pipeline has all statuses present
    assert "APPLIED" in stats["pipeline"]


def test_job_search_filters(client: TestClient) -> None:
    _seed_job(
        "ML Engineer", "RemoteFirst", region=Region.USA,
        sponsorship=SponsorshipUS.SPONSORSHIP_LIKELY, eligibility="ELIGIBLE",
        recommendation="APPLY", score=88.0, remote=True, country="USA",
    )
    _seed_job(
        "Onsite SWE", "OfficeCo", region=Region.EUROPE,
        sponsorship=None, eligibility="REVIEW", recommendation="REVIEW",
        score=60.0, remote=False, country="France",
    )

    # region filter
    usa = client.get("/api/jobs", params={"region": "USA"}).json()
    assert all(item["region"] == "USA" for item in usa)

    # recommendation filter
    apply_only = client.get("/api/jobs", params={"recommendation": "APPLY"}).json()
    assert all(item["recommendation"] == "APPLY" for item in apply_only)
    assert any(item["title"] == "ML Engineer" for item in apply_only)

    # min_score filter
    high = client.get("/api/jobs", params={"min_score": 80}).json()
    assert all((item["match_score"] or 0) >= 80 for item in high)

    # remote filter
    remote = client.get("/api/jobs", params={"remote_only": "true"}).json()
    assert all(item["remote"] for item in remote)

    # text search
    ml = client.get("/api/jobs", params={"q": "ML Engineer"}).json()
    assert any(item["title"] == "ML Engineer" for item in ml)


def test_job_detail(client: TestClient) -> None:
    job_id = _seed_job(
        "Detail Job", "DetailCo", region=Region.USA,
        sponsorship=SponsorshipUS.SPONSORSHIP_EXPLICIT, eligibility="ELIGIBLE",
        recommendation="APPLY", score=90.0, country="USA",
    )
    detail = client.get(f"/api/jobs/{job_id}/detail").json()
    assert detail["job"]["title"] == "Detail Job"
    assert detail["analysis"]["region"] == "USA"
    assert detail["match"]["recommendation"] == "APPLY"
