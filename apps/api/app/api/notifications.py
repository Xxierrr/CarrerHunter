"""
Notification API routes.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, update

from app.api.deps import CurrentUser, DbSession
from app.models.notification import Notification, EmailPreference
from app.schemas.notification import (
    NotificationResponse,
    EmailPreferenceUpdate,
    EmailPreferenceResponse,
)

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    current_user: CurrentUser,
    db: DbSession,
    unread_only: bool = False,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get user notifications."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    return [NotificationResponse.model_validate(n) for n in result.scalars().all()]


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    return {"message": "Marked as read"}


@router.patch("/read-all")
async def mark_all_read(current_user: CurrentUser, db: DbSession):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    return {"message": "All notifications marked as read"}


@router.get("/preferences", response_model=EmailPreferenceResponse)
async def get_email_preferences(current_user: CurrentUser, db: DbSession):
    """Get email notification preferences."""
    result = await db.execute(
        select(EmailPreference).where(EmailPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        # Create default preferences
        pref = EmailPreference(user_id=current_user.id)
        db.add(pref)
        await db.flush()
        await db.refresh(pref)
    return EmailPreferenceResponse.model_validate(pref)


@router.put("/preferences", response_model=EmailPreferenceResponse)
async def update_email_preferences(
    updates: EmailPreferenceUpdate, current_user: CurrentUser, db: DbSession
):
    """Update email notification preferences."""
    result = await db.execute(
        select(EmailPreference).where(EmailPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = EmailPreference(user_id=current_user.id)
        db.add(pref)
        await db.flush()

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pref, field, value)

    await db.flush()
    await db.refresh(pref)
    return EmailPreferenceResponse.model_validate(pref)
