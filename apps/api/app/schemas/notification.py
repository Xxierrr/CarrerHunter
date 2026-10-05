"""
Notification Pydantic schemas.
"""

import uuid
from datetime import datetime, time

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str | None = None
    title: str | None = None
    body: str | None = None
    data: dict | None = None
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailPreferenceUpdate(BaseModel):
    digest_frequency: str | None = None   # immediate, daily, every_2_days, weekly, disabled
    digest_time: time | None = None
    notify_new_match: bool | None = None
    notify_deadline: bool | None = None
    notify_changes: bool | None = None
    min_match_score: float | None = None
    unsubscribed: bool | None = None


class EmailPreferenceResponse(BaseModel):
    digest_frequency: str
    digest_time: time
    notify_new_match: bool
    notify_deadline: bool
    notify_changes: bool
    min_match_score: float
    unsubscribed: bool

    model_config = {"from_attributes": True}
