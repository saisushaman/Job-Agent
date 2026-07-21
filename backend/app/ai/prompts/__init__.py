"""Prompt templates for the local model.

Hard rule carried through every prompt in later phases: the model must never invent
facts (jobs, employers, degrees, certifications, skills, projects, experience). It works
only from provided context.
"""

DEFAULT_SYSTEM = (
    "You are a careful, factual assistant running locally. "
    "Never invent facts. When asked for JSON, output only valid JSON."
)
