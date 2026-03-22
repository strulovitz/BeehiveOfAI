# Phase 5 — Detailed Coding Plan

> This file contains the exact code changes needed for Phase 5.
> Sonnet 4.6 should follow this plan step by step.

## Desktop LAN IP: 10.0.0.4

---

## PART B: BeehiveOfAI (Website) Changes

### B1. Bind Flask to 0.0.0.0

In `app.py`, change the last line from:
```python
app.run(debug=True)
```
to:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

This allows the laptop to reach the website over LAN.

### B2. Add Worker API Endpoints

Add these new API endpoints to `app.py` (after the existing API routes):

#### Endpoint: GET /api/hive/<id>/subtasks/available
- Auth: Worker must be a member of the hive
- Returns: List of subtasks with status 'pending' (not yet claimed by any worker)
- Response: `[{id, subtask_text, job_id, status}]`

#### Endpoint: PUT /api/subtask/<id>/claim
- Auth: Worker must be a member of the subtask's hive
- Changes subtask status from 'pending' to 'assigned'
- Sets subtask worker_id to current user
- Response: `{status: "claimed", subtask_id, subtask_text}`
- If subtask is already claimed: return 409 Conflict

#### Endpoint: PUT /api/subtask/<id>/result (already exists!)
- Already supports Workers submitting results
- No changes needed

#### Endpoint: POST /api/worker/heartbeat
- Auth: Any authenticated worker
- Updates a last_seen timestamp (optional, nice to have)
- Response: `{status: "ok", server_time}`

---

## PART C: HoneycombOfAI (Desktop Client) Changes

### C1. Update api_client.py

Add these new methods to the `BeehiveAPIClient` class:

```python
def get_available_subtasks(self, hive_id):
    """Poll for available subtasks in a hive."""
    response = self._get(f'/api/hive/{hive_id}/subtasks/available')
    return response

def claim_subtask(self, subtask_id):
    """Claim a subtask for processing."""
    response = self._put(f'/api/subtask/{subtask_id}/claim')
    return response

def submit_subtask_result(self, subtask_id, result_text):
    """Submit result for a completed subtask."""
    response = self._put(f'/api/subtask/{subtask_id}/result', json={'result': result_text})
    return response
```

### C2. Rewrite worker_bee.py for API-Driven Loop

The worker should:
1. Login to the website API
2. Enter a polling loop:
   a. GET /api/hive/{hive_id}/subtasks/available
   b. If subtasks found: claim one, process it with Ollama, submit result
   c. If no subtasks: wait 5 seconds, try again
3. Display status using Rich console

```
WORKER LOOP:
┌─────────────────────────────────┐
│  Poll for subtasks              │
│  ↓                              │
│  Found one? → Claim it          │
│  ↓                              │
│  Process with Ollama            │
│  ↓                              │
│  Submit result via API          │
│  ↓                              │
│  Back to polling                │
└─────────────────────────────────┘
```

### C3. Update queen_bee.py for Multi-Machine Workflow

The queen's `process_from_website()` method should:
1. Poll for pending jobs (already works)
2. Claim job (already works)
3. Split task into subtasks using AI (already works)
4. Create subtasks via API (already works)
5. **NEW: Wait for workers to complete subtasks** (poll subtask statuses)
6. Once all subtasks complete, combine results
7. Submit final result via API (already works)

Key change: Instead of processing subtasks locally, the Queen creates them via API and WAITS for Workers to pick them up and complete them.

### C4. Update config.yaml

```yaml
# Mode: worker, queen, or beekeeper
mode: worker  # Change per machine

# Server connection
server:
  url: http://10.0.0.4:5000  # Desktop's LAN IP (change to localhost if on desktop)

# Ollama settings
ollama:
  model: llama3.2:3b
  temperature: 0.7

# Worker settings
worker:
  id: worker-laptop-001  # Unique per machine
  hive_id: 1  # Which hive to join
  poll_interval: 5  # Seconds between polls

# Queen settings (only used in queen mode)
queen:
  email: queen1@test.com
  password: test123
  hive_id: 1
```

### C5. Update honeycomb.py

Update the main launcher to:
1. Load config
2. Based on mode, start the appropriate role
3. Worker mode: run the polling loop
4. Queen mode: run the job-watching loop
5. Handle Ctrl+C gracefully
