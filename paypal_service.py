"""
paypal_service.py — PayPal REST API integration for BeehiveOfAI
================================================================
Uses Orders API v2 for checkout, Payouts API for worker/queen payments.
No PayPal SDK — direct REST calls with requests library.
"""

import os
import uuid
import requests

# PayPal base URLs
SANDBOX_BASE = 'https://api-m.sandbox.paypal.com'
LIVE_BASE    = 'https://api-m.paypal.com'


def _get_base_url():
    mode = os.environ.get('PAYPAL_MODE', 'sandbox')
    return LIVE_BASE if mode == 'live' else SANDBOX_BASE


def _get_credentials():
    client_id     = os.environ.get('PAYPAL_CLIENT_ID', '')
    client_secret = os.environ.get('PAYPAL_CLIENT_SECRET', '')
    if not client_id or not client_secret:
        raise RuntimeError('PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set')
    return client_id, client_secret


def get_access_token():
    """Get an OAuth2 access token from PayPal."""
    client_id, client_secret = _get_credentials()
    resp = requests.post(
        f'{_get_base_url()}/v1/oauth2/token',
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'},
        headers={'Accept': 'application/json'},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def create_order(package_name, amount_usd, return_url, cancel_url):
    """
    Create a PayPal order for a Nectar package purchase.
    Returns: dict with 'id' (order ID) and 'approve_url' (redirect buyer here).
    """
    token = get_access_token()
    order_data = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'description': f'BeehiveOfAI — {package_name}',
            'amount': {
                'currency_code': 'USD',
                'value': f'{amount_usd:.2f}',
            },
        }],
        'application_context': {
            'brand_name':  'BeehiveOfAI',
            'landing_page': 'LOGIN',
            'user_action':  'PAY_NOW',
            'return_url':   return_url,
            'cancel_url':   cancel_url,
        },
    }
    resp = requests.post(
        f'{_get_base_url()}/v2/checkout/orders',
        json=order_data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json',
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    approve_url = next(link['href'] for link in data['links'] if link['rel'] == 'approve')
    return {'id': data['id'], 'approve_url': approve_url}


def capture_order(order_id):
    """
    Capture (finalize) a PayPal order after buyer approval.
    Returns: dict with capture details including 'status'.
    """
    token = get_access_token()
    resp = requests.post(
        f'{_get_base_url()}/v2/checkout/orders/{order_id}/capture',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json',
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def send_payout(recipient_email, amount_usd, note='Honey Harvest from BeehiveOfAI'):
    """
    Send a payout to a single recipient via PayPal Payouts API.
    Returns: dict with payout batch details.
    """
    token = get_access_token()
    payout_data = {
        'sender_batch_header': {
            'sender_batch_id': f'beehive-harvest-{uuid.uuid4().hex[:12]}',
            'email_subject':   'You received a Honey Harvest from BeehiveOfAI!',
            'email_message':    note,
        },
        'items': [{
            'recipient_type': 'EMAIL',
            'receiver':       recipient_email,
            'amount': {
                'currency': 'USD',
                'value':    f'{amount_usd:.2f}',
            },
            'note': note,
        }],
    }
    resp = requests.post(
        f'{_get_base_url()}/v1/payments/payouts',
        json=payout_data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json',
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def is_configured():
    """Check if PayPal credentials are set in environment variables."""
    return bool(
        os.environ.get('PAYPAL_CLIENT_ID', '') and
        os.environ.get('PAYPAL_CLIENT_SECRET', '')
    )


def get_client_id():
    """Get the PayPal Client ID (needed for JS SDK on the frontend)."""
    return os.environ.get('PAYPAL_CLIENT_ID', '')


def get_mode():
    """Get current PayPal mode: 'sandbox' or 'live'."""
    return os.environ.get('PAYPAL_MODE', 'sandbox')
