# Phase 7B: Ratings Improvements — Detailed Plan for Sonnet 4.6

> **Opus 4.6 planned this. Sonnet 4.6 codes it.**
> Read this entire plan before writing any code. Follow it step by step.

---

## What Exists Now

### Current Rating System (Beekeeper → Hive/Queen only)
- **Who rates:** Beekeepers only (after a job completes)
- **Who gets rated:** The Hive's Queen only (via `rated_user_id=hive.queen_id`)
- **What updates:** `hive.trust_score` (running average, scaled from 1-5 stars to 0-10 trust score)
- **Route:** `rate_job()` at `/job/<job_id>/rate` — restricted to `@role_required('beekeeper')`
- **Form:** `RatingForm` in `forms.py` — score (1-5 stars) + optional comment
- **Model:** `Rating` in `models.py` — rater_id, rated_user_id, job_id, score, comment
- **Display:** Profile page shows ratings received + average

### What's Missing
1. **Queen cannot rate Workers** — After a job completes, the Queen sees the results but has no way to rate which Workers did good/bad work
2. **Worker trust scores never change** — `user.trust_score` starts at 5.0 and never updates
3. **Workers cannot rate the Queen** — Workers who contributed to a job can't rate their Queen
4. **No way to see Worker contributions** — On the job status page, there's no list of which Workers did which subtasks

---

## What to Build

### Feature 1: Queen Rates Workers (after job completion)

**The flow:**
1. A job completes via `api_complete_job()`
2. The Queen visits the job status page (`/job/<job_id>`)
3. She sees a list of Workers who completed subtasks on this job
4. Next to each Worker, there's a "Rate Worker" button (only if not already rated)
5. She clicks it, rates 1-5 stars + optional comment
6. The Worker's `user.trust_score` updates based on the running average of all ratings they've received

**Implementation:**

#### Step 1: Update `job_status.html` — Show Worker contributions

After the Honey result section, add a "Worker Contributions" section. This section is visible to the Queen of the Hive (check `current_user.id == hive.queen_id`).

```
{% if current_user.id == hive.queen_id and job.status == 'completed' %}
<div class="card">
  <div class="card-header">🐝 Worker Contributions</div>
  {% for st in job.subtasks %}
    {% if st.status == 'completed' and st.worker_id %}
    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.75rem 1rem;border-bottom:1px solid var(--cream-d)">
      <div>
        <strong>{{ st.worker.username }}</strong>
        <span class="text-muted" style="font-size:0.82rem">
          — completed {{ st.completed_at.strftime('%b %d, %H:%M') if st.completed_at else '' }}
        </span>
        <div class="text-muted" style="font-size:0.82rem">
          Subtask: {{ st.subtask_text[:80] }}{% if st.subtask_text|length > 80 %}…{% endif %}
        </div>
      </div>
      <div>
        {% if st.id in rated_subtask_ids %}
          <span class="badge badge-green">✅ Rated</span>
        {% else %}
          <a href="{{ url_for('rate_worker', subtask_id=st.id) }}" class="btn btn-gold btn-sm">⭐ Rate</a>
        {% endif %}
      </div>
    </div>
    {% endif %}
  {% endfor %}
</div>
{% endif %}
```

**Important:** To make `st.worker` work, you need to add a relationship to the SubTask model:

In `models.py`, add to `SubTask`:
```python
worker = db.relationship('User', foreign_keys=[worker_id])
```

#### Step 2: Add `rated_subtask_ids` to the job_status route

In `app.py`, in the `job_status()` route, add (after the existing `rated_job_ids` logic):

```python
rated_subtask_ids = set()
if current_user.role == 'queen':
    rated_subtask_ids = {r.subtask_id for r in Rating.query.filter_by(rater_id=current_user.id).all() if r.subtask_id}
```

Pass `rated_subtask_ids=rated_subtask_ids` to the template.

**Wait** — the Rating model doesn't have a `subtask_id` field yet. We need to add it.

#### Step 3: Add `subtask_id` to the Rating model

In `models.py`, add to the `Rating` class:
```python
subtask_id = db.Column(db.Integer, db.ForeignKey('subtasks.id'), nullable=True)
```

This field is nullable because existing Beekeeper ratings don't relate to specific subtasks — they rate the overall job. Queen→Worker ratings DO relate to a specific subtask.

