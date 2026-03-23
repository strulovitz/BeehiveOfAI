"""
models.py — Database Models for BeehiveOfAI
=============================================
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """A registered user — can be a Worker Bee, Queen Bee, or Beekeeper."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'worker', 'queen', 'beekeeper'
    trust_score = db.Column(db.Float, default=5.0)  # 0.0 to 10.0
    total_jobs = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    nectar_balance = db.Column(db.Integer, default=0)        # Beekeeper's question credits
    honeycomb_balance = db.Column(db.Float, default=0.0)     # Queen/Worker's available earnings (pending harvest)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    managed_hives = db.relationship('Hive', backref='queen', lazy=True, foreign_keys='Hive.queen_id')
    memberships = db.relationship('HiveMember', backref='user', lazy=True)
    submitted_jobs = db.relationship('Job', backref='beekeeper', lazy=True, foreign_keys='Job.beekeeper_id')
    ratings_given = db.relationship('Rating', backref='rater', lazy=True, foreign_keys='Rating.rater_id')
    ratings_received = db.relationship('Rating', backref='rated_user', lazy=True, foreign_keys='Rating.rated_user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_role(self):
        roles = {'worker': '🐝 Worker Bee', 'queen': '👑 Queen Bee', 'beekeeper': '🏢 Beekeeper'}
        return roles.get(self.role, self.role)


class Hive(db.Model):
    """A team of computers working together — led by a Queen Bee."""
    __tablename__ = 'hives'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    queen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_family = db.Column(db.String(50), nullable=False)  # 'deepseek', 'qwen', 'glm', 'llama', 'other'
    worker_model = db.Column(db.String(100), nullable=False)  # e.g. 'deepseek-r1:70b'
    queen_model = db.Column(db.String(100), nullable=False)   # e.g. 'deepseek-r1:671b'
    specialty = db.Column(db.String(50), nullable=False)  # 'general', 'coding', 'research', 'creative'
    price_per_job = db.Column(db.Float, default=0.50)  # in dollars
    max_workers = db.Column(db.Integer, default=20)
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'full'
    trust_score = db.Column(db.Float, default=5.0)
    total_jobs_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    members = db.relationship('HiveMember', backref='hive', lazy=True)
    jobs = db.relationship('Job', backref='hive', lazy=True)

    @property
    def worker_count(self):
        return HiveMember.query.filter_by(hive_id=self.id, role='worker', status='active').count()

    @property
    def is_full(self):
        return self.worker_count >= self.max_workers


class HiveMember(db.Model):
    """Membership of a user in a Hive."""
    __tablename__ = 'hive_members'

    id = db.Column(db.Integer, primary_key=True)
    hive_id = db.Column(db.Integer, db.ForeignKey('hives.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'queen' or 'worker'
    status = db.Column(db.String(20), default='active')
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Job(db.Model):
    """A task submitted by a Beekeeper to a Hive."""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    hive_id = db.Column(db.Integer, db.ForeignKey('hives.id'), nullable=False)
    beekeeper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nectar = db.Column(db.Text, nullable=False)  # The task/question
    honey = db.Column(db.Text, nullable=True)     # The final answer (null until complete)
    status = db.Column(db.String(20), default='pending')  # pending, splitting, processing, combining, completed, failed
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    subtasks = db.relationship('SubTask', backref='job', lazy=True)


class SubTask(db.Model):
    """One piece of a Job, assigned to a Worker Bee."""
    __tablename__ = 'subtasks'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subtask_text = db.Column(db.Text, nullable=False)
    result_text = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, assigned, processing, completed, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)


class Rating(db.Model):
    """A rating/review from one user to another after a job."""
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    score = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class NectarTransaction(db.Model):
    """Log of Nectar credit movements — purchases, spending, refunds."""
    __tablename__ = 'nectar_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)           # positive = credit, negative = debit
    balance_after = db.Column(db.Integer, nullable=False)    # balance after this transaction
    transaction_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'spend', 'refund', 'bonus'
    description = db.Column(db.String(200), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='nectar_transactions')


class EarningsTransaction(db.Model):
    """Log of earnings for Queens and Workers — earned from jobs, or harvested (paid out)."""
    __tablename__ = 'earnings_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)             # positive = earned, negative = harvested
    balance_after = db.Column(db.Float, nullable=False)      # honeycomb balance after this transaction
    transaction_type = db.Column(db.String(20), nullable=False)  # 'earned', 'harvested'
    description = db.Column(db.String(200), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='earnings_transactions')


class PayPalOrder(db.Model):
    """Track PayPal checkout orders — maps PayPal order ID to our package purchase."""
    __tablename__ = 'paypal_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paypal_order_id = db.Column(db.String(100), unique=True, nullable=False)
    package_id = db.Column(db.String(20), nullable=False)   # 'honey_drop', 'honey_jar', 'honey_pot'
    amount_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='created')    # 'created', 'captured', 'cancelled', 'failed'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    captured_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='paypal_orders')
