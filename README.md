# Turn Many Weak AIs Into One Powerful AI

**Companies: slash your AI costs by up to 90%. Individuals: make money from your idle computer. Built with free, open-source software anyone can deploy.**

---

Your computer sits idle most of the day. So does your neighbor's. So does every computer in every office after 6 PM.

What if all those idle computers could work together — like bees in a hive — to deliver AI services as powerful as the ones that cost thousands per month from OpenAI or Google?

That's BeehiveOfAI.

It takes many small, cheap computers, each running a free open-source AI model, and combines their work into results that rival expensive cloud AI. No million-dollar GPU clusters. No monthly subscriptions. No vendor lock-in.

**One computer is weak. A hive of them is unstoppable.**

---

## Two Ways to Win

### You Want to Save Money (Companies & Teams)

You're paying OpenAI, Google, or Azure thousands per month for AI. Your own office computers sit idle evenings, nights, and weekends. With BeehiveOfAI, you submit your AI tasks to a Hive of ordinary computers running free, open-source models. Same work gets done — at a fraction of the cost.

> *"We replaced our $3,000/month AI API bill with 12 office PCs running overnight."*
> — The kind of story BeehiveOfAI makes possible.

### You Want to Make Money (Individuals & Entrepreneurs)

You have a computer with a GPU. Maybe a gaming PC, maybe a workstation, maybe just a decent laptop. Install our free software, join a Hive, and your computer starts earning money by processing AI tasks — while you sleep, work, or watch Netflix.

Or go bigger: recruit other people's computers, organize them into Hives, and build an AI services business. The platform handles the jobs, the payments, and the coordination. You just manage the operation.

---

## How It Works — The Beehive

BeehiveOfAI works exactly like a real beehive:

```
   A Beekeeper brings a task (Nectar)
              |
              v
   The Queen Bee splits it into pieces
         /    |    \
        v     v     v
   Worker  Worker  Worker     (each processes a piece on their own computer)
        \     |    /
         v    v   v
   The Queen Bee combines the results
              |
              v
   The Beekeeper gets the final answer (Honey)
```

| Role | Who | What They Do |
|------|-----|-------------|
| **Worker Bee** | Anyone with a computer | Processes AI sub-tasks locally, earns money |
| **Queen Bee** | Team organizer | Manages a Hive, splits tasks, combines results, earns a commission |
| **Beekeeper** | Company or individual | Submits tasks, pays with Nectar credits, gets results |
| **Hive** | A team | One Queen + many Workers, working together |

Every Worker runs a complete AI model on their own machine. If one Worker goes offline, the others keep working. No single point of failure. No synchronization headaches.

---

## Why This Is Different

Other distributed AI projects (like Petals or EXO) split the *AI model* across machines — meaning if any single machine disconnects, everything breaks.

BeehiveOfAI splits the *work* instead:

- Workers can drop in and out freely — the system is fault-tolerant by design
- Each Worker runs a complete model locally — no complex synchronization
- Works with any open-source model: DeepSeek, Llama, Qwen, Mistral, and more
- Built-in business model: credits, earnings, payouts — ready for real money

---

## Deploy Your Own BeehiveOfAI

This is a complete, working platform. You can deploy your own instance in about 15 minutes.

### Quick Start (Test Mode — No Payments, Free to Try)

```bash
git clone https://github.com/strulovitz/BeehiveOfAI.git
cd BeehiveOfAI
pip install -r requirements.txt
python seed_data.py    # creates database with sample data
python app.py          # starts the website
```

Open http://localhost:5000 in your browser.

**Test accounts (password: `test123` for all):**

| Role | Email |
|------|-------|
| Worker Bee | worker1@test.com |
| Queen Bee | queen1@test.com |
| Beekeeper | company1@test.com |

Everything works out of the box — submitting tasks, splitting work, combining results, earning credits. No payment provider needed. This is test mode: all purchases are free, so you can explore the entire system.

### Going Live — Your Domain, Your Payment Provider

When you're ready to deploy for real:

1. **Get a domain** — Any domain works (yourhive.com, aibees.io, whatever you want)
2. **Set up hosting** — A VPS, a cloud server, or even your own computer + Cloudflare Tunnel → **[Full deployment guide](DEPLOY.md)**
3. **Connect payments** — See the next section, or the **[detailed payment guide](PAYMENT_GUIDE.md)**

