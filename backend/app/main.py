from fastapi import FastAPI

from app.core.settings import settings
from app.api.routes.emails import router as emails_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

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