# Phase 7A Layer 2: PayPal Commerce Platform — Real Payments

## Prompt for Sonnet 4.6 (the coder)

> Nir: Copy-paste this ENTIRE file to Sonnet 4.6 AFTER you complete the prerequisite steps below.

---

## Context

Phase 7A Layer 1 is DONE — we have the full internal Nectar Credits engine working (buy packages, deduct on job submission, revenue split on completion, Honeycomb Balance, Honey Harvest request). Everything is tracked in the database.

Layer 2 connects the **real money** part — when a Beekeeper buys a Honey Package, they pay real dollars via PayPal. When a Queen/Worker requests a Honey Harvest, they receive real dollars to their PayPal account.

**APIs used:**
- **PayPal Orders API v2** — for accepting payments (checkout)
- **PayPal Payouts API** — for sending money to Queens/Workers
- **PayPal JS SDK** — for rendering PayPal checkout buttons on the frontend
- **No Python SDK needed** — we use direct REST calls with `requests`

---

## PREREQUISITE — Nir Must Do This BEFORE Coding

### Step 1: Create a PayPal Developer Account

1. Go to https://developer.paypal.com/
2. Log in with your PayPal account (or create one)
3. You need a PayPal **Business** account (not Personal). If you have Personal, upgrade it at paypal.com.

### Step 2: Create a Sandbox App

1. In the PayPal Developer Dashboard, go to **Apps & Credentials**
2. Make sure you're in **Sandbox** mode (toggle at the top)
3. Click **Create App**
4. Name it: "BeehiveOfAI"
5. Copy the **Client ID** and **Client Secret** — you'll need these

### Step 3: Create Sandbox Test Accounts

1. In the Developer Dashboard, go to **Sandbox** → **Accounts**
2. PayPal usually creates two default sandbox accounts automatically:
   - A **Business** account (simulating the merchant — BeehiveOfAI)
   - A **Personal** account (simulating a buyer — the Beekeeper)
3. Note the **email** and **password** of the Personal sandbox account — you'll use these to test checkout
4. Note the **email** of the Business sandbox account — payouts will come FROM this account

### Step 4: Request Payouts API Access (may take time)

1. In the Developer Dashboard, check if Payouts API is available for your app
2. If not, you may need to apply for it — PayPal sometimes requires approval
3. **We can build and test checkout (Orders API) right away** — Payouts can wait if approval takes time

### Step 5: Set Environment Variables

On the Desktop (where the website runs), set these env vars before running the server:

```bash
export PAYPAL_CLIENT_ID="your-sandbox-client-id"
export PAYPAL_CLIENT_SECRET="your-sandbox-client-secret"
export PAYPAL_MODE="sandbox"
```

When ready for production, change `PAYPAL_MODE` to `"live"` and use live credentials.

---

## What to Build

### 1. New File: `paypal_service.py`

Create a new file `paypal_service.py` in the project root. This handles all PayPal API communication.

```python
"""
paypal_service.py — PayPal REST API integration for BeehiveOfAI
================================================================
Uses Orders API v2 for checkout, Payouts API for worker/queen payments.
No PayPal SDK — direct REST calls with requests library.
"""

import os
import requests
from functools import lru_cache

# PayPal endpoints
SANDBOX_BASE = 'https://api-m.sandbox.paypal.com'
LIVE_BASE = 'https://api-m.paypal.com'


def _get_base_url():
    mode = os.environ.get('PAYPAL_MODE', 'sandbox')
    return LIVE_BASE if mode == 'live' else SANDBOX_BASE


def _get_credentials():
    client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
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
            'brand_name': 'BeehiveOfAI',
            'landing_page': 'LOGIN',
            'user_action': 'PAY_NOW',
            'return_url': return_url,
            'cancel_url': cancel_url,
        },
    }
    resp = requests.post(
        f'{_get_base_url()}/v2/checkout/orders',
        json=order_data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
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
            'Content-Type': 'application/json',
        },
    )
    resp.raise_for_status()
    return resp.json()


def send_payout(recipient_email, amount_usd, note='Honey Harvest from BeehiveOfAI'):
    """
    Send a payout to a single recipient via PayPal Payouts API.
    Returns: dict with payout batch details.
    """
    import uuid
    token = get_access_token()
    payout_data = {
        'sender_batch_header': {
            'sender_batch_id': f'beehive-harvest-{uuid.uuid4().hex[:12]}',
            'email_subject': 'You received a Honey Harvest from BeehiveOfAI!',
            'email_message': note,
        },
        'items': [{
            'recipient_type': 'EMAIL',
            'receiver': recipient_email,
            'amount': {
                'currency': 'USD',
                'value': f'{amount_usd:.2f}',
            },
            'note': note,
        }],
    }
    resp = requests.post(
        f'{_get_base_url()}/v1/payments/payouts',
        json=payout_data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
    )
    resp.raise_for_status()
    return resp.json()


def is_configured():
    """Check if PayPal credentials are set."""
    client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
    client_secret = os.environ.get('PAYPAL_CLIENT_SECRET', '')
    return bool(client_id and client_secret)


def get_client_id():
    """Get the PayPal Client ID (needed for JS SDK on the frontend)."""
    return os.environ.get('PAYPAL_CLIENT_ID', '')


def get_mode():
    """Get current PayPal mode (sandbox or live)."""
    return os.environ.get('PAYPAL_MODE', 'sandbox')
```

