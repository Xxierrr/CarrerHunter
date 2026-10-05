"""
Notification, Email, and Preference models.
"""

import uuid
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.compat import GUID, JSONType


class EmailPreference(Base):
    __tablename__ = "email_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    digest_frequency: Mapped[str] = mapped_column(String(20), default="daily")
    digest_time: Mapped[time] = mapped_column(Time, default=time(8, 0))
    notify_new_match: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_deadline: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_changes: Mapped[bool] = mapped_column(Boolean, default=True)
    min_match_score: Mapped[float] = mapped_column(Numeric(5, 2), default=70.0)
    unsubscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="email_preferences")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    type: Mapped[str | None] = mapped_column(String(30))
    title: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    data: Mapped[dict | None] = mapped_column(JSONType())
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_via_email: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notifications")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id")
    )
    provider: Mapped[str | None] = mapped_column(String(50))
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    to_email: Mapped[str | None] = mapped_column(String(255))
    subject: Mapped[str | None] = mapped_column(String(500))
    template: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
