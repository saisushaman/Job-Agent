"""Canonical resume tracks. Single source of truth for the seed migration and the app."""

from __future__ import annotations

# (kind, display name) — order defines display order.
DEFAULT_TRACKS: list[tuple[str, str]] = [
    ("MASTER", "Master Resume"),
    ("SOFTWARE_ENGINEER", "Software Engineer"),
    ("AI_ENGINEER", "AI Engineer"),
    ("CLOUD_ENGINEER", "Cloud Engineer"),
    ("DEVOPS_ENGINEER", "DevOps Engineer"),
]

VALID_KINDS = {kind for kind, _ in DEFAULT_TRACKS}
