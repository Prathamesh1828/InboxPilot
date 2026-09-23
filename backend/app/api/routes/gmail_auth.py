import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.core.settings import settings
from app.integrations.gmail.oauth import create_google_flow
from app.repositories.google_account_repository import create_or_update_google_account
from fastapi import HTTPException


router = APIRouter(
    prefix="/auth/gmail",
    tags=["Gmail Authentication"],
)

# Serializer used to sign the OAuth state token.
# The signed token carries the PKCE code_verifier so no session cookie is needed.
_signer = URLSafeSerializer(settings.session_secret)


@router.get("/login")
@limiter.limit("5/minute")
def gmail_login(request: Request, intent: str = "connect"):
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
        "intent": intent,
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
@limiter.limit("5/minute")
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
    name = user_info.get("name", email)
    google_user_id = user_info.get("id")

    if not email:
        return {"error": "Failed to retrieve email address from Google"}
        
    if not credentials or not credentials.token:
        return {"error": "Failed to retrieve access token from Google"}

    intent = state_payload.get("intent", "connect")
    
    if intent == "login":
        from app.services.auth_service import AuthService
        from app.core.security import create_access_token
        from app.api.routes.auth import ACCESS_TOKEN_EXPIRE_MINUTES
        from datetime import timedelta
        
        auth_service = AuthService(db)
        
        # This will raise 401 if user is password-only
        user = auth_service.oauth_login(email=email, name=name)
        
        # Create session
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        
        # Redirect to frontend dashboard
        response = RedirectResponse(url=f"{settings.frontend_url}/dashboard", status_code=302)
        response.set_cookie(
            key="session",
            value=access_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response

    else:
        # Require authenticated user to connect an account
        try:
            user = get_current_user(request=request, db=db)
        except HTTPException:
            return {"error": "You must be logged in to connect a Google account."}

        # Save credentials securely in the database
        create_or_update_google_account(
            db=db,
            user_id=user.id,
            email=email,
            google_user_id=google_user_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry,
        )

        print(f"Successfully connected Google account for {email} to user {user.id}")

        # Trigger an immediate background ingestion of their inbox
        from app.workers.tasks import ingest_all_gmail
        ingest_all_gmail.delay()

        return RedirectResponse(url=f"{settings.frontend_url}/integrations", status_code=302)