# Internship Intelligence Platform

A production-quality web application that continuously discovers internship opportunities, determines eligibility, and notifies users about relevant matches.

## Architecture

- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python 3.12 + SQLAlchemy 2.0
- **Database**: PostgreSQL (with pgvector for future semantic search)
- **Cache/Queue**: Redis
- **AI**: Gemini Flash (free tier) via google-genai SDK
- **Email**: Resend

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis

### Backend Setup

```bash
cd apps/api
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp ../../.env.example .env   # Edit with your values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd apps/web
npm install
cp ../../.env.example .env.local  # Edit with your values
npm run dev
```

### Docker (Full Stack)

```bash
docker-compose up -d
```

## Project Structure

```
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── workers/          # Background job workers
├── tests/            # Test suites
├── docs/             # Documentation
├── docker-compose.yml
├── .env.example
└── CHECKPOINT.md     # Development progress tracker
```

## Environment Variables

See `.env.example` for all required configuration.

## License

Private — All rights reserved.
