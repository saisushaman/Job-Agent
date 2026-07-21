"""Job analysis service — runs the local model and applies the eligibility rule."""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.prompts.job_analysis import JOB_ANALYSIS_SYSTEM, build_job_analysis_prompt
from app.models.job import Job
from app.schemas.job_analysis import (
    Eligibility,
    JobAnalysisResult,
    compute_eligibility,
)


def analyze_job(provider: AIProvider, job: Job) -> JobAnalysisResult:
    """Analyze a job with the local model, then set eligibility deterministically."""
    prompt = build_job_analysis_prompt(
        title=job.title,
        company=job.company,
        country=job.country,
        city=job.city,
        description=job.description,
    )
    result = provider.generate_json(
        prompt, JobAnalysisResult, system=JOB_ANALYSIS_SYSTEM
    )

    # Never trust the model's own eligibility — recompute from hard rules.
    result.eligibility = compute_eligibility(result)

    # Make the reason explicit in concerns when we exclude the job.
    if result.eligibility is Eligibility.NOT_ELIGIBLE:
        if result.citizenship_required:
            reason = "Requires citizenship — excluded (candidate needs sponsorship)."
        elif result.security_clearance_required:
            reason = "Requires security clearance — excluded."
        else:
            reason = "No viable sponsorship / work authorization — excluded."
        if reason not in result.concerns:
            result.concerns.insert(0, reason)

    return result
