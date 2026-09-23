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
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid session")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
        
    return user