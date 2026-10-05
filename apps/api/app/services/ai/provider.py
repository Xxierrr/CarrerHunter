"""
AI Provider abstraction — the rest of the app never calls Gemini directly.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for AI providers. Swap implementations without changing business logic."""

    @abstractmethod
    async def extract_requirements(self, job_description: str, job_title: str) -> dict:
        """
        Extract structured requirements from a job description.
        Returns structured dict with degree, skills, experience, etc.
        """
        ...

    @abstractmethod
    async def classify_role(self, title: str, description: str) -> dict:
        """Classify an internship role into categories."""
        ...

    @abstractmethod
    async def explain_eligibility(
        self, candidate_summary: dict, job_summary: dict, criteria: list[dict]
    ) -> str:
        """Generate a human-readable eligibility explanation."""
        ...

    @abstractmethod
    async def generate_cover_letter(
        self, candidate_summary: dict, job_summary: dict
    ) -> str:
        """Generate a tailored cover letter using only verified candidate info."""
        ...

    @abstractmethod
    async def parse_resume_text(self, resume_text: str) -> dict:
        """Extract structured information from resume text."""
        ...

    @abstractmethod
    async def get_usage_stats(self) -> dict:
        """Return current usage statistics."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the AI provider is currently available (within quota)."""
        ...
