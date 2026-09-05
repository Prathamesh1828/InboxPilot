from app.integrations.gmail.oauth import create_google_flow


flow = create_google_flow()

authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    prompt="consent",
)

print("OAuth flow created successfully!")
print("State generated:", state)
print("Authorization URL:")
print(authorization_url)