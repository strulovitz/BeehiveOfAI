# Phase 7C: SMS Notifications via Twilio — Detailed Plan for Sonnet 4.6

> **Opus 4.6 planned this. Sonnet 4.6 codes it.**
> Read this entire plan before writing any code. Follow it step by step.

---

## Overview

Add optional SMS notifications to BeehiveOfAI using Twilio. Same two-mode architecture as PayPal: if Twilio env vars are set → real SMS; if not → log to console (no crash, no error).

**SMS notifications to implement:**
1. **Job submitted** → Queen gets SMS ("New job in your Hive!")
2. **Job completed** → Beekeeper gets SMS ("Your job is ready!")
3. **Worker joined Hive** → Queen gets SMS ("A new Worker joined your Hive!")
4. **Honey Harvest requested** → User gets SMS ("Your payout of $X has been requested")

**Only send SMS to users who have a phone number set.** The phone field already exists in the User model (`phone = db.Column(db.String(20), nullable=True)`) and the registration form.

---

## Step 1: Create `sms_service.py`

Create a new file `sms_service.py` in the project root. Same pattern as `paypal_service.py` — check env vars, provide simple functions, never crash.

```python
"""
sms_service.py — Twilio SMS integration for BeehiveOfAI
========================================================
Two-mode: if TWILIO env vars set → real SMS, otherwise → console log.
"""

import os

# Check if Twilio is configured
def is_configured():
    return bool(
        os.environ.get('TWILIO_ACCOUNT_SID', '') and
        os.environ.get('TWILIO_AUTH_TOKEN', '') and
        os.environ.get('TWILIO_PHONE_NUMBER', '')
    )


def send_sms(to_phone, message):
    """Send an SMS. Returns True on success, False on failure. Never raises."""
    if not to_phone:
        return False

    if is_configured():
        try:
            from twilio.rest import Client
            client = Client(
                os.environ['TWILIO_ACCOUNT_SID'],
                os.environ['TWILIO_AUTH_TOKEN'],
            )
            msg = client.messages.create(
                body=message,
                from_=os.environ['TWILIO_PHONE_NUMBER'],
                to=to_phone,
            )
            print(f"[SMS] Sent to {to_phone}: {msg.sid}")
            return True
        except Exception as e:
            print(f"[SMS] Failed to send to {to_phone}: {e}")
            return False
    else:
        # Test mode — just log
        print(f"[SMS TEST MODE] To: {to_phone} | Message: {message}")
        return True
```

**Key design decisions:**
- `send_sms()` NEVER raises exceptions — it catches everything and returns True/False
- Import `twilio` inside the function so the app doesn't crash if `twilio` package isn't installed
- Test mode prints to console — useful for development
- Phone number validation is NOT our job — Twilio handles that

---

## Step 2: Add `twilio` to requirements.txt

Add this line to `requirements.txt`:

```
twilio>=8.0.0
```

---

## Step 3: Add SMS notifications to `app.py`

Import the service at the top of `app.py` (next to `import paypal_service`):

```python
import sms_service
```

Then add SMS calls in these four places:

### 3a: Job submitted → SMS to Queen

In the `submit_job()` route, AFTER the job is created and committed, add:

```python
# Notify Queen via SMS
queen = hive.queen
if queen.phone:
    sms_service.send_sms(
        queen.phone,
        f"🐝 BeehiveOfAI: New job submitted to your Hive '{hive.name}'! "
        f"Job #{job.id} is waiting to be processed."
    )
```

Find the line `flash('Your task has been submitted! 1 Nectar spent.', 'success')` and add the SMS code just BEFORE that flash.

### 3b: Job completed → SMS to Beekeeper

In the `api_complete_job()` route, AFTER the commit (after `db.session.commit()`), add:

```python
# Notify Beekeeper via SMS
beekeeper = job.beekeeper
if beekeeper.phone:
    sms_service.send_sms(
        beekeeper.phone,
        f"🍯 BeehiveOfAI: Your job #{job.id} is complete! "
        f"The Honey is ready — log in to see your results."
    )
```

