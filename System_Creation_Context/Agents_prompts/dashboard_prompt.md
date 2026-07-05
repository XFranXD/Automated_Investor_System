[Build — new system, Dashboard — build after Phases 0-7 are complete and exercised]

# TBE — Dashboard (Read-Only Web Interface)

## Goal

Build a static, read-only dashboard for viewing TBE's trades and system state — the human-facing counterpart to the six MongoDB collections, presented cleanly instead of as raw documents. Two pages: **Trades** and **System**. This is purely a reporting layer over data that already exists by the time this is built; it has no influence on any trading decision.

**Build this only after Phases 0-7 already exist and have real data flowing through them** — this is not a dependency for any other phase, and there's little to render correctly against until trades and audit records actually exist.

## Context & Constraints

- **Fully static site: HTML, CSS, JavaScript only. No running server, no backend framework.** A Python script queries MongoDB Atlas (same `MONGODB_URI` used everywhere else in this project), renders the two HTML pages, and the rendered output is published via **GitHub Pages**. This is the same pattern already used successfully in a prior project (a `dashboard_builder.py`-style generator producing static HTML from Python).
- **All database access happens server-side, only, during the scheduled build step — never from the browser.** The MongoDB query must happen inside the Python generator script, which runs inside the GitHub Actions workflow with access to the real `MONGODB_URI` secret. The published site is plain, already-rendered HTML/CSS/JS containing no database connection string, no API key, and no live query of any kind — a visitor's browser never talks to MongoDB directly, under any circumstance. This is a hard security requirement, not a style preference: a static site's client-side JavaScript is fully visible to anyone viewing the page source, so any credential embedded there is effectively public.
- **The dashboard's GitHub Actions workflow reads `MONGODB_URI` from GitHub Secrets**, the same mechanism already used by the Trading Cycle and Learn workflows (Phase 0) — not a new or different secret, just the same one wired into this new workflow's environment.
- **This is not the git-commit-state anti-pattern from Phase 0.** Committing the *rendered output* (disposable, fully regenerable from MongoDB at any time) to publish via GitHub Pages is fine and is the intended mechanism here. What Phase 0 ruled out was using git commits as the operational *source of truth* for live trading state — that rule is unaffected; MongoDB Atlas remains the only source of truth, and this dashboard only ever reads from it.
- **Strictly read-only, with no exceptions.** There must be no button, form, API endpoint, or code path anywhere in this dashboard — now or added later — that writes to any TBE collection. No resetting the kill switch from the UI, no triggering a trade, no editing a record. If a future need for a write action ever comes up, that's a deliberate, separate decision — not something to build in "for convenience" here.
- **Deployment:** a new, independent GitHub Actions workflow (e.g. "Dashboard Build") that runs the generator script and publishes to GitHub Pages. **Trigger it automatically via `workflow_run`, chained to fire immediately after both the Trading Cycle workflow and the Learn workflow (Phase 0) complete** — not on a fixed time-based schedule. This keeps the dashboard exactly as fresh as the underlying data actually is (updated after every Trading Cycle run during market hours, and after the weekly Learn run), with no manual action ever required and no wasted rebuilds when nothing has changed.
- **Design freedom:** the specific data listed below for each page is mandatory and complete — nothing on this list is optional. Everything about *how* it's presented — layout, color palette, typography, chart style, exact page structure within each of the two pages — is entirely up to you. Use your own design judgment; this does not need to resemble any specific prior project's visual style.

## Page 1: Trades

**Summary header** (all-time, computed across all trades):
- Total realized PnL, overall win rate, total closed trade count, current open position count.

**Calendar view** (concept only — a from-scratch implementation, not a reproduction of any prior version):
- Month/week grid; each day cell shows that day's total realized PnL (visually distinguished win/loss days, e.g. by color).
- Selecting a day shows the list of trades that closed that day.

**Trade list:**
- Every trade (open and closed): ticker, direction, entry date/time, exit date/time (or "OPEN"), entry price, exit price (if closed), share count, realized PnL (closed) or current unrealized PnL (open, computed from live price), status.

