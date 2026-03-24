# BeehiveOfAI — Project Status

> This file is shared between Desktop and Laptop Claude Code instances via GitHub.
> Update it whenever significant progress is made.

## Last Updated: 2026-03-23 (late evening)

## Current Phase: Phase 7 — Next Steps (Phase 6 COMPLETE ✅)

### Network Info
- **Desktop IP (LAN):** 10.0.0.4
- **Website URL (from laptop):** http://10.0.0.4:5000
- **Website URL (from desktop):** http://localhost:5000

### What's Done
- [x] Phase 0-4: All complete (tools, skeleton, demo, website, REST API)
- [x] Laptop setup: Python 3.12.11, Node.js v24.14.0, Ollama 0.18.2, Claude Code, all repos cloned
- [x] Both machines on same LAN (router)
- [x] Phase 5 plan created by Opus 4.6
- [x] Bind Flask to 0.0.0.0 (laptop can reach website over LAN)
- [x] Add Worker API endpoints (poll subtasks, claim subtasks, submit results)
- [x] Update HoneycombOfAI worker_bee.py for API-driven workflow
- [x] Update HoneycombOfAI queen_bee.py for multi-machine orchestration
- [x] Update config.yaml for LAN setup (Desktop=Queen, Laptop=Worker)
- [x] **END-TO-END TEST PASSED on 2026-03-22** 🎉
- [x] Chapter 7 written: "The Technical Blueprint — Inside the Code" ✅
- [x] Phase 6A: Security hardening — Waitress production server, SECRET_KEY from env var ✅
- [x] Phase 6B: Cloudflare Tunnel — beehiveofai.com LIVE on the internet! ✅ (2026-03-22 evening)
- [x] **WEBSITE VERIFIED FROM MOBILE PHONE (not on home Wi-Fi)** 🎉🎉🎉
- [x] Phase 7A Layer 1: Nectar Credits engine, Honeycomb Balance, revenue split ✅ (2026-03-23)
- [x] Phase 7A Layer 2: PayPal checkout tested & working in sandbox ✅ (2026-03-23)
- [x] Phase 7B: Ratings — Queen↔Worker mutual ratings, trust score updates ✅ (2026-03-23)
- [x] **THE PIVOT:** Project reframed as open-source for OTHERS to deploy (2026-03-23)
- [x] README.md completely rewritten with "Turn Many Weak AIs Into One Powerful AI" pitch ✅
- [x] DEPLOY.md — full deployment guide (home/VPS/PaaS) ✅
- [x] PAYMENT_GUIDE.md — payment provider by country + vibe coding approach ✅
- [x] Chapter 8: "The Business Engine — Money, Honey, and the Invisible Walls" ✅

### Phase 5 Test Result — SUCCESS
On 2026-03-22, Nir submitted a real job via the Beekeeper dashboard (company1@test.com).
- Desktop ran: BeehiveOfAI website (Flask) + Queen Bee (split task, combined results)
- Laptop ran: Worker Bee (polled over LAN, claimed subtasks, processed with local Ollama llama3.2:3b, submitted results)
- Result appeared on website with today's date ✅
- This is the first real two-machine distributed AI job in the project's history!

