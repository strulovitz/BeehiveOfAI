# BeehiveOfAI — Project Status

> This file is shared between Desktop and Laptop Claude Code instances via GitHub.
> Update it whenever significant progress is made.

## Last Updated: 2026-03-26 (evening)

## Current Phase: Phase 8 — INTERNET TEST COMPLETE ✅ (Phase 6 ✅, Linux LAN Test ✅, Internet Test ✅)

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

**Phase 8: Desktop Linux Mint Setup + Linux Cross-Machine Test ✅ DONE (2026-03-25)**

The Desktop computer was set up on Linux Mint 22.2 (Cinnamon) and a full cross-machine test was run between the two Linux machines:

- Desktop Linux Mint 22.2 Setup:
  - GitHub CLI (gh) installed and authenticated as strulovitz
  - Python 3.12.3 with venv at ~/beehive-venv (BeehiveOfAI) and ~/honeycomb-venv (HoneycombOfAI)
  - Ollama installed with llama3.2:3b model (RTX 4070 Ti GPU, Driver 580, CUDA 13.0)
  - All dependencies installed for both BeehiveOfAI and HoneycombOfAI
  - cmake and build-essential available for future builds

- **LINUX CROSS-MACHINE TEST PASSED on 2026-03-25** 🎉🎉🎉
  - Desktop (Linux Mint 22.2, RTX 4070 Ti): Website + Worker Bee (Ollama, llama3.2:3b)
  - Laptop (Debian 13, RTX 5090): Queen Bee (Ollama, llama3.2:3b)
  - Beekeeper submitted job via website → Queen claimed → Queen split into subtasks via AI → Worker processed 2 subtasks (environmental impact + economic feasibility of geothermal energy) → Queen combined → Honey delivered
  - Total pipeline time: ~1 minute (14:11:40 submit → 14:12:44 complete)
  - Worker output: subtask #7 (2647 chars), subtask #8 (3639 chars)
  - Desktop IP: 10.0.0.4, Laptop IP: 10.0.0.7
  - Beekeeper rated the completed job ✅
  - This is the first successful Linux-to-Linux distributed AI test! 🐧🐧

- Machine Roles for Linux Test:
  - **Desktop (10.0.0.4, Linux Mint):** `python app.py` (website) + `python honeycomb.py` (Worker, Ollama)
  - **Laptop (10.0.0.7, Debian 13):** `python honeycomb.py --mode queen` (Queen, Ollama)

**Phase 8B: FULL INTERNET TEST PASSED on 2026-03-25 ✅ 🎉🎉🎉**

The most complete test of the entire platform to date:

- **Website served to the REAL INTERNET** via Cloudflare Tunnel from Desktop Linux Mint 22.2
  - New tunnel created: `beehive-linux` (ID: 96467138-c2c4-4caa-9885-bc976b48a97c)
  - DNS updated: beehiveofai.com now routes to the Linux Mint tunnel
  - Config at: `/home/nir/.cloudflared/config.yml`
  - 4 tunnel connections established (Tel Aviv tlv01 + Frankfurt fra06/fra20)

- **Real SMS phone verification via Twilio** ✅
  - Twilio credentials configured as environment variables on Desktop Linux Mint
  - Nir received real SMS on his phone (+972544752626)
  - Verified successfully, then submitted a job

- **Full Internet Pipeline Test** — Job #4 "AI in Space" (2026-03-25 14:50):
  - Beekeeper submitted job via https://beehiveofai.com (real internet, through Cloudflare)
  - Queen (Laptop Debian 13, 10.0.0.7) claimed job via internet → split into 2 subtasks using AI
  - Worker (Desktop Linux Mint, 10.0.0.4) claimed & processed subtask #9 and #10 using Ollama (RTX 4070 Ti)
  - Queen combined results → JOB COMPLETE
  - Total pipeline time: ~27 seconds (14:50:21 submit → 14:50:50 complete)
  - Beekeeper rated the job ✅

- **Everything verified end-to-end:**
  - [x] Real internet access via Cloudflare Tunnel
  - [x] Real SMS verification via Twilio Verify API
  - [x] Queen connecting via beehiveofai.com (not LAN IP)
  - [x] Worker processing subtasks with local AI (Ollama, RTX 4070 Ti)
  - [x] Revenue split and job completion
  - [x] Job rating by Beekeeper