The platform is designed to run independently on any domain. You're deploying YOUR business, not ours.

---

## Connect Your Payment Provider (The Vibe Coding Way)

BeehiveOfAI includes a complete, tested PayPal integration as a reference example. But you should use whatever payment provider works best in YOUR country:

| Your Country | Recommended Provider |
|-------------|---------------------|
| USA | Stripe Connect |
| Europe | Stripe or PayPal |
| UK | Stripe or PayPal |
| Canada | Stripe |
| Australia | Stripe or PayPal |
| Other | PayPal, or check what's available locally |

**You don't need to be a payment expert.** Here's the modern way to do it:

1. Sign up for your payment provider (Stripe, PayPal, etc.)
2. Get your API keys
3. Open an AI coding assistant (Claude Code, Cursor, GitHub Copilot — whatever you use)
4. Tell it:

> *"I have a BeehiveOfAI instance. Here are my Stripe API keys. Connect Stripe to handle Nectar credit purchases and Honey Harvest payouts. Use paypal_service.py as a reference for the integration pattern."*

The AI assistant will read the existing PayPal code, understand the pattern, and wire up your provider. We've seen this take about 10-15 minutes.

The platform already handles all the business logic — credits, balances, revenue splits, transaction history. The payment provider just needs to plug into two points: **money in** (buying Nectars) and **money out** (Honey Harvest payouts).

---

## The Business Model (Built In)

BeehiveOfAI comes with a complete, thought-through business model:

### For Your Customers (Beekeepers)

Customers buy **Nectar credits** in packages:

| Package | Credits | Price | Savings |
|---------|---------|-------|---------|
| Honey Drop | 20 | $18 | 10% off |
| Honey Jar | 50 | $40 | 20% off |
| Honey Pot | 100 | $75 | 25% off |

Each credit = one task submitted. Buying in bulk keeps payment processing fees low (3% instead of 33% on micro-transactions).

*Prices are defaults — you set whatever pricing works for your market.*

### For Your Workers and Queens

Workers and Queens earn a share of every task they help complete:

- **5%** → You (the platform operator)
- **30%** → The Queen Bee (task coordinator)
- **65%** → The Worker Bees (task processors)

Earnings accumulate in each user's **Honeycomb Balance**. When it reaches the threshold (default $50), they can request a **Honey Harvest** — a payout to their account.

*Revenue splits are configurable. Adjust them for your market.*

---

## The Complete Stack

| Component | Description |
|-----------|------------|
| **BeehiveOfAI** (this repo) | The website — user management, job queue, payments, dashboards |
| **[HoneycombOfAI](https://github.com/strulovitz/HoneycombOfAI)** | The client software that runs on Worker/Queen computers |
| **[The Distributed AI Revolution](https://github.com/strulovitz/TheDistributedAIRevolution)** | The book — full story, business model, technical deep-dive |

### Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite (swap for PostgreSQL in production)
- **Auth:** Flask-Login with password hashing
- **Security:** CSRF protection, rate limiting, production server (Waitress)
- **AI Runtime:** Ollama (with LM Studio, llama.cpp, vLLM support planned)
- **Payments:** PayPal integration included (Stripe-ready architecture)

---

## Project Structure

```
BeehiveOfAI/
├── app.py              # Main Flask app — all routes and business logic
├── models.py           # Database models (User, Hive, Job, Transactions...)
├── paypal_service.py   # PayPal REST API wrapper (reference implementation)
├── forms.py            # Form definitions with validation
├── seed_data.py        # Sample data for testing
├── run_production.py   # Production server launcher (Waitress)
├── requirements.txt
└── templates/          # All HTML templates (Jinja2)
```

---

## The Story Behind This

BeehiveOfAI was created by one developer in Israel who wanted to prove that ordinary people with ordinary computers could compete with billion-dollar AI companies.

The full story — including the technical architecture, the business model design, the payment infrastructure nightmare, and the decision to open-source everything — is told in the book:

**[The Distributed AI Revolution](https://github.com/strulovitz/TheDistributedAIRevolution)** — free to read on GitHub.

---

## Contributing

This is an open-source project and contributions are welcome. Whether you want to add a new payment provider, support a new AI backend, improve the UI, or translate the platform — PRs are open.

---

## License

MIT License — use it, modify it, deploy it, build a business on it. See [LICENSE](LICENSE) for details.
