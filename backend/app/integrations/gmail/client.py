from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.google_account import GoogleAccount


def get_google_credentials(
    db: Session,
    account: GoogleAccount,
) -> Credentials:
    """
    Create Google OAuth credentials from the credentials
    stored in the database.

    If the access token has expired, refresh it using the
    stored refresh token and persist the new access token.
    """

    if not account.access_token:
        raise RuntimeError("Google account has no access token")

    credentials = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
        ],
    )

    # Refresh the access token if necessary.
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        # Make sure Google returned a new access token.
        if not credentials.token:
            raise RuntimeError(
                "Google token refresh succeeded but no access token was returned"
            )

        # Save the refreshed access token.
        account.access_token = credentials.token

        # Save the new expiry time if Google provided one.
        if credentials.expiry is not None:
            account.token_expiry = credentials.expiry

        # The GoogleAccount model already handles updated_at
        # through SQLAlchemy's onupdate configuration.
        db.commit()
        db.refresh(account)

    return credentials


def get_gmail_service(
    db: Session,
    account: GoogleAccount,
):
    """
    Build and return an authenticated Gmail API service.
    """

    credentials = get_google_credentials(
        db=db,
        account=account,
    )

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )