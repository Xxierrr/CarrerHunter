# Internship Intelligence Platform — Development Checkpoint

> **INSTRUCTIONS FOR RESUMING**: If you switch accounts or start a new conversation,
> share this file with the AI and say: "Continue building from checkpoint."
> The AI will read the completed steps and resume from the next incomplete step.

## Project Location
```
c:\Users\Gyan Prakash Tiwari\OneDrive\Documents\Internship_searcher
```

## Tech Stack
- **Backend**: FastAPI + Python 3.12 + SQLAlchemy 2.0 + Alembic
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS v4
- **Database**: PostgreSQL (Neon free tier)
- **Cache/Queue**: Redis (Upstash free tier)
- **AI**: Gemini Flash (free tier) via google-genai SDK
- **Email**: Resend (free tier)

---

## Phase 1 — MVP Checklist

### Step 1: Project Foundation
- [x] 1.1 — Root project files (.env.example, .gitignore, README.md, docker-compose.yml)
- [x] 1.2 — Backend project structure (apps/api/)
- [x] 1.3 — Backend dependencies (requirements.txt)
- [x] 1.4 — FastAPI app skeleton (main.py, config.py, database.py)
- [x] 1.5 — SQLAlchemy models (all database tables)
- [x] 1.6 — Alembic migration setup

### Step 2: Authentication
- [x] 2.1 — Auth schemas (Pydantic)
- [x] 2.2 — Auth service (register, login, JWT)
- [x] 2.3 — Auth API routes
- [x] 2.4 — Auth dependencies (get_current_user)

### Step 3: User Profile
- [x] 3.1 — Profile schemas
- [x] 3.2 — Profile service (CRUD) — integrated into API routes
- [x] 3.3 — Profile API routes
- [x] 3.4 — Skills management
- [x] 3.5 — Experience management
- [x] 3.6 — Resume upload

### Step 4: Source Adapter Framework
- [x] 4.1 — Base adapter (JobSourceAdapter ABC)
- [x] 4.2 — Adapter registry
- [x] 4.3 — robots.txt checker
- [x] 4.4 — Greenhouse adapter
- [x] 4.5 — Lever adapter
- [x] 4.6 — Ashby adapter
- [x] 4.7 — SmartRecruiters adapter
- [x] 4.8 — Generic career page adapter
- [x] 4.9 — Source configuration seeding (15 sources)

### Step 5: Data Pipeline
- [x] 5.1 — Job normalizer (built into base adapter)
- [x] 5.2 — Deduplication engine (4-level)
- [x] 5.3 — Content hash + change detection
- [x] 5.4 — Background job scheduler (asyncio worker)
- [x] 5.5 — Crawl pipeline (discover → fetch → parse → normalize → store)

### Step 6: AI Service
- [x] 6.1 — AI provider abstraction (AIProvider ABC)
- [x] 6.2 — Gemini provider implementation
- [x] 6.3 — AI cache (PostgreSQL-backed)
- [x] 6.4 — Rate limiter + quota manager (RPM/RPD)
- [x] 6.5 — Structured output schemas (Pydantic)
- [x] 6.6 — Prompt templates
- [x] 6.7 — Requirement extraction
- [x] 6.8 — Role classification

### Step 7: Eligibility Engine
- [x] 7.1 — Deterministic eligibility (Stage 1)
- [x] 7.2 — AI eligibility interpretation (Stage 2) — via Gemini provider
- [x] 7.3 — Eligibility result aggregation
- [x] 7.4 — Match scoring engine (5 dimensions)
- [x] 7.5 — Search service (PostgreSQL FTS + ILIKE fallback)

### Step 8: Internship API
- [x] 8.1 — Internship schemas
- [x] 8.2 — Internship list/detail/search endpoints
- [x] 8.3 — Save/unsave endpoints
- [x] 8.4 — Recommendations endpoint
- [x] 8.5 — Eligibility/match endpoints

### Step 9: Application Tracker
- [x] 9.1 — Application schemas
- [x] 9.2 — Application CRUD API
- [x] 9.3 — Application status transitions
- [x] 9.4 — Application events log

### Step 10: Notifications & Email
- [x] 10.1 — Email provider abstraction
- [x] 10.2 — Resend provider implementation
- [x] 10.3 — Email templates (new match, deadline, digest)
- [x] 10.4 — Notification service — via API routes
- [x] 10.5 — Email preferences API
- [x] 10.6 — Digest builder + scheduler

### Step 11: Admin Panel API
- [x] 11.1 — Admin routes (sources, AI usage, stats)
- [x] 11.2 — Source health monitoring
- [x] 11.3 — Crawl run history

### Step 12: Frontend Foundation
- [x] 12.1 — Next.js project setup
- [x] 12.2 — Tailwind v4 CSS setup + design system
- [x] 12.3 — API client library (axios + interceptors)
- [x] 12.4 — Auth context + protected routes
- [x] 12.5 — Layout (sidebar + top bar + mobile responsive)

### Step 13: Frontend Pages
- [x] 13.1 — Landing page (hero, features, CTA)
- [x] 13.2 — Login / Register pages (password validation)
- [x] 13.3 — Onboarding wizard (3-step: education, skills, preferences)
- [x] 13.4 — Dashboard (stats, latest internships, applications, recommendations)
- [x] 13.5 — Internship list + search/filter (pagination, save)
- [x] 13.6 — Internship detail + eligibility + match breakdown
- [x] 13.7 — Saved internships
- [x] 13.8 — Application tracker (Kanban + list view)
- [x] 13.9 — Profile management (5-tab: personal, education, skills, experience, links)
- [x] 13.10 — Notification center (type icons, mark read)
- [x] 13.11 — Settings / preferences (digest frequency, toggles, min score)
- [x] 13.12 — Admin panel pages (overview, sources, AI usage, crawl runs)