### 2. Add `requests` to `requirements.txt`

Add `requests` to requirements.txt if not already present.

### 3. New Database Model: `PayPalOrder` (in `models.py`)

Track PayPal orders so we can match the callback to the right user/package.

Add this model after `EarningsTransaction`:

```python
class PayPalOrder(db.Model):
    """Track PayPal checkout orders — maps PayPal order ID to our package purchase."""
    __tablename__ = 'paypal_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paypal_order_id = db.Column(db.String(100), unique=True, nullable=False)
    package_id = db.Column(db.String(20), nullable=False)  # 'honey_drop', 'honey_jar', 'honey_pot'
    amount_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='created')  # 'created', 'captured', 'cancelled', 'failed'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    captured_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='paypal_orders')
```

### 4. Modify `app.py` — Import paypal_service and add new routes

Add to imports at the top of `app.py`:

```python
import paypal_service
from models import db, User, Hive, HiveMember, Job, SubTask, Rating, NectarTransaction, EarningsTransaction, PayPalOrder
```

### 5. Modify the `/buy-nectars` Route — Two Modes

The route should work in TWO modes:
- **If PayPal is NOT configured** (no env vars): keep the current free test mode (Layer 1 behavior)
- **If PayPal IS configured** (env vars set): use real PayPal checkout

Replace the existing `buy_nectars()` function:

```python
@app.route('/buy-nectars', methods=['GET', 'POST'])
@login_required
@role_required('beekeeper')
def buy_nectars():
    paypal_enabled = paypal_service.is_configured()

    if request.method == 'POST':
        package_id = request.form.get('package_id')
        package = NECTAR_PACKAGES.get(package_id)
        if not package:
            flash('Invalid package selected.', 'danger')
            return redirect(url_for('buy_nectars'))

        if paypal_enabled:
            # Real PayPal checkout — create order and redirect to PayPal
            try:
                result = paypal_service.create_order(
                    package_name=package['name'],
                    amount_usd=package['price'],
                    return_url=url_for('paypal_success', _external=True),
                    cancel_url=url_for('paypal_cancel', _external=True),
                )
                # Save order to DB so we can match it on return
                pp_order = PayPalOrder(
                    user_id=current_user.id,
                    paypal_order_id=result['id'],
                    package_id=package_id,
                    amount_usd=package['price'],
                    status='created',
                )
                db.session.add(pp_order)
                db.session.commit()
                # Redirect to PayPal
                return redirect(result['approve_url'])
            except Exception as e:
                flash(f'PayPal error: {str(e)}. Please try again.', 'danger')
                return redirect(url_for('buy_nectars'))
        else:
            # Test mode — free Nectars (Layer 1 behavior)
            current_user.nectar_balance += package['nectars']
            db.session.add(NectarTransaction(
                user_id=current_user.id,
                amount=package['nectars'],
                balance_after=current_user.nectar_balance,
                transaction_type='purchase',
                description=f"Purchased {package['name']} ({package['nectars']} Nectars) — TEST MODE",
            ))
            db.session.commit()
            flash(f"TEST MODE: No real payment charged. You received {package['nectars']} Nectars ({package['name']})!", 'success')
            return redirect(url_for('dashboard'))

    return render_template('buy_nectars.html', packages=NECTAR_PACKAGES, paypal_enabled=paypal_enabled)
```

