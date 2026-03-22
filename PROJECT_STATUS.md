# BeehiveOfAI — Project Status

> This file is shared between Desktop and Laptop Claude Code instances via GitHub.
> Update it whenever significant progress is made.

## Last Updated: 2026-03-22

## Current Phase: Phase 5 — Desktop ↔ Laptop Testing

### Network Info
- **Desktop IP (LAN):** 10.0.0.4
- **Website URL (from laptop):** http://10.0.0.4:5000
- **Website URL (from desktop):** http://localhost:5000

### What's Done
- [x] Phase 0-4: All complete (tools, skeleton, demo, website, REST API)
- [x] Laptop setup: Python 3.12.11, Node.js v24.14.0, Ollama 0.18.2, Claude Code, all repos cloned
- [x] Both machines on same LAN (router)
- [x] Phase 5 plan created by Opus 4.6

### What's In Progress
- [ ] Bind Flask to 0.0.0.0 (so laptop can reach website)
- [ ] Add Worker API endpoints (register, poll subtasks, claim subtasks)
- [ ] Update HoneycombOfAI worker_bee.py for API-driven workflow
- [ ] Update HoneycombOfAI queen_bee.py for multi-machine orchestration
- [ ] Update config.yaml for LAN setup
- [ ] End-to-end test: Desktop (Queen) + Laptop (Worker) processing a job together

### Machine Roles for Testing
- **Desktop (10.0.0.4):** Runs website (Flask) + Queen Bee mode
- **Laptop:** Runs Worker Bee mode, connects to desktop

### Test Credentials (from seed_data.py)
- Worker: worker1@test.com / test123
- Queen: queen1@test.com / test123
- Beekeeper: company1@test.com / test123

## Phase 5 Coding Plan

### BeehiveOfAI (Website) Changes:
1. `app.py` — Change `app.run()` to bind to `0.0.0.0:5000`
2. `app.py` — Add `POST /api/worker/register` — Worker announces itself
3. `app.py` — Add `GET /api/hive/<id>/subtasks/available` — Worker polls for work
4. `app.py` — Add `PUT /api/subtask/<id>/claim` — Worker claims a subtask
5. `models.py` — (optional) Track worker online status

### HoneycombOfAI (Desktop Client) Changes:
6. `api_client.py` — Add worker methods: poll_subtasks, claim_subtask, submit_result
7. `worker_bee.py` — Rewrite for API-driven loop (poll → claim → process → submit)
8. `queen_bee.py` — Update to create subtasks via API, wait for workers
9. `config.yaml` — Add LAN IP config, per-machine settings
10. `honeycomb.py` — Update for new API-driven workflow
