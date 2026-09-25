#!/usr/bin/env python
"""
Email Encryption Backfill Script
=================================
Safely migrates existing plaintext email records to AES-256-GCM encrypted storage.

Usage:
    python scripts/encrypt_existing_emails.py [--dry-run] [--batch-size N]

Requirements:
    - EMAIL_ENCRYPTION_KEY must be set in environment BEFORE running.
    - DATABASE_URL must be set or a .env file present.
    - Run with a DB backup already taken.

Safety properties:
    - Idempotent: already-encrypted rows are skipped (is_encrypted check).
    - Resumable: any failure leaves the DB in a consistent state.
    - Dry-run: preview without writing.
    - Each batch is committed independently.
"""

import argparse
import logging
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env for local runs
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("encrypt_backfill")


def main():
    parser = argparse.ArgumentParser(description="Backfill email encryption")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing changes")
    parser.add_argument("--batch-size", type=int, default=100, help="Records per transaction batch")
    args = parser.parse_args()

    # Validate key before touching DB
    from app.security.encryption import _AESGCM, encrypt_email_field, encrypt_email_recipients, is_encrypted
    if _AESGCM is None:
        logger.error("EMAIL_ENCRYPTION_KEY is not set. Aborting.")
        sys.exit(1)

    from app.db.database import SessionLocal
    from app.models.email import Email
    import json

    db = SessionLocal()
    try:
        total = db.query(Email).count()
        logger.info("Total email records in DB: %d", total)

        processed = 0
        encrypted_count = 0
        skipped_count = 0
        offset = 0

        while True:
            batch = db.query(Email).order_by(Email.id.asc()).offset(offset).limit(args.batch_size).all()
            if not batch:
                break

            for email in batch:
                needs_update = False

                # --- sender ---
                if not is_encrypted(email.sender):
                    new_sender = encrypt_email_field(email.sender)
                    if new_sender and not args.dry_run:
                        email.sender = new_sender
                    needs_update = True

                # --- subject ---
                if email.subject is not None and not is_encrypted(email.subject):
                    new_subject = encrypt_email_field(email.subject)
                    if not args.dry_run:
                        email.subject = new_subject
                    needs_update = True

                # --- body ---
                if not is_encrypted(email.body):
                    new_body = encrypt_email_field(email.body)
                    if new_body and not args.dry_run:
                        email.body = new_body
                    needs_update = True

                # --- recipients ---
                # recipients may be stored as JSON list or already as encrypted string
                if isinstance(email.recipients, list):
                    # Plaintext list — encrypt it
                    enc_recipients = encrypt_email_recipients(email.recipients)
                    if enc_recipients and not args.dry_run:
                        email.recipients = enc_recipients
                    needs_update = True
                elif isinstance(email.recipients, str) and not is_encrypted(email.recipients):
                    # Plaintext JSON string — parse and encrypt
                    try:
                        rlist = json.loads(email.recipients)
                        enc_recipients = encrypt_email_recipients(rlist)
                        if enc_recipients and not args.dry_run:
                            email.recipients = enc_recipients
                        needs_update = True
                    except Exception:
                        logger.warning("Could not parse recipients for email id=%d, skipping recipients field", email.id)

                if needs_update:
                    encrypted_count += 1
                    if args.dry_run:
                        logger.info("[DRY-RUN] Would encrypt email id=%d", email.id)
                else:
                    skipped_count += 1

                processed += 1

            if not args.dry_run:
                db.commit()
                logger.info("Committed batch: processed=%d (cumulative)", processed)

            offset += args.batch_size

        logger.info(
            "Backfill complete. Total=%d, Encrypted=%d, Already-encrypted/skipped=%d",
            processed, encrypted_count, skipped_count
        )
        if args.dry_run:
            logger.info("DRY-RUN mode: no changes written.")

    except Exception as exc:
        logger.error("Backfill failed: %s", exc, exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
