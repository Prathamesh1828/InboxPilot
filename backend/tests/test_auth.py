import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.models.user import User
from app.core.security import verify_password
from unittest.mock import patch, MagicMock
import uuid
import secrets

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_signup_success(db):
    email = f"test_{uuid.uuid4()}@example.com"
    response = client.post("/auth/signup", json={
        "name": "Test User",
        "email": email,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.auth_provider == "password"
    assert verify_password("testpassword123", user.password_hash)

def test_signup_duplicate_email(db):
    email = f"dup_{uuid.uuid4()}@example.com"
    client.post("/auth/signup", json={"name": "Test User", "email": email, "password": "pwd"})
    response = client.post("/auth/signup", json={"name": "Test User 2", "email": email, "password": "pwd"})
    assert response.status_code == 400

def test_login_success(db):
    email = f"login_{uuid.uuid4()}@example.com"
    client.post("/auth/signup", json={"name": "Test Login", "email": email, "password": "pwd"})
    response = client.post("/auth/login", json={"email": email, "password": "pwd"})
    assert response.status_code == 200
    assert "session" in response.cookies

def test_logout(db):
    email = f"logout_{uuid.uuid4()}@example.com"
    client.post("/auth/signup", json={"name": "Test Logout", "email": email, "password": "pwd"})
    login_resp = client.post("/auth/login", json={"email": email, "password": "pwd"})
    
    response = client.post("/auth/logout", cookies={"session": login_resp.cookies.get("session")})
    assert response.status_code == 200
    # Cookie should be cleared
    assert not response.cookies.get("session")

def test_google_only_account_attempting_password_login(db):
    from app.services.auth_service import AuthService
    
    # Create Google user
    email = f"google_only_{uuid.uuid4()}@example.com"
    auth_service = AuthService(db)
    auth_service.oauth_login(email=email, name="Google User")
    
    # Attempt password login
    response = client.post("/auth/login", json={"email": email, "password": "somepassword"})
    assert response.status_code == 401
    assert "uses Google sign-in" in response.json()["detail"]

def test_password_account_attempting_google_login(db):
    from app.services.auth_service import AuthService
    from fastapi import HTTPException
    
    # Create Password user
    email = f"password_only_{uuid.uuid4()}@example.com"
    client.post("/auth/signup", json={"name": "Password User", "email": email, "password": "pwd"})
    
    auth_service = AuthService(db)
    
    with pytest.raises(HTTPException) as excinfo:
        auth_service.oauth_login(email=email, name="Google User")
    assert excinfo.value.status_code == 401
    assert "registered with a password" in excinfo.value.detail

@patch("app.api.routes.gmail_auth.create_google_flow")
def test_google_signup_login_flow(mock_create_flow, db):
    email = f"google_flow_{uuid.uuid4()}@example.com"
    
    # Mock the flow and session
    mock_flow = MagicMock()
    mock_credentials = MagicMock()
    mock_credentials.token = "fake-token"
    mock_credentials.refresh_token = "fake-refresh"
    mock_credentials.expiry = "2099-01-01"
    mock_flow.credentials = mock_credentials
    
    mock_session = MagicMock()
    mock_session.get.return_value.json.return_value = {
        "email": email,
        "name": "Flow User",
        "id": "12345"
    }
    mock_flow.authorized_session.return_value = mock_session
    mock_create_flow.return_value = mock_flow

    from app.api.routes.gmail_auth import _signer
    state = _signer.dumps({"nonce": "nonce", "cv": "cv", "intent": "login"})
    
    response = client.get(f"/auth/gmail/callback?state={state}", follow_redirects=False)
    assert response.status_code == 302
    assert "dashboard" in response.headers["location"]
    assert "session" in response.cookies
    
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.auth_provider == "google"
    assert user.password_hash is None

def test_invalid_oauth_callback(db):
    # No state
    response = client.get("/auth/gmail/callback")
    assert response.status_code == 200
    assert response.json() == {"error": "Missing OAuth state"}
    
    # Invalid state
    response = client.get("/auth/gmail/callback?state=invalidstate123")
    assert response.status_code == 200
    assert "signature verification failed" in response.json()["error"]
