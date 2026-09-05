from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.settings import settings
from app.api.routes.gmail_auth import router as gmail_auth_router
from app.api.routes.emails import router as emails_router


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


# Session support
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=False, 
)


# Routers
app.include_router(gmail_auth_router)
app.include_router(emails_router)


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