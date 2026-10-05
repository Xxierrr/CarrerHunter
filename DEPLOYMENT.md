# Internship Intelligence Platform — Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Environment Variables](#environment-variables)
- [Manual Setup (Development)](#manual-setup-development)
- [Production Deployment](#production-deployment)
- [Database Migrations](#database-migrations)
- [Architecture Overview](#architecture-overview)

---

## Prerequisites

- **Docker** & **Docker Compose** (recommended for deployment)
- **Node.js 22+** (for frontend development)
- **Python 3.12+** (for backend development)
- **PostgreSQL 16** (Neon free tier or local)
- **Redis** (Upstash free tier or local)

## Quick Start (Docker)

1. **Clone and configure:**
   ```bash
   git clone <repo-url>
   cd Internship_searcher
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start all services:**
   ```bash
   docker compose up -d
   ```

3. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **First-time setup:**
   ```bash
   # Run database migrations
   docker compose exec api alembic upgrade head
   ```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key (free tier) | ✅ |
| `JWT_SECRET` | Secret for JWT token signing | ✅ |
| `EMAIL_API_KEY` | Resend API key (optional for MVP) | ❌ |
| `EMAIL_FROM` | Sender email address | ❌ |
| `FRONTEND_URL` | Frontend URL for CORS | ✅ |
| `APP_ENV` | `development` or `production` | ✅ |

### Getting Free API Keys

- **Gemini**: https://aistudio.google.com/apikey (free, 15 RPM / 1500 RPD)
- **Neon PostgreSQL**: https://neon.tech (free tier, 0.5GB)
- **Upstash Redis**: https://upstash.com (free tier, 10K commands/day)
- **Resend Email**: https://resend.com (free, 100 emails/day)

## Manual Setup (Development)

### Backend

```bash
cd apps/api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/web

# Install dependencies
npm install

# Run dev server
npm run dev
```

### Background Worker

```bash
cd apps/api
python -m workers.scheduler
```

## Production Deployment

### Option 1: Docker Compose (VPS)

```bash
# Build and start in production mode
docker compose -f docker-compose.yml up -d --build

# Check logs
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f web
```

### Option 2: Platform Deployment

**Backend (Railway / Render / Fly.io):**
- Set `apps/api` as the root directory
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set all environment variables

**Worker (same platform, separate service):**
- Same root directory as backend
- Start command: `python -m workers.scheduler`
- Same environment variables

**Frontend (Vercel):**
- Set `apps/web` as the root directory
- Framework preset: Next.js
- Set `NEXT_PUBLIC_API_URL` to your backend URL

### Option 3: Neon + Upstash (Serverless)

For a fully free deployment:
1. **Database**: Neon PostgreSQL (free tier)
2. **Cache**: Upstash Redis (free tier)
3. **Backend**: Railway free tier or Render free tier
4. **Frontend**: Vercel free tier
5. **Email**: Resend free tier

## Database Migrations

```bash
# Create a new migration
cd apps/api
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Architecture Overview

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Next.js    │───▶│   FastAPI    │───▶│  PostgreSQL  │
│   Frontend   │    │   Backend    │    │   (Neon)     │
│   (Vercel)   │    │  (Railway)   │    └──────────────┘
└──────────────┘    │              │    ┌──────────────┐
                    │              │───▶│    Redis     │
                    └──────┬───────┘    │  (Upstash)   │
                           │            └──────────────┘
                    ┌──────┴───────┐
                    │   Worker     │    ┌──────────────┐
                    │  Scheduler   │───▶│  Gemini AI   │
                    │              │    │  (Free tier) │
                    └──────────────┘    └──────────────┘
```

### Services

| Service | Purpose | Port |
|---------|---------|------|
| `web` | Next.js frontend | 3000 |
| `api` | FastAPI backend | 8000 |
| `worker` | Background crawler + digest scheduler | — |
| `db` | PostgreSQL database | 5432 |
| `redis` | Cache + queue | 6379 |

### Data Flow

1. **Worker** crawls 15+ sources every 5 minutes
2. Jobs are normalized, deduplicated, and stored in PostgreSQL
3. **AI** (Gemini) extracts requirements and determines eligibility
4. **API** serves data to the frontend with user-specific scoring
5. **Digest** emails are sent based on user frequency preferences
