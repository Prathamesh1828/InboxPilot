from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate, ProfileUpdate, PasswordUpdate
from app.core.security import verify_password, get_password_hash
import logging

router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)

def get_user_settings(db: Session, user_id: str) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("", response_model=UserSettingsResponse)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_settings(db, current_user.id)

@router.patch("", response_model=UserSettingsResponse)
def update_settings(
    settings_in: UserSettingsUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    settings = get_user_settings(db, current_user.id)
    
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    db.commit()
    db.refresh(settings)
    return settings

@router.patch("/profile")
def update_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.name = profile_in.name
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}

@router.post("/change-password")
def change_password(
    password_in: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.password_hash:
        raise HTTPException(status_code=400, detail="Google authenticated accounts cannot change password here")
        
    if not verify_password(password_in.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    current_user.password_hash = get_password_hash(password_in.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/logout-all")
def logout_all_sessions(response: Response, current_user: User = Depends(get_current_user)):
    # With cookie-based stateless JWTs, true logout-all requires a token blacklist or changing a user's token version.
    # For now, we just clear the current cookie to sign out this session. 
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return {"message": "Signed out of current session successfully"}

@router.delete("/account")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This will cascade delete everything linked to user.id if foreign keys are set up with CASCADE
    logger.info(f"User deleted account: {current_user.email}")
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
