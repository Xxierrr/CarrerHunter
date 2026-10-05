"""
Application tracking API routes.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application, ApplicationEvent
from app.models.internship import Internship, Company
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationEventResponse,
    VALID_STATUSES,
)

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(
    data: ApplicationCreate, current_user: CurrentUser, db: DbSession
):
    """Create a new application tracker entry."""
    # Verify internship exists
    result = await db.execute(
        select(Internship).where(Internship.id == data.internship_id)
    )
    internship = result.scalar_one_or_none()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    # Check for existing application
    existing = await db.execute(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.internship_id == data.internship_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Application already exists for this internship")

    app = Application(
        user_id=current_user.id,
        internship_id=data.internship_id,
        status=data.status,
        notes=data.notes,
        application_url=data.application_url or internship.application_url,
    )
    if data.status == "applied":
        app.applied_at = datetime.now(timezone.utc)

    db.add(app)
    await db.flush()

    # Create initial event
    event = ApplicationEvent(
        application_id=app.id,
        from_status=None,
        to_status=data.status,
    )
    db.add(event)

    # Get company name
    company_name = None
    if internship.company_id:
        comp_result = await db.execute(
            select(Company).where(Company.id == internship.company_id)
        )
        company = comp_result.scalar_one_or_none()
        if company:
            company_name = company.name

    await db.refresh(app)
    return ApplicationResponse(
        id=app.id,
        user_id=app.user_id,
        internship_id=app.internship_id,
        status=app.status,
        applied_at=app.applied_at,
        notes=app.notes,
        application_url=app.application_url,
        follow_up_date=app.follow_up_date,
        created_at=app.created_at,
        updated_at=app.updated_at,
        internship_title=internship.title,
        company_name=company_name,
    )


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    current_user: CurrentUser,
    db: DbSession,
    status: str | None = None,
):
    """List all applications, optionally filtered by status."""
    query = select(Application).where(Application.user_id == current_user.id)
    if status:
        query = query.where(Application.status == status)
    query = query.order_by(Application.updated_at.desc())

    result = await db.execute(query)
    applications = result.scalars().all()

    items = []
    for app in applications:
        # Load internship info
        intern_result = await db.execute(
            select(Internship).where(Internship.id == app.internship_id)
        )
        internship = intern_result.scalar_one_or_none()
        company_name = None
        if internship and internship.company_id:
            comp_result = await db.execute(
                select(Company).where(Company.id == internship.company_id)
            )
            company = comp_result.scalar_one_or_none()
            if company:
                company_name = company.name

        items.append(ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            internship_id=app.internship_id,
            status=app.status,
            applied_at=app.applied_at,
            notes=app.notes,
            application_url=app.application_url,
            follow_up_date=app.follow_up_date,
            created_at=app.created_at,
            updated_at=app.updated_at,
            internship_title=internship.title if internship else None,
            company_name=company_name,
        ))

    return items


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: uuid.UUID,
    updates: ApplicationUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update an application's status, notes, or follow-up date."""
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status
    update_data = updates.model_dump(exclude_unset=True)

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

        if new_status == "applied" and not app.applied_at:
            app.applied_at = datetime.now(timezone.utc)

        # Log status change
        event = ApplicationEvent(
            application_id=app.id,
            from_status=old_status,
            to_status=new_status,
            notes=update_data.get("notes"),
        )
        db.add(event)

    for field, value in update_data.items():
        setattr(app, field, value)

    await db.flush()
    await db.refresh(app)

    # Load internship info
    intern_result = await db.execute(
        select(Internship).where(Internship.id == app.internship_id)
    )
    internship = intern_result.scalar_one_or_none()
    company_name = None
    if internship and internship.company_id:
        comp_result = await db.execute(
            select(Company).where(Company.id == internship.company_id)
        )
        company = comp_result.scalar_one_or_none()
        if company:
            company_name = company.name

    return ApplicationResponse(
        id=app.id,
        user_id=app.user_id,
        internship_id=app.internship_id,
        status=app.status,
        applied_at=app.applied_at,
        notes=app.notes,
        application_url=app.application_url,
        follow_up_date=app.follow_up_date,
        created_at=app.created_at,
        updated_at=app.updated_at,
        internship_title=internship.title if internship else None,
        company_name=company_name,
    )


@router.delete("/{application_id}", status_code=204)
async def delete_application(
    application_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Delete an application."""
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(app)


@router.get("/{application_id}/events", response_model=list[ApplicationEventResponse])
async def get_application_events(
    application_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Get status change history for an application."""
    # Verify ownership
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Application not found")

    events_result = await db.execute(
        select(ApplicationEvent)
        .where(ApplicationEvent.application_id == application_id)
        .order_by(ApplicationEvent.created_at.desc())
    )
    return [
        ApplicationEventResponse.model_validate(e)
        for e in events_result.scalars().all()
    ]
