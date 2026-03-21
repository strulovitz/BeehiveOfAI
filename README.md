# 🐝 Beehive Of AI

**Personal Computers Working Together as One Powerful AI**

---

## Quick Start

```bash
pip install -r requirements.txt
python seed_data.py    # creates database with sample data
python app.py          # starts the website
```

Open http://localhost:5000 in your browser.

**Test accounts (password: `test123` for all):**

| Role | Email |
|------|-------|
| 🐝 Worker Bee | worker1@test.com |
| 👑 Queen Bee | queen1@test.com |
| 🏢 Beekeeper | company1@test.com |

---

## What Is This?

Beehive Of AI is a distributed AI processing platform where:

- **Worker Bees** earn money by sharing their computer's idle GPU/CPU power
- **Queen Bees** manage teams and coordinate AI task decomposition
- **Beekeepers** (companies) submit AI tasks and receive results

Think of it like Airbnb — but instead of renting a spare room, you rent your computer's idle AI processing power.

---

## The Beehive Metaphor

| Term | What It Means |
|------|--------------|
| **Queen Bee** | Team manager whose computer splits big AI tasks into sub-tasks and combines results |
| **Worker Bee** | Home computer owner who processes individual AI sub-tasks locally |
| **Hive** | A team of computers (one Queen + many Workers) working together |
| **Honey** | The final answer delivered to the client — the polished combined result |
| **Nectar** | The initial task submitted by the client — the raw input |
| **Beekeeper** | The company or individual who pays for AI work to be done |

---

## How It Works

1. A **Beekeeper** submits **Nectar** (a task) to a **Hive**
2. The **Queen Bee** AI splits the Nectar into parallel **Sub-tasks**
3. Each **Worker Bee** processes their Sub-task using a local Ollama model
4. The **Queen Bee** AI combines all results into **Honey**
5. The **Honey** is delivered back to the **Beekeeper**

---

## Why Not Petals / EXO?

Existing distributed AI projects split *model layers* across machines — meaning if any single machine goes offline, the entire task fails. Beehive Of AI splits the *work* instead:

- Workers can drop in/out freely (fault-tolerant by design)
- Each worker runs a complete small model locally (no synchronization needed)
- Built-in payment system for workers

---

## Tech Stack

- **Backend:** Python Flask
- **Auth:** Flask-Login
- **Database:** SQLite via Flask-SQLAlchemy
- **Forms:** Flask-WTF with CSRF protection
- **AI Runtime:** Ollama (for the HoneycombOfAI client software)

---

## Project Structure

```
BeehiveOfAI/
├── app.py          # Main Flask application (all routes)
├── models.py       # Database models (User, Hive, Job, etc.)
├── forms.py        # WTForms form definitions
├── seed_data.py    # Sample data for testing
├── requirements.txt
└── templates/
    ├── base.html
    ├── home.html
    ├── about.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── hives.html
    ├── hive_detail.html
    ├── create_hive.html
    ├── submit_job.html
    ├── job_status.html
    └── profile.html
```

---

## Related Projects

- [HoneycombOfAI](https://github.com/strulovitz/HoneycombOfAI) — the client software that runs on Worker/Queen Bee computers

---

## License

MIT License — see [LICENSE](LICENSE) for details.
