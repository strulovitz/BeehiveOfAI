"""
app.py — Main Flask Application for BeehiveOfAI
=================================================
"""

import base64
from datetime import datetime, timezone
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from models import db, User, Hive, HiveMember, Job, SubTask, Rating
from forms import RegisterForm, LoginForm, CreateHiveForm, SubmitJobForm, RatingForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beehive-of-ai-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beehive.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── Role decorators ────────────────────────────────────────────────────────────

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access that page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── API auth decorator ─────────────────────────────────────────────────────────

def api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            decoded = base64.b64decode(token).decode('utf-8')
            email, password = decoded.split(':', 1)
        except Exception:
            return jsonify({"error": "Invalid token format"}), 401
        user = User.query.filter_by(email=email.lower()).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401
        request.api_user = user
        return f(*args, **kwargs)
    return decorated


# ── Public routes ──────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Username already taken.')
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data.lower()).first():
            form.email.errors.append('Email already registered.')
            return render_template('register.html', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            phone=form.phone.data or None,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ── Authenticated routes ───────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    data = {}
    if current_user.role == 'worker':
        memberships = HiveMember.query.filter_by(user_id=current_user.id, status='active').all()
        hives = [m.hive for m in memberships]
        data['hives'] = hives
    elif current_user.role == 'queen':
        hives = Hive.query.filter_by(queen_id=current_user.id).all()
        data['hives'] = hives
    elif current_user.role == 'beekeeper':
        jobs = Job.query.filter_by(beekeeper_id=current_user.id).order_by(Job.created_at.desc()).limit(10).all()
        data['jobs'] = jobs
        data['total_spent'] = sum(j.price for j in Job.query.filter_by(beekeeper_id=current_user.id).all())
    return render_template('dashboard.html', data=data)


@app.route('/hives')
def hives():
    specialty = request.args.get('specialty', 'all')
    sort = request.args.get('sort', 'trust')

    query = Hive.query.filter_by(status='active')
    if specialty != 'all':
        query = query.filter_by(specialty=specialty)

    if sort == 'price_asc':
        query = query.order_by(Hive.price_per_job.asc())
    elif sort == 'price_desc':
        query = query.order_by(Hive.price_per_job.desc())
    elif sort == 'workers':
        query = query.order_by(Hive.total_jobs_completed.desc())
    else:
        query = query.order_by(Hive.trust_score.desc())

    all_hives = query.all()
    return render_template('hives.html', hives=all_hives, specialty=specialty, sort=sort)


@app.route('/hive/create', methods=['GET', 'POST'])
@login_required
@role_required('queen')
def create_hive():
    form = CreateHiveForm()
    if form.validate_on_submit():
        if Hive.query.filter_by(name=form.name.data).first():
            form.name.errors.append('A Hive with this name already exists.')
            return render_template('create_hive.html', form=form)
        hive = Hive(
            name=form.name.data,
            description=form.description.data,
            queen_id=current_user.id,
            model_family=form.model_family.data,
            worker_model=form.worker_model.data,
            queen_model=form.queen_model.data,
            specialty=form.specialty.data,
            price_per_job=form.price_per_job.data,
            max_workers=form.max_workers.data,
        )
        db.session.add(hive)
        db.session.flush()
        membership = HiveMember(hive_id=hive.id, user_id=current_user.id, role='queen')
        db.session.add(membership)
        db.session.commit()
        flash(f'Hive "{hive.name}" created successfully!', 'success')
        return redirect(url_for('hive_detail', hive_id=hive.id))
    return render_template('create_hive.html', form=form)


@app.route('/hive/<int:hive_id>')
def hive_detail(hive_id):
    hive = db.session.get(Hive, hive_id) or abort(404)
    members = HiveMember.query.filter_by(hive_id=hive_id, status='active').all()
    is_member = False
    if current_user.is_authenticated:
        user_membership = HiveMember.query.filter_by(
            hive_id=hive_id, user_id=current_user.id, status='active'
        ).first()
        is_member = user_membership is not None
    recent_jobs = Job.query.filter_by(hive_id=hive_id).order_by(Job.created_at.desc()).limit(5).all()
    return render_template('hive_detail.html', hive=hive, members=members,
                           is_member=is_member, recent_jobs=recent_jobs)


@app.route('/hive/<int:hive_id>/join', methods=['POST'])
@login_required
@role_required('worker')
def join_hive(hive_id):
    hive = db.session.get(Hive, hive_id) or abort(404)
    existing = HiveMember.query.filter_by(hive_id=hive_id, user_id=current_user.id).first()
    if existing:
        if existing.status == 'active':
            flash('You are already a member of this Hive.', 'info')
        else:
            existing.status = 'active'
            db.session.commit()
            flash(f'Welcome back to {hive.name}!', 'success')
        return redirect(url_for('hive_detail', hive_id=hive_id))
    if hive.is_full:
        flash('This Hive is full. Try another one!', 'warning')
        return redirect(url_for('hive_detail', hive_id=hive_id))
    membership = HiveMember(hive_id=hive_id, user_id=current_user.id, role='worker')
    db.session.add(membership)
    db.session.commit()
    flash(f'You have joined {hive.name}!', 'success')
    return redirect(url_for('hive_detail', hive_id=hive_id))


@app.route('/hive/<int:hive_id>/leave', methods=['POST'])
@login_required
def leave_hive(hive_id):
    membership = HiveMember.query.filter_by(
        hive_id=hive_id, user_id=current_user.id, status='active'
    ).first()
    if not membership:
        flash('You are not a member of this Hive.', 'info')
        return redirect(url_for('hive_detail', hive_id=hive_id))
    membership.status = 'inactive'
    db.session.commit()
    hive = db.session.get(Hive, hive_id)
    flash(f'You have left {hive.name}.', 'info')
    return redirect(url_for('hive_detail', hive_id=hive_id))


@app.route('/hive/<int:hive_id>/submit', methods=['GET', 'POST'])
@login_required
@role_required('beekeeper')
def submit_job(hive_id):
    hive = db.session.get(Hive, hive_id) or abort(404)
    form = SubmitJobForm()
    if form.validate_on_submit():
        job = Job(
            hive_id=hive_id,
            beekeeper_id=current_user.id,
            nectar=form.nectar.data,
            price=hive.price_per_job,
            status='pending',
        )
        db.session.add(job)
        current_user.total_jobs += 1
        db.session.commit()
        flash('Your task has been submitted! The Hive will process it shortly.', 'success')
        return redirect(url_for('job_status', job_id=job.id))
    return render_template('submit_job.html', hive=hive, form=form)


@app.route('/job/<int:job_id>')
@login_required
def job_status(job_id):
    job = db.session.get(Job, job_id) or abort(404)
    hive = job.hive
    is_beekeeper = job.beekeeper_id == current_user.id
    is_hive_member = HiveMember.query.filter_by(
        hive_id=hive.id, user_id=current_user.id, status='active'
    ).first() is not None
    if not is_beekeeper and not is_hive_member and current_user.id != hive.queen_id:
        flash('You do not have access to this job.', 'danger')
        return redirect(url_for('dashboard'))
    status_steps = ['pending', 'splitting', 'processing', 'combining', 'completed']
    try:
        step_index = status_steps.index(job.status)
    except ValueError:
        step_index = 0
    rated_job_ids = set()
    if is_beekeeper:
        rated_job_ids = {r.job_id for r in Rating.query.filter_by(rater_id=current_user.id).all()}
    return render_template('job_status.html', job=job, hive=hive,
                           status_steps=status_steps, step_index=step_index,
                           is_beekeeper=is_beekeeper, rated_job_ids=rated_job_ids)


@app.route('/job/<int:job_id>/rate', methods=['GET', 'POST'])
@login_required
@role_required('beekeeper')
def rate_job(job_id):
    job = db.session.get(Job, job_id) or abort(404)
    if job.beekeeper_id != current_user.id:
        flash('You can only rate your own jobs.', 'danger')
        return redirect(url_for('dashboard'))
    if job.status != 'completed':
        flash('You can only rate completed jobs.', 'warning')
        return redirect(url_for('job_status', job_id=job_id))
    existing = Rating.query.filter_by(rater_id=current_user.id, job_id=job_id).first()
    if existing:
        flash('You have already rated this job.', 'info')
        return redirect(url_for('job_status', job_id=job_id))
    form = RatingForm()
    hive = job.hive
    if form.validate_on_submit():
        rating = Rating(
            rater_id=current_user.id,
            rated_user_id=hive.queen_id,
            job_id=job_id,
            score=int(form.score.data),
            comment=form.comment.data or None,
        )
        db.session.add(rating)
        # Update hive trust score (running average)
        all_ratings = Rating.query.filter_by(rated_user_id=hive.queen_id).all()
        new_avg = (sum(r.score for r in all_ratings) + int(form.score.data)) / (len(all_ratings) + 1)
        hive.trust_score = round(new_avg * 2, 1)  # Scale 1-5 stars to 0-10 trust score
        db.session.commit()
        flash('Thank you for rating this Hive!', 'success')
        return redirect(url_for('job_status', job_id=job_id))
    return render_template('rate_job.html', job=job, hive=hive, form=form)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = db.session.get(User, user_id) or abort(404)
    ratings = Rating.query.filter_by(rated_user_id=user_id).order_by(Rating.created_at.desc()).all()
    avg_rating = (sum(r.score for r in ratings) / len(ratings)) if ratings else None
    is_own_profile = current_user.is_authenticated and current_user.id == user_id
    return render_template('profile.html', user=user, ratings=ratings,
                           avg_rating=avg_rating, is_own_profile=is_own_profile)


# ── API ────────────────────────────────────────────────────────────────────────

@app.route('/api/status')
def api_status():
    return jsonify({"name": "BeehiveOfAI", "version": "0.4.0", "status": "running"})


@app.route('/api/auth/login', methods=['POST'])
@csrf.exempt
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').lower()
    password = data.get('password', '')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = base64.b64encode(f"{email}:{password}".encode()).decode()
    return jsonify({"token": token, "user_id": user.id, "username": user.username, "role": user.role})


@app.route('/api/hive/<int:hive_id>/jobs/pending')
@csrf.exempt
@api_auth_required
def api_pending_jobs(hive_id):
    hive = db.session.get(Hive, hive_id)
    if not hive:
        return jsonify({"error": "Hive not found"}), 404
    if request.api_user.id != hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    jobs = Job.query.filter_by(hive_id=hive_id, status='pending').order_by(Job.created_at.asc()).all()
    return jsonify({"jobs": [
        {"id": j.id, "nectar": j.nectar, "price": j.price, "created_at": j.created_at.isoformat()}
        for j in jobs
    ]})


@app.route('/api/job/<int:job_id>/claim', methods=['POST'])
@csrf.exempt
@api_auth_required
def api_claim_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if request.api_user.id != job.hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    if job.status != 'pending':
        return jsonify({"error": f"Job is already {job.status}"}), 409
    job.status = 'splitting'
    db.session.commit()
    return jsonify({"status": "claimed", "job_id": job.id})


@app.route('/api/job/<int:job_id>/status', methods=['PUT'])
@csrf.exempt
@api_auth_required
def api_update_job_status(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if request.api_user.id != job.hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    data = request.get_json() or {}
    new_status = data.get('status')
    valid = ['splitting', 'processing', 'combining', 'failed']
    if new_status not in valid:
        return jsonify({"error": f"Invalid status. Must be one of: {valid}"}), 400
    job.status = new_status
    db.session.commit()
    return jsonify({"status": new_status, "job_id": job.id})


@app.route('/api/job/<int:job_id>/subtasks', methods=['POST'])
@csrf.exempt
@api_auth_required
def api_create_subtasks(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if request.api_user.id != job.hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    data = request.get_json() or {}
    subtask_texts = data.get('subtasks', [])
    if not subtask_texts:
        return jsonify({"error": "No subtasks provided"}), 400
    created = []
    for text in subtask_texts:
        st = SubTask(job_id=job.id, subtask_text=text, status='pending')
        db.session.add(st)
        db.session.flush()
        created.append({"id": st.id, "text": text})
    db.session.commit()
    return jsonify({"subtasks": created})


@app.route('/api/subtask/<int:subtask_id>/result', methods=['PUT'])
@csrf.exempt
@api_auth_required
def api_subtask_result(subtask_id):
    st = db.session.get(SubTask, subtask_id)
    if not st:
        return jsonify({"error": "Subtask not found"}), 404
    if request.api_user.id != st.job.hive.queen_id:
        return jsonify({"error": "Not the queen of this hive"}), 403
    data = request.get_json() or {}
    st.result_text = data.get('result', '')
    st.status = 'completed'
    st.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"status": "completed", "subtask_id": st.id})


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
    db.session.commit()
    return jsonify({"status": "completed", "job_id": job.id})


# ── Startup ────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