### Machine Roles (confirmed working)
- **Desktop (10.0.0.4):** `python app.py` + `python honeycomb.py --mode queen`
- **Laptop:** `python honeycomb.py --mode worker` (config.yaml: mode=worker, server=http://10.0.0.4:5000, worker_id=worker-laptop-001)

### Test Credentials (from seed_data.py)
- Worker: worker1@test.com / test123
- Queen: queen1@test.com / test123
- Beekeeper: company1@test.com / test123

### Book Status
- Chapter 1: The Vision ✅
- Chapter 2: The Problem ✅
- Chapter 3: Task Parallelism ✅
- Chapter 4: How It All Works ✅
- Chapter 5: The Humans in the Hive ✅
- Chapter 6: The Road Ahead ✅
- Chapter 7: The Technical Blueprint ✅
- Chapter 8: "The Business Engine — Money, Honey, and the Invisible Walls" ✅ (2026-03-23)
- Chapter 9: TBD — scale, multi-machine growth

### Key Architecture Decisions (from Chapter 7)
- **Multi-backend AI:** Must support Ollama, LM Studio, llama.cpp, and vLLM (not just Ollama)
- **Native GUI:** HoneycombOfAI will become a native desktop app (Windows/Linux/macOS installers), CLI stays as dev/automation option
- **One app, three modes:** HoneycombOfAI is one single application — Worker/Queen/Beekeeper are modes, not separate programs

### Production Setup (Desktop)
- Website: `python run_production.py` (needs BEEHIVE_SECRET_KEY env var set first)
- Tunnel: `cloudflared tunnel run beehive` (separate Command Prompt window)
- Both windows must stay open for the site to be live
- Tunnel ID: 18a52f43-e0b4-4f5b-9efd-804027df6884
- Config: C:\Users\nir_s\.cloudflared\config.yml

### Nectar Credits & Honey Packages — Business Model (decided 2026-03-23)

Micro-transactions don't work with PayPal fees (~2.9% + $0.30 per transaction).
Selling one question at $1 loses 33% to fees. Solution: **sell in bundles, pay out in batches.**

**Customer-facing packages (buying Nectar credits):**
| Package | Questions (Nectars) | Price | Discount | Name |
|---------|---------------------|-------|----------|------|
| Small | 20 | $18 | 10% off | **Honey Drop** |
| Medium | 50 | $40 | 20% off | **Honey Jar** |
| Large | 100 | $75 | 25% off | **Honey Pot** |

- Internal credit unit = **Nectar** (1 question = 1 Nectar, or more for premium)
- PayPal fee on $75 Honey Pot = ~$2.48 (3.3%) vs $0.33 per $1 transaction (33%)

**Payout system (earnings for Queens & Workers):**
- Accumulated earnings = **Honeycomb Balance**
- Payout request = **Honey Harvest**
- Minimum payout threshold = **Harvest Threshold** ($50 or $100)
- PayPal fee on $50 payout = ~$1.75 (3.5%) — acceptable
- PayPal fee on $100 payout = ~$3.20 (3.2%) — even better

**Revenue split per question (using Honey Pot / 100 Nectars at $75):**
- After PayPal intake: $72.52 net → $0.725 per Nectar
- Hub (platform fee): 5% = $0.036
- Queen Bee: 30% of remainder = $0.207
- Worker Bees: 70% of remainder = $0.482 (split among all workers on the job)

**Full bee-themed glossary:**
| Business Concept | Bee Name |
|-----------------|----------|
| Credit/token | **Nectar** |
| Small bundle (20) | **Honey Drop** |
| Medium bundle (50) | **Honey Jar** |
| Large bundle (100) | **Honey Pot** |
| Accumulated earnings | **Honeycomb Balance** |
| Payout request | **Honey Harvest** |
| Minimum payout threshold | **Harvest Threshold** |

### THE PIVOT (decided 2026-03-23 evening)

**Running payments from Israel as a solo developer is not viable.** After exhaustive research:
- **Stripe** — Requires US LLC ($400-700/year + IRS risk). REJECTED.
- **PayPal Commerce Platform** — Doesn't support Israel. REJECTED.
- **PayPal Merchant (Orders API)** — Works for RECEIVING payments ✅ (tested in sandbox)
- **PayPal Payouts** — Applied for access, unlikely to be approved (no real users, website offline at night)
- **Payoneer** — Israeli company, but horror stories: frozen funds, locked accounts, poor support. REJECTED.
- **Wise, Paddle, Tipalti** — Researched, each has limitations. Not pursuing.

**New Direction: BeehiveOfAI is now a FREE, OPEN-SOURCE project.**

The project is reframed from "I am running this business" to:
> "I built the complete blueprint — here's how YOU can build this business."

**Target audiences for the project:**
1. **Companies with idle GPU capacity** — "Use your computers' idle time to earn money processing AI tasks"
2. **Entrepreneurs** — "Start a lucrative AI services business using this free platform"
3. **AI developers** — "Deploy your own distributed AI marketplace"

**How Nir benefits:**
- Publicity from the project + book → visibility in AI/tech communities
- Consulting/implementation services for companies wanting to deploy
- Acqui-hire opportunity (OpenClaw→OpenAI, MoltBook→Meta pattern)
- The book as a portfolio piece and lead generator
- Enterprise licensing for self-hosted deployments

**The book is being reframed** to address the READER as "YOU" — the person who will deploy this.
Payment chapter becomes a guide: "if YOU are in the US, use Stripe Connect. If YOU are in EU, use PayPal. Here are all the options we researched."

### What Was Built (Phase 7A) — Stays in the Repo as Working Example
- Layer 1: Internal Nectar Credits engine, Honeycomb Balance, revenue split ✅
- Layer 2: PayPal Orders API integration (checkout works!) ✅
- paypal_service.py: Complete REST API wrapper, two-mode (sandbox/live) ✅
- All payment code stays as a working reference for deployers

### What's Next

**Part 7B: Ratings improvements ✅ DONE (2026-03-23)**
- Queen can rate individual Workers per subtask after job completion ✅
- Workers can rate their Queen's coordination after job completion ✅
- Trust scores auto-update based on running average of all ratings ✅
- Worker Contributions panel on job status page (Queen view) ✅
- Role badges on profile reviews (Beekeeper/Queen/Worker Review) ✅
- New routes: `/subtask/<id>/rate-worker`, `/job/<id>/rate-queen`
- New templates: `rate_worker.html`, `rate_queen.html`

**Part 7C: SMS Phone Verification ✅ DONE (2026-03-23 late night)**
- Using Twilio Verify API — no phone number purchase or A2P 10DLC needed
- Nir tested with real Twilio credentials — received real SMS on his phone ✅
- Flow: Register (phone required) → 6-digit code via SMS → type code in 6-box page → verified
- Unverified users blocked from: submit jobs, join hives, create hives, harvest payouts
- Profile page shows phone edit form for unverified users (to add/change phone + trigger new code)
- Reuses existing `is_verified` field + "✅ Verified" badge on profiles
- New files: `sms_service.py`, `templates/verify_phone.html`
- Modified: `app.py`, `forms.py`, `requirements.txt`, `seed_data.py`, `templates/register.html`, `templates/profile.html`

**Deployer Documentation ✅ DONE (2026-03-23)**
- `DEPLOY.md` — Three hosting options (free/cheap/PaaS), step-by-step ✅
- `PAYMENT_GUIDE.md` — Provider by country, vibe coding approach ✅
- `README.md` — Complete rewrite with "YOU" framing ✅

**Known Platform Findings (2026-03-24):**
- **LM Studio on Linux requires manual server start.** On Windows, LM Studio auto-serves its API on port 1234 when a model is loaded. On Linux, the user must go to the Developer/Local Server tab and click "Start Server" manually. Without this, HoneycombOfAI's backend detector will show LM Studio as "not detected." The detection code is correct and platform-agnostic — this is a LM Studio behavior difference. Documented in: Chapter 7 of the book, HoneycombOfAI README, HoneycombOfAI PLATFORM_NOTES.md.

**Future:**
- Multi-backend support: Add LM Studio, llama.cpp, vLLM backends to HoneycombOfAI
- GUI development: Native graphical interface for HoneycombOfAI

### Payment Research Archive (2026-03-23)

All providers researched, with Israel-specific findings:
- PayPal: Cannot fund from Israeli bank, $750/day withdrawal limit, enterprise features unavailable
- Payoneer: Frozen funds horror stories, account closures without warning
- Stripe: Needs US LLC, IRS obligations
- Tipalti: $299+/mo, enterprise only
- Wise: Good for payouts only, no marketplace features
- Paddle: Merchant of Record, 5%+$0.50, good for credit sales but not marketplace payouts
- Israeli gateways (Tranzila, CardCom, Meshulam): Collection only, no payout capabilities

Total marketplace fees for someone who CAN run payments: ~5-9% (receive + payout + currency conversion)

### Chapter 8 — "The Business Engine — Money, Honey, and the Invisible Walls" ✅
Written 2026-03-23. Covers: micro-transaction problem, Nectar Credits solution, PayPal's invisible walls (country, approval, funding, withdrawal), the Platform vs Project fork.
