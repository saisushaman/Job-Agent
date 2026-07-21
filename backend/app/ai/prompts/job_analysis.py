"""Prompt construction for job analysis (Phase 4)."""

from __future__ import annotations

JOB_ANALYSIS_SYSTEM = (
    "You are an expert immigration-aware technical recruiter analyzing a single job "
    "posting for a candidate who REQUIRES visa sponsorship (they are NOT a citizen or "
    "permanent resident of the US or EU). "
    "Base every field ONLY on the provided job text. Do not invent facts. "
    "If something is not stated, use the 'UNCLEAR'/'UNKNOWN'/'NOT_MENTIONED' value and "
    "leave evidence empty. "
    "NEVER claim a visa or sponsorship is guaranteed — sponsorship categories express "
    "likelihood based on evidence only. "
    "Flag citizenship_required=true if the posting requires citizenship (e.g. 'must be a "
    "U.S. citizen', 'US persons only', 'EU citizens only') and quote it in "
    "citizenship_evidence. Flag security_clearance_required=true if it requires a "
    "government security clearance. Output only valid JSON."
)


def build_job_analysis_prompt(
    *,
    title: str,
    company: str,
    country: str | None,
    city: str | None,
    description: str | None,
) -> str:
    location = ", ".join(p for p in (city, country) if p) or "Not specified"
    return (
        "Analyze this job posting.\n\n"
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Location: {location}\n"
        "Description:\n"
        f"{description or '(no description provided)'}\n\n"
        "Determine: region (USA/EUROPE/OTHER/UNKNOWN); for USA the sponsorship_us "
        "category and for EUROPE the visa_support_eu category; whether existing work "
        "authorization is required; whether citizenship or a security clearance is "
        "required (with citizenship_evidence quote); relocation stance; English-language "
        "compatibility; technical_skills; minimum experience years and level; salary if "
        "stated; sponsorship_evidence quotes; concerns; and a short summary. "
        "Do not set the eligibility field yourself."
    )
