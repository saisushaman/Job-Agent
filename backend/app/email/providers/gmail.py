"""Gmail provider (read-only via OAuth).

Inactive until the user supplies OAuth credentials and completes the consent flow — we
never handle a password. Requires the optional 'gmail' dependency group. Uses the
read-only scope; it can never delete or modify mail.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from app.config import settings
from app.email.base import EmailNotConfiguredError, EmailProvider, RawEmail

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


class GmailProvider(EmailProvider):
    name = "gmail"

    def _load_credentials(self):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
        except ImportError as exc:  # pragma: no cover - optional dep
            raise EmailNotConfiguredError(
                "Gmail support needs the optional dependencies: "
                "uv sync --extra gmail"
            ) from exc

        if not os.path.exists(settings.gmail_token_file):
            raise EmailNotConfiguredError(
                "Gmail is not authorized yet. Complete the one-time OAuth flow to create "
                f"{settings.gmail_token_file} (see docs). No password is ever stored."
            )

        creds = Credentials.from_authorized_user_file(
            settings.gmail_token_file, [GMAIL_READONLY_SCOPE]
        )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    def fetch(self, limit: int = 50) -> list[RawEmail]:  # pragma: no cover - needs OAuth
        from googleapiclient.discovery import build

        creds = self._load_credentials()
        service = build("gmail", "v1", credentials=creds)
        listing = (
            service.users()
            .messages()
            .list(userId="me", maxResults=limit)
            .execute()
        )
        out: list[RawEmail] = []
        for ref in listing.get("messages", []):
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=ref["id"], format="metadata")
                .execute()
            )
            headers = {
                h["name"].lower(): h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            out.append(
                RawEmail(
                    external_id=ref["id"],
                    thread_id=msg.get("threadId"),
                    sender=headers.get("from", ""),
                    sender_email=headers.get("from", ""),
                    subject=headers.get("subject", ""),
                    snippet=msg.get("snippet", ""),
                    body=msg.get("snippet", ""),
                    received_at=datetime.now(timezone.utc),
                )
            )
        return out

    def status(self) -> dict:
        try:
            self._load_credentials()
            configured = True
            detail = "Gmail authorized (read-only)."
        except EmailNotConfiguredError as exc:
            configured = False
            detail = str(exc)
        return {"provider": "gmail", "configured": configured, "detail": detail}
