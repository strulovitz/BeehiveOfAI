# BeehiveOfAI — Project Status

> This file is shared between Desktop and Laptop Claude Code instances via GitHub.
> Update it whenever significant progress is made.

## Last Updated: 2026-03-22 (evening)

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
- Chapter 8: "The Business Engine" — collecting notes below, will write when ready

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
- Layer 1: Internal earnings engine — Nectar credits, Honeycomb Balance tracking, revenue split (5% Hub / 30% Queen / 70% Workers of remainder)
- Layer 2: PayPal Commerce Platform — Honey Drop/Jar/Pot purchase pages, Honey Harvest payout system
- Payment provider decision: PayPal ONLY. No Stripe, no US LLC, no Rapyd.

**Part 7B: Ratings improvements**
- Allow Queen to rate Workers after job completion
- Update Worker trust scores based on Queen ratings

**Part 7C: SMS notifications**
- Twilio integration for job submitted / completed notifications

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
- **SMS notifications (Twilio):** How the hive keeps everyone informed — buzz alerts when jobs arrive, complete, etc. (add details after Phase 7C)
- *(add more ideas here as they come up)*
