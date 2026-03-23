# Phase 7C: SMS Phone Verification via Twilio Verify API — Plan for Sonnet 4.6

> **Opus 4.6 planned this. Sonnet 4.6 codes it.**
> Read this entire plan before writing any code. Follow it step by step.

---

## What This Is (And What It's NOT)

This is **phone number verification** — proving that a person registering on the platform actually owns a real phone number. This is an anti-bot, anti-sybil-attack security measure.

This is NOT SMS notifications (those were removed). The word "SMS" here means: "we send you a 6-digit code to prove you own this phone."

**Why this matters:**
- Without phone verification, a bot farm could create 500 fake worker accounts
- A sybil attacker could create 10 accounts and manipulate ratings
- Phone numbers cost real money and are tied to real identities in most countries
- This is the same flow used by Uber, Airbnb, WhatsApp, and every serious platform

---

## How Twilio Verify API Works

We are NOT using Twilio's basic Messages API. We are using the **Verify API**, which is a completely different product:

- **No phone number purchase needed** — Twilio sends from their own pre-registered numbers
- **No A2P 10DLC registration needed** — Twilio handles all carrier compliance
- **Twilio generates the code** — we don't generate or store codes ourselves
- **Twilio checks the code** — we just ask "is this code correct?" and get a yes/no answer
- **Works from any country** — including Israel
- **Cost:** $0.05 per successful verification (free for failed attempts)

### Sending a verification (two lines of code):
```python
from twilio.rest import Client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

verification = client.verify.v2.services(VERIFY_SERVICE_SID) \
    .verifications.create(to='+972544752626', channel='sms')
# verification.status == 'pending'
```

### Checking a verification (two lines of code):
```python
check = client.verify.v2.services(VERIFY_SERVICE_SID) \
    .verification_checks.create(to='+972544752626', code='847291')
# check.status == 'approved' if correct, 'pending' if wrong
```

That's it. Twilio does everything else — generating the code, sending the SMS, expiring after 10 minutes, rate limiting to 5 attempts.

### Environment variables needed:
```
TWILIO_ACCOUNT_SID       — starts with AC...
TWILIO_AUTH_TOKEN         — long random string
TWILIO_VERIFY_SERVICE_SID — starts with VA...
```

Note: there is NO `TWILIO_PHONE_NUMBER` — the Verify API doesn't need one.

---

## The User Flow (What the User Experiences)

Here is exactly what happens from the user's perspective:

1. User goes to the **Register** page
2. User fills in: username, email, password, confirm password, **phone number** (REQUIRED), role
3. User clicks "Create Account"
4. Instead of going to login, user is redirected to a **"Verify Your Phone"** page
5. The page says: "We sent a 6-digit code to +972****2626. Enter it below."
6. The page shows **6 individual digit input boxes** in a row (each box holds 1 digit)
7. User checks their phone, sees the SMS: "Your BeehiveOfAI verification code is: 847291"
8. User types the 6 digits into the boxes
9. User clicks "Verify"
10. If correct → user is redirected to Login with a success message: "Phone verified! Please log in."
11. If incorrect → error message "Invalid code. Please try again." (stays on same page)
12. There is a "Resend Code" link (with 60-second cooldown) in case the SMS didn't arrive

**After verification:**
- The user's `is_verified` field is set to `True`
- Their profile shows the green "✅ Verified" badge (this already exists in the code!)
- Unverified users can log in but see a banner telling them to verify

---

## Step 1: Create `sms_service.py`

Create a new file `sms_service.py` in the project root. This wraps the Twilio Verify API with the same two-mode pattern as PayPal: if env vars set → real Twilio, if not → test mode.

```python
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
```

**Key design decisions:**
- `send_verification()` and `check_verification()` NEVER raise exceptions
- `twilio` is imported inside the functions so the app doesn't crash if the package isn't installed
- Test mode generates a real 6-digit code and prints it to the console — perfect for development
- Test mode stores codes in a simple dictionary (no database needed for test codes)
- In production, Twilio handles code generation, storage, expiry, and rate limiting

---

## Step 2: Add `twilio` to requirements.txt

Add this line to `requirements.txt`:

```
twilio>=8.0.0
```

---

## Step 3: Update `forms.py`

### 3a: Make phone number REQUIRED in RegisterForm

Change the phone field from optional to required, and add a helpful label:

```python
phone = StringField('Phone Number (e.g. +972544752626)',
                     validators=[DataRequired(), Length(min=10, max=20)])
```

The old line was:
```python
phone = StringField('Phone Number (optional)', validators=[Optional()])
```

### 3b: Add a new VerifyPhoneForm

Add this new form class at the end of forms.py:

```python
class VerifyPhoneForm(FlaskForm):
    digit1 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit2 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit3 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit4 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit5 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit6 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    submit = SubmitField('Verify')
```

---

## Step 4: Update the registration flow in `app.py`

### 4a: Import the new form and service

At the top of app.py, update the imports:

Add `import sms_service` after `import paypal_service`.

Update the forms import line to include `VerifyPhoneForm`:
```python
from forms import RegisterForm, LoginForm, CreateHiveForm, SubmitJobForm, RatingForm, VerifyPhoneForm
```

