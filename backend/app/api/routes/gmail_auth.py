import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.settings import settings
from app.integrations.gmail.oauth import create_google_flow
from app.repositories.google_account_repository import create_or_update_google_account


router = APIRouter(
    prefix="/auth/gmail",
    tags=["Gmail Authentication"],
)

# Serializer used to sign the OAuth state token.
# The signed token carries the PKCE code_verifier so no session cookie is needed.
_signer = URLSafeSerializer(settings.session_secret)


@router.get("/login")
def gmail_login(request: Request):
    """
    Start Google OAuth flow.

    Instead of storing state/code_verifier in a session cookie (which is
    unreliable across the localhost->Google->localhost redirect chain), we
    embed a signed payload inside the OAuth ``state`` parameter.  Google
    echoes the state back unchanged, so we can recover the verifier in the
    callback without any server-side state.
    """

    # 1. Pre-generate a PKCE code_verifier (43-128 URL-safe chars).
    #    token_urlsafe(96) -> 128-char base64url string, within PKCE spec.
    code_verifier = secrets.token_urlsafe(96)

    # 2. Build a signed state token that contains the verifier + a random nonce.
    #    URLSafeSerializer signs + base64url-encodes -> URL-safe output.
    state_payload = {
        "nonce": secrets.token_urlsafe(16),
        "cv": code_verifier,
    }
    signed_state = _signer.dumps(state_payload)

    # 3. Create the flow with our pre-generated verifier so that
    #    authorization_url() uses it for the PKCE code_challenge.
    flow = create_google_flow(code_verifier=code_verifier)

    # 4. Generate the authorization URL, injecting our signed state.
    #    Passing state= here puts it into the URL; the callback creates
    #    a brand-new flow so _state consistency doesn't matter here.
    authorization_url, _ = flow.authorization_url(
        state=signed_state,
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    print("OAuth login started - signed state embedded in URL")
    print("Code verifier length:", len(code_verifier))

    return RedirectResponse(url=authorization_url, status_code=302)


@router.get("/callback")
def gmail_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle Google's OAuth callback.

    The ``state`` query-parameter returned by Google is the signed token we
    created in /login. We verify its signature and extract the code_verifier
    from it, then exchange the authorization code for tokens.
    """

    google_state = request.query_params.get("state")

    if not google_state:
        return {"error": "Missing OAuth state"}

    # Verify signature and decode the payload.
    try:
        state_payload = _signer.loads(google_state)
    except BadSignature:
        return {"error": "Invalid OAuth state - signature verification failed"}

    code_verifier = state_payload.get("cv")

    print("Code verifier recovered from signed state:", bool(code_verifier))

    if not code_verifier:
        return {"error": "Missing code verifier in state payload"}

    # Create a fresh flow. Passing state= initialises oauth2session._state so
    # fetch_token can validate the state echoed back in the authorization_response.
    flow = create_google_flow(
        state=google_state,
        code_verifier=code_verifier,
    )

    # Exchange the authorization code for tokens.
    # fetch_token uses self.code_verifier automatically (set via constructor).
    flow.fetch_token(
        authorization_response=str(request.url),
    )

    credentials = flow.credentials

    # Fetch user info using the authorized session
    auth_session = flow.authorized_session()
    user_info_resp = auth_session.get("https://www.googleapis.com/oauth2/v2/userinfo")
    user_info = user_info_resp.json()

    email = user_info.get("email")
    google_user_id = user_info.get("id")

    if not email:
        return {"error": "Failed to retrieve email address from Google"}

    # Save credentials securely in the database
    create_or_update_google_account(
        db=db,
        email=email,
        google_user_id=google_user_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_expiry=credentials.expiry,
    )

    print(f"Successfully connected Google account for {email}")

    return {
        "message": "Google account connected",
        "email": email,
    }