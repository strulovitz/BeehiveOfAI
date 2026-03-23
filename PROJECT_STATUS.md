# BeehiveOfAI — Project Status

> This file is shared between Desktop and Laptop Claude Code instances via GitHub.
> Update it whenever significant progress is made.

## Last Updated: 2026-03-23 (evening)

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

### What's Next — Phase 7 (starting 2026-03-23)

**Part 7A: Payments**
- Layer 1: Internal earnings engine ✅ DONE (2026-03-23) — Nectar credits, Honeycomb Balance, revenue split, buy/harvest pages, navbar balances, tested live on beehiveofai.com
- Layer 2: PayPal Merchant mode (Orders API v2 + Standard Payouts API) — CODE DONE ✅
  - PayPal checkout (buying Nectars): TESTED & WORKING in sandbox ✅ (2026-03-23)
  - PayPal Payouts (Honey Harvest): Code ready, WAITING for PayPal to approve Payouts API access ⏳
  - paypal_service.py: Direct REST API wrapper (no SDK), two-mode (sandbox/live)
  - PayPalOrder model: Tracks orders for double-spend protection
  - Graceful fallback: If PayPal env vars not set → free test mode
- Payment provider decision: PayPal ONLY. No Stripe, no US LLC, no Rapyd.
- PayPal Commerce Platform REJECTED — doesn't support Israel (only ~32 countries)
- Using regular PayPal Merchant mode instead — Israel is "Fully Localized"

**Part 7B: Ratings improvements**
- Allow Queen to rate Workers after job completion
- Update Worker trust scores based on Queen ratings

**Part 7C: SMS notifications**
- Twilio integration for job submitted / completed notifications

**Pivot Strategy (if payments don't work):**
- Release as free/open-source project for companies to deploy
- Offer consulting/implementation services
- Acqui-hire path (like OpenClaw→OpenAI, MoltBook→Meta)
- Enterprise self-hosted licensing (no external payments needed)
- The book as portfolio piece / lead generator

**Alternative Payment Providers Researched (2026-03-23):**
- **Payoneer** (Israeli company, Petah Tikva!) — STRONGEST alternative. Used by Fiverr, Upwork, Amazon. Mass Payout API, $1.50/payout, 1-3 day approval. If PayPal Payouts denied, pivot to Payoneer.
- **Wise Business** — Works from Israel, 0.4-1.5% fees, API for batch payments. Good for payouts only.
- **Paddle** — Merchant of Record, handles all tax/compliance, 5%+$0.50. Good for selling Nectar credits.
- **Tipalti** — Israeli company, enterprise-level ($299+/mo), good at scale.
- REJECTED: Stripe (needs US LLC), Deel (HR not marketplace), crypto (too niche)

**Future (not Phase 7):**
- Multi-backend support: Add LM Studio, llama.cpp, vLLM backends to HoneycombOfAI
- GUI development: Native graphical interface for HoneycombOfAI

### Chapter 8 Notes — "The Business Engine" (collecting ideas)

This chapter will cover the full business/economic model in depth. Collecting notes here as we design and build.

- **The micro-transaction problem:** Why per-question billing fails with payment processor fees (the 33% fee trap)
- **Nectar Credits system:** The bus ticket analogy — buy in bulk, use one at a time, get a discount for bigger packages
- **Honey Drop / Jar / Pot:** Tiered pricing with volume discounts (10% / 20% / 25% off)
- **Honeycomb Balance & Honey Harvest:** How workers/queens accumulate earnings and get paid in batches, not per-answer
- **The math that makes everyone profitable:** Fee analysis showing how bundling drops PayPal's cut from 33% to ~3%
- **PayPal from Israel — the real story:** Israel is "Fully Localized" for PayPal Merchant mode, but cannot fund PayPal from Israeli bank (balance comes from received payments only). $750/day withdrawal limit via Visa card. No hidden IRS trap (unlike Stripe). Total marketplace cycle fees: 5-9%.
- **PayPal Commerce Platform vs Merchant mode:** Why we use Merchant mode (Commerce Platform doesn't support Israel). Orders API v2 for money-in, Standard Payouts API for money-out. Our code handles the marketplace splitting logic internally.
- **SMS notifications (Twilio):** How the hive keeps everyone informed — buzz alerts when jobs arrive, complete, etc. (add details after Phase 7C)
- *(add more ideas here as they come up)*

### PayPal Israel Limitations (documented 2026-03-23)
- Cannot fund PayPal from Israeli bank — balance ONLY from received payments
- $750/day withdrawal limit via Israeli Visa card (workaround: US bank account, $35/withdrawal)
- Cannot use Israeli credit card to send money — only PayPal balance
- Most enterprise features NOT available for Israeli accounts
- Fees: 3.4%+1.20ILS (receive) + 2% capped (payout) + 2.5% (currency conversion)
- Tax: Report to Israeli Tax Authority + Bituach Leumi + VAT (17%). Need Israeli accountant.
- NO US entity required, NO IRS 1099 risk to us (unlike Stripe)
