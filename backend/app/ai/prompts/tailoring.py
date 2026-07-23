"""Prompts for resume tailoring & cover letters (Phase 8)."""

from __future__ import annotations

TAILORING_SYSTEM = (
    "You tailor an EXISTING resume to a specific job for a candidate who needs visa "
    "sponsorship. ABSOLUTE RULE: never invent or exaggerate. Do not add employers, job "
    "titles, dates, degrees, certifications, skills, projects, metrics, or achievements "
    "that are not already present in the provided resume/profile. You may only: reorder "
    "and re-emphasize existing content, rephrase for clarity, adjust the summary, and "
    "surface existing skills that match the job. If the resume lacks something the job "
    "wants, do NOT fabricate it — note it in changes_summary instead. The cover letter "
    "must rely only on real facts from the resume/profile. Output only valid JSON."
)


def build_tailoring_prompt(
    *,
    resume_text: str,
    profile_summary: str,
    job_title: str,
    company: str,
    job_description: str,
    questions: list[str],
) -> str:
    q_block = (
        "\n".join(f"- {q}" for q in questions)
        if questions
        else "- Why are you interested in this role?\n- Why are you a strong fit?"
    )
    return (
        f"JOB\nTitle: {job_title}\nCompany: {company}\n"
        f"Description:\n{job_description[:6000]}\n\n"
        f"CANDIDATE PROFILE (facts you may use):\n{profile_summary}\n\n"
        f"CURRENT RESUME (the ONLY source of experience/skills you may use):\n"
        f"{resume_text[:8000]}\n\n"
        "TASK: Produce a tailored_resume (reordered/re-emphasized from the current "
        "resume, no invented content), a cover_letter grounded only in real facts, "
        "draft_answers for the questions below, and a changes_summary listing what you "
        "emphasized or noted as missing.\n"
        f"QUESTIONS:\n{q_block}"
    )
