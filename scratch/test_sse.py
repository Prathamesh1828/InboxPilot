import requests
import time

url = "http://localhost:8000/audit/stream"
# We need a valid token. Let's get one by logging in.
# I'll just write a quick script to test the backend directly using httpx async client to see the raw chunks.