### Step 14: Testing
- [x] 14.1 — Unit tests (match scoring, dedup, robots checker, normalization)
- [x] 14.2 — Integration tests (adapters, registry, templates, schemas)
- [ ] 14.3 — End-to-end smoke tests

### Step 15: Deployment Prep
- [x] 15.1 — Dockerfiles (API, frontend, worker via compose)
- [x] 15.2 — Production configs (docker-compose.yml, standalone Next.js)
- [x] 15.3 — Deployment documentation (DEPLOYMENT.md)

---

## Current Status
**Last completed step**: Steps 1-13 (full stack) + Steps 14.1-14.2 + Steps 15.1-15.3 ✅
**Last updated**: 2026-10-04T12:19:00+05:30
**Next step to build**: Step 14.3 — End-to-end smoke tests (optional)

## Files Created

### Backend (apps/api/)
```
apps/api/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Pydantic settings
│   ├── database.py                  # Async SQLAlchemy
│   ├── main.py                      # FastAPI app
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  # Auth dependencies
│   │   ├── auth.py                  # Auth routes
│   │   ├── profile.py               # Profile routes
│   │   ├── internships.py           # Internship routes + recommendations
│   │   ├── applications.py          # Application routes
│   │   ├── notifications.py         # Notification routes
│   │   ├── ai.py                    # AI routes
│   │   └── admin.py                 # Admin routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py               # Profile, Skill, UserSkill, Experience, Resume
│   │   ├── internship.py            # Internship, Company, Source, InternshipSkill
│   │   ├── application.py           # Application, ApplicationEvent, SavedInternship
│   │   ├── notification.py          # EmailPreference, Notification, EmailLog
│   │   └── system.py                # EligibilityResult, MatchScore, CrawlRun, AIRequest, AICache
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── internship.py
│   │   ├── application.py
│   │   └── notification.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Password hashing, JWT, register/login
│   │   ├── eligibility.py           # Two-stage eligibility engine
│   │   ├── matching.py              # 5-dimension match scorer
│   │   ├── deduplication.py         # 4-level dedup engine
│   │   ├── recommendations.py       # Personalized recommendation engine
│   │   ├── digest.py                # Digest builder + deadline reminders
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── provider.py          # AIProvider ABC
│   │       ├── gemini.py            # GeminiProvider (caching, rate limiting)
│   │       ├── schemas.py           # AI output validation
│   │       ├── prompts.py           # Prompt templates
│   │       ├── cache.py             # AI response cache
│   │       └── rate_limiter.py      # RPM/RPD tracker
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base.py                  # JobSourceAdapter ABC
│   │   ├── registry.py              # Adapter registry
│   │   ├── robots_checker.py        # robots.txt compliance checker
│   │   ├── seed_sources.py          # 15 initial sources
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── greenhouse.py
│   │       ├── lever.py
│   │       ├── ashby.py
│   │       ├── smartrecruiters.py
│   │       └── generic_career_page.py
│   └── email/
│       ├── __init__.py
│       ├── provider.py              # EmailProvider ABC
│       ├── resend_provider.py       # Resend implementation
│       └── templates.py             # HTML email templates
├── tests/
│   ├── __init__.py
│   ├── test_unit.py                 # Unit tests (matching, dedup, robots)
│   └── test_integration.py          # Integration tests (adapters, templates)
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

### Frontend (apps/web/)
```
apps/web/
├── src/
│   ├── app/
│   │   ├── globals.css              # Design system + utilities
│   │   ├── layout.tsx               # Root layout + metadata
│   │   ├── providers.tsx            # React Query + Auth providers
│   │   ├── page.tsx                 # Landing page
│   │   ├── login/page.tsx           # Login
│   │   ├── register/page.tsx        # Register (password checks)
│   │   ├── onboarding/page.tsx      # 3-step onboarding wizard
│   │   └── (dashboard)/
│   │       ├── layout.tsx           # Sidebar + top bar layout
│   │       ├── dashboard/page.tsx   # Dashboard + recommendations
│   │       ├── internships/
│   │       │   ├── page.tsx         # Search + filter + pagination
│   │       │   └── [id]/page.tsx    # Detail + eligibility + match
│   │       ├── saved/page.tsx       # Saved internships
│   │       ├── applications/page.tsx # Kanban + list tracker
│   │       ├── profile/page.tsx     # 5-tab profile manager
│   │       ├── notifications/page.tsx # Notification center
│   │       ├── settings/page.tsx    # Email preferences
│   │       └── admin/page.tsx       # Admin panel (4 tabs)
│   └── lib/
│       ├── api.ts                   # Axios API client
│       ├── auth.tsx                 # Auth context + hooks
│       └── utils.ts                 # Utilities
├── next.config.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

### Root
```
├── docker-compose.yml               # All services orchestration
├── .env.example                     # Environment template
├── .gitignore
├── README.md
├── CHECKPOINT.md                    # This file
├── DEPLOYMENT.md                    # Deployment guide
└── workers/
    └── scheduler.py                 # Background crawl + digest worker
```

## Notes
- Design document: see technical_design.md in conversation artifacts
- Gemini model: gemini-2.0-flash (free tier)
- 15 sources configured: 8 ATS (Greenhouse/Lever) + 7 major companies (UNSUPPORTED_AUTOMATION)
- All secrets go in .env (never committed)
- Full stack complete: backend + frontend + worker + deployment
- Search uses PostgreSQL FTS with ILIKE fallback
- Recommendations use composite scoring: 60% match + 20% skills + 15% recency + 5% location
- Digest supports daily, every_2_days, weekly frequencies with deadline reminders
