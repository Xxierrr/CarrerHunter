"""
Source configuration seed data.

These are the initial sources with their adapter configurations.
Run this script to populate the sources table.
"""

# Each entry defines a source with its adapter name and configuration
INITIAL_SOURCES = [
    # --- ATS Sources (Public APIs) ---
    {
        "name": "Stripe (Greenhouse)",
        "type": "ats",
        "adapter_name": "greenhouse",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/stripe",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 3,
        "config": {"board_token": "stripe", "company_name": "Stripe"},
    },
    {
        "name": "Cloudflare (Greenhouse)",
        "type": "ats",
        "adapter_name": "greenhouse",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/cloudflare",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 3,
        "config": {"board_token": "cloudflare", "company_name": "Cloudflare"},
    },
    {
        "name": "Airbnb (Greenhouse)",
        "type": "ats",
        "adapter_name": "greenhouse",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/airbnb",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 3,
        "config": {"board_token": "airbnb", "company_name": "Airbnb"},
    },
    {
        "name": "Coinbase (Greenhouse)",
        "type": "ats",
        "adapter_name": "greenhouse",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/coinbase",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 4,
        "config": {"board_token": "coinbase", "company_name": "Coinbase"},
    },
    {
        "name": "Twitch (Greenhouse)",
        "type": "ats",
        "adapter_name": "greenhouse",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/twitch",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 4,
        "config": {"board_token": "twitch", "company_name": "Twitch"},
    },
    {
        "name": "Figma (Lever)",
        "type": "ats",
        "adapter_name": "lever",
        "base_url": "https://api.lever.co/v0/postings/figma",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 3,
        "config": {"company_slug": "figma", "company_name": "Figma"},
    },
    {
        "name": "Notion (Lever)",
        "type": "ats",
        "adapter_name": "lever",
        "base_url": "https://api.lever.co/v0/postings/notion",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 3,
        "config": {"company_slug": "notion", "company_name": "Notion"},
    },
    {
        "name": "Reddit (Lever)",
        "type": "ats",
        "adapter_name": "lever",
        "base_url": "https://api.lever.co/v0/postings/reddit",
        "crawl_frequency_minutes": 360,
        "automation_status": "supported",
        "priority": 4,
        "config": {"company_slug": "reddit", "company_name": "Reddit"},
    },

    # --- Major Companies (UNSUPPORTED_AUTOMATION — link to official pages) ---
    {
        "name": "Google Careers",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://careers.google.com/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 1,
        "config": {"company_name": "Google", "career_url": "https://careers.google.com/jobs/results/?employment_type=INTERN"},
    },
    {
        "name": "Microsoft Careers",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://careers.microsoft.com/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 1,
        "config": {"company_name": "Microsoft", "career_url": "https://careers.microsoft.com/us/en/search-results?keywords=intern"},
    },
    {
        "name": "Amazon Jobs",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://www.amazon.jobs/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 1,
        "config": {"company_name": "Amazon", "career_url": "https://www.amazon.jobs/en/search?base_query=intern"},
    },
    {
        "name": "Meta Careers",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://www.metacareers.com/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 1,
        "config": {"company_name": "Meta", "career_url": "https://www.metacareers.com/jobs?q=intern"},
    },
    {
        "name": "Apple Jobs",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://jobs.apple.com/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 1,
        "config": {"company_name": "Apple", "career_url": "https://jobs.apple.com/en-us/search?search=intern"},
    },
    {
        "name": "NVIDIA Careers",
        "type": "career_page",
        "adapter_name": "generic_career_page",
        "base_url": "https://nvidia.wd5.myworkdayjobs.com/",
        "crawl_frequency_minutes": 1440,
        "automation_status": "unsupported_automation",
        "priority": 2,
        "config": {"company_name": "NVIDIA", "career_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=intern"},
    },
]


async def seed_sources(db):
    """Seed the database with initial source configurations."""
    from sqlalchemy import select
    from app.models.internship import Source

    for source_data in INITIAL_SOURCES:
        # Check if source already exists
        result = await db.execute(
            select(Source).where(Source.name == source_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        source = Source(
            name=source_data["name"],
            type=source_data["type"],
            base_url=source_data.get("base_url"),
            adapter_name=source_data["adapter_name"],
            crawl_frequency_minutes=source_data.get("crawl_frequency_minutes", 360),
            automation_status=source_data.get("automation_status", "supported"),
            priority=source_data.get("priority", 5),
            config=source_data.get("config", {}),
            enabled=True,
        )
        db.add(source)

    await db.flush()
