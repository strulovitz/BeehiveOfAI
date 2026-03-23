"""
seed_data.py — Populate the database with sample data for testing
==================================================================
Run: python seed_data.py
"""

from app import app
from models import db, User, Hive, HiveMember, Job, SubTask, Rating, NectarTransaction, EarningsTransaction
from datetime import datetime, timezone, timedelta


def seed():
    with app.app_context():
        db.create_all()

        # ── Clear existing data ──────────────────────────────────────────────
        EarningsTransaction.query.delete()
        NectarTransaction.query.delete()
        Rating.query.delete()
        SubTask.query.delete()
        Job.query.delete()
        HiveMember.query.delete()
        Hive.query.delete()
        User.query.delete()
        db.session.commit()
        print("Cleared existing data.")

        # ── Users ────────────────────────────────────────────────────────────
        worker1 = User(
            username='worker1',
            email='worker1@test.com',
            role='worker',
            trust_score=7.5,
            total_jobs=12,
            total_earnings=18.60,
            honeycomb_balance=18.60,
            is_verified=True,
        )
        worker1.set_password('test123')
        worker1.phone = '+972501234567'

        queen1 = User(
            username='queen1',
            email='queen1@test.com',
            role='queen',
            trust_score=8.9,
            total_jobs=45,
            total_earnings=112.50,
            honeycomb_balance=35.00,
            is_verified=True,
        )
        queen1.set_password('test123')
        queen1.phone = '+972509876543'

        company1 = User(
            username='company1',
            email='company1@test.com',
            role='beekeeper',
            trust_score=6.0,
            total_jobs=8,
            total_earnings=0.0,
            nectar_balance=50,
            is_verified=False,
        )
        company1.set_password('test123')

        db.session.add_all([worker1, queen1, company1])
        db.session.flush()
        print(f"Created users: {worker1.username}, {queen1.username}, {company1.username}")

        # ── Hives ────────────────────────────────────────────────────────────
        hive1 = Hive(
            name='DeepSeek Reasoning Hive',
            description=(
                'A general-purpose reasoning Hive powered by DeepSeek-R1 models. '
                'We specialize in complex multi-step reasoning tasks, document analysis, '
                'question answering, and knowledge synthesis. Our Queen model handles '
                'task decomposition while Worker Bees run 70B parameter models locally.'
            ),
            queen_id=queen1.id,
            model_family='deepseek',
            worker_model='deepseek-r1:70b',
            queen_model='deepseek-r1:671b',
            specialty='general',
            price_per_job=0.75,
            max_workers=20,
            status='active',
            trust_score=8.5,
            total_jobs_completed=34,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        )

        hive2 = Hive(
            name='Qwen Code Hive',
            description=(
                'Specialized coding Hive using Qwen2.5-Coder models. '
                'Perfect for code generation, debugging, refactoring, code review, '
                'and technical documentation. Our Worker Bees each run Qwen2.5-Coder:32b '
                'while the Queen coordinates with the 72B instruct model for final synthesis.'
            ),
            queen_id=queen1.id,
            model_family='qwen',
            worker_model='qwen2.5-coder:32b',
            queen_model='qwen2.5:72b-instruct',
            specialty='coding',
            price_per_job=0.50,
            max_workers=15,
            status='active',
            trust_score=9.1,
            total_jobs_completed=67,
            created_at=datetime.now(timezone.utc) - timedelta(days=14),
        )

        db.session.add_all([hive1, hive2])
        db.session.flush()
        print(f"Created hives: {hive1.name}, {hive2.name}")

        # ── Memberships ──────────────────────────────────────────────────────
        queen_membership1 = HiveMember(
            hive_id=hive1.id, user_id=queen1.id, role='queen', status='active',
            joined_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        queen_membership2 = HiveMember(
            hive_id=hive2.id, user_id=queen1.id, role='queen', status='active',
            joined_at=datetime.now(timezone.utc) - timedelta(days=14),
        )
        worker_membership = HiveMember(
            hive_id=hive1.id, user_id=worker1.id, role='worker', status='active',
            joined_at=datetime.now(timezone.utc) - timedelta(days=20),
        )
        db.session.add_all([queen_membership1, queen_membership2, worker_membership])
        db.session.flush()
        print("Created memberships.")

        # ── Completed Job ────────────────────────────────────────────────────
        job1 = Job(
            hive_id=hive1.id,
            beekeeper_id=company1.id,
            nectar=(
                'Analyze the following business scenario and provide a comprehensive '
                'SWOT analysis:\n\n'
                'A mid-sized e-commerce company (500 employees, $50M annual revenue) '
                'is considering expanding into the Southeast Asian market. They currently '
                'operate only in North America and have strong brand recognition in the '
                'outdoor sports equipment niche. They have $5M available for international '
                'expansion and need to decide within 3 months.'
            ),
            honey=(
                '## SWOT Analysis: SE Asian Market Expansion\n\n'
                '### Strengths\n'
                '- Strong brand identity in outdoor/sports niche — transferable to active '
                'SE Asian demographics in Thailand, Vietnam, Indonesia\n'
                '- $5M expansion budget provides runway for market entry and initial marketing\n'
                '- Proven e-commerce operations infrastructure and logistics expertise\n'
                '- Established supplier relationships can be leveraged for regional sourcing\n\n'
                '### Weaknesses\n'
                '- No existing brand recognition in SE Asia; significant marketing investment required\n'
                '- Limited cross-cultural expertise and local market knowledge\n'
                '- 3-month timeline is aggressive for thorough due diligence\n'
                '- English-first operations will need localization for multiple languages\n\n'
                '### Opportunities\n'
                '- SE Asian e-commerce growing at ~15% annually (Statista 2024)\n'
                '- Rising middle class with increased disposable income for outdoor recreation\n'
                '- Lower market saturation compared to North America in this niche\n'
                '- Regional free trade agreements reduce import costs\n\n'
                '### Threats\n'
                '- Entrenched local competitors (Shopee, Lazada ecosystem) with deep market knowledge\n'
                '- Complex multi-jurisdiction regulatory environment (7 countries, different rules)\n'
                '- Currency and economic volatility risk in emerging markets\n'
                '- Supply chain complexity for the region\n\n'
                '### Recommendation\n'
                'Start with a focused pilot in Singapore (English-speaking, high income, familiar '
                'regulations) and Thailand (large outdoor market). Allocate $2M to this phase '
                'with clear 12-month KPIs before broader regional commitment.'
            ),
            status='completed',
            price=0.75,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
            completed_at=datetime.now(timezone.utc) - timedelta(days=4, hours=22),
        )
        db.session.add(job1)
        db.session.flush()

        # Sub-tasks for the completed job
        subtasks = [
            SubTask(
                job_id=job1.id,
                worker_id=worker1.id,
                subtask_text='Identify and analyze Strengths of expanding to SE Asian market',
                result_text='Strong brand in outdoor niche, $5M budget, proven e-commerce ops, supplier relationships.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
                completed_at=datetime.now(timezone.utc) - timedelta(days=4, hours=23, minutes=30),
            ),
            SubTask(
                job_id=job1.id,
                worker_id=worker1.id,
                subtask_text='Identify and analyze Weaknesses of expanding to SE Asian market',
                result_text='No brand recognition in region, cultural gap, aggressive 3-month timeline, localization needed.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
                completed_at=datetime.now(timezone.utc) - timedelta(days=4, hours=23, minutes=15),
            ),
            SubTask(
                job_id=job1.id,
                worker_id=None,
                subtask_text='Research Opportunities in SE Asian e-commerce and outdoor market',
                result_text='15% annual growth, rising middle class, lower saturation, trade agreements.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
                completed_at=datetime.now(timezone.utc) - timedelta(days=4, hours=23),
            ),
            SubTask(
                job_id=job1.id,
                worker_id=None,
                subtask_text='Assess Threats and competitive landscape in SE Asian market',
                result_text='Shopee/Lazada dominance, multi-jurisdiction regulations, currency risk, supply chain complexity.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
                completed_at=datetime.now(timezone.utc) - timedelta(days=4, hours=22, minutes=45),
            ),
        ]
        db.session.add_all(subtasks)

        # Update stats
        company1.total_jobs = 1
        queen1.total_earnings = 112.50
        worker1.total_jobs = 12
        hive1.total_jobs_completed = 34

        db.session.flush()  # ensure subtask IDs are available

        # Beekeeper rates the Hive/Queen (existing flow)
        rating1 = Rating(
            rater_id=company1.id,
            rated_user_id=queen1.id,
            job_id=job1.id,
            score=5,
            comment='Excellent work! The SWOT analysis was thorough and actionable. Will use this Hive again.',
            created_at=datetime.now(timezone.utc) - timedelta(days=4),
        )
        # Queen rates Worker for first subtask (new flow)
        rating2 = Rating(
            rater_id=queen1.id,
            rated_user_id=worker1.id,
            job_id=job1.id,
            subtask_id=subtasks[0].id,
            score=5,
            comment='Outstanding work on the Strengths analysis. Clear and well-structured.',
            created_at=datetime.now(timezone.utc) - timedelta(days=4),
        )
        # Worker rates Queen (new flow)
        rating3 = Rating(
            rater_id=worker1.id,
            rated_user_id=queen1.id,
            job_id=job1.id,
            score=5,
            comment='Excellent task splitting. Each subtask was clear and well-scoped.',
            created_at=datetime.now(timezone.utc) - timedelta(days=4),
        )
        db.session.add_all([rating1, rating2, rating3])

        # Update trust scores based on ratings
        queen1.trust_score = 10.0   # avg 5 stars * 2
        worker1.trust_score = 10.0  # avg 5 stars * 2

        # ── Second completed job (NOT rated — so you can test rating!) ────
        job2 = Job(
            hive_id=hive2.id,
            beekeeper_id=company1.id,
            nectar=(
                'Write a Python function that takes a list of product names and prices, '
                'and returns the top 3 most expensive products sorted by price descending. '
                'Include error handling and type hints.'
            ),
            honey=(
                '```python\n'
                'def top_expensive(products: list[tuple[str, float]], n: int = 3) -> list[tuple[str, float]]:\n'
                '    """Return the top N most expensive products sorted by price descending.\n\n'
                '    Args:\n'
                '        products: List of (name, price) tuples.\n'
                '        n: Number of top products to return (default 3).\n\n'
                '    Returns:\n'
                '        Sorted list of (name, price) tuples, most expensive first.\n\n'
                '    Raises:\n'
                '        ValueError: If products list is empty or n < 1.\n'
                '    """\n'
                '    if not products:\n'
                '        raise ValueError("Products list cannot be empty")\n'
                '    if n < 1:\n'
                '        raise ValueError("n must be at least 1")\n'
                '    return sorted(products, key=lambda p: p[1], reverse=True)[:n]\n'
                '```\n\n'
                'Usage example:\n'
                '```python\n'
                'items = [("Laptop", 999.99), ("Mouse", 29.99), ("Monitor", 449.00), '
                '("Keyboard", 79.99), ("Headset", 149.99)]\n'
                'print(top_expensive(items))  \n'
                '# [("Laptop", 999.99), ("Monitor", 449.00), ("Headset", 149.99)]\n'
                '```'
            ),
            status='completed',
            price=0.50,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=23),
        )
        db.session.add(job2)
        db.session.flush()

        subtasks2 = [
            SubTask(
                job_id=job2.id,
                worker_id=worker1.id,
                subtask_text='Write the core sorting function with type hints',
                result_text='Created top_expensive() using sorted() with lambda key on price, returns sliced list.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
                completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=23, minutes=45),
            ),
            SubTask(
                job_id=job2.id,
                worker_id=None,
                subtask_text='Add error handling and docstring',
                result_text='Added ValueError for empty list and n<1, comprehensive docstring with Args/Returns/Raises.',
                status='completed',
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
                completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=23, minutes=30),
            ),
        ]
        db.session.add_all(subtasks2)
        company1.total_jobs = 2
        hive2.total_jobs_completed = 68
        print("Created second completed job (unrated — ready for you to test rating!).")

        # ── Nectar Transactions for company1 (Beekeeper) ─────────────────────
        nectar_purchase = NectarTransaction(
            user_id=company1.id,
            amount=50,
            balance_after=50,
            transaction_type='purchase',
            description='Purchased Honey Jar (50 Nectars) — TEST MODE',
            created_at=datetime.now(timezone.utc) - timedelta(days=6),
        )
        nectar_spend1 = NectarTransaction(
            user_id=company1.id,
            amount=-1,
            balance_after=49,
            transaction_type='spend',
            description=f'Submitted job to {hive1.name}',
            job_id=job1.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        )
        nectar_spend2 = NectarTransaction(
            user_id=company1.id,
            amount=-1,
            balance_after=48,
            transaction_type='spend',
            description=f'Submitted job to {hive2.name}',
            job_id=job2.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db.session.add_all([nectar_purchase, nectar_spend1, nectar_spend2])
        # Fix company1's actual balance (50 purchased - 2 spent = 48, but we seeded 50 for demo friendliness)

        # ── Earnings Transactions for queen1 ──────────────────────────────────
        # Queen share: 30% of 95% of $0.75 = ~$0.2138 per job
        queen_earn1 = EarningsTransaction(
            user_id=queen1.id,
            amount=0.2138,
            balance_after=0.2138,
            transaction_type='earned',
            description=f'Queen share for job #{job1.id} in {hive1.name}',
            job_id=job1.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=4, hours=22),
        )
        queen_earn2 = EarningsTransaction(
            user_id=queen1.id,
            amount=0.2138,
            balance_after=0.4275,
            transaction_type='earned',
            description=f'Queen share for job #{job2.id} in {hive2.name}',
            job_id=job2.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=1, hours=23),
        )
        db.session.add_all([queen_earn1, queen_earn2])

        # ── Earnings Transactions for worker1 ─────────────────────────────────
        # Worker share: 70% of 95% of $0.75 = ~$0.4988 per job (1 worker on each job)
        worker_earn1 = EarningsTransaction(
            user_id=worker1.id,
            amount=0.4988,
            balance_after=0.4988,
            transaction_type='earned',
            description=f'Worker share for job #{job1.id} in {hive1.name}',
            job_id=job1.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=4, hours=22),
        )
        worker_earn2 = EarningsTransaction(
            user_id=worker1.id,
            amount=0.4988,
            balance_after=0.9975,
            transaction_type='earned',
            description=f'Worker share for job #{job2.id} in {hive2.name}',
            job_id=job2.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=1, hours=23),
        )
        db.session.add_all([worker_earn1, worker_earn2])

        db.session.commit()
        print("Created sample jobs with subtasks and ratings.")
        print("\nSeed data created successfully!")
        print("\nTest accounts:")
        print("  Worker:     worker1@test.com    / test123")
        print("  Queen:      queen1@test.com     / test123")
        print("  Beekeeper:  company1@test.com   / test123")


if __name__ == '__main__':
    seed()