### 4b: Modify the `register()` route

Currently, after registration the user is redirected to Login. Instead, we want to:
1. Create the user account (with `is_verified=False`)
2. Send a verification SMS to their phone
3. Redirect to the verification page

Change the end of the `register()` route from:
```python
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
```

To:
```python
        # Send verification SMS
        sms_service.send_verification(user.phone)
        flash('Account created! We sent a verification code to your phone.', 'info')
        return redirect(url_for('verify_phone', user_id=user.id))
```

### 4c: Add the `verify_phone()` route

Add this new route after the `register()` route:

```python
@app.route('/verify-phone/<int:user_id>', methods=['GET', 'POST'])
def verify_phone(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.is_verified:
        flash('Your phone is already verified!', 'info')
        return redirect(url_for('login'))

    form = VerifyPhoneForm()

    if form.validate_on_submit():
        code = (form.digit1.data + form.digit2.data + form.digit3.data +
                form.digit4.data + form.digit5.data + form.digit6.data)
        if sms_service.check_verification(user.phone, code):
            user.is_verified = True
            db.session.commit()
            flash('Phone verified! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid code. Please check your phone and try again.', 'danger')

    # Mask the phone number for display: +972****2626
    masked = user.phone[:4] + '****' + user.phone[-4:] if len(user.phone) > 8 else '****'
    return render_template('verify_phone.html', form=form, user=user, masked_phone=masked)


@app.route('/verify-phone/<int:user_id>/resend', methods=['POST'])
def resend_verification(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.is_verified:
        flash('Your phone is already verified!', 'info')
        return redirect(url_for('login'))
    sms_service.send_verification(user.phone)
    flash('A new verification code has been sent to your phone!', 'info')
    return redirect(url_for('verify_phone', user_id=user.id))
```

**Important:** These two routes do NOT require `@login_required` — the user hasn't logged in yet, they just registered. The `user_id` is passed in the URL from the registration redirect.

### 4d: Add a verification reminder for unverified users

In the `dashboard()` route, at the very beginning (after `@login_required`), add a check:

```python
    if not current_user.is_verified:
        flash('Please verify your phone number to use the platform.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
```

This means: if someone somehow logs in without being verified (e.g. seed data user, or if they bypassed verification), they get sent back to verification. They cannot use the platform until their phone is verified.

### 4e: Add verification check to sensitive routes

Add the same check to these routes — just the two-line redirect at the top of each function, after `@login_required`:

- `submit_job()` — can't submit jobs without verification
- `join_hive()` — can't join hives without verification
- `create_hive()` — can't create hives without verification
- `harvest()` — can't request payouts without verification

The pattern for each is the same two lines:
```python
    if not current_user.is_verified:
        flash('Please verify your phone number first.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
```

Add these two lines AFTER the `@login_required` / `@role_required(...)` decorators run, meaning at the very start of the function body.

Do NOT add this check to: `profile()`, `login()`, `logout()`, `my_balance()`, `hives()`, `hive_detail()`. These are safe for unverified users to view.

---

## Step 5: Create the verification template

Create `templates/verify_phone.html`:

```html
{% extends "base.html" %}
{% block title %}Verify Your Phone — Beehive Of AI{% endblock %}

{% block content %}
<div style="max-width:480px;margin:2rem auto">
  <div class="card">
    <div class="text-center mb-2">
      <div style="font-size:2.5rem">📱</div>
      <h2 style="margin-bottom:0.25rem">Verify Your Phone</h2>
      <p class="text-muted">We sent a 6-digit code to <strong>{{ masked_phone }}</strong></p>
    </div>

    <form method="POST" action="{{ url_for('verify_phone', user_id=user.id) }}">
      {{ form.hidden_tag() }}

      <div style="display:flex;justify-content:center;gap:0.5rem;margin:1.5rem 0">
        {{ form.digit1(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]", autocomplete="one-time-code") }}
        {{ form.digit2(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]") }}
        {{ form.digit3(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]") }}
        {{ form.digit4(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]") }}
        {{ form.digit5(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]") }}
        {{ form.digit6(class="form-control", style="width:3rem;height:3.5rem;text-align:center;font-size:1.5rem;font-weight:700", maxlength="1", inputmode="numeric", pattern="[0-9]") }}
      </div>

      {% for field in [form.digit1, form.digit2, form.digit3, form.digit4, form.digit5, form.digit6] %}
        {% for error in field.errors %}
          <div class="field-error text-center">{{ error }}</div>
        {% endfor %}
      {% endfor %}

      <div class="mt-2">
        {{ form.submit(class="btn btn-gold btn-lg", style="width:100%") }}
      </div>
    </form>

    <div class="text-center mt-2">
      <p class="text-muted" style="font-size:0.85rem">Didn't receive the code?</p>
      <form method="POST" action="{{ url_for('resend_verification', user_id=user.id) }}" style="display:inline">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <button type="submit" class="btn btn-outline btn-sm">Resend Code</button>
      </form>
    </div>
  </div>
</div>

<script>
// Auto-advance: when user types a digit, focus moves to the next box
document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('input[maxlength="1"]');
  inputs.forEach(function(input, index) {
    input.addEventListener('input', function() {
      if (this.value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });
    // Allow backspace to go to previous box
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace' && this.value === '' && index > 0) {
        inputs[index - 1].focus();
      }
    });
  });
  // Auto-focus first box
  if (inputs.length > 0) inputs[0].focus();
});
</script>
{% endblock %}
```

