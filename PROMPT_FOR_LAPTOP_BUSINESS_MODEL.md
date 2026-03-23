# Prompt for Laptop Claude Code (Opus 4.6) — Business Model Context

> Copy-paste this entire prompt to the Laptop's Claude Code so it has full context about the Nectar Credits business model decided on 2026-03-23.

---

## Context

Hi! I'm Nir, the creator of BeehiveOfAI. The Desktop Claude Code (also Opus 4.6) and I just designed the business model for how payments will work in our platform. I need you to have this complete context so we're all on the same page.

## The Problem We Solved

PayPal Commerce Platform (our ONLY payment provider — no Stripe, no alternatives) charges approximately **2.9% + $0.30 per transaction**. This makes micro-transactions ($1 per question) completely unfeasible — we'd lose ~33% to fees on every single question. The same problem exists on the payout side: if we paid Workers/Queens after every single answer, the fees would eat their entire earnings.

## The Solution: Nectar Credits & Honey Packages

### How Customers Buy (Bee-Themed Bundles)

Instead of paying per question, customers (Beekeepers) buy **Nectar** credits in packages:

| Package Name | Nectars (Questions) | Price | Discount | PayPal Fee | Fee % |
|-------------|---------------------|-------|----------|------------|-------|
| **Honey Drop** | 20 | $18 | 10% off | ~$0.82 | 4.6% |
| **Honey Jar** | 50 | $40 | 20% off | ~$1.46 | 3.7% |
| **Honey Pot** | 100 | $75 | 25% off | ~$2.48 | 3.3% |

- **1 Nectar = 1 question** (premium/complex queries may cost more Nectars)
- Nectars are tracked internally in our database — PayPal is ONLY involved at the moment of purchasing a package
- Bigger packages = bigger discount (like the multi-ride bus tickets)

### How Workers & Queens Get Paid (Honey Harvest)

- Every completed job adds earnings to the participant's **Honeycomb Balance** (internal ledger tracked in our database)
- When a Queen or Worker's Honeycomb Balance reaches the **Harvest Threshold** (minimum $50 or $100), they can request a **Honey Harvest** (payout via PayPal)
- PayPal is ONLY involved at payout time, not after every individual answer
- PayPal fee on $50 payout = ~$1.75 (3.5%) — acceptable
- PayPal fee on $100 payout = ~$3.20 (3.2%) — even better

### Revenue Split (Per Question, from Chapter 5 of the book)

From each Nectar consumed:
- **5% → The Hive (Hub/Platform)** — BeehiveOfAI.com (Nir's website)
- **Of the remaining 95%:**
  - **30% → Queen Bee** — task splitting, synthesis, quality control
  - **70% → Worker Bees** — split among all workers who processed subtasks

Example with Honey Pot ($75 for 100 Nectars):
- After PayPal intake fee: $72.52 net → $0.725 per Nectar
- Hub: $0.036 per question
- Queen: $0.207 per question
- Workers: $0.482 per question (split among all)

### Complete Bee-Themed Glossary

| Business Concept | Bee Name |
|-----------------|----------|
| Credit/token (1 per question) | **Nectar** |
| Small bundle (20 Nectars, $18) | **Honey Drop** |
| Medium bundle (50 Nectars, $40) | **Honey Jar** |
| Large bundle (100 Nectars, $75) | **Honey Pot** |
| Accumulated earnings | **Honeycomb Balance** |
| Payout request | **Honey Harvest** |
| Minimum payout threshold | **Harvest Threshold** |

## Implementation Notes for Phase 7A

When we build this (Opus plans, Sonnet codes), the architecture should be:

1. **Layer 1 — Internal Nectar Engine (no PayPal involved):**
   - Database models: NectarBalance (per user), NectarTransaction (log of credits/debits), HoneycombBalance (per Queen/Worker), EarningsTransaction (log of earnings per job)
   - When a Beekeeper submits a job: deduct Nectars from their balance
   - When a job completes: credit Honeycomb Balances for Queen and Workers based on the split
   - All of this is internal database operations — fast, free, no PayPal fees

2. **Layer 2 — PayPal Commerce Platform (only for real money movement):**
   - Purchase flow: Beekeeper clicks "Buy Honey Jar" → PayPal checkout → on success, add 50 Nectars to their balance
   - Payout flow: Queen/Worker clicks "Request Honey Harvest" → if Honeycomb Balance >= Harvest Threshold → PayPal payout API → deduct from Honeycomb Balance

## Current Project State (for your reference)

- Phase 6 COMPLETE: beehiveofai.com is live via Cloudflare Tunnel
- Phase 7 starting NOW (2026-03-23)
- Payment provider: PayPal Commerce Platform ONLY (works from Israel, zero setup cost)
- Book: 7 chapters written, Chapter 8 next (will likely cover this business model)
- GitHub repos: BeehiveOfAI (website), HoneycombOfAI (desktop client), TheDistributedAIRevolution (book)

Please confirm you've absorbed all of this context!
