# TBE Architecture
### Automated Investor Bot — System Architecture Specification
**Version 1.0 — July 2026**

This document defines *how TBE's pieces fit together* — not the build sequence (Roadmap) and not the line-by-line behavior of each piece (Subsystem Specs, next). Every decision here follows directly from the Constitution, the Deep Research report, the Roadmap's phase boundaries, and the locked deployment answers below.

## 1. Deployment Model

**Principle: the pipeline is trigger-agnostic. Where it runs and when it runs are configuration, not architecture.**

TBE runs today on GitHub Actions (free tier) and is designed to run unchanged on a VPS once budget allows. Both are legitimate homes for the same code — GitHub Actions' scheduling imprecision (an hour or more of drift) doesn't matter here, because TBE's 2–20 day swing horizon isn't sensitive to whether a job fires at 9:35 or 11:15. This would be disqualifying for an intraday system; it isn't one for TBE.

What *is* disqualifying is any dependency on local disk surviving between runs — GitHub Actions runners are ephemeral and wipe their filesystem after every job. So the rule is structural, not a preference:

> **All state lives in an external, network-reachable store. No pipeline code reads or writes anything to local disk that needs to exist on the next invocation.**

This is what makes "GitHub Actions now, VPS later, zero code changes" literally true rather than aspirational. The only thing that changes when TBE moves to a VPS is the trigger mechanism (`cron` instead of a GitHub Actions schedule) and where secrets are read from (environment file instead of GitHub Secrets) — the pipeline code itself is identical.

**A second, related principle follows from this: GitHub Actions' schedule is a best-effort trigger, not a clock.** GitHub's own documentation states that scheduled workflows can be delayed during high load, and queued runs can be dropped outright if load is high enough. This is not a rare edge case — it is documented, expected behavior. Every job in this architecture must therefore be self-contained and idempotent: a run does not assume anything about when the previous run happened, does not depend on a specific run having occurred at a specific time, and produces the same correct outcome whether it fires on schedule, 90 minutes late, or after a prior run was silently dropped. This is why the pipeline is structured as one recurring job rather than several differently-timed ones (see Section 3) — a late or dropped run of a single, repeating job just means a check happened later than ideal; a late or dropped run in a system of multiple distinct scheduled jobs can mean two jobs collide or a step is silently skipped, which is a documented failure mode this architecture is designed to avoid.

## 2. Data Layer

**Store: MongoDB Atlas, free tier.** Reachable via URI from anywhere — GitHub Actions runner, VPS, or a laptop — which is exactly the portability the deployment model requires.

