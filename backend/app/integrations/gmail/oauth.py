from google_auth_oauthlib.flow import Flow

from app.core.settings import settings


GMAIL_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def create_google_flow(**kwargs) -> Flow:
    """
    Create and configure the Google OAuth flow.
    """

    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                settings.google_redirect_uri
            ],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=GMAIL_SCOPES,
        redirect_uri=settings.google_redirect_uri,
        **kwargs
    )

    return flow