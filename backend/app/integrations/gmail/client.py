import base64
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.google_account import GoogleAccount
from app.integrations.gmail.oauth import GOOGLE_SCOPES

logger = logging.getLogger(__name__)


def get_google_credentials(
    db: Session,
    account: GoogleAccount,
) -> Credentials:
    """
    Create Google OAuth credentials from the credentials
    stored in the database.

    If the access token has expired (or is close to expiring),
    refresh it using the stored refresh token and persist the
    new access token.

    Raises ``RuntimeError`` with a safe message if the token
    cannot be refreshed (e.g. revoked by user).
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

    # Always attempt refresh when the token looks expired or
    # we don't have a reliable expiry time.  The google-auth
    # `expired` flag only works if the Credentials object was
    # constructed with an expiry, which we don't do here.
    needs_refresh = (
        credentials.expired
        or account.token_expiry is None
        or (
            account.token_expiry is not None
            and account.token_expiry <= datetime.now(timezone.utc)
        )
    )

    if needs_refresh and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception as refresh_exc:
            raise RuntimeError(
                f"Failed to refresh Google token for integration "
                f"{account.id}: {type(refresh_exc).__name__}"
            ) from refresh_exc

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

    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={
                "removeLabelIds": ["INBOX"],
            },
        ).execute()
    except Exception as exc:
        raise RuntimeError(
            f"Gmail API error while archiving message {message_id}: {exc}"
        ) from exc

    return message_id


def create_gmail_draft(
    db: Session,
    account: GoogleAccount,
    to: str,
    subject: str,
    body: str,
    thread_id: str | None = None,
) -> str:
    """
    Create a Gmail draft.

    Returns the Gmail draft ID.
    """

    service = get_gmail_service(
        db=db,
        account=account,
    )

    message = MIMEText(body)

    message["to"] = to
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    draft_body = {
        "message": {
            "raw": encoded_message,
        }
    }

    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    try:
        draft = (
            service.users()
            .drafts()
            .create(
                userId="me",
                body=draft_body,
            )
            .execute()
        )
    except Exception as e:
        # If testing with fake emails, Gmail rejects fake threadIds with a 400 error.
        # We fallback to creating a standalone draft without the threadId.
        if "Invalid thread_id value" in str(e) and "threadId" in draft_body["message"]:
            del draft_body["message"]["threadId"]
            draft = (
                service.users()
                .drafts()
                .create(
                    userId="me",
                    body=draft_body,
                )
                .execute()
            )
        else:
            raise e

    return draft["id"]