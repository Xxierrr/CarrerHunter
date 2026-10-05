"""
Database models package.
Imports all models so that SQLAlchemy declarative registry resolves all relationships.
"""

from app.models.user import User
from app.models.profile import (
    UserProfile,
    Skill,
    UserSkill,
    UserExperience,
    Resume,
)
from app.models.internship import (
    Company,
    Source,
    Internship,
    InternshipSkill,
)
from app.models.application import (
    Application,
    ApplicationEvent,
    SavedInternship,
)
from app.models.notification import (
    Notification,
    EmailPreference,
    EmailLog,
)
from app.models.system import (
    EligibilityResult,
    MatchScore,
    CrawlRun,
    AIRequest,
    AICache,
)

__all__ = [
    "User",
    "UserProfile",
    "Skill",
    "UserSkill",
    "UserExperience",
    "Resume",
    "Company",
    "Source",
    "Internship",
    "InternshipSkill",
    "Application",
    "ApplicationEvent",
    "SavedInternship",
    "Notification",
    "EmailPreference",
    "EmailLog",
    "EligibilityResult",
    "MatchScore",
    "CrawlRun",
    "AIRequest",
    "AICache",
]

