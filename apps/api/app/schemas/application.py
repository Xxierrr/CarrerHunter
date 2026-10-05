"""
Application tracking Pydantic schemas.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


VALID_STATUSES = [
    "interested", "saved", "preparing", "applied",
    "assessment", "interview", "offer",
    "rejected", "withdrawn", "expired",
]


class ApplicationCreate(BaseModel):
    internship_id: uuid.UUID
    status: str = "interested"
    notes: str | None = None
    application_url: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    application_url: str | None = None
    follow_up_date: date | None = None

    def model_post_init(self, __context):
        if self.status and self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {VALID_STATUSES}")


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    internship_id: uuid.UUID
    status: str
    applied_at: datetime | None = None
    notes: str | None = None
    application_url: str | None = None
    follow_up_date: date | None = None
    created_at: datetime
    updated_at: datetime

    # Populated from internship
    internship_title: str | None = None
    company_name: str | None = None

    model_config = {"from_attributes": True}


class ApplicationEventResponse(BaseModel):
    id: uuid.UUID
    from_status: str | None = None
    to_status: str | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
