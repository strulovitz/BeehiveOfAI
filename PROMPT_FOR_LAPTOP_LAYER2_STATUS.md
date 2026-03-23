# Laptop Sync — Phase 7A Layer 2 Status (2026-03-23)

> Context for laptop's Claude Code to understand what was built today.

## What Was Built Today

### Phase 7A Layer 2 — PayPal Real Payments Integration

**New file: `paypal_service.py`**
- Complete PayPal REST API wrapper using direct HTTP calls (requests library, no SDK)
- Functions: `get_access_token()`, `create_order()`, `capture_order()`, `send_payout()`, `is_configured()`, `get_client_id()`, `get_mode()`
- Two-mode: sandbox (`api-m.sandbox.paypal.com`) or live (`api-m.paypal.com`)
- Uses env vars: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_MODE`

**Updated `models.py`:**
- Added `PayPalOrder` model — tracks PayPal checkout orders for double-spend protection

**Updated `app.py`:**
- `buy_nectars()`: Two-mode (real PayPal redirect if configured, free test mode if not)
- `paypal_success()`: New route — handles PayPal return, captures order, credits Nectars
- `paypal_cancel()`: New route — handles buyer cancellation
- `harvest()`: Two-mode (real PayPal payout if configured, test mode if not)
- Context processor exposes `paypal_enabled` to all templates

**Updated templates:**
- `buy_nectars.html`: Conditional "Secure payments via PayPal" vs "TEST MODE" notice
- `my_balance.html`: Conditional PayPal email vs "TEST MODE" harvest notice

**Updated `requirements.txt`:**
- Added `requests>=2.31.0`

## Current Status

- PayPal checkout (Orders API v2): **TESTED AND WORKING** in sandbox ✅
- PayPal Payouts (Standard Payouts API): Code ready but **WAITING for PayPal to approve Payouts access** ⏳
- System gracefully falls back to test mode if PayPal env vars not set

## Environment Variables Needed (for real PayPal)

```
set PAYPAL_CLIENT_ID=your_client_id_here
set PAYPAL_CLIENT_SECRET=your_secret_here
set PAYPAL_MODE=sandbox
set BEEHIVE_SECRET_KEY=your_secret_key_here
```

## Israel-Specific PayPal Limitations Discovered

- Cannot fund PayPal from Israeli bank — balance only from received payments
- $750/day withdrawal limit via Israeli Visa card
- PayPal Commerce Platform doesn't support Israel — we use regular Merchant mode
- Total marketplace fees: ~5-9% depending on currencies
- No US entity needed, no IRS risk (unlike Stripe)

## Next Steps

- Phase 7B: Ratings improvements (Queen rates Workers after job completion)
- Phase 7C: SMS notifications via Twilio
- Chapter 8: "The Business Engine" — collecting notes, will write when ready

Pull `main` from GitHub to get all changes: `git pull origin main`
