from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.email_service import get_email
from app.schemas.email import EmailResponse

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)

@router.get(
    "/{email_id}",
    response_model=EmailResponse,
)

def read_email(
    email_id: int,
    db: Session = Depends(get_db),
):
    email = get_email(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email