### Production Setup (Desktop Linux Mint — CURRENT)
- Website: `source ~/beehive-venv/bin/activate && cd ~/BeehiveOfAI && python app.py` (needs Twilio env vars)
- Tunnel: `cloudflared tunnel run beehive-linux`
- Worker: `source ~/honeycomb-venv/bin/activate && cd ~/HoneycombOfAI && python honeycomb.py`
- Twilio env vars needed: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID (stored in ~/BeehiveOfAI/.env, NOT committed to git)

**Known Platform Findings (2026-03-25):**
- **Linux GUI requires `libxcb-cursor0` system package.** PyQt6 will crash on startup without it. Fix: `sudo apt install -y libxcb-cursor0`. Applies to all Debian-based distros (Debian, Ubuntu, Linux Mint). Discovered on Desktop Linux Mint 22.2, 2026-03-25.
- **LM Studio on Linux requires manual server start.** On Windows, LM Studio auto-serves its API on port 1234 when a model is loaded. On Linux, the user must go to the Developer/Local Server tab and click "Start Server" manually. Without this, HoneycombOfAI's backend detector will show LM Studio as "not detected." The detection code is correct and platform-agnostic — this is a LM Studio behavior difference. Documented in: Chapter 7 of the book, HoneycombOfAI README, HoneycombOfAI PLATFORM_NOTES.md.

**Phase 6 Backend Status (updated 2026-03-24 night):**
- Ollama: PASS (Windows + Debian)
- LM Studio: PASS (Windows + Debian — requires manual server start on Linux, see notes above)
- llama.cpp server: PASS (Windows)
- llama.cpp Python: PASS (Windows, CPU-only)
- vLLM: **NOT DONE — next task.** Install inside ~/honeycomb-venv on Debian. RTX 5090 Blackwell CUDA compatibility must be verified carefully.

**Phase 6 Backend Status (updated 2026-03-25):**
- All 5 backends PASS on Laptop Debian 13 (Ollama, LM Studio, llama.cpp server, llama.cpp Python, vLLM)
- Desktop Linux Mint: Ollama PASS (others available to set up as needed)

**Phase 9: PyQt6 Native Desktop GUI for HoneycombOfAI — DONE (2026-03-25 evening)**

The HoneycombOfAI desktop client now has a full native GUI built with PyQt6. All three roles tested and working on Desktop Windows 11.

- **GUI Files Created:**
  - `gui_main.py` — Main window, mode selector (card-based first screen), app entry point
  - `gui_worker.py` — Worker Bee dashboard: status indicator, stat cards (tasks, chars, uptime), activity log
  - `gui_queen.py` — Queen Bee console: job board table with progress bars, subtask tracking, activity log
  - `gui_beekeeper.py` — Beekeeper portal: task text area, submit button, live status polling, results display, star rating
  - `gui_settings.py` — Settings dialog: 4 tabs (General, AI Model, Authentication, Backends), backend auto-detection, connection test, saves to config.yaml
  - `gui_threads.py` — QThread wrappers for Worker/Queen polling loops (thread-safe GUI updates via signals/slots)
  - `gui_styles.py` — Bee-themed dark/amber stylesheet (honey gold accents, dark background)

- **API Endpoints Added to BeehiveOfAI:**
  - `POST /api/hive/<hive_id>/jobs` — Job submission API (for Beekeeper GUI)
  - `GET /api/job/<job_id>` — Job status polling API (for Beekeeper GUI)

