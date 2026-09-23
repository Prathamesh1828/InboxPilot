from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserLogin
from app.models.user import User
from app.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def signup(self, user_in: UserCreate) -> User:
        if self.user_repo.get_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
        )
        user = self.user_repo.create(user)
        
        logger.info(f"User signed up: {user.email}")
        return user

    def login(self, login_in: UserLogin) -> User:
        user = self.user_repo.get_by_email(login_in.email)
        
        if user and user.auth_provider == "google":
            raise HTTPException(
                status_code=401, 
                detail="This account uses Google sign-in. Please continue with Google."
            )
            
        if not user or not user.password_hash or not verify_password(login_in.password, user.password_hash):
            logger.warning(f"Failed login attempt for {login_in.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        user.last_login_at = datetime.now(timezone.utc)
        self.user_repo.update(user)

        logger.info(f"User logged in: {user.email}")
        return user
        
    def oauth_login(self, email: str, name: str) -> User:
        user = self.user_repo.get_by_email(email)
        
        if user:
            if user.auth_provider == "password":
                raise HTTPException(
                    status_code=401,
                    detail="This email is registered with a password. Please log in with email and password."
                )
            
            if not user.is_active:
                raise HTTPException(status_code=400, detail="Inactive user")
                
            user.last_login_at = datetime.now(timezone.utc)
            self.user_repo.update(user)
            logger.info(f"User logged in via Google: {user.email}")
            return user
            
        # Create new google user
        new_user = User(
            name=name,
            email=email,
            password_hash=None,
            auth_provider="google"
        )
        new_user = self.user_repo.create(new_user)
        logger.info(f"User signed up via Google: {new_user.email}")
        return new_user
