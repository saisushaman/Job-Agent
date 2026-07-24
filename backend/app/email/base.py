"""Email provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class EmailNotConfiguredError(RuntimeError):
    """Raised when a real provider (Gmail) is selected but not yet configured."""


class RawEmail(BaseModel):
    external_id: str
    thread_id: str | None = None
    sender: str = ""
    sender_email: str = ""
    subject: str = ""
    snippet: str = ""
    body: str = ""
    received_at: datetime | None = None


class EmailProvider(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self, limit: int = 50) -> list[RawEmail]:
        """Return recent emails (read-only). Must never delete or modify remote mail."""

    @abstractmethod
    def status(self) -> dict:
        """Return {provider, configured, detail}."""
