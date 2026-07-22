"""Canonical application status lifecycle (used by dashboard stats + Phase 7 tracker)."""

from __future__ import annotations

APPLICATION_STATUSES: list[str] = [
    "DISCOVERED",
    "REVIEW",
    "APPROVED",
    "APPLICATION_READY",
    "APPLYING",
    "APPLIED",
    "RESPONSE_RECEIVED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "ON_HOLD",
    "NOT_ELIGIBLE",
]
