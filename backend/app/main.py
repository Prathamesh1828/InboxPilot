from fastapi import FastAPI
from app.core.settings import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

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