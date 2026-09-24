from collections.abc import Generator

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.settings import settings
from fastapi import Request, Depends
from jose import jwt, JWTError
from app.core.security import ALGORITHM
from app.repositories.user_repository import UserRepository
from app.models.user import User

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )
    return api_key

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Resolves the authenticated user from:
      1. The 'session' HTTP-only cookie (set by login/signup endpoints).
      2. The 'Authorization: Bearer <token>' header (fallback for clients
         that cannot use cookies, e.g. mobile apps or when cookie is blocked).

    Both sources are validated identically. This dual approach ensures
    production cross-site auth works even if the browser blocks the cookie
    on the first request before SameSite=None is fully established.
    """
    token: str | None = None

    # 1. Try the HTTP-only session cookie first (preferred)
    token = request.cookies.get("session")

    # 2. Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid session token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")

    return user