### 6. New Routes: PayPal Success and Cancel Callbacks

```python
@app.route('/paypal/success')
@login_required
def paypal_success():
    """PayPal redirects here after the buyer approves the payment."""
    # PayPal adds ?token=ORDER_ID to the return URL
    order_id = request.args.get('token')
    if not order_id:
        flash('Invalid PayPal response.', 'danger')
        return redirect(url_for('buy_nectars'))

    # Look up the order in our DB
    pp_order = PayPalOrder.query.filter_by(paypal_order_id=order_id, user_id=current_user.id).first()
    if not pp_order or pp_order.status != 'created':
        flash('Order not found or already processed.', 'warning')
        return redirect(url_for('buy_nectars'))

    # Capture the payment (actually charge the buyer)
    try:
        capture = paypal_service.capture_order(order_id)
        if capture.get('status') == 'COMPLETED':
            # Payment successful — add Nectars
            package = NECTAR_PACKAGES.get(pp_order.package_id)
            if package:
                current_user.nectar_balance += package['nectars']
                db.session.add(NectarTransaction(
                    user_id=current_user.id,
                    amount=package['nectars'],
                    balance_after=current_user.nectar_balance,
                    transaction_type='purchase',
                    description=f"Purchased {package['name']} ({package['nectars']} Nectars) via PayPal",
                ))
                pp_order.status = 'captured'
                pp_order.captured_at = datetime.now(timezone.utc)
                db.session.commit()
                flash(f"Payment successful! You received {package['nectars']} Nectars ({package['name']})!", 'success')
            else:
                flash('Package not found. Please contact support.', 'danger')
        else:
            pp_order.status = 'failed'
            db.session.commit()
            flash('Payment was not completed. Please try again.', 'warning')
    except Exception as e:
        pp_order.status = 'failed'
        db.session.commit()
        flash(f'Error capturing payment: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/paypal/cancel')
@login_required
def paypal_cancel():
    """PayPal redirects here if the buyer cancels."""
    order_id = request.args.get('token')
    if order_id:
        pp_order = PayPalOrder.query.filter_by(paypal_order_id=order_id, user_id=current_user.id).first()
        if pp_order and pp_order.status == 'created':
            pp_order.status = 'cancelled'
            db.session.commit()
    flash('Payment cancelled. No charges were made.', 'info')
    return redirect(url_for('buy_nectars'))
```

### 7. Modify the `/harvest` Route — Real PayPal Payouts

Replace the existing `harvest()` function to support both test mode and real PayPal payouts:

```python
@app.route('/harvest', methods=['POST'])
@login_required
@role_required('queen', 'worker')
def harvest():
    if current_user.honeycomb_balance < HARVEST_THRESHOLD:
        flash(f'You need at least ${HARVEST_THRESHOLD:.2f} in your Honeycomb Balance to harvest. '
              f'Current balance: ${current_user.honeycomb_balance:.2f}', 'warning')
        return redirect(url_for('my_balance'))

    amount = current_user.honeycomb_balance
    paypal_enabled = paypal_service.is_configured()

    if paypal_enabled:
        # Real PayPal payout
        recipient_email = current_user.email  # They must have a PayPal account with this email
        try:
            result = paypal_service.send_payout(
                recipient_email=recipient_email,
                amount_usd=amount,
                note=f'Honey Harvest from BeehiveOfAI — Thank you for your work!',
            )
            db.session.add(EarningsTransaction(
                user_id=current_user.id,
                amount=-amount,
                balance_after=0.0,
                transaction_type='harvested',
                description=f'Honey Harvest of ${amount:.2f} sent to {recipient_email} via PayPal',
            ))
            current_user.honeycomb_balance = 0.0
            db.session.commit()
            flash(f'🍯 Honey Harvest complete! ${amount:.2f} has been sent to your PayPal ({recipient_email}).', 'success')
        except Exception as e:
            flash(f'PayPal payout error: {str(e)}. Your balance has not been changed. Please try again.', 'danger')
    else:
        # Test mode (no PayPal)
        db.session.add(EarningsTransaction(
            user_id=current_user.id,
            amount=-amount,
            balance_after=0.0,
            transaction_type='harvested',
            description=f'Honey Harvest of ${amount:.2f} — TEST MODE (PayPal payout coming soon)',
        ))
        current_user.honeycomb_balance = 0.0
        db.session.commit()
        flash(f'🍯 Honey Harvest requested! ${amount:.2f} will be sent to your PayPal. '
              f'(TEST MODE: No real payout yet)', 'success')

    return redirect(url_for('my_balance'))
```

