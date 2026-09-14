from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.google_account import GoogleAccount
from app.integrations.gmail.oauth import GOOGLE_SCOPES


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
        scopes=GOOGLE_SCOPES,
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        if not credentials.token:
            raise RuntimeError(
                "Google token refresh succeeded but no access token was returned"
            )

        account.access_token = credentials.token

        if credentials.expiry is not None:
            account.token_expiry = credentials.expiry

        db.commit()
        db.refresh(account)

    return credentials


def get_gmail_service(
    db: Session,
    account: GoogleAccount,
) -> Any:
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


def archive_email(
    db: Session,
    account: GoogleAccount,
    message_id: str,
) -> str:
    """
    Archive a Gmail message by removing its INBOX label.

    Returns the Gmail message ID.
    """

    service = get_gmail_service(
        db=db,
        account=account,
    )

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": ["INBOX"],
        },
    ).execute()

    return message_id