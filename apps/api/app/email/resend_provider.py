"""
Resend email provider implementation.
Free tier: 100 emails/day, 3000/month.
"""

import logging
from app.email.provider import EmailProvider, EmailResult
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ResendProvider(EmailProvider):
    """Email provider using Resend API."""

    def __init__(self):
        self.api_key = settings.email_api_key
        self.from_email = settings.email_from
        self.daily_limit = settings.email_daily_limit
        self._daily_sent = 0
        self._client = None

        if self.api_key and self.api_key != "re_your_resend_api_key_here":
            try:
                import resend
                resend.api_key = self.api_key
                self._client = resend
            except ImportError:
                logger.warning("resend package not installed")

    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
    ) -> EmailResult:
        """Send a single email via Resend."""
        if not self._client:
            logger.warning("Resend client not initialized. Email not sent.")
            return EmailResult(success=False, error="Email provider not configured")

        if self._daily_sent >= self.daily_limit:
            logger.warning("Daily email limit reached")
            return EmailResult(success=False, error="Daily email limit reached")

        try:
            params = {
                "from_": self.from_email,
                "to": [to],
                "subject": subject,
                "html": html,
            }
            if text:
                params["text"] = text

            response = self._client.Emails.send(params)
            self._daily_sent += 1

            return EmailResult(
                success=True,
                provider_message_id=response.get("id") if isinstance(response, dict) else str(response),
            )
        except Exception as e:
            logger.error(f"Resend send error: {e}")
            return EmailResult(success=False, error=str(e))

    async def send_batch(
        self, recipients: list[dict]
    ) -> list[EmailResult]:
        """Send batch emails sequentially (Resend free tier doesn't support batch)."""
        results = []
        for recipient in recipients:
            if self._daily_sent >= self.daily_limit:
                results.append(EmailResult(success=False, error="Daily limit reached"))
                continue

            result = await self.send(
                to=recipient["to"],
                subject=recipient["subject"],
                html=recipient["html"],
                text=recipient.get("text"),
            )
            results.append(result)
        return results


# Singleton
_email_provider: EmailProvider | None = None


def get_email_provider() -> EmailProvider:
    """Get or create the singleton email provider."""
    global _email_provider
    if _email_provider is None:
        _email_provider = ResendProvider()
    return _email_provider
