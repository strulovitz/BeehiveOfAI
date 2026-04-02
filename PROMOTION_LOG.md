# BeehiveOfAI — Promotion Log

> Track every post, what happened, and whether it was shadow-banned or removed.
> ALWAYS update this file after posting. Check with Firefox Private Mode to verify.

## YouTube Videos
- **Video 1 (Private Mode):** https://www.youtube.com/watch?v=o8R58VuJFx8
- **Video 2 (Public Mode):** https://www.youtube.com/watch?v=PTnAqZCAClw

## Reddit Posts

| Date | Subreddit | Post Title | Status | Verified (Private Mode)? |
|------|-----------|------------|--------|--------------------------|
| 2026-04-02 | r/LocalLLaMA | (not posted) | BLOCKED by Rule 4 — requires post history before self-promotion | N/A |

## Reddit — Rule 4 Problem (2026-04-02)

r/LocalLLaMA blocks self-promotion if you don't have post history on the sub. The body field turns red immediately when pasting promotional content. To post there, you need to first leave 5-10 genuine helpful comments over a few days (NOT mentioning BeehiveOfAI), then try again.

**This likely applies to most tech subreddits.** Before trying any new subreddit, check their rules for self-promotion requirements.

## Prepared Post (ready to use when we have enough history)

**Title:**
```
I made a 2-minute animated video explaining why multi-agent frameworks aren't actually distributed AI (and what is)
```

**Body:**
```
I've been working on this for a while and finally have something to show.

The problem: every "distributed AI" framework I tried turned out to be either (a) multiple agents sharing one computer (CrewAI, LangGraph, Swarms) or (b) splitting one model across machines with pipeline parallelism (Petals, Exo). Neither actually distributes the WORK.

What I built: each machine gets its own complete local LLM and its own piece of the project, planned in advance. They all run in parallel. No shared brain, no pipeline dependencies, no waiting.

Two modes:
- **Private Mode** — for organizations that can't send data outside. Combine your office computers into one powerful AI. Your data never leaves the building.
- **Public Mode** — for individuals. Your idle computer picks up tasks from a marketplace and earns money while you sleep. 65% goes to workers, 30% to managers, 5% to the platform.

I made two short animated explainer videos (2 minutes each):
- Private Mode (for organizations): https://www.youtube.com/watch?v=o8R58VuJFx8
- Public Mode (for everyone): https://www.youtube.com/watch?v=PTnAqZCAClw

Open source: https://github.com/strulovitz

Happy to answer any questions about the architecture or how the parallel task distribution works.
```

## Other Platforms

| Date | Platform | What Was Posted | Status |
|------|----------|----------------|--------|
| 2026-04-02 | GitHub profile | Video thumbnails on github.com/strulovitz | DONE |
| 2026-04-02 | GitHub BeehiveOfAI | Video thumbnails + "17 min" setup in README | DONE |
| 2026-04-02 | YouTube | Video 1: Actual Distributed Parallel AI — Private Mode for Organizations | LIVE |
| 2026-04-02 | YouTube | Video 2: Actual Distributed Parallel AI — Public Mode for Everyone | LIVE |

## Known Blocked/Shadow-Banned Subreddits

(Add any subreddit that silently removes posts here so we never waste time trying again)

| Subreddit | Date Discovered | What Happened |
|-----------|----------------|---------------|
| r/LocalLLaMA | 2026-04-02 | Rule 4: requires post history before self-promotion. Body turns red, Post button disabled. Need 5-10 helpful comments first. |

## Platforms Still To Try

- **LinkedIn** — write a post about data privacy + AI, embed video. Good for Private Mode audience.
- **Hacker News** — "Show HN: BeehiveOfAI — Actual Distributed Parallel AI". Post weekday mornings US time (14:00-16:00 Israel time).
- **Product Hunt** — launch as a free product.
- **Dev.to / Medium** — write article "Why Multi-Agent Frameworks Don't Actually Distribute AI"
- **Twitter/X** — post 30-second teaser clip, tag competitor accounts.
- **Discord** — AI community #showcase channels.
