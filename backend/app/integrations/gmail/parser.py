import base64
from datetime import datetime, timezone
from email.utils import getaddresses
from typing import Any


def decode_body(data: str | None) -> str:
    """
    Decode a Gmail base64url-encoded message body.
    """

    if not data:
        return ""

    try:
        decoded = base64.urlsafe_b64decode(
            data + "=" * (-len(data) % 4)
        )

        return decoded.decode("utf-8", errors="replace")

    except Exception:
        return ""


def extract_headers(
    headers: list[dict[str, Any]],
) -> dict[str, str]:
    """
    Convert Gmail headers into a simple dictionary.
    """

    result: dict[str, str] = {}

    for header in headers:
        name = header.get("name", "")
        value = header.get("value", "")

        if name:
            result[name.lower()] = value

    return result


def extract_recipients(
    to_header: str | None,
) -> list[str]:
    """
    Extract email addresses from the To header.
    """

    if not to_header:
        return []

    addresses = getaddresses([to_header])

    return [
        address
        for _, address in addresses
        if address
    ]


def extract_body(payload: dict[str, Any]) -> str:
    """
    Extract the email body from a Gmail message payload.

    Preference:
    1. text/plain
    2. text/html

    Handles nested multipart messages recursively.
    """

    mime_type = payload.get("mimeType")
    body = payload.get("body", {})
    data = body.get("data")

    # Prefer plain text.
    if mime_type == "text/plain" and data:
        return decode_body(data)

    parts = payload.get("parts", [])

    # First search for text/plain.
    for part in parts:
        if part.get("mimeType") == "text/plain":
            part_body = extract_body(part)

            if part_body:
                return part_body

    # If plain text isn't available, use HTML.
    for part in parts:
        if part.get("mimeType") == "text/html":
            part_body = extract_body(part)

            if part_body:
                return part_body

    # Some messages have the body directly in the payload.
    if data:
        return decode_body(data)

    # Recursively inspect nested multipart structures.
    for part in parts:
        part_body = extract_body(part)

        if part_body:
            return part_body

    return ""


def parse_gmail_message(
    message: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a raw Gmail API message into the structure
    required by the Email database model.
    """

    message_id = message.get("id")

    if not message_id:
        raise ValueError("Gmail message is missing an ID")

    thread_id = message.get("threadId")

    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    header_map = extract_headers(headers)

    sender = header_map.get("from", "")

    if not sender:
        raise ValueError(
            f"Gmail message {message_id} is missing a sender"
        )

    recipients = extract_recipients(
        header_map.get("to")
    )

    subject = header_map.get("subject")

    body = extract_body(payload)

    # Gmail's internalDate is milliseconds since Unix epoch.
    internal_date = message.get("internalDate")

    if internal_date:
        received_at = datetime.fromtimestamp(
            int(internal_date) / 1000,
            tz=timezone.utc,
        )
    else:
        received_at = datetime.now(timezone.utc)

    return {
        "provider_message_id": message_id,
        "thread_id": thread_id,
        "sender": sender,
        "recipients": recipients,
        "subject": subject,
        "body": body,
        "received_at": received_at,
    }