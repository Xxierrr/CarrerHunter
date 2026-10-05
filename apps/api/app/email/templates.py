"""
Email templates for notifications.
HTML email templates for new matches, deadlines, digests, etc.
"""


def new_match_email(internship: dict, match_info: dict) -> dict:
    """Generate a new internship match notification email."""
    company = internship.get("company_name", "A company")
    title = internship.get("title", "Internship")
    match_score = match_info.get("match_score", "N/A")
    eligibility = match_info.get("eligibility_status", "Unknown")
    location = internship.get("location", "Unknown")
    remote = internship.get("remote_status", "")
    skills = internship.get("skills", [])
    url = internship.get("application_url", "#")

    skills_html = "".join(f"<li>{s}</li>" for s in skills[:5])

    html = f"""
    <div style="font-family: -apple-system, system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px 12px 0 0; color: white;">
            <h2 style="margin: 0 0 8px;">🎯 New Internship Match</h2>
            <p style="margin: 0; opacity: 0.9;">A new opportunity matches your profile</p>
        </div>
        <div style="background: #ffffff; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
            <h3 style="margin: 0 0 4px; color: #111827;">{company}</h3>
            <p style="margin: 0 0 16px; color: #6b7280; font-size: 18px;">{title}</p>
            
            <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                <span style="background: #ecfdf5; color: #059669; padding: 4px 12px; border-radius: 20px; font-size: 14px;">
                    Match: {match_score}%
                </span>
                <span style="background: #f0fdf4; color: #16a34a; padding: 4px 12px; border-radius: 20px; font-size: 14px;">
                    {eligibility}
                </span>
            </div>
            
            <p style="color: #6b7280; margin: 0 0 8px;">📍 {location} {('• ' + remote) if remote else ''}</p>
            
            {"<div style='margin: 16px 0;'><strong>Key Skills:</strong><ul style='margin: 4px 0;'>" + skills_html + "</ul></div>" if skills else ""}
            
            <a href="{url}" style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px;">
                View Internship →
            </a>
        </div>
        <p style="color: #9ca3af; font-size: 12px; margin-top: 16px; text-align: center;">
            Based on the information available in the job posting.
        </p>
    </div>
    """

    return {
        "subject": f"🎯 New Match: {title} at {company}",
        "html": html,
        "text": f"New internship match: {title} at {company}. Match: {match_score}%. View: {url}",
    }


def deadline_reminder_email(internship: dict, days_remaining: int) -> dict:
    """Generate a deadline reminder email."""
    company = internship.get("company_name", "A company")
    title = internship.get("title", "Internship")
    url = internship.get("application_url", "#")

    html = f"""
    <div style="font-family: -apple-system, system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 24px; border-radius: 12px 12px 0 0; color: white;">
            <h2 style="margin: 0 0 8px;">⏰ Deadline Approaching</h2>
            <p style="margin: 0; opacity: 0.9;">{days_remaining} day{'s' if days_remaining != 1 else ''} remaining</p>
        </div>
        <div style="background: #ffffff; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
            <h3 style="margin: 0 0 4px; color: #111827;">{company}</h3>
            <p style="margin: 0 0 16px; color: #6b7280; font-size: 18px;">{title}</p>
            <a href="{url}" style="display: inline-block; background: #f59e0b; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                Apply Now →
            </a>
        </div>
    </div>
    """

    return {
        "subject": f"⏰ {days_remaining} days left: {title} at {company}",
        "html": html,
        "text": f"Deadline approaching: {title} at {company}. {days_remaining} days remaining. Apply: {url}",
    }


def daily_digest_email(matches: list[dict], stats: dict) -> dict:
    """Generate daily digest email."""
    new_count = stats.get("new_matches", 0)
    closing_count = stats.get("closing_soon", 0)

    matches_html = ""
    for m in matches[:10]:
        matches_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">
                <strong>{m.get('company_name', '')}</strong><br>
                <span style="color: #6b7280;">{m.get('title', '')}</span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #f3f4f6; text-align: center;">
                <span style="background: #ecfdf5; color: #059669; padding: 2px 8px; border-radius: 10px; font-size: 13px;">
                    {m.get('match_score', 'N/A')}%
                </span>
            </td>
        </tr>
        """

    html = f"""
    <div style="font-family: -apple-system, system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px 12px 0 0; color: white;">
            <h2 style="margin: 0 0 8px;">📋 Your Daily Internship Digest</h2>
            <p style="margin: 0; opacity: 0.9;">{new_count} new matches • {closing_count} closing soon</p>
        </div>
        <div style="background: #ffffff; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
            <h3 style="margin: 0 0 16px; color: #111827;">Top Matches</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f9fafb;">
                        <th style="padding: 8px 12px; text-align: left; font-size: 13px; color: #6b7280;">Company & Role</th>
                        <th style="padding: 8px 12px; text-align: center; font-size: 13px; color: #6b7280;">Match</th>
                    </tr>
                </thead>
                <tbody>
                    {matches_html}
                </tbody>
            </table>
        </div>
    </div>
    """

    return {
        "subject": f"📋 Daily Digest: {new_count} new internship matches",
        "html": html,
        "text": f"Your daily digest: {new_count} new matches, {closing_count} closing soon.",
    }
