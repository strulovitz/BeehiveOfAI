"""
app.py — Main Flask Application for BeehiveOfAI
=================================================
"""

import base64
import os
from datetime import datetime, timezone
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import paypal_service
import sms_service
from models import db, User, Hive, HiveMember, Job, SubTask, Rating, NectarTransaction, EarningsTransaction, PayPalOrder
from forms import RegisterForm, LoginForm, CreateHiveForm, SubmitJobForm, RatingForm, VerifyPhoneForm, UpdatePhoneForm

# ── Nectar Credit Packages ────────────────────────────────────────────────────
NECTAR_PACKAGES = {
    'honey_drop': {'name': 'Honey Drop', 'nectars': 20,  'price': 18.00, 'discount': '10%', 'emoji': '💧'},
    'honey_jar':  {'name': 'Honey Jar',  'nectars': 50,  'price': 40.00, 'discount': '20%', 'emoji': '🍯'},
    'honey_pot':  {'name': 'Honey Pot',  'nectars': 100, 'price': 75.00, 'discount': '25%', 'emoji': '🏺'},
}

# Revenue split percentages
PLATFORM_FEE_PERCENT = 5    # 5% to the Hub (BeehiveOfAI platform)
QUEEN_SHARE_PERCENT = 30    # 30% of remainder to Queen Bee
WORKER_SHARE_PERCENT = 70   # 70% of remainder to Worker Bees

# Base dollar value per Nectar (for revenue split calculations — based on Honey Pot rate)
NECTAR_BASE_VALUE = 0.75  # dollars

# Harvest (payout) threshold
HARVEST_THRESHOLD = 10.00  # minimum Honeycomb Balance to request a payout (lowered for testing)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('BEEHIVE_SECRET_KEY', 'dev-only-secret-key-not-for-production')
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


@app.context_processor
def inject_balances():
    """Make balance info available in all templates."""
    paypal_on = paypal_service.is_configured()
    if current_user.is_authenticated:
        return {
            'user_nectar_balance':    current_user.nectar_balance,
            'user_honeycomb_balance': current_user.honeycomb_balance,
            'paypal_enabled':         paypal_on,
        }
    return {'paypal_enabled': paypal_on}


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
        # Send verification SMS
        sms_service.send_verification(user.phone)
        flash('Account created! We sent a verification code to your phone.', 'info')
        return redirect(url_for('verify_phone', user_id=user.id))
    return render_template('register.html', form=form)