### 8. Modify `buy_nectars.html` — Show Real Prices When PayPal is Enabled

Update the test mode notice. Change this section:

```html
  <!-- Test mode notice — only show when PayPal is NOT configured -->
  {% if not paypal_enabled %}
  <div class="alert alert-info" style="margin-bottom:1.5rem">
    ℹ️ <strong>TEST MODE:</strong> Purchases are free during beta — no real payment is charged.
    PayPal integration coming soon!
  </div>
  {% else %}
  <div class="alert alert-success" style="margin-bottom:1.5rem">
    ✅ <strong>Secure payments via PayPal.</strong> You will be redirected to PayPal to complete your purchase.
  </div>
  {% endif %}
```

The rest of the buy_nectars.html template stays the same — the package cards and buy buttons work for both modes.

### 9. Update `my_balance.html` — Harvest Payout Notice

In the Queen/Worker harvest section, update the TEST MODE notice to be conditional:

When PayPal IS configured, show:
```html
<p class="text-muted" style="font-size:0.82rem;margin-top:0.75rem">
  Payout will be sent to your PayPal account ({{ current_user.email }}).
</p>
```

When PayPal is NOT configured, show the existing test mode notice.

To make `paypal_enabled` available, pass it from the `/my-balance` route or add it to the context processor.

### 10. Update Context Processor (in `app.py`)

Add `paypal_enabled` so all templates can check it:

```python
@app.context_processor
def inject_balances():
    if current_user.is_authenticated:
        return {
            'user_nectar_balance': current_user.nectar_balance,
            'user_honeycomb_balance': current_user.honeycomb_balance,
            'paypal_enabled': paypal_service.is_configured(),
        }
    return {'paypal_enabled': paypal_service.is_configured()}
```

---

## Files to Modify (Summary)

| File | Changes |
|------|---------|
| `paypal_service.py` | **NEW** — PayPal REST API wrapper (auth, create order, capture, payout) |
| `models.py` | Add `PayPalOrder` model |
| `app.py` | Import paypal_service + PayPalOrder; modify buy_nectars + harvest routes; add paypal_success + paypal_cancel routes; update context processor |
| `requirements.txt` | Add `requests` if not present |
| `templates/buy_nectars.html` | Conditional test mode vs PayPal notice |
| `templates/my_balance.html` | Conditional harvest payout notice |

---

## How to Test (Sandbox Mode)

### Test 1: Checkout Flow (buying Nectars with PayPal)

1. Set env vars: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_MODE=sandbox`
2. Delete `instance/beehive.db`, run `python seed_data.py`
3. Run `python app.py`
4. Login as `company1@test.com / test123`
5. Go to `/buy-nectars` — should see "Secure payments via PayPal" notice
6. Click "Buy Honey Drop"
7. You should be redirected to PayPal's sandbox checkout page
8. Log in with the sandbox **Personal** buyer account
9. Approve the payment
10. You should be redirected back to your site with a success message
11. Check: Nectar balance increased by 20, NectarTransaction created

### Test 2: Without PayPal (test mode fallback)

1. Start the server WITHOUT PayPal env vars set
2. Everything works exactly like Layer 1 — free test purchases
3. No errors, no PayPal references in the UI

### Test 3: Payout (if Payouts API access is granted)

1. Login as queen1 or worker1
2. Manually increase their honeycomb_balance to $50+ (or submit/complete enough jobs)
3. Click "Request Honey Harvest" on `/my-balance`
4. Check PayPal sandbox dashboard — payout should appear

---

## Important Notes

- **Graceful fallback:** If PayPal is not configured (no env vars), the app works exactly like Layer 1 — free test mode. No crashes, no errors.
- **Security:** PayPal credentials are NEVER stored in code — only in environment variables.
- **CSRF:** The PayPal callbacks (`/paypal/success` and `/paypal/cancel`) are GET requests (PayPal redirects back). They don't need CSRF exemption because they're just GETs that then do server-side verification.
- **Double-spend protection:** We check `pp_order.status == 'created'` before capturing — prevents double captures.
- **Delete `instance/beehive.db` before testing** — new PayPalOrder table needs to be created.
- **Add `requests` to requirements.txt** — needed for PayPal API calls.
