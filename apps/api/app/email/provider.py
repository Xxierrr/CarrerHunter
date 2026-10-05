"""
Email Provider abstraction — swappable email service backend.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmailResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class EmailProvider(ABC):
    """Abstract email provider. Implement for Resend, SendGrid, SES, etc."""

    @abstractmethod
    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
    ) -> EmailResult:
        """Send an email. Returns EmailResult."""
        ...

    @abstractmethod
    async def send_batch(
        self,
        recipients: list[dict],  # [{to, subject, html, text}, ...]
    ) -> list[EmailResult]:
        """Send batch emails. Default implementation sends sequentially."""
        ...