@app.route('/verify-phone/<int:user_id>', methods=['GET', 'POST'])
def verify_phone(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if user.is_verified:
        flash('Your phone is already verified!', 'info')
        return redirect(url_for('login'))

    # User has no phone number — can't verify. Send them to their profile to add one.
    if not user.phone:
        flash('You need to add a phone number to your profile before you can verify.', 'warning')
        return redirect(url_for('profile', user_id=user.id))

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
    if not current_user.is_verified:
        flash('Please verify your phone number to use the platform.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
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
    if not current_user.is_verified:
        flash('Please verify your phone number first.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
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
    if not current_user.is_verified:
        flash('Please verify your phone number first.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
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
    if not current_user.is_verified:
        flash('Please verify your phone number first.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
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
        )
        db.session.add(nectar_tx)
        current_user.total_jobs += 1
        db.session.flush()  # get job.id
        nectar_tx.job_id = job.id
        db.session.commit()
        flash('Your task has been submitted! 1 Nectar spent.', 'success')
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

    rated_subtask_ids = set()
    if current_user.role == 'queen':
        rated_subtask_ids = {r.subtask_id for r in Rating.query.filter_by(rater_id=current_user.id).all() if r.subtask_id}

    is_worker_on_job = False
    worker_rated_queen = False
    if current_user.role == 'worker':
        is_worker_on_job = any(
            st.worker_id == current_user.id and st.status == 'completed'
            for st in job.subtasks
        )
        if is_worker_on_job:
            worker_rated_queen = Rating.query.filter_by(
                rater_id=current_user.id, rated_user_id=hive.queen_id, job_id=job.id
            ).first() is not None

    return render_template('job_status.html', job=job, hive=hive,
                           status_steps=status_steps, step_index=step_index,
                           is_beekeeper=is_beekeeper, rated_job_ids=rated_job_ids,
                           rated_subtask_ids=rated_subtask_ids,
                           is_worker_on_job=is_worker_on_job,
                           worker_rated_queen=worker_rated_queen)


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


@app.route('/subtask/<int:subtask_id>/rate-worker', methods=['GET', 'POST'])
@login_required
@role_required('queen')
def rate_worker(subtask_id):
    st = db.session.get(SubTask, subtask_id) or abort(404)
    job = st.job
    hive = job.hive

    if current_user.id != hive.queen_id:
        flash('Only the Queen of this Hive can rate Workers.', 'danger')
        return redirect(url_for('dashboard'))
    if st.status != 'completed' or not st.worker_id:
        flash('This subtask is not completed.', 'warning')
        return redirect(url_for('job_status', job_id=job.id))
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
        all_worker_ratings = Rating.query.filter_by(rated_user_id=st.worker_id).all()
        total = sum(r.score for r in all_worker_ratings) + int(form.score.data)
        count = len(all_worker_ratings) + 1
        worker.trust_score = round((total / count) * 2, 1)
        db.session.commit()
        flash(f'Thank you for rating {worker.username}!', 'success')
        return redirect(url_for('job_status', job_id=job.id))

    return render_template('rate_worker.html', subtask=st, job=job, worker=worker, form=form)


@app.route('/job/<int:job_id>/rate-queen', methods=['GET', 'POST'])
@login_required
@role_required('worker')
def rate_queen(job_id):
    job = db.session.get(Job, job_id) or abort(404)
    hive = job.hive

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
        all_queen_ratings = Rating.query.filter_by(rated_user_id=hive.queen_id).all()
        total = sum(r.score for r in all_queen_ratings) + int(form.score.data)
        count = len(all_queen_ratings) + 1
        new_score = round((total / count) * 2, 1)
        queen.trust_score = new_score
        hive.trust_score = new_score
        db.session.commit()
        flash(f'Thank you for rating Queen {queen.username}!', 'success')
        return redirect(url_for('job_status', job_id=job_id))

    return render_template('rate_queen.html', job=job, queen=queen, hive=hive, form=form)


@app.route('/buy-nectars', methods=['GET', 'POST'])
@login_required
@role_required('beekeeper')
def buy_nectars():
    if request.method == 'POST':
        package_id = request.form.get('package_id')
        package = NECTAR_PACKAGES.get(package_id)
        if not package:
            flash('Invalid package selected.', 'danger')
            return redirect(url_for('buy_nectars'))

        if paypal_service.is_configured():
            # Real PayPal checkout — create order and redirect buyer to PayPal
            try:
                result = paypal_service.create_order(
                    package_name=package['name'],
                    amount_usd=package['price'],
                    return_url=url_for('paypal_success', _external=True),
                    cancel_url=url_for('paypal_cancel', _external=True),
                )
                pp_order = PayPalOrder(
                    user_id=current_user.id,
                    paypal_order_id=result['id'],
                    package_id=package_id,
                    amount_usd=package['price'],
                    status='created',
                )
                db.session.add(pp_order)
                db.session.commit()
                return redirect(result['approve_url'])
            except Exception as e:
                flash(f'PayPal error: {str(e)}. Please try again.', 'danger')
                return redirect(url_for('buy_nectars'))
        else:
            # Test mode — free Nectars, no real payment
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

    return render_template('buy_nectars.html', packages=NECTAR_PACKAGES)


@app.route('/paypal/success')
@login_required
def paypal_success():
    """PayPal redirects here after the buyer approves the payment."""
    order_id = request.args.get('token')
    if not order_id:
        flash('Invalid PayPal response.', 'danger')
        return redirect(url_for('buy_nectars'))

    pp_order = PayPalOrder.query.filter_by(
        paypal_order_id=order_id, user_id=current_user.id
    ).first()
    if not pp_order or pp_order.status != 'created':
        flash('Order not found or already processed.', 'warning')
        return redirect(url_for('buy_nectars'))

    try:
        capture = paypal_service.capture_order(order_id)
        if capture.get('status') == 'COMPLETED':
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
                flash(f"Payment successful! {package['nectars']} Nectars ({package['name']}) added to your account.", 'success')
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
        pp_order = PayPalOrder.query.filter_by(
            paypal_order_id=order_id, user_id=current_user.id
        ).first()
        if pp_order and pp_order.status == 'created':
            pp_order.status = 'cancelled'
            db.session.commit()
    flash('Payment cancelled. No charges were made.', 'info')
    return redirect(url_for('buy_nectars'))


@app.route('/my-balance')
@login_required
def my_balance():
    if current_user.role == 'beekeeper':
        transactions = (NectarTransaction.query
                        .filter_by(user_id=current_user.id)
                        .order_by(NectarTransaction.created_at.desc())
                        .limit(20).all())
        return render_template('my_balance.html', transactions=transactions,
                               harvest_threshold=HARVEST_THRESHOLD)
    else:
        transactions = (EarningsTransaction.query
                        .filter_by(user_id=current_user.id)
                        .order_by(EarningsTransaction.created_at.desc())
                        .limit(20).all())
        return render_template('my_balance.html', transactions=transactions,
                               harvest_threshold=HARVEST_THRESHOLD)


@app.route('/harvest', methods=['POST'])
@login_required
@role_required('queen', 'worker')
def harvest():
    if not current_user.is_verified:
        flash('Please verify your phone number first.', 'warning')
        return redirect(url_for('verify_phone', user_id=current_user.id))
    if current_user.honeycomb_balance < HARVEST_THRESHOLD:
        flash(f'You need at least ${HARVEST_THRESHOLD:.2f} in your Honeycomb Balance to harvest. '
              f'Current balance: ${current_user.honeycomb_balance:.2f}', 'warning')
        return redirect(url_for('my_balance'))

    amount = current_user.honeycomb_balance

    if paypal_service.is_configured():
        # Real PayPal payout
        try:
            paypal_service.send_payout(
                recipient_email=current_user.email,
                amount_usd=amount,
                note='Honey Harvest from BeehiveOfAI — Thank you for your work!',
            )
            db.session.add(EarningsTransaction(
                user_id=current_user.id,
                amount=-amount,
                balance_after=0.0,
                transaction_type='harvested',
                description=f'Honey Harvest of ${amount:.2f} sent to {current_user.email} via PayPal',
            ))
            current_user.honeycomb_balance = 0.0
            db.session.commit()
            flash(f'🍯 Honey Harvest complete! ${amount:.2f} has been sent to your PayPal ({current_user.email}).', 'success')
        except Exception as e:
            flash(f'PayPal payout error: {str(e)}. Your balance has not been changed. Please try again.', 'danger')
    else:
        # Test mode — no real payment
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


@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = db.session.get(User, user_id) or abort(404)
    ratings = Rating.query.filter_by(rated_user_id=user_id).order_by(Rating.created_at.desc()).all()
    avg_rating = (sum(r.score for r in ratings) / len(ratings)) if ratings else None
    is_own_profile = current_user.is_authenticated and current_user.id == user_id
    phone_form = UpdatePhoneForm() if is_own_profile else None
    return render_template('profile.html', user=user, ratings=ratings,
                           avg_rating=avg_rating, is_own_profile=is_own_profile,
                           phone_form=phone_form)


@app.route('/profile/<int:user_id>/update-phone', methods=['POST'])
@login_required
def update_phone(user_id):
    if current_user.id != user_id:
        abort(403)
    form = UpdatePhoneForm()
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.is_verified = False  # Must re-verify new number
        db.session.commit()
        sms_service.send_verification(current_user.phone)
        flash('Phone number saved! We sent a verification code to your phone.', 'info')
        return redirect(url_for('verify_phone', user_id=current_user.id))
    # Form validation failed — go back to profile
    flash('Invalid phone number. Please use international format, e.g. +972544752626', 'danger')
    return redirect(url_for('profile', user_id=user_id))


# ── API ────────────────────────────────────────────────────────────────────────

@app.route('/api/status')
def api_status():
    return jsonify({"name": "BeehiveOfAI", "version": "0.5.0", "status": "running"})


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
    is_queen = request.api_user.id == st.job.hive.queen_id
    is_assigned_worker = request.api_user.id == st.worker_id
    if not is_queen and not is_assigned_worker:
        return jsonify({"error": "Not authorized to submit result for this subtask"}), 403
    data = request.get_json() or {}
    st.result_text = data.get('result', '')
    st.status = 'completed'
    st.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"status": "completed", "subtask_id": st.id})


@app.route('/api/job/<int:job_id>/subtasks')
@csrf.exempt
@api_auth_required
def api_job_subtasks(job_id):
    """Get all subtasks for a job with their current status and results."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    is_queen = request.api_user.id == job.hive.queen_id
    is_member = HiveMember.query.filter_by(
        hive_id=job.hive_id, user_id=request.api_user.id, status='active'
    ).first()
    if not is_queen and not is_member:
        return jsonify({"error": "Not authorized to view this job's subtasks"}), 403
    return jsonify({"subtasks": [
        {
            "id": st.id,
            "subtask_text": st.subtask_text,
            "result_text": st.result_text,
            "status": st.status,
            "worker_id": st.worker_id,
        }
        for st in job.subtasks
    ]})


@app.route('/api/hive/<int:hive_id>/subtasks/available')
@csrf.exempt
@api_auth_required
def api_available_subtasks(hive_id):
    """Worker polls this endpoint to find pending subtasks to process."""
    hive = db.session.get(Hive, hive_id)
    if not hive:
        return jsonify({"error": "Hive not found"}), 404
    membership = HiveMember.query.filter_by(
        hive_id=hive_id, user_id=request.api_user.id, status='active'
    ).first()
    if not membership:
        return jsonify({"error": "You are not a member of this hive"}), 403
    subtasks = (SubTask.query
                .join(Job)
                .filter(Job.hive_id == hive_id, SubTask.status == 'pending')
                .order_by(SubTask.created_at.asc())
                .all())
    return jsonify({"subtasks": [
        {"id": st.id, "job_id": st.job_id, "subtask_text": st.subtask_text, "status": st.status}
        for st in subtasks
    ]})


@app.route('/api/subtask/<int:subtask_id>/claim', methods=['PUT'])
@csrf.exempt
@api_auth_required
def api_claim_subtask(subtask_id):
    """Worker claims a specific subtask to process."""
    st = db.session.get(SubTask, subtask_id)
    if not st:
        return jsonify({"error": "Subtask not found"}), 404
    membership = HiveMember.query.filter_by(
        hive_id=st.job.hive_id, user_id=request.api_user.id, status='active'
    ).first()
    if not membership:
        return jsonify({"error": "You are not a member of this hive"}), 403
    if st.status != 'pending':
        return jsonify({"error": f"Subtask already {st.status}"}), 409
    st.status = 'assigned'
    st.worker_id = request.api_user.id
    db.session.commit()
    return jsonify({"status": "claimed", "subtask_id": st.id, "subtask_text": st.subtask_text})


@app.route('/api/worker/heartbeat', methods=['POST'])
@csrf.exempt
@api_auth_required
def api_worker_heartbeat():
    """Worker sends a heartbeat to show it is online."""
    return jsonify({"status": "ok", "server_time": datetime.now(timezone.utc).isoformat()})


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

    # ── Revenue split ──────────────────────────────────────────────────────────
    total_value = NECTAR_BASE_VALUE  # $0.75 per Nectar
    platform_cut = total_value * (PLATFORM_FEE_PERCENT / 100)
    remainder = total_value - platform_cut
    queen_cut = remainder * (QUEEN_SHARE_PERCENT / 100)
    worker_pool = remainder * (WORKER_SHARE_PERCENT / 100)

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


@app.route('/api/hive/<int:hive_id>/jobs', methods=['POST'])
@csrf.exempt
@api_auth_required
def api_submit_job(hive_id):
    """API endpoint for Beekeeper to submit a job (used by HoneycombOfAI GUI)."""
    hive = db.session.get(Hive, hive_id)
    if not hive:
        return jsonify({"error": "Hive not found"}), 404
    user = request.api_user
    if user.role != 'beekeeper':
        return jsonify({"error": "Only beekeepers can submit jobs"}), 403
    data = request.get_json() or {}
    nectar = data.get('nectar', '').strip()
    if not nectar or len(nectar) < 10:
        return jsonify({"error": "Task text (nectar) is too short — minimum 10 characters"}), 400
    if user.nectar_balance < 1:
        return jsonify({"error": "Not enough Nectars. Please buy a Nectar package on the website first."}), 402
    job = Job(
        hive_id=hive_id,
        beekeeper_id=user.id,
        nectar=nectar,
        price=hive.price_per_job,
        status='pending',
    )
    db.session.add(job)
    user.nectar_balance -= 1
    nectar_tx = NectarTransaction(
        user_id=user.id,
        amount=-1,
        balance_after=user.nectar_balance,
        transaction_type='spend',
        description=f'Submitted job to {hive.name} (via API)',
    )
    db.session.add(nectar_tx)
    user.total_jobs += 1
    db.session.flush()
    nectar_tx.job_id = job.id
    db.session.commit()
    return jsonify({
        "id": job.id,
        "hive_id": hive_id,
        "status": "pending",
        "nectar_balance": user.nectar_balance,
    }), 201


@app.route('/api/job/<int:job_id>')
@csrf.exempt
@api_auth_required
def api_get_job(job_id):
    """API endpoint to get job status (used by HoneycombOfAI GUI for polling)."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    result = {
        "id": job.id,
        "hive_id": job.hive_id,
        "status": job.status,
        "nectar": job.nectar,
        "honey": job.honey or "",
        "price": job.price,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
    return jsonify(result)


# ── Startup ────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