### 3c: Worker joined Hive → SMS to Queen

Find the route where a Worker joins a Hive. Look for where `HiveMember` is created with `role='worker'`. After the commit, add:

```python
# Notify Queen via SMS
queen = hive.queen
if queen.phone:
    sms_service.send_sms(
        queen.phone,
        f"🐝 BeehiveOfAI: {current_user.username} joined your Hive '{hive.name}'! "
        f"You now have {hive.worker_count} Worker(s)."
    )
```

### 3d: Honey Harvest requested → SMS to user

In the `harvest()` route, after a harvest is processed (both real PayPal and test mode), add:

```python
# Notify user via SMS
if current_user.phone:
    sms_service.send_sms(
        current_user.phone,
        f"🍯 BeehiveOfAI: Your Honey Harvest of ${payout_amount:.2f} has been requested! "
        f"It will be sent to your PayPal account."
    )
```

Note: `payout_amount` is the amount being harvested — check the harvest route to find the variable name used. It's `current_user.honeycomb_balance` captured before it's reset to 0.

---

## Step 4: Add SMS status to the context processor

In the `inject_balances()` context processor, add `sms_enabled`:

```python
'sms_enabled': sms_service.is_configured(),
```

This lets templates show/hide SMS-related notices if needed.

---

## Step 5: Show SMS notification status on dashboard

On the dashboard page, add a small info card showing whether SMS notifications are active. This helps users know if they should add a phone number.

In `templates/dashboard.html`, add somewhere appropriate (maybe after the main stats):

```html
{% if not current_user.phone %}
<div class="alert alert-info" style="font-size:0.85rem">
  📱 <strong>Want SMS notifications?</strong>
  <a href="{{ url_for('profile', user_id=current_user.id) }}">Add your phone number</a>
  to get notified when jobs arrive, complete, or payouts are processed.
</div>
{% endif %}
```

---

## Step 6: Update seed_data.py

Update the seed users to have phone numbers for testing:

```python
# Add phone numbers to test users (use your real number for testing, or leave as example)
worker1.phone = '+972501234567'   # Example Israeli number
queen1.phone = '+972509876543'    # Example Israeli number
# company1 has no phone — tests the "no phone" path
```

---

## Step 7: Verify and test

After all changes, run:
```
python -m py_compile app.py sms_service.py
```

Then delete and reseed the DB:
```
del instance\beehive.db
python seed_data.py
python run_production.py
```

**Test without Twilio credentials** (test mode):
1. Login as company1, submit a job to a Hive
2. Check the server console — you should see: `[SMS TEST MODE] To: +972509876543 | Message: 🐝 BeehiveOfAI: New job submitted...`
3. The SMS is logged but not actually sent — this is correct for test mode

**Test with Twilio credentials** (after signing up for Twilio trial):
```
set TWILIO_ACCOUNT_SID=your_sid_here
set TWILIO_AUTH_TOKEN=your_token_here
set TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
```
Then the same test will send real SMS to the verified trial numbers.

---

## Summary of All Changes

| File | Change |
|------|--------|
| `sms_service.py` | NEW — Twilio SMS wrapper (two-mode: real or console log) |
| `requirements.txt` | Add `twilio>=8.0.0` |
| `app.py` | Import sms_service, add 4 SMS notification calls, update context processor |
| `templates/dashboard.html` | Add "Want SMS notifications?" info card |
| `seed_data.py` | Add phone numbers to test users |

## Important Notes

1. **Never crash on SMS failure** — `send_sms()` catches all exceptions. A failed SMS must never block a job submission or completion.
2. **Don't modify any payment or ratings code** — This phase is SMS only.
3. **Phone format:** Twilio requires E.164 format (+country_code + number, e.g. `+972501234567`). We don't validate this — Twilio will reject bad numbers gracefully.
4. **The `twilio` package import is inside `send_sms()`** — so if a deployer doesn't install twilio and doesn't set env vars, the app still works fine (test mode logs to console).
5. **Harvest threshold** is still set to $10.00 for testing (line 33 in app.py). Don't change it in this phase.
