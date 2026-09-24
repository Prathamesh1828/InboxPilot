from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.logging import setup_logging
from app.core.settings import settings
from app.api.routes import auth, emails, approvals, telegram, gmail_auth, audit, dashboard, integrations
from app.core.limiter import limiter

setup_logging()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Rate limiter middleware
app.add_middleware(SlowAPIMiddleware)

# Security Headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# CORS — explicit origins required when allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "x-auth-token"],
    expose_headers=["Set-Cookie"],
)


# Session support (for OAuth state only — JWT auth uses cookies/headers directly)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="none",          # Required for cross-domain
    https_only=True,           # Must be True when SameSite=none
)


# Routers
app.include_router(gmail_auth.router)
app.include_router(emails.router)
app.include_router(approvals.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(telegram.router)
app.include_router(auth.router)
app.include_router(integrations.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to InboxPilot API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }