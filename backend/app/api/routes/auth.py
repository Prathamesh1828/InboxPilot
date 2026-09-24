from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.core.settings import settings
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.signup(user_in)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    result = UserResponse.model_validate(user)
    result.access_token = access_token
    return result

@router.post("/login", response_model=UserResponse)
def login(login_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.login(login_in)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    result = UserResponse.model_validate(user)
    result.access_token = access_token
    return result

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
