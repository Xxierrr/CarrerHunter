"""
Internship Intelligence Platform — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.database import init_db

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    # Startup
    if settings.is_development:
        await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.app_name,
    description="Continuously discover internship opportunities, determine eligibility, and notify users.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# --- Health Check ---

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


# --- Register API Routers ---
# Import and include routers after app is created to avoid circular imports

from app.api import auth, profile, internships, applications, notifications, ai, admin  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(internships.router, prefix="/api/internships", tags=["internships"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
