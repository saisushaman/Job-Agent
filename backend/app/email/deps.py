"""Email provider selection."""

from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.email.base import EmailProvider
from app.email.providers.mock import MockEmailProvider


@lru_cache
def get_email_provider() -> EmailProvider:
    if settings.email_provider == "gmail":
        from app.email.providers.gmail import GmailProvider

        return GmailProvider()
    return MockEmailProvider()
