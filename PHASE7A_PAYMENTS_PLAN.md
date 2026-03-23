# Phase 7A: Payments — Nectar Credits & Honey Harvest

## Prompt for Sonnet 4.6 (the coder)

> Nir: Copy-paste this ENTIRE file to Sonnet 4.6 and ask it to implement everything below.

---

## Context

You are working on **BeehiveOfAI**, a Flask web application that is a distributed AI marketplace. The project uses Flask, SQLAlchemy, SQLite, Flask-Login, Flask-WTF, and Jinja2 templates. It is currently live at beehiveofai.com.

**The problem we're solving:** PayPal charges ~2.9% + $0.30 per transaction. If a customer pays $1 per question, we lose 33% to fees. If we pay a Worker $0.50 per answer, the PayPal fee eats it alive. Solution: customers buy credits in bulk (low fee %), workers accumulate earnings and get paid in batches (low fee %).

**This is Layer 1 ONLY** — the internal credits engine. No PayPal integration yet (that's Layer 2, a separate task). Layer 1 tracks everything in the database. For testing, we add a "free test Nectars" button so the Beekeeper can try the system without real money.

---

## What to Build

### 1. New Database Models (in `models.py`)

Add these two new models AFTER the existing Rating model:

```python
class NectarTransaction(db.Model):
    """Log of Nectar credit movements — purchases, spending, refunds."""
    __tablename__ = 'nectar_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # positive = credit, negative = debit
    balance_after = db.Column(db.Integer, nullable=False)  # balance after this transaction
    transaction_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'spend', 'refund', 'bonus'
    description = db.Column(db.String(200), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)  # linked job, if any
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='nectar_transactions')


class EarningsTransaction(db.Model):
    """Log of earnings for Queens and Workers — earned from jobs, or harvested (paid out)."""
    __tablename__ = 'earnings_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # positive = earned, negative = harvested
    balance_after = db.Column(db.Float, nullable=False)  # honeycomb balance after this transaction
    transaction_type = db.Column(db.String(20), nullable=False)  # 'earned', 'harvested'
    description = db.Column(db.String(200), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='earnings_transactions')
```

### 2. Add Columns to Existing User Model (in `models.py`)

Add these two new columns to the `User` model, after `total_earnings`:

```python
    nectar_balance = db.Column(db.Integer, default=0)  # Beekeeper's question credits
    honeycomb_balance = db.Column(db.Float, default=0.0)  # Queen/Worker's accumulated earnings (available to harvest)
```

**Keep `total_earnings` as-is** — it stays as a lifetime total. The new `honeycomb_balance` is the AVAILABLE balance (earnings minus harvests).

### 3. Add Constants at Top of `app.py`

Add these right after the imports, before the Flask app creation:

```python
# ── Nectar Credit Packages ────────────────────────────────────────────────────
NECTAR_PACKAGES = {
    'honey_drop': {'name': 'Honey Drop', 'nectars': 20, 'price': 18.00, 'discount': '10%', 'emoji': '💧'},
    'honey_jar':  {'name': 'Honey Jar',  'nectars': 50, 'price': 40.00, 'discount': '20%', 'emoji': '🍯'},
    'honey_pot':  {'name': 'Honey Pot',  'nectars': 100, 'price': 75.00, 'discount': '25%', 'emoji': '🏺'},
}

# Revenue split percentages
PLATFORM_FEE_PERCENT = 5    # 5% to the Hub (BeehiveOfAI platform)
QUEEN_SHARE_PERCENT = 30    # 30% of remainder to Queen Bee
WORKER_SHARE_PERCENT = 70   # 70% of remainder to Worker Bees

# Base dollar value per Nectar (for revenue split calculations)
NECTAR_BASE_VALUE = 0.75  # dollars — based on Honey Pot rate

# Harvest (payout) threshold
HARVEST_THRESHOLD = 50.00  # minimum Honeycomb Balance to request a payout
```

### 4. New Routes in `app.py`

#### 4a. Buy Nectars Page (Beekeeper only)

```
GET /buy-nectars → show the 3 packages as cards
POST /buy-nectars → for Layer 1: "test purchase" that adds Nectars for free (simulating PayPal)
```

Route handler:
- GET: render `buy_nectars.html` with NECTAR_PACKAGES and current balance
- POST: receive `package_id` (honey_drop/honey_jar/honey_pot) from form
  - Look up the package in NECTAR_PACKAGES
  - Add nectars to `current_user.nectar_balance`
  - Create a NectarTransaction record (type='purchase', amount=+nectars)
  - Flash success message: "You purchased a {name}! {nectars} Nectars added to your balance."
  - Redirect to dashboard

**Important:** Since this is Layer 1 (no PayPal yet), the purchase is FREE — it's a test/demo mode. Add a flash message noting this: "TEST MODE: No real payment charged. PayPal integration coming soon!"

#### 4b. My Balance Page (all authenticated users)

```
GET /my-balance → show balance info + transaction history
```

Route handler:
- For **Beekeepers**: show `nectar_balance` + recent NectarTransactions
- For **Queens/Workers**: show `honeycomb_balance` + `total_earnings` (lifetime) + recent EarningsTransactions
- For **Queens/Workers**: if `honeycomb_balance >= HARVEST_THRESHOLD`, show a "Request Honey Harvest" button
- Show last 20 transactions in a table

#### 4c. Request Honey Harvest (Queen/Worker only)

```
POST /harvest → request a payout
```

Route handler:
- Check `current_user.honeycomb_balance >= HARVEST_THRESHOLD`
- If yes:
  - Create EarningsTransaction (type='harvested', amount=-honeycomb_balance)
  - Set `current_user.honeycomb_balance = 0.0`
  - Flash: "Honey Harvest requested! ${amount} will be sent to your PayPal. (TEST MODE: No real payout yet)"
- If no:
  - Flash warning: "You need at least ${HARVEST_THRESHOLD} in your Honeycomb Balance to harvest."
- Redirect to `/my-balance`

### 5. Modify Existing Job Submission (in `app.py`)

**File:** `app.py`, the `submit_job()` function (around line 261)

Currently it just creates a Job. Add Nectar deduction:

```python
@app.route('/hive/<int:hive_id>/submit', methods=['GET', 'POST'])
@login_required
@role_required('beekeeper')
def submit_job(hive_id):
    hive = db.session.get(Hive, hive_id) or abort(404)
    form = SubmitJobForm()
    if form.validate_on_submit():
        # Check Nectar balance
        if current_user.nectar_balance < 1:
            flash('You need at least 1 Nectar to submit a job. Please buy a Nectar package first!', 'warning')
            return redirect(url_for('buy_nectars'))

        job = Job(
            hive_id=hive_id,
            beekeeper_id=current_user.id,
            nectar=form.nectar.data,
            price=hive.price_per_job,
            status='pending',
        )
        db.session.add(job)

        # Deduct 1 Nectar
        current_user.nectar_balance -= 1
        nectar_tx = NectarTransaction(
            user_id=current_user.id,
            amount=-1,
            balance_after=current_user.nectar_balance,
            transaction_type='spend',
            description=f'Submitted job to {hive.name}',
            job_id=None  # will be set after flush
        )
        db.session.add(nectar_tx)

        current_user.total_jobs += 1
        db.session.flush()  # get job.id
        nectar_tx.job_id = job.id
        db.session.commit()
        flash('Your task has been submitted! 1 Nectar spent.', 'success')
        return redirect(url_for('job_status', job_id=job.id))
    return render_template('submit_job.html', hive=hive, form=form)
```

### 6. Modify Job Completion API (in `app.py`)

**File:** `app.py`, the `api_complete_job()` function (around line 546)

When a job is completed, automatically split the revenue:

```python
@app.route('/api/job/<int:job_id>/complete', methods=['POST'])
@csrf.exempt
@api_auth_required
def api_complete_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if request.api_user.id != job.hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    data = request.get_json() or {}
    honey = data.get('honey', '')
    if not honey:
        return jsonify({"error": "No honey provided"}), 400

    job.honey = honey
    job.status = 'completed'
    job.completed_at = datetime.now(timezone.utc)
    job.hive.total_jobs_completed += 1

    # ── Revenue split ──────────────────────────────────────────────
    total_value = NECTAR_BASE_VALUE  # $0.75 per Nectar
    platform_cut = total_value * (PLATFORM_FEE_PERCENT / 100)  # 5%
    remainder = total_value - platform_cut
    queen_cut = remainder * (QUEEN_SHARE_PERCENT / 100)  # 30% of remainder
    worker_pool = remainder * (WORKER_SHARE_PERCENT / 100)  # 70% of remainder

    # Credit Queen Bee
    queen = job.hive.queen
    queen.honeycomb_balance += queen_cut
    queen.total_earnings += queen_cut
    db.session.add(EarningsTransaction(
        user_id=queen.id,
        amount=queen_cut,
        balance_after=queen.honeycomb_balance,
        transaction_type='earned',
        description=f'Queen share for job #{job.id} in {job.hive.name}',
        job_id=job.id,
    ))

    # Credit Worker Bees (split equally among workers who completed subtasks)
    completed_subtasks = [st for st in job.subtasks if st.status == 'completed' and st.worker_id]
    worker_ids = list(set(st.worker_id for st in completed_subtasks))
    if worker_ids:
        per_worker = worker_pool / len(worker_ids)
        for worker_id in worker_ids:
            worker = db.session.get(User, worker_id)
            worker.honeycomb_balance += per_worker
            worker.total_earnings += per_worker
            db.session.add(EarningsTransaction(
                user_id=worker_id,
                amount=per_worker,
                balance_after=worker.honeycomb_balance,
                transaction_type='earned',
                description=f'Worker share for job #{job.id} in {job.hive.name}',
                job_id=job.id,
            ))

    db.session.commit()
    return jsonify({
        "status": "completed",
        "job_id": job.id,
        "revenue_split": {
            "platform": round(platform_cut, 4),
            "queen": round(queen_cut, 4),
            "worker_pool": round(worker_pool, 4),
            "workers_count": len(worker_ids),
        }
    })
```

### 7. Modify Dashboard (in `app.py`)

**File:** `app.py`, the `dashboard()` function (around line 136)

Add `nectar_balance` to the template context for Beekeepers, and `honeycomb_balance` for Queens/Workers. The dashboard route currently passes a `data` dict — add the new fields to it.

For Beekeepers, add: `data['nectar_balance'] = current_user.nectar_balance`

### 8. New Template: `buy_nectars.html`

Create `templates/buy_nectars.html`. Show 3 package cards in a row (grid-3):

Each card should show:
- Package emoji + name (e.g., "💧 Honey Drop")
- Number of Nectars (e.g., "20 Nectars")
- Price (e.g., "$18.00")
- Discount badge (e.g., "10% off")
- Price per Nectar (e.g., "$0.90/Nectar")
- A "Buy" button (form POST to `/buy-nectars` with hidden field `package_id`)

At the top, show current balance: "Your Nectar Balance: {X} 🍯"

Add a notice: "TEST MODE: Purchases are free during beta. PayPal integration coming soon!"

Style it consistently with the existing site (use the same CSS classes: card, btn-gold, grid-3, stat-box, badge, etc.)

### 9. New Template: `my_balance.html`

Create `templates/my_balance.html`.

**For Beekeepers:**
- Show Nectar Balance (big number) + "Buy More Nectars" button
- Transaction history table: Date | Type | Amount | Balance After | Description

**For Queens/Workers:**
- Show Honeycomb Balance (big number, in $)
- Show Total Lifetime Earnings (smaller)
- If balance >= $50: show "🍯 Request Honey Harvest" button
- If balance < $50: show progress bar toward $50 threshold
- Transaction history table: Date | Type | Amount | Balance After | Description

### 10. Modify Template: `dashboard.html`

**For Beekeepers** (the section starting at `{% elif current_user.role == 'beekeeper' %}`):
- Add a stat box showing Nectar Balance between the existing stat boxes
- Change the stat boxes from grid-2 to grid-3:
  - "Recent Jobs" (existing)
  - "Nectar Balance" (NEW — show current_user.nectar_balance with a 🍯 icon)
  - "Total Spent" (existing)
- Below the stats, add a link: "Buy more Nectars →" pointing to `/buy-nectars`

**For Workers:**
- Change "Total Earnings" stat to show `honeycomb_balance` (available to harvest) instead of `total_earnings`
- Add label "Honeycomb Balance" instead of "Total Earnings"
- Add small link: "View balance details →" pointing to `/my-balance`

**For Queens:**
- Same as Workers: show honeycomb_balance + link to `/my-balance`

### 11. Modify Template: `submit_job.html`

Add a Nectar balance notice before the form:
- Show current balance: "Your Nectar Balance: {X}"
- If balance == 0: show warning "You have no Nectars! Buy a package to submit jobs." with link to `/buy-nectars`
- If balance > 0: show info "This job will cost 1 Nectar. Balance after: {X-1}"

### 12. Modify Template: `base.html` (Navigation)

In the nav bar, after "Dashboard" and before the username link, add a new link:
- For Beekeepers: "🍯 {nectar_balance} Nectars" → links to `/buy-nectars`
- For Queens/Workers: "💰 ${honeycomb_balance}" → links to `/my-balance`

To make `nectar_balance` and `honeycomb_balance` available in ALL templates (not just routes that pass them), add a **context processor** in `app.py`:

```python
@app.context_processor
def inject_balances():
    if current_user.is_authenticated:
        return {
            'user_nectar_balance': current_user.nectar_balance,
            'user_honeycomb_balance': current_user.honeycomb_balance,
        }
    return {}
```

### 13. Update `seed_data.py`

Give test users some starting balances:
- `company1` (Beekeeper): `nectar_balance = 50` (so they can test submitting jobs)
- `queen1` (Queen): `honeycomb_balance = 35.00, total_earnings = 112.50`
- `worker1` (Worker): `honeycomb_balance = 18.60, total_earnings = 18.60`

Add some sample NectarTransactions for company1:
- A purchase: +50 Nectars, type='purchase', description='Purchased Honey Jar (test)'
- A spend: -1 Nectar for each existing job (2 jobs exist, so 2 spend records)

Add some sample EarningsTransactions for queen1 and worker1:
- Earnings from the 2 existing completed jobs

### 14. Update `models.py` Import

Make sure the `NectarTransaction` and `EarningsTransaction` models are importable. Update the import in `app.py`:

```python
from models import db, User, Hive, HiveMember, Job, SubTask, Rating, NectarTransaction, EarningsTransaction
```

### 15. Update `about.html`

Find the line that says "No built-in payment" (or similar) and update it to reflect that the Nectar Credits system now exists. Change it to something like: "✅ Nectar Credits system — Buy question credits in packages (Honey Drop, Honey Jar, Honey Pot)"

---

## Files to Modify (Summary)

| File | Changes |
|------|---------|
| `models.py` | Add `nectar_balance` + `honeycomb_balance` to User; add NectarTransaction + EarningsTransaction models |
| `app.py` | Add constants, context processor, 3 new routes (buy-nectars, my-balance, harvest), modify submit_job + api_complete_job + dashboard |
| `forms.py` | No changes needed (buy form uses plain HTML form, not WTForms) |
| `seed_data.py` | Add starting balances + sample transactions |
| `templates/base.html` | Add balance display in navbar |
| `templates/dashboard.html` | Add Nectar/Honeycomb balance displays |
| `templates/submit_job.html` | Add Nectar balance check + info |
| `templates/buy_nectars.html` | NEW — package purchase page |
| `templates/my_balance.html` | NEW — balance + transaction history |
| `templates/about.html` | Update "no payment" line |

---

## How to Test

1. Delete the old database: delete `instance/beehive.db`
2. Run `python seed_data.py` to create fresh data with balances
3. Run `python app.py` (or `python run_production.py`)
4. Log in as `company1@test.com / test123` (Beekeeper):
   - Dashboard should show Nectar Balance: 50
   - Navbar should show "🍯 50 Nectars"
   - Go to `/buy-nectars` — should see 3 package cards
   - Click "Buy" on Honey Drop — balance should become 70
   - Go to a Hive, submit a job — balance should become 69
   - Go to `/my-balance` — should see transaction history
5. Log in as `queen1@test.com / test123` (Queen):
   - Dashboard should show Honeycomb Balance: $35.00
   - Navbar should show "💰 $35.00"
   - Go to `/my-balance` — should see "Need $15.00 more to harvest" progress bar
6. Log in as `worker1@test.com / test123` (Worker):
   - Similar to Queen but with $18.60 balance
7. Test end-to-end: submit a job as Beekeeper, process it via API (or HoneycombOfAI), complete it — verify Queen and Worker balances increase

---

## Important Notes

- **DO NOT touch Job.nectar or Job.honey columns** — those are the task input/output, not payment credits. The naming overlap is intentional (bee theme). Context makes it clear.
- **Keep ALL existing functionality working** — don't break login, registration, hive browsing, job submission, ratings, API endpoints, or anything else.
- **Style consistency** — use the same CSS variables and classes as the existing templates (var(--gold), var(--brown), .card, .btn-gold, .stat-box, .grid-3, etc.)
- **This is Layer 1 only** — no PayPal SDK, no real money, no external API calls. Everything is internal database operations.
- **Delete instance/beehive.db before testing** — the schema changes require a fresh database.
