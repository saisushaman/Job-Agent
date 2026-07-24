"""Mock email provider — deterministic local fixtures for development/testing.

Fixtures reference "GlobalTech" so they match the sample AI Engineer job/application.
No network, no real inbox.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.email.base import EmailProvider, RawEmail

_FIXTURES: list[RawEmail] = [
    RawEmail(
        external_id="mock-1",
        thread_id="t1",
        sender="GlobalTech Careers",
        sender_email="careers@globaltech.com",
        subject="We received your application — AI Engineer",
        snippet="Thanks for applying to GlobalTech...",
        body=(
            "Hi Sai,\n\nThank you for applying to the AI Engineer role at GlobalTech. "
            "We have received your application and our team will review it shortly."
        ),
        received_at=datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc),
    ),
    RawEmail(
        external_id="mock-2",
        thread_id="t1",
        sender="Dana (GlobalTech)",
        sender_email="dana.recruiter@globaltech.com",
        subject="Interview invitation — AI Engineer at GlobalTech",
        snippet="We'd love to schedule an interview...",
        body=(
            "Hi Sai,\n\nWe were impressed by your background and would like to invite you "
            "to a first interview next week. Please share your availability."
        ),
        received_at=datetime(2026, 7, 21, 14, 30, tzinfo=timezone.utc),
    ),
    RawEmail(
        external_id="mock-3",
        thread_id="t2",
        sender="TechJobs Weekly",
        sender_email="newsletter@techjobsweekly.com",
        subject="10 remote AI jobs this week",
        snippet="This week's roundup...",
        body="Check out this week's remote AI engineering roles from various companies.",
        received_at=datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc),
    ),
    RawEmail(
        external_id="mock-4",
        thread_id="t3",
        sender="GlobalTech Assessments",
        sender_email="assessments@globaltech.com",
        subject="Coding assessment for your GlobalTech application",
        snippet="Please complete the following assessment...",
        body=(
            "Hi Sai,\n\nAs part of the process for the AI Engineer role, please complete "
            "this take-home coding assessment within 5 days."
        ),
        received_at=datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc),
    ),
]


class MockEmailProvider(EmailProvider):
    name = "mock"

    def fetch(self, limit: int = 50) -> list[RawEmail]:
        return _FIXTURES[:limit]

    def status(self) -> dict:
        return {
            "provider": "mock",
            "configured": True,
            "detail": "Using local mock fixtures (no real inbox).",
        }
