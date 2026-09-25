"""
Email field encryption using AES-256-GCM (authenticated encryption).

Architecture:
  - AES-256-GCM provides confidentiality + integrity (tamper detection).
  - Each field encryption produces a unique random nonce (96-bit / 12 bytes).
  - Ciphertext format (URL-safe base64):  v1:<key_version>:<nonce_b64>:<ciphertext+tag_b64>
  - Key version prefix allows future key rotation without a full re-encryption.
  - Key is loaded once from environment at module import time and reused.

Security boundary:
  Protects email content from direct database inspection.
  Does NOT protect against someone who controls both the backend AND its secrets.
"""

import base64
import json
import logging
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# KEY MANAGEMENT
# ---------------------------------------------------------------------------

_KEY_ENV = "EMAIL_ENCRYPTION_KEY"
_KEY_VERSION = "1"
_NONCE_BYTES = 12     # 96-bit nonce recommended for AES-GCM
_SENTINEL_PREFIX = "v1:"

def _load_key() -> AESGCM | None:
    """
    Load and decode the email encryption key from the environment.

    Priority: EMAIL_ENCRYPTION_KEY env var (also read by pydantic settings).
    Returns None when the key is not configured so the app starts in
    plaintext-passthrough mode (useful for local dev without the secret).
    """
    raw = os.environ.get(_KEY_ENV, "").strip()
    if not raw:
        logger.warning(
            "EMAIL_ENCRYPTION_KEY is not set. "
            "Email fields will NOT be encrypted at rest. "
            "Set this variable in production."
        )
        return None
    try:
        # urlsafe_b64decode is lenient about padding
        key_bytes = base64.urlsafe_b64decode(raw + "==")
        if len(key_bytes) != 32:
            raise ValueError(f"Key must be 32 bytes for AES-256, got {len(key_bytes)}")
        return AESGCM(key_bytes)
    except Exception as exc:
        logger.error("Failed to load email encryption key: %s", exc)
        raise RuntimeError("EMAIL_ENCRYPTION_KEY is invalid") from exc


# Singleton — loaded once per worker process.
_AESGCM: AESGCM | None = _load_key()


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def encrypt_email_field(plaintext: str | None) -> str | None:
    """
    Encrypt a single email field value.

    Returns:
        Encrypted token string if encryption is enabled and plaintext is not None.
        None if plaintext is None.
        Plaintext unchanged if encryption key is not configured.
    """
    if plaintext is None:
        return None
    if _AESGCM is None:
        return plaintext  # passthrough in dev/test without key

    import secrets as _secrets
    nonce = _secrets.token_bytes(_NONCE_BYTES)

    ciphertext_with_tag = _AESGCM.encrypt(nonce, plaintext.encode("utf-8"), None)

    nonce_b64 = base64.urlsafe_b64encode(nonce).decode()
    ct_b64 = base64.urlsafe_b64encode(ciphertext_with_tag).decode()

    return f"{_SENTINEL_PREFIX}{_KEY_VERSION}:{nonce_b64}:{ct_b64}"


def decrypt_email_field(token: str | None) -> str | None:
    """
    Decrypt a single email field value.

    Returns:
        Decrypted plaintext string.
        None if token is None.
        Token unchanged if it does not start with our sentinel prefix
        (handles legacy/plaintext rows safely).
    """
    if token is None:
        return None
    if not token.startswith(_SENTINEL_PREFIX):
        # Plaintext or unrecognized format — return as-is.
        return token

    if _AESGCM is None:
        # Key not configured but we have an encrypted token. Log and raise.
        logger.error("Cannot decrypt email field: EMAIL_ENCRYPTION_KEY is not set.")
        raise RuntimeError("Encryption key is not configured.")

    try:
        rest = token[len(_SENTINEL_PREFIX):]         # "<version>:<nonce>:<ct>"
        parts = rest.split(":", 2)
        if len(parts) != 3:
            raise ValueError("Malformed encrypted token")

        _version, nonce_b64, ct_b64 = parts
        nonce = base64.urlsafe_b64decode(nonce_b64)
        ciphertext_with_tag = base64.urlsafe_b64decode(ct_b64)
        plaintext_bytes = _AESGCM.decrypt(nonce, ciphertext_with_tag, None)
        return plaintext_bytes.decode("utf-8")

    except InvalidTag:
        logger.error("AES-GCM authentication tag mismatch — ciphertext may be corrupted or tampered.")
        raise ValueError("Email field decryption failed: integrity check failed.")
    except Exception as exc:
        logger.error("Email field decryption error: %s", type(exc).__name__)
        raise ValueError(f"Email field decryption failed: {exc}") from exc


def encrypt_email_recipients(recipients: list[str] | None) -> str | None:
    """
    Encrypt a JSON-serialized recipients list into a single encrypted token.
    Returns None if recipients is None.
    """
    if recipients is None:
        return None
    return encrypt_email_field(json.dumps(recipients))


def decrypt_email_recipients(token: str | None) -> list[str]:
    """
    Decrypt recipients back to a Python list.
    Falls back gracefully for legacy plaintext JSON stored directly.
    """
    if token is None:
        return []
    decrypted = decrypt_email_field(token)
    if decrypted is None:
        return []
    try:
        return json.loads(decrypted)
    except (json.JSONDecodeError, TypeError):
        return []


def is_encrypted(value: str | None) -> bool:
    """Return True if the value appears to be an encrypted token."""
    return value is not None and value.startswith(_SENTINEL_PREFIX)