**Trade detail** (per trade, all fields required):
- Core: ticker, direction, trigger_type, entry_price, exit_price, share_count, entry_timestamp, exit_timestamp, status, exit_reason (`STOP`/`TAKE_PROFIT`), realized_pnl.
- Risk/sizing: initial_stop, current_stop (if open), take_profit, confidence_tier, combined_score, risk_pct_used.
- Reasoning chain (this is the "specific to this trade" system data): the linked AI evaluation's conviction, risk_flags, and rationale; the trigger_details that qualified this candidate (surprise % or filing item + price/volume confirmation); which gates it passed.

**Market indices** — current VIX level and current S&P 500 level relative to its 50-day SMA, shown for context alongside trade performance.

## Page 2: System

**Kill switch panel:**
- Current status (active/inactive). If active: when it triggered, the drawdown % at the time, and which positions contributed most.

**Equity curve** (concept only — a from-scratch implementation, not a reproduction of any prior version):
- Portfolio equity over time, with the high-water mark and current drawdown % clearly indicated (e.g. shaded region between equity and high-water mark).

**Regime panel:**
- Current state (`RISK_ON`/`RISK_OFF`) and *why*: current VIX value against the 30 threshold, current S&P 500 position against its 50-day SMA — show the actual values that produced the state, not just the resulting label.
- Current correlation cap in effect (0.6 or 0.4) and current sector exposure snapshot.

**Rejection / abstain breakdown:**
- Counts grouped by reason code (hard-gate rejection codes and scoring abstain codes) over a selectable recent period (e.g. today / this week / this month). This is what answers "why isn't the system trading" at a glance — every distinct reason code from the Hard-Gate Engine and Scoring & Regime Filter specs should be representable here, not just a generic "no trades" count.

**Learning Aggregator stats:**
- Pulled directly from `stats_aggregates`. For each of the five buckets (overall, by direction, by trigger type, by confidence tier, by regime): trade count, win rate, average PnL/expectancy, profit factor, max win, max loss. Present all five buckets — this is the data the Decision Log's deferred parameters (e.g. the LIMITED-info penalty, the combined-score bucket cutoffs) depend on eventually being reviewed against.

## Boundaries (explicitly out of scope)

- No write capability of any kind, anywhere, ever (see Constraints above) — this is the one non-negotiable rule for this entire build.
- No live/streaming updates — a periodically-regenerated static site is sufficient; no WebSocket, no polling backend.
- No user authentication/login system — if the GitHub Pages URL needs to be private, that's a repo-visibility setting, not something to build into the site itself.
- No modification to any other phase's code — this only reads from collections Phases 0-7 already populate.

## Definition of Done

1. Given a MongoDB instance with a mix of open, closed-win, and closed-loss trades across several days, the Trades page's calendar correctly aggregates each day's realized PnL, and the summary header's total PnL and win rate match a manual calculation from the same data.
2. Selecting an individual trade shows every field listed under Trade Detail above, including its linked AI rationale and the gates it passed — confirm none of these are silently omitted for a trade that has them available.
3. Given a mocked `kill_switch_active = true` state with a specific `triggered_at` and drawdown %, the System page displays both correctly, and the equity curve visually reflects the current drawdown relative to the high-water mark.
4. Given a mocked `RISK_OFF` state driven by `VIX = 34`, confirm the System page shows the actual VIX value and the 30 threshold it crossed — not just the word "RISK_OFF."
5. Given mocked `stats_aggregates` documents for all five dimension buckets, confirm all five are rendered on the System page with correctly derived win rate/expectancy/profit factor.
6. Confirm — by code review, not just by testing the UI — that there is no code path anywhere in this dashboard's codebase that issues a write, update, or delete against any MongoDB collection.
7. Confirm — by inspecting the published site's actual HTML/CSS/JS output, not just the source repo — that no database connection string, API key, or live query exists anywhere in what gets shipped to the browser. Everything the visitor receives must be pre-rendered, static content.
8. Confirm the generated output is fully static (opens correctly with no backend running) and the dedicated GitHub Actions workflow successfully publishes it to GitHub Pages end to end.
