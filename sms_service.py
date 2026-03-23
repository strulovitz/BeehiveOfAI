"""
sms_service.py — Twilio Verify API integration for BeehiveOfAI
================================================================
Two-mode: if TWILIO env vars set → real verification SMS, otherwise → test mode.
Uses the Verify API (NOT the Messages API) — no phone number purchase needed.
"""

import os
import random
import string

# ── Configuration ────────────────────────────────────────────────────────────

def is_configured():
    """Check if Twilio Verify credentials are set."""
    return bool(
        os.environ.get('TWILIO_ACCOUNT_SID', '') and
        os.environ.get('TWILIO_AUTH_TOKEN', '') and
        os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')
    )


# Test mode: store codes in memory (only used when Twilio is NOT configured)
_test_codes = {}


def send_verification(phone_number):
    """
    Send a 6-digit verification code to the given phone number.
    Returns True on success, False on failure. Never raises.
    """
    if not phone_number:
        return False

    if is_configured():
        try:
            from twilio.rest import Client
            client = Client(
                os.environ['TWILIO_ACCOUNT_SID'],
                os.environ['TWILIO_AUTH_TOKEN'],
            )
            verification = client.verify.v2 \
                .services(os.environ['TWILIO_VERIFY_SERVICE_SID']) \
                .verifications.create(to=phone_number, channel='sms')
            print(f"[SMS VERIFY] Code sent to {phone_number} — status: {verification.status}")
            return True
        except Exception as e:
            print(f"[SMS VERIFY] Failed to send to {phone_number}: {e}")
            return False
    else:
        # Test mode — generate a code and store it in memory
        code = ''.join(random.choices(string.digits, k=6))
        _test_codes[phone_number] = code
        print(f"[SMS VERIFY TEST MODE] Code for {phone_number}: {code}")
        return True


def check_verification(phone_number, code):
    """
    Check if the given code is correct for the given phone number.
    Returns True if verified, False if not. Never raises.
    """
    if not phone_number or not code:
        return False

    if is_configured():
        try:
            from twilio.rest import Client
            client = Client(
                os.environ['TWILIO_ACCOUNT_SID'],
                os.environ['TWILIO_AUTH_TOKEN'],
            )
            check = client.verify.v2 \
                .services(os.environ['TWILIO_VERIFY_SERVICE_SID']) \
                .verification_checks.create(to=phone_number, code=code)
            approved = check.status == 'approved'
            print(f"[SMS VERIFY] Check for {phone_number}: {check.status}")
            return approved
        except Exception as e:
            print(f"[SMS VERIFY] Check failed for {phone_number}: {e}")
            return False
    else:
        # Test mode — check against stored code
        expected = _test_codes.get(phone_number)
        if expected and expected == code:
            del _test_codes[phone_number]
            print(f"[SMS VERIFY TEST MODE] {phone_number} verified successfully!")
            return True
        else:
            print(f"[SMS VERIFY TEST MODE] {phone_number} verification FAILED (expected {expected}, got {code})")
            return False