- **Key Design Decisions:**
  - Config.yaml remains the single source of truth (GUI reads/writes it via Settings dialog)
  - All polling runs in QThreads, GUI updates via Qt signals/slots (thread-safe)
  - User-friendly error messages for all connection/auth failures (not raw exceptions)
  - All errors logged to `honeycomb_gui.log` (user can't copy-paste from Windows dialog boxes)
  - Cross-platform: same code runs on Windows, Debian, Linux Mint (PyQt6 is fully cross-platform)
  - Terminal CLI (`python honeycomb.py`) continues to work alongside the GUI

- **Test Results (Desktop Windows 11, 2026-03-25 evening):**
  - Beekeeper: Submit task, receive Honey result, rate job — PASS
  - Worker Bee: Start worker, process subtasks with live dashboard — PASS
  - Queen Bee: Start queen, split tasks, track subtask progress, combine results — PASS

- **How to Launch:** `python gui_main.py`
- **How to Launch on Linux:** `source ~/honeycomb-venv/bin/activate && pip install PyQt6 && cd ~/HoneycombOfAI && python gui_main.py`

**Future:**
- Test GUI on Linux (Debian 13 + Linux Mint 22.2) — should work identically
- GUI polish: icons, notifications, tray icon, auto-start
- Installers: Windows (.exe), Linux (.deb), macOS (.app)

**Phase 11: macOS VM Setup + Distributed Test Attempt (2026-03-26)**

Both macOS Sequoia VMs (VMware guests, CPU-only, no GPU) were fully set up and configured:

- **Desktop macOS VM (10.0.0.7):**
  - Homebrew 5.1.1, Python 3.12.13, Git 2.39.5, GitHub CLI 2.89.0 (authenticated)
  - Both repos cloned, venvs created, all dependencies installed (including PyQt6 6.9.0)
  - Ollama working with llama3.2:3b (CPU-only, ~12s per response)
  - PyQt6 GUI tested and working
  - CLI tested and working
  - Configured as Queen Bee

- **Laptop macOS VM (10.0.0.9):**
  - Python 3.9.6 (pre-installed), Git 2.39.5
  - All three repos cloned, venvs created, all dependencies installed
  - Ollama working with llama3.2:3b (CPU-only, ~9s per response)
  - PyQt6 GUI tested and working
  - CLI tested and working
  - Configured as Worker Bee (worker-laptop-macos-009)

- **macOS Distributed Test — NOT YET COMPLETED:**
  - Queen on Desktop Mac connected to beehiveofai.com, saw 2 workers
  - Worker on Laptop Mac reported connected and polling
  - Job #6 submitted — Queen split into 2 subtasks, but Worker never claimed them → timed out (5min)
  - Job #7 submitted (simpler) — same issue: subtasks created but Worker never claimed
  - Root cause: Laptop Worker process likely died after initial startup (session ended or SSL issue)
  - **TO RETRY TOMORROW** with both terminals open and monitored simultaneously
  - See BRIEFING_MACOS_DISTRIBUTED_TEST_STATUS.md in HoneycombOfAI for full details

- **macOS Platform Findings:**
  - PyQt6 installs cleanly via pip on macOS Sequoia — no `brew install qt@6` needed
  - Ollama CPU-only is slow but fully functional (~9-12 seconds per simple query)
  - macOS Sequoia has Python 3.9.6 at /usr/bin/python3 (after Xcode CLT installed)
  - Homebrew installs to /usr/local on Intel Macs (VMware x86_64)
  - urllib3/LibreSSL warning in stderr is harmless
  - Copy-paste in VMware macOS is difficult — use GitHub to share files between instances

**Phase 10: COMPLETE BOOK REWRITE — IN PROGRESS (2026-03-25 night)**

The book (TheDistributedAIRevolution) has been completely rewritten from scratch by Desktop Windows Claude Code (Opus 4.6). The old 8 chapters were deleted. The new book has a completely different vision:

- **New vision:** Written for EVERYONE, not just developers. Non-technical, conversational, enthusiastic. "For Dummies" style — any term a layperson wouldn't know gets explained simply.
- **Two modes emphasized from Chapter 1:** Public mode (open marketplace, home computers earn money) AND Private mode (organizations use their own idle computers, sensitive data never leaves the building).
- **New structure:** Prologue + 10 chapters + Epilogue (was: 8 chapters, no prologue/epilogue)
- **Key themes:** Task parallelism as a NEW INVENTION (not the failed model-splitting approach), the chess analogy, Pirate Bay reputation system / Privateer metaphor, Queen Bee as powerful AI brain (not just coordinator), vibe coding, open source as gift to the world

**Published (on GitHub):**
- Prologue — A Dream Worth Coding For (personal story, girlfriend's dreams, motivation)
- Chapter 1 — What If Your Computers Could Make Money While Everyone Sleeps?
- Chapter 2 — The Beehive: A Simple Idea That Changes Everything
- Chapter 3 — The Secret Ingredient: AI That Lives on Your Computer (DeepSeek R1, MoE, chain of thought, NOT an agent)
- Chapter 4 — One App, Three Dreams (Queen tiers: dual-GPU / DGX Spark / VPS, reputation system)
- Chapter 5 — The Marketplace: Where Tasks Meet Computers
- Chapter 6 — Show Me the Honey: How Everyone Earns (Nectar credits, 65/30/5 split, escrow, flywheel)
- Chapter 7 — From Zero to Beehive: Anyone Can Set This Up (step-by-step setup for all 3 roles, public + private)

**Remaining (to be written next session):**
- Chapter 8 — The Proof: We Actually Did It
- Chapter 9 — Vibe Coding: How One Person Built All of This
- Chapter 10 — The Future: A World of Beehives
- Epilogue — Tokyo, Paris, and the Open Road

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
