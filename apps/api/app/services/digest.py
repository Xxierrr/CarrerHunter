"""
Digest Builder & Scheduler — Step 10.6

Builds and sends periodic email digests to users containing:
- New internship matches since last digest
- Upcoming deadlines for saved internships
- Summary statistics

Supports frequency options: immediate, daily, every_2_days, weekly, disabled
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.profile import UserProfile, UserSkill, Skill
from app.models.internship import Internship, Company, InternshipSkill
from app.models.application import SavedInternship
from app.models.notification import EmailPreference, Notification, EmailLog
from app.models.system import MatchScore, EligibilityResult
from app.email.resend_provider import get_email_provider
from app.email.templates import daily_digest_email, deadline_reminder_email

logger = logging.getLogger(__name__)

# Frequency -> timedelta mapping
FREQUENCY_INTERVALS = {
    "immediate": timedelta(hours=0),
    "daily": timedelta(days=1),
    "every_2_days": timedelta(days=2),
    "weekly": timedelta(weeks=1),
}


async def build_user_digest(
    db: AsyncSession,
    user: User,
    since: datetime,
) -> dict | None:
    """
    Build a digest payload for a single user.

    Returns None if there's nothing new to report.
    """
    user_id = user.id

    # Find new internships posted since `since`
    new_internships_q = (
        select(Internship)
        .where(
            Internship.status == "active",
            Internship.first_seen_at >= since,
        )
        .order_by(Internship.posted_at.desc().nullslast())
        .limit(20)
    )
    result = await db.execute(new_internships_q)
    new_internships = result.scalars().all()

    if not new_internships:
        return None

    # Get match scores for these internships
    matches = []
    for internship in new_internships:
        # Get company name
        company_name = None
        if internship.company_id:
            comp_result = await db.execute(
                select(Company.name).where(Company.id == internship.company_id)
            )
            company_name = comp_result.scalar_one_or_none()

        # Get match score
        match_result = await db.execute(
            select(MatchScore).where(
                MatchScore.user_id == user_id,
                MatchScore.internship_id == internship.id,
            )
        )
        match = match_result.scalar_one_or_none()

        matches.append({
            "id": str(internship.id),
            "title": internship.title,
            "company_name": company_name or "Unknown",
            "location": internship.location,
            "remote_status": internship.remote_status,
            "match_score": round(float(match.overall_score), 1) if match and match.overall_score else None,
            "application_url": internship.application_url,
            "posted_at": str(internship.posted_at) if internship.posted_at else None,
        })

    # Filter and sort: show highest-match items first
    scored_matches = [m for m in matches if m["match_score"] is not None]
    unscored_matches = [m for m in matches if m["match_score"] is None]
    scored_matches.sort(key=lambda x: x["match_score"] or 0, reverse=True)
    top_matches = (scored_matches + unscored_matches)[:10]

    # Count deadlines approaching in next 7 days
    deadline_cutoff = datetime.now(timezone.utc) + timedelta(days=7)
    deadline_q = (
        select(func.count())
        .select_from(SavedInternship)
        .join(Internship, Internship.id == SavedInternship.internship_id)
        .where(
            SavedInternship.user_id == user_id,
            Internship.application_deadline != None,
            Internship.application_deadline <= deadline_cutoff.date(),
            Internship.application_deadline >= datetime.now(timezone.utc).date(),
            Internship.status == "active",
        )
    )
    deadline_result = await db.execute(deadline_q)
    closing_soon = deadline_result.scalar() or 0

    return {
        "matches": top_matches,
        "stats": {
            "new_matches": len(new_internships),
            "closing_soon": closing_soon,
        },
    }


async def send_digest_for_user(
    db: AsyncSession,
    user: User,
    preference: EmailPreference,
) -> bool:
    """
    Build and send a digest email for a single user.
    Returns True if email was sent successfully.
    """
    # Calculate "since" based on frequency
    interval = FREQUENCY_INTERVALS.get(
        preference.digest_frequency, timedelta(days=1)
    )

    # If frequency is "disabled" or "immediate", skip digest
    if preference.digest_frequency in ("disabled", "immediate"):
        return False

    # Use interval to determine what's new
    since = datetime.now(timezone.utc) - interval

    # Build digest
    digest = await build_user_digest(db, user, since)
    if not digest:
        logger.debug(f"No new content for digest: user={user.email}")
        return False

    # Filter by min_match_score preference
    min_score = float(preference.min_match_score or 0)
    if min_score > 0:
        digest["matches"] = [
            m for m in digest["matches"]
            if m["match_score"] is None or m["match_score"] >= min_score
        ]
        if not digest["matches"]:
            return False

    # Generate email
    email_data = daily_digest_email(
        matches=digest["matches"],
        stats=digest["stats"],
    )

    # Send email
    provider = get_email_provider()
    result = await provider.send(
        to=user.email,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data.get("text"),
    )

    # Log the email
    email_log = EmailLog(
        user_id=user.id,
        provider="resend",
        provider_message_id=result.provider_message_id,
        to_email=user.email,
        subject=email_data["subject"],
        template="digest",
        status="sent" if result.success else "failed",
        error=result.error,
    )
    db.add(email_log)

    # Create in-app notification
    if result.success:
        notification = Notification(
            user_id=user.id,
            type="digest",
            title=f"📋 Digest: {digest['stats']['new_matches']} new matches",
            body=f"{digest['stats']['new_matches']} new internships found, "
                 f"{digest['stats']['closing_soon']} closing soon.",
            data={"matches_count": digest["stats"]["new_matches"]},
        )
        db.add(notification)

    return result.success


async def send_deadline_reminders(db: AsyncSession):
    """
    Send deadline reminders for saved internships with deadlines
    approaching in the next 3 days.
    """
    now = datetime.now(timezone.utc)
    reminder_window = now + timedelta(days=3)

    # Find saved internships with approaching deadlines
    query = (
        select(SavedInternship, Internship, User)
        .join(Internship, Internship.id == SavedInternship.internship_id)
        .join(User, User.id == SavedInternship.user_id)
        .where(
            Internship.application_deadline != None,
            Internship.application_deadline <= reminder_window.date(),
            Internship.application_deadline >= now.date(),
            Internship.status == "active",
        )
    )
    result = await db.execute(query)
    rows = result.all()

    sent_count = 0
    for saved, internship, user in rows:
        # Check user preference
        pref_result = await db.execute(
            select(EmailPreference).where(EmailPreference.user_id == user.id)
        )
        pref = pref_result.scalar_one_or_none()
        if pref and (not pref.notify_deadline or pref.unsubscribed):
            continue

        # Check if we already sent a reminder for this
        existing = await db.execute(
            select(EmailLog).where(
                EmailLog.user_id == user.id,
                EmailLog.template == "deadline_reminder",
                EmailLog.subject.contains(internship.title),
                EmailLog.sent_at >= now - timedelta(days=1),
            )
        )
        if existing.scalar_one_or_none():
            continue

        # Get company name
        company_name = "A company"
        if internship.company_id:
            comp_result = await db.execute(
                select(Company.name).where(Company.id == internship.company_id)
            )
            company_name = comp_result.scalar_one_or_none() or company_name

        days_remaining = (internship.application_deadline - now.date()).days

        # Generate and send email
        email_data = deadline_reminder_email(
            internship={
                "company_name": company_name,
                "title": internship.title,
                "application_url": internship.application_url or "#",
            },
            days_remaining=max(0, days_remaining),
        )

        provider = get_email_provider()
        send_result = await provider.send(
            to=user.email,
            subject=email_data["subject"],
            html=email_data["html"],
            text=email_data.get("text"),
        )

        # Log
        db.add(EmailLog(
            user_id=user.id,
            provider="resend",
            provider_message_id=send_result.provider_message_id,
            to_email=user.email,
            subject=email_data["subject"],
            template="deadline_reminder",
            status="sent" if send_result.success else "failed",
            error=send_result.error,
        ))

        # In-app notification
        db.add(Notification(
            user_id=user.id,
            type="deadline",
            title=f"⏰ {days_remaining}d left: {internship.title}",
            body=f"Application deadline for {internship.title} at {company_name} "
                 f"is in {days_remaining} days.",
            data={"internship_id": str(internship.id)},
        ))

        sent_count += 1

    if sent_count > 0:
        logger.info(f"Sent {sent_count} deadline reminders")

    return sent_count


async def run_digest_cycle(db: AsyncSession):
    """
    Run a full digest cycle:
    1. Send digests to users whose frequency interval has elapsed
    2. Send deadline reminders
    """
    logger.info("Starting digest cycle...")

    # Get all users with email preferences
    query = (
        select(User, EmailPreference)
        .outerjoin(EmailPreference, EmailPreference.user_id == User.id)
        .where(User.is_active == True)
    )
    result = await db.execute(query)
    rows = result.all()

    digest_sent = 0
    for user, preference in rows:
        if not preference:
            continue

        if preference.unsubscribed or preference.digest_frequency == "disabled":
            continue

        # Check if it's time to send based on last email
        last_email_q = (
            select(EmailLog.sent_at)
            .where(
                EmailLog.user_id == user.id,
                EmailLog.template == "digest",
                EmailLog.status == "sent",
            )
            .order_by(EmailLog.sent_at.desc())
            .limit(1)
        )
        last_result = await db.execute(last_email_q)
        last_sent_at = last_result.scalar_one_or_none()

        interval = FREQUENCY_INTERVALS.get(
            preference.digest_frequency, timedelta(days=1)
        )

        if last_sent_at and datetime.now(timezone.utc) - last_sent_at < interval:
            continue

        try:
            if await send_digest_for_user(db, user, preference):
                digest_sent += 1
        except Exception as e:
            logger.error(f"Failed to send digest for {user.email}: {e}")

    # Send deadline reminders
    reminder_count = await send_deadline_reminders(db)

    await db.commit()
    logger.info(
        f"Digest cycle complete: {digest_sent} digests, "
        f"{reminder_count} deadline reminders sent"
    )