**Key UX features:**
- 6 individual boxes, large font, centered
- Auto-advance: typing a digit automatically moves focus to the next box
- Backspace goes back to the previous box
- First box auto-focuses on page load
- `inputmode="numeric"` shows the number keyboard on mobile phones
- Masked phone number shown (e.g. `+972****2626`) so user knows where to look
- Resend button below the form

---

## Step 6: Update the registration template

In `templates/register.html`, update the phone field section to make it clear this is required and explain why:

Change the phone form-group from:
```html
      <div class="form-group">
        {{ form.phone.label }}
        {{ form.phone(class="form-control", placeholder="+1 555 000 0000") }}
        {% for error in form.phone.errors %}
          <div class="field-error">{{ error }}</div>
        {% endfor %}
      </div>
```

To:
```html
      <div class="form-group">
        {{ form.phone.label }}
        {{ form.phone(class="form-control", placeholder="+972544752626") }}
        <p class="text-muted mt-1" style="font-size:0.8rem">
          Required for verification. Use international format with country code (e.g. +972 for Israel, +1 for US).
          We'll send a one-time code to verify you're a real person.
        </p>
        {% for error in form.phone.errors %}
          <div class="field-error">{{ error }}</div>
        {% endfor %}
      </div>
```

---

## Step 7: Update seed_data.py

The seed data users need phone numbers and verification status for testing:

```python
worker1.phone = '+972501234567'
# worker1 already has is_verified=True in seed data — this is correct

queen1.phone = '+972509876543'
# queen1 already has is_verified=True in seed data — this is correct

# company1 keeps is_verified=False and no phone — tests the "unverified" path
```

Add the phone number lines AFTER the `set_password()` calls for worker1 and queen1, same as before.

---

## Step 8: Verify and test

After all changes, run:
```
python -m py_compile app.py sms_service.py forms.py
```

Then delete and reseed the DB:
```
del instance\beehive.db
pip install twilio>=8.0.0
python seed_data.py
```

### Test WITHOUT Twilio (test mode):

Start the server WITHOUT Twilio env vars:
```
python run_production.py
```

1. Go to the Register page
2. Fill in a new user — use phone number `+972544752626`
3. Click Create Account
4. You'll be redirected to the Verify Phone page
5. Look at the **Command Prompt window** — you'll see: `[SMS VERIFY TEST MODE] Code for +972544752626: 847291`
6. Type that code into the 6 boxes on screen
7. Click Verify → should redirect to Login with "Phone verified!"
8. Log in → should work normally

Also test: log in as company1@test.com (unverified) → should be redirected to verification page when trying to access dashboard.

### Test WITH Twilio (real SMS to Nir's phone):

Start the server WITH Twilio env vars:
```
set TWILIO_ACCOUNT_SID=ACxxxxxxxxxx
set TWILIO_AUTH_TOKEN=xxxxxxxxxx
set TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxx
python run_production.py
```

1. Same registration flow as above
2. This time, instead of a console message, you'll receive a **real SMS on your phone**
3. The SMS will say something like: "Your BeehiveOfAI verification code is: 847291"
4. Type the code → verified!

---

## Summary of All Changes

| File | Change |
|------|--------|
| `sms_service.py` | NEW — Twilio Verify API wrapper (two-mode: real or test) |
| `requirements.txt` | Add `twilio>=8.0.0` |
| `forms.py` | Phone field required + new `VerifyPhoneForm` |
| `app.py` | Import sms_service, modify register route, add verify_phone + resend routes, add verification checks to sensitive routes |
| `templates/verify_phone.html` | NEW — 6-digit code entry page with auto-advance |
| `templates/register.html` | Update phone field label and helper text |
| `seed_data.py` | Add phone numbers to worker1 and queen1 |

## Important Notes

1. **Never crash on SMS failure** — `send_verification()` and `check_verification()` catch all exceptions.
2. **Don't modify any payment or ratings code** — This phase is verification only.
3. **Phone format:** Twilio requires E.164 format (+country_code + number). We don't validate format — Twilio rejects bad numbers gracefully.
4. **The `twilio` package import is inside the functions** — so if a deployer doesn't install twilio and doesn't set env vars, the app still works fine (test mode).
5. **The `is_verified` field already exists** in the User model and the profile template already shows a "✅ Verified" badge — we reuse both of these, no model changes needed.
6. **Twilio Verify handles rate limiting** — max 5 attempts per phone number, 10-minute code expiry. We don't need to implement these ourselves.
7. **The verify_phone and resend_verification routes do NOT use @login_required** — the user hasn't logged in yet.
8. **CSRF protection:** The resend form includes a CSRF token. The verify form uses FlaskForm which includes it automatically via `form.hidden_tag()`.