#### Step 4: Create the `rate_worker` route

In `app.py`, add a new route:

```python
@app.route('/subtask/<int:subtask_id>/rate-worker', methods=['GET', 'POST'])
@login_required
@role_required('queen')
def rate_worker(subtask_id):
    st = db.session.get(SubTask, subtask_id) or abort(404)
    job = st.job
    hive = job.hive

    # Only the Queen of this Hive can rate
    if current_user.id != hive.queen_id:
        flash('Only the Queen of this Hive can rate Workers.', 'danger')
        return redirect(url_for('dashboard'))

    # Must be a completed subtask with a worker
    if st.status != 'completed' or not st.worker_id:
        flash('This subtask is not completed.', 'warning')
        return redirect(url_for('job_status', job_id=job.id))

    # Check if already rated
    existing = Rating.query.filter_by(rater_id=current_user.id, subtask_id=subtask_id).first()
    if existing:
        flash('You have already rated this Worker for this subtask.', 'info')
        return redirect(url_for('job_status', job_id=job.id))

    form = RatingForm()
    worker = db.session.get(User, st.worker_id)

    if form.validate_on_submit():
        rating = Rating(
            rater_id=current_user.id,
            rated_user_id=st.worker_id,
            job_id=job.id,
            subtask_id=subtask_id,
            score=int(form.score.data),
            comment=form.comment.data or None,
        )
        db.session.add(rating)

        # Update worker's trust score (running average of ALL ratings they've received)
        all_worker_ratings = Rating.query.filter_by(rated_user_id=st.worker_id).all()
        total = sum(r.score for r in all_worker_ratings) + int(form.score.data)
        count = len(all_worker_ratings) + 1
        new_avg = total / count
        worker.trust_score = round(new_avg * 2, 1)  # Scale 1-5 stars to 0-10 trust score

        db.session.commit()
        flash(f'Thank you for rating {worker.username}!', 'success')
        return redirect(url_for('job_status', job_id=job.id))

    return render_template('rate_worker.html', subtask=st, job=job, worker=worker, form=form)
```

#### Step 5: Create `rate_worker.html` template

Create `templates/rate_worker.html` — similar to `rate_job.html` but for Worker rating:

```html
{% extends "base.html" %}
{% block title %}Rate Worker — Beehive Of AI{% endblock %}

{% block content %}
<div style="max-width:520px;margin:2rem auto">
  <div class="card">
    <div class="text-center mb-2">
      <div style="font-size:2.5rem">🐝</div>
      <h2 style="margin-bottom:0.25rem">Rate Worker</h2>
      <p class="text-muted">How did <strong>{{ worker.username }}</strong> perform on this subtask?</p>
    </div>

    <div style="background:var(--cream-d);border-radius:8px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.88rem">
      <strong>Subtask:</strong> {{ subtask.subtask_text[:200] }}{% if subtask.subtask_text|length > 200 %}…{% endif %}
    </div>

    {% if subtask.result_text %}
    <div style="background:#f0f9f0;border-radius:8px;padding:0.75rem 1rem;margin-bottom:1.5rem;font-size:0.88rem">
      <strong>Worker's Result:</strong> {{ subtask.result_text[:200] }}{% if subtask.result_text|length > 200 %}…{% endif %}
    </div>
    {% endif %}

    <form method="POST" action="{{ url_for('rate_worker', subtask_id=subtask.id) }}">
      {{ form.hidden_tag() }}

      <div class="form-group">
        {{ form.score.label }}
        {{ form.score(class="form-control") }}
        {% for error in form.score.errors %}
          <div class="field-error">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="form-group">
        {{ form.comment.label }}
        {{ form.comment(class="form-control", placeholder="How was the quality of this Worker's contribution?", rows=4) }}
        {% for error in form.comment.errors %}
          <div class="field-error">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="mt-2">
        {{ form.submit(class="btn btn-gold btn-lg", style="width:100%") }}
      </div>
    </form>

    <div class="text-center mt-2">
      <a href="{{ url_for('job_status', job_id=job.id) }}">← Back to Job</a>
    </div>
  </div>
</div>
{% endblock %}
```

### Feature 2: Worker Rates Queen (after job completion)