Collections, by responsibility (not final schema — that's the DB Spec):

- **candidates** — output of the Discovery job: ticker, trigger type, trigger timestamp, gate results with pass/fail reasons.
- **evaluations** — AI Reasoning Layer output for gate-surviving candidates: structured qualitative assessment, schema-validated, tied to the candidate that produced it.
- **trades** — open and closed positions: entry/exit conditions, size, stop/target levels, full reasoning trace back to the candidate and evaluation that justified the entry.
- **portfolio_state** — current aggregate exposure: sector concentration, correlation snapshot, running drawdown, regime state (risk-on/risk-off).
- **stats_aggregates** — batch records from the Learning job (sum/count-style mergeable fields), not raw trade history — this is what lets performance stats scale without unbounded storage growth.
- **audit_log** — every decision the system makes, including rejections and abstentions, with its reasoning. This is the explainability record, and it's append-only.

## 3. Scheduler / Trigger Design

**Revised from v1.0: the daily chain and Monitor are merged into a single, self-contained Trading Cycle job, run repeatedly through market hours, rather than split into separately-timed jobs.** The original design assumed reliable, precisely-timed triggers; it does not survive contact with GitHub Actions' documented best-effort scheduling (see Section 1). Splitting Discovery, AI-score, Execute, and Monitor into distinct scheduled jobs created exactly the failure mode GitHub warns about: a delayed run can collide with or crowd out the next scheduled job, silently dropping work. A single repeating job that always does the full check sidesteps this — a late or occasionally dropped run degrades gracefully (the next cycle catches up) instead of corrupting the day's pipeline state.

There are now two scheduled jobs instead of five:

| Job | Roadmap phases | Cadence | Internal order | Reads | Writes |
|---|---|---|---|---|---|
| **Trading Cycle** | 1–2, 3–4, 5, 6 combined | ~5x during market hours (e.g. 9:45, 11:15, 12:45, 2:15, 3:45) | Monitor → Discover → AI-score → Execute, every run, in that order | Market/filings data, `trades`, `candidates`, `portfolio_state` | `trades`, `candidates`, `evaluations`, `portfolio_state`, `audit_log` |
| **Learn** | 7 (observational learning) | Weekly | — | `trades` (newly closed) | `stats_aggregates` |

**Why this order within each cycle:** Monitor runs first, before Discovery, so protecting existing open positions is never delayed by time spent looking for new opportunities — a direct expression of the capital-preservation-first objective, not just an implementation convenience.

**Why one job instead of four for the daily chain:** Discovery is trigger-first, not universe-first (see Section 4) — it re-derives its candidate pool fresh every cycle from that day's earnings/filings events, so there's no state to carry between cycles that would justify splitting these steps apart. A candidate found at 11:15 is evaluated and, if justified, executed within that same cycle — it does not wait for a separate next-day Discovery run, which directly fixes the missed-same-day-opportunity problem the original once-daily design had.

**Efficiency note carried to the spec layer:** because Discovery now runs multiple times a day, the AI-score step must not re-evaluate a candidate it already scored earlier the same day unless something material changed. This is a Discovery/AI-score subsystem spec detail, not an architectural one, but it exists specifically to keep Gemini free-tier usage proportional to genuinely new information, not to cycle count.

**Fault isolation within a single Trading Cycle run:** even though all four steps now share one trigger, they remain independently fault-tolerant *within* that run — a failure in AI-score (e.g. an API timeout) must not prevent Monitor or Discovery from completing in that same cycle. This is enforced at the code level (each step wrapped independently), not by splitting the schedule.

## 4. Subsystem Map

Each subsystem corresponds to a Roadmap phase; this section states its boundaries, not its internals.

- **Hard-Gate Engine** (Phase 1) — deterministic only. Beneish M-Score, Altman Z-Score, auditor/filing checks, liquidity minimums, sanctions screening. Fixed formulas, no calibration, no historical-window dependency.
- **Discovery Engine** (Phase 2) — deterministic only. Trigger-first, not universe-first: it re-derives its candidate pool fresh on every Trading Cycle run from that day's events (earnings surprises, material filings), rather than maintaining or rotating a fixed watchlist. A ticker becomes eligible because something happened to it, not because it was pre-selected. Produces the *only* entry point for a candidate into the pipeline — nothing downstream can originate a candidate on its own. Scope of the scan (e.g. minimum market cap, exchange listing requirements) is a Discovery subsystem spec detail; the liquidity gate in the Hard-Gate Engine is the intended filter for tradability, not a second parallel filter in Discovery.
- **AI Reasoning Layer** (Phase 3) — the sole AI-touching subsystem. Runs only on candidates that already cleared the Hard-Gate Engine and Discovery Engine. Output is schema-constrained JSON, never free text consumed downstream. Uses Gemini's free tier for its API calls.
- **Scoring & Regime Filter** (Phase 4) — deterministic only. Combines deterministic and AI-qualitative evidence with equal weighting, applies the simple regime signal (volatility index + trend filter, not the deferred statistical machinery), and produces a confidence score or an explicit abstention.
- **Execution Engine** (Phase 5) — deterministic only. ATR-based sizing, Chandelier Exit stops, correlation and sector checks, kill-switch logic. No subsystem outside this one is permitted to write to a trade's stop-loss level.
- **Portfolio Monitor** (Phase 6) — deterministic only. Aggregate exposure tracking and the drawdown circuit breaker. Operates across the whole book, not per-trade.
- **Learning Aggregator** (Phase 7) — deterministic only. Converts closed trades into mergeable batch statistics. Informational — it does not modify any other subsystem's behavior automatically in v1.

## 5. The AI / Deterministic Boundary, Enforced Structurally

The Constitution states this as a philosophy; the architecture makes it a hard boundary, not a convention:

- The AI Reasoning Layer is invoked **only** by the AI-score job, **only** on candidates already present in `candidates` with passing gate results. There is no code path that lets AI evaluate a candidate that hasn't cleared deterministic gates first — this is the "external trigger required before AI reasoning engages" rule from the research report, implemented as a call-order constraint, not a guideline.
- AI output is schema-validated JSON. Anything that fails schema validation is treated as a failed evaluation (abstain), never passed through as-is.
- The Execution Engine and Portfolio Monitor have no dependency on, or callable interface to, the AI Reasoning Layer. Once a trade is live, nothing AI-generated can alter its stop-loss, size, or exit condition — this directly implements the "AI never touches a number that controls capital" rule and the never-list's "stop-loss never loosens live" rule.

## 6. Secrets & Configuration

A single configuration interface (environment variables) is read identically regardless of trigger source: `MONGODB_URI`, the AI API key, and market-data API keys. On GitHub Actions these are populated from GitHub Secrets; on a VPS, from an environment file. The pipeline code reads `os.environ` either way and has no branch logic for "which platform am I on" — if that branch ever needs to exist, it's a sign the portability principle has been violated somewhere.

## 7. Audit & Explainability Layer

Every job writes to `audit_log`, including the Discovery job's rejections, the AI-score job's abstentions, and the Execution Engine's every sizing decision. This is append-only and is what makes the Constitution's explainability requirement ("every investment decision leaves an auditable record") true in practice rather than in principle — nothing in the pipeline is permitted to make a silent decision.

## 8. Never-List Enforcement Map

Each of the six locked architectural laws has a specific structural home — none of them are left as "policy" for a subsystem to remember to honor:

| Rule | Enforced in |
|---|---|
| Kill switch required | Execution Engine + Portfolio Monitor, checked before every new position and on every Monitor run |
| Position never exceeds liquidity capacity | Hard-Gate Engine (liquidity minimums) + Execution Engine (sizing) |
| Stop-loss never loosens live | Execution Engine only — no other subsystem has write access to an open trade's stop field |
| Never average down | Execution Engine — a new entry on an existing symbol is treated as a new, independently gated candidate, never a size-up on a loser |
| Never assume historical correlation holds in a crisis | Portfolio Monitor — correlation caps are voided (treated as untrusted) whenever the regime filter flags risk-off |
| Never trade live capital to explore/learn | Structural, by scope — this entire architecture is paper-trading only; there is no code path to a real broker anywhere in it |

## 9. Explicitly Out of Scope (Architectural, Not Just Roadmap)

These have no subsystem, no collection, and no job in this architecture. They are not partially built and paused — they don't exist yet:

- Absorption Ratio / Turbulence Index regime detection.
- Conformal Risk Control / VaR calibration.
- Any self-calibration engine.
- Real broker integration or live capital movement of any kind.
- Any AI-originated candidate that bypasses the Discovery Engine's external-trigger requirement.

---

*This architecture is the reference point for the Subsystem Specs that follow. Any spec that requires violating a boundary defined here (AI touching a number, a subsystem reading local disk state, a candidate originating outside Discovery) is wrong, not this document.*