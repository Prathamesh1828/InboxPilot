from datetime import datetime

from sqlalchemy.orm import Session

from app.models.google_account import GoogleAccount


def get_google_account_by_email(
    db: Session,
    email: str,
) -> GoogleAccount | None:
    """
    Find a Google account by email address.
    """

    return (
        db.query(GoogleAccount)
        .filter(GoogleAccount.email == email)
        .first()
    )


def create_or_update_google_account(
    db: Session,
    email: str,
    google_user_id: str | None,
    access_token: str,
    refresh_token: str | None,
    token_expiry: datetime | None,
) -> GoogleAccount:
    """
    Create a new Google account or update an existing one.

    The refresh token is preserved when Google does not
    provide a new refresh token.
    """

    account = get_google_account_by_email(
        db=db,
        email=email,
    )

    if account:
        # Update Google user ID when available.
        if google_user_id is not None:
            setattr(account, "google_user_id", google_user_id)

        # Always update the access token.
        setattr(account, "access_token", access_token)

        # Only replace the refresh token when Google
        # actually provides a new one.
        if refresh_token is not None:
            setattr(account, "refresh_token", refresh_token)

        # Update expiry when available.
        if token_expiry is not None:
            setattr(account, "token_expiry", token_expiry)

        # Do NOT manually update updated_at.
        # The GoogleAccount model handles this using
        # SQLAlchemy's onupdate configuration.

    else:
        account = GoogleAccount(
            email=email,
            google_user_id=google_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
        )

        db.add(account)

    db.commit()
    db.refresh(account)

    return account