**The flow:**
1. A Worker visits a job they participated in
2. If the job is completed, they see a "Rate your Queen" button
3. They rate 1-5 stars + optional comment
4. The Queen's `user.trust_score` updates (in addition to the Hive trust score)

**Implementation:**

#### Step 6: Update `job_status` route to detect Worker participation

In `app.py`, in the `job_status()` route, add:

```python
is_worker_on_job = False
if current_user.role == 'worker':
    is_worker_on_job = any(
        st.worker_id == current_user.id and st.status == 'completed'
        for st in job.subtasks
    )
```

Also check if this Worker has already rated the Queen for this job:

```python
worker_rated_queen = False
if is_worker_on_job:
    worker_rated_queen = Rating.query.filter_by(
        rater_id=current_user.id, rated_user_id=hive.queen_id, job_id=job.id
    ).first() is not None
```

Pass both `is_worker_on_job` and `worker_rated_queen` to the template.

#### Step 7: Update `job_status.html` — Worker can rate Queen

After the honey result section (and the Beekeeper rating section), add:

```html
{% if is_worker_on_job and job.status == 'completed' %}
  {% if worker_rated_queen %}
  <div class="card text-center">
    <p>✅ You have already rated Queen {{ hive.queen.username }} for this job.</p>
  </div>
  {% else %}
  <div class="card text-center">
    <div style="font-size:1.5rem;margin-bottom:0.5rem">👑</div>
    <p class="mb-1"><strong>How was your Queen's coordination?</strong></p>
    <p class="text-muted mb-1" style="font-size:0.85rem">Your rating helps improve Hive management.</p>
    <a href="{{ url_for('rate_queen', job_id=job.id) }}" class="btn btn-gold">👑 Rate Your Queen</a>
  </div>
  {% endif %}
{% endif %}
```

#### Step 8: Create the `rate_queen` route

In `app.py`, add:

```python
@app.route('/job/<int:job_id>/rate-queen', methods=['GET', 'POST'])
@login_required
@role_required('worker')
def rate_queen(job_id):
    job = db.session.get(Job, job_id) or abort(404)
    hive = job.hive

    # Must be a Worker who completed subtasks on this job
    participated = any(
        st.worker_id == current_user.id and st.status == 'completed'
        for st in job.subtasks
    )
    if not participated:
        flash('You did not work on this job.', 'danger')
        return redirect(url_for('dashboard'))

    if job.status != 'completed':
        flash('The job is not completed yet.', 'warning')
        return redirect(url_for('job_status', job_id=job_id))

    existing = Rating.query.filter_by(
        rater_id=current_user.id, rated_user_id=hive.queen_id, job_id=job_id
    ).first()
    if existing:
        flash('You have already rated the Queen for this job.', 'info')
        return redirect(url_for('job_status', job_id=job_id))

    form = RatingForm()
    queen = hive.queen

    if form.validate_on_submit():
        rating = Rating(
            rater_id=current_user.id,
            rated_user_id=hive.queen_id,
            job_id=job_id,
            score=int(form.score.data),
            comment=form.comment.data or None,
        )
        db.session.add(rating)

        # Update Queen's personal trust score
        all_queen_ratings = Rating.query.filter_by(rated_user_id=hive.queen_id).all()
        total = sum(r.score for r in all_queen_ratings) + int(form.score.data)
        count = len(all_queen_ratings) + 1
        new_avg = total / count
        queen.trust_score = round(new_avg * 2, 1)

        # Also update Hive trust score
        hive.trust_score = queen.trust_score

        db.session.commit()
        flash(f'Thank you for rating Queen {queen.username}!', 'success')
        return redirect(url_for('job_status', job_id=job_id))

    return render_template('rate_queen.html', job=job, queen=queen, hive=hive, form=form)
```

#### Step 9: Create `rate_queen.html` template

Create `templates/rate_queen.html`:

```html
{% extends "base.html" %}
{% block title %}Rate Queen — Beehive Of AI{% endblock %}

{% block content %}
<div style="max-width:520px;margin:2rem auto">
  <div class="card">
    <div class="text-center mb-2">
      <div style="font-size:2.5rem">👑</div>
      <h2 style="margin-bottom:0.25rem">Rate Your Queen</h2>
      <p class="text-muted">How did <strong>{{ queen.username }}</strong> coordinate Job #{{ job.id }}?</p>
    </div>

    <div style="background:var(--cream-d);border-radius:8px;padding:0.75rem 1rem;margin-bottom:1.5rem;font-size:0.88rem">
      <strong>Hive:</strong> {{ hive.name }}<br>
      <strong>Task:</strong> {{ job.nectar[:120] }}{% if job.nectar|length > 120 %}…{% endif %}
    </div>

    <form method="POST" action="{{ url_for('rate_queen', job_id=job.id) }}">
      {{ form.hidden_tag() }}

      <div class="form-group">
        {{ form.score.label }}
        {{ form.score(class="form-control") }}
      </div>

      <div class="form-group">
        {{ form.comment.label }}
        {{ form.comment(class="form-control", placeholder="How was the task splitting and coordination?", rows=4) }}
      </div>

      <div class="mt-2">
        {{ form.submit(class="btn btn-gold btn-lg", style="width:100%") }}
      </div>
    </form>

    <div class="text-center mt-2">
      <a href="{{ url_for('job_status', job_id=job.id) }}">← Back to Job</a>
    </div>
  </div>
</div>
{% endblock %}
```

### Feature 3: Profile Page Improvements

#### Step 10: Show trust score with context on profile page

The profile page already shows ratings. Improve it by showing who rated them (Beekeeper, Queen, or Worker) and the trust score more prominently.

In `profile.py` route (`app.py` line ~575), when querying ratings, also pass the user's trust score:
```python
# Already passed: ratings, avg_rating, is_own_profile
# No code change needed — just template update
```

In `templates/profile.html`, update the ratings section to show the rater's role badge:

For each rating in the list, show:
```
{% if rating.rater.role == 'beekeeper' %}
  <span class="badge badge-gold">Beekeeper Review</span>
{% elif rating.rater.role == 'queen' %}
  <span class="badge badge-blue">Queen Review</span>
{% elif rating.rater.role == 'worker' %}
  <span class="badge badge-green">Worker Review</span>
{% endif %}
```

### Feature 4: Update seed_data.py

#### Step 11: Add sample ratings to seed data

In `seed_data.py`, after creating jobs, add a few sample ratings:

```python
# Beekeeper rates the Hive (existing flow)
r1 = Rating(rater_id=company1.id, rated_user_id=queen1.id, job_id=job1.id,
            score=5, comment="Excellent work! Fast and accurate.")

# Queen rates Worker (new flow)
r2 = Rating(rater_id=queen1.id, rated_user_id=worker1.id, job_id=job1.id,
            subtask_id=1,  # first subtask
            score=4, comment="Good work, completed quickly.")

# Worker rates Queen (new flow)
r3 = Rating(rater_id=worker1.id, rated_user_id=queen1.id, job_id=job1.id,
            score=5, comment="Great coordination, clear task splitting.")

db.session.add_all([r1, r2, r3])

# Update trust scores to reflect ratings
queen1.trust_score = 10.0   # 5-star avg * 2
worker1.trust_score = 8.0   # 4-star avg * 2
```

---

## Summary of All Changes

| File | Change |
|------|--------|
| `models.py` | Add `subtask_id` to Rating model, add `worker` relationship to SubTask |
| `app.py` | Add `rate_worker()` route, add `rate_queen()` route, update `job_status()` to pass new template vars |
| `forms.py` | No changes needed (RatingForm is reused) |
| `templates/job_status.html` | Add Worker Contributions section (Queen view), add Rate Queen button (Worker view) |
| `templates/rate_worker.html` | NEW — Queen rates Worker form |
| `templates/rate_queen.html` | NEW — Worker rates Queen form |
| `templates/profile.html` | Add role badges to ratings |
| `seed_data.py` | Add sample ratings |

## Important Notes

1. **Database migration:** Adding `subtask_id` to Rating requires deleting and reseeding the DB: `del instance\beehive.db && python seed_data.py`
2. **Reuse `RatingForm`** — The same form works for all three rating types (Beekeeper→Hive, Queen→Worker, Worker→Queen). No new form needed.
3. **Trust score formula:** All trust scores use the same formula: `avg_stars * 2` to convert 1-5 star scale to 0-10 trust score.
4. **Harvest threshold:** Currently set to $10.00 for testing (line 33 in app.py). Change back to $50.00 before going to production.
5. **Don't modify any payment code** — This phase is ratings only.
