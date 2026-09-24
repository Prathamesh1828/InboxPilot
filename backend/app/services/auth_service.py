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
        # Normalize email to lowercase
        email = user_in.email.strip().lower()

        if self.user_repo.get_by_email(email):
            raise HTTPException(status_code=409, detail="An account with this email already exists")

        user = User(
            name=user_in.name.strip(),
            email=email,
            password_hash=get_password_hash(user_in.password),
            auth_provider="password",
        )
        user = self.user_repo.create(user)

        logger.info(f"User signed up: {user.email}")
        return user

    def login(self, login_in: UserLogin) -> User:
        # Normalize email to lowercase
        email = login_in.email.strip().lower()
        user = self.user_repo.get_by_email(email)

        # Generic error to prevent user enumeration
        invalid_credentials_error = HTTPException(
            status_code=401, detail="Invalid email or password"
        )

        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            raise invalid_credentials_error

        # If the user has no password (Google-only account), they must use Google login
        if not user.password_hash:
            raise HTTPException(
                status_code=401,
                detail="This account uses Google sign-in. Please click 'Continue with Google'."
            )

        if not verify_password(login_in.password, user.password_hash):
            logger.warning(f"Failed login attempt for {email}: incorrect password")
            raise invalid_credentials_error

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Your account has been deactivated")

        user.last_login_at = datetime.now(timezone.utc)
        self.user_repo.update(user)

        logger.info(f"User logged in: {user.email}")
        return user

    def oauth_login(self, email: str, name: str) -> User:
        """Find or create a user via Google OAuth."""
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        if user:
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Your account has been deactivated")

            # If account was originally created with email/password, link it to Google seamlessly.
            # Google has verified the email ownership, so this is safe.
            if user.auth_provider == "password":
                logger.info(f"Linking existing password account to Google: {email}")
                user.auth_provider = "google"

            user.last_login_at = datetime.now(timezone.utc)
            self.user_repo.update(user)
            logger.info(f"User logged in via Google: {user.email}")
            return user

        # Create new Google user
        new_user = User(
            name=name.strip() if name else email,
            email=email,
            password_hash=None,
            auth_provider="google",
        )
        new_user = self.user_repo.create(new_user)
        logger.info(f"User signed up via Google: {new_user.email}")
        return new_user
