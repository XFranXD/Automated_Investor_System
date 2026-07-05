[Build — new system, Phase 0 of 8]

# TBE — Phase 0: Foundations & Infrastructure

## Goal

Build the skeleton for TBE (Automated Investor Bot), an autonomous investment decision system. This phase produces zero trading logic — it produces the plumbing every later phase will build on: database schema, a paper-trading harness, an audit-logging utility, shared market-data client modules, and the deployment skeleton. When this phase is done, a ticker can be pulled from each data source, a simulated trade can be opened and closed on paper, and the full lifecycle is queryable with an audit trail — nothing more.

This is Phase 0 of an 8-phase build (Phases 1-7 follow, one subsystem each, in the same repo). Structure this code so later phases import and extend it — do not build anything that assumes it's the final structure of the project, but do build it as production-shaped, not a throwaway prototype.

## Context & Constraints

- **Language:** Python (required — later phases depend on the `yfinance` library, which is Python-only).
- **Database:** MongoDB Atlas, free tier. Connection string read from environment variable `MONGODB_URI`. No local disk state may persist anything needed by a future run — assume the filesystem is wiped between every invocation (this will run on GitHub Actions' ephemeral runners).
- **Deployment target:** GitHub Actions today, a VPS later, with zero code changes required to migrate. Concretely: no branching logic anywhere based on "which platform am I on" — secrets are always read from `os.environ`, regardless of source (GitHub Secrets today, an env file later).
- **Scheduling reality:** GitHub Actions' cron schedule is documented best-effort — it can be delayed 40-90+ minutes or dropped entirely under load. Every job this phase scaffolds must be idempotent and self-contained: safe to run late, safe to run twice, safe to have a prior run silently not have happened.
- **No paid APIs, no Alpha Vantage anywhere** (its free tier is 25 requests/day, confirmed too low to be a working fallback for anything in this system).
- **Dependency installation is normal and does not violate portability.** The GitHub Actions workflow installs Python dependencies fresh (`pip install -r requirements.txt`) at the start of every run, inside the disposable runner container. This is expected and lightweight — it has nothing to do with the local-disk-state prohibition below and does not need to be avoided or worked around.
- **No git-commit-state pattern, anywhere, under any circumstance.** Some GitHub Actions projects without a database work around ephemeral storage by having the workflow commit a JSON/data file back to the repo at the end of each run. **Do not use this pattern.** MongoDB Atlas is the single source of truth for all state, specifically so this workaround is never needed — a git-commit-based store would not be atomic across the ~5x/day Trading Cycle cadence (GitHub Actions' scheduling is documented best-effort and can run late or overlap), would risk conflicting commits between runs, and would require the workflow to hold write access to the repository for no benefit over what MongoDB Atlas already provides for free.
- **This applies identically on a VPS**, even though a VPS's disk does persist between runs and could technically get away with local files. All state goes through MongoDB Atlas on both platforms, on purpose, so the exact same code runs unmodified on either — VPS-only local-disk logic would require an actual code change to migrate, which defeats the "zero code changes" portability goal this architecture is built around.
- **No real secret value may ever be committed to the repository, in any form.** If a local `.env` file (or similar) is created purely for local development convenience, it must be added to `.gitignore` before it's ever populated with a real value — never committed, not even once, not even in an early commit later amended. If a template/example file is useful (e.g. `.env.example`), it must contain only placeholder text, never a real key or URI. On GitHub Actions, secrets are injected by the platform via GitHub Secrets; on a VPS, an environment file lives only on that machine's disk and is never part of any git repository at all.

## Assumption (stated explicitly — adjust only if it conflicts with something below)

A shared data-source client module is being introduced here, in Phase 0, even though no subsystem spec explicitly says to centralize it. Four later phases (Hard-Gate Engine, Discovery Engine, AI Reasoning Layer, Scoring & Regime Filter) each independently rely on the same SEC EDGAR / Finnhub / yfinance waterfall-fallback pattern for fetching fundamentals, filings, and price/volume data. Building one shared, well-tested client here — instead of four separate reimplementations — is a reasonable engineering call within the boundaries already set by the specs, not a new design decision. Each later phase's prompt will reference this module directly instead of re-specifying fallback logic.

## What to Build

### 1. Project skeleton
Standard Python project layout. Load all required environment variables at startup and fail fast with a clear error if any required variable (`MONGODB_URI`, `FINNHUB_API_KEY`, `SEC_EDGAR_USER_AGENT`) is missing. Do not hardcode or default any secret.

### 2. MongoDB Atlas connection + schema
Create the following six collections. These field lists are the union of what all seven later subsystem specs will need to read or write — build the schema now so no later phase needs to alter it, only populate it.

- **`candidates`** — `ticker`, `trigger_type` (`EARNINGS_SURPRISE`|`MATERIAL_FILING`), `direction` (`LONG`|`SHORT`), `trigger_details` (object — surprise % or filing item + price/volume confirmation), `discovery_timestamp`, `trading_cycle_run_id`, `calendar_day` (for same-day dedup), `gate_result` (`PASSED`|`REJECTED`), `gate_reason_code`, `gate_data_sources_consulted`, `combined_score`, `trigger_strength_score`, `ai_conviction_score`, `information_sufficiency_modifier`, `regime_state_at_decision`, `final_outcome` (`PROCEED`|`ABSTAIN`), `abstain_reason_code`, `confidence_tier` (`STRONG`|`MODERATE`).
- **`evaluations`** — `candidate_id` (ref), `conviction`, `risk_flags` (array), `information_sufficiency`, `rationale`, `status` (`SUCCESS`|`ABSTAIN`), `abstain_reason_code`, `model_used`, `timestamp`.
- **`trades`** — `ticker`, `direction`, `entry_price`, `share_count`, `combined_score`, `risk_pct_used`, `initial_stop`, `current_stop`, `take_profit`, `confidence_tier`, `status` (`OPEN`|`CLOSED`), `entry_timestamp`, `exit_price`, `exit_timestamp`, `exit_reason` (`STOP`|`TAKE_PROFIT`), `realized_pnl`, `highest_high_since_entry`, `lowest_low_since_entry`, `reasoning_chain` (candidate_id, evaluation_id, scoring snapshot).
- **`portfolio_state`** — single current-state document: `portfolio_equity`, `high_water_mark`, `drawdown_pct`, `kill_switch_active` (bool), `kill_switch_triggered_at`, `sector_exposure` (map), `correlation_snapshot`, `regime_state` (`RISK_ON`|`RISK_OFF`), `correlation_cap_current`, `last_updated`.
- **`stats_aggregates`** — `dimension_type` (`overall`|`direction`|`trigger_type`|`confidence_tier`|`regime`), `dimension_value`, `tradeCount`, `wins`, `losses`, `sumPnL`, `sumPnLSquared`, `grossProfit`, `grossLoss`, `maxWin`, `maxLoss`, `last_processed_timestamp`.
- **`audit_log`** — append-only: `timestamp`, `subsystem`, `trading_cycle_run_id`, `ticker` (nullable), `action`, `decision`, `reasoning`, `data_sources_consulted` (nullable), `reason_code` (nullable).

### 3. Audit-logging utility
One function, e.g. `write_audit_log(subsystem, action, decision, reasoning, **kwargs)`, that every later phase calls for every decision it makes — including rejections, abstentions, and no-action outcomes. This is the single write path into `audit_log`; no phase should write to that collection any other way.

### 4. Shared data-source client module
Three client wrappers, each exposing a consistent interface (e.g. `get_fundamentals(ticker)`, `get_price_volume(ticker)`, `get_filings(ticker, item_types)`, `get_earnings(ticker)`, `get_news(ticker)` — implement only the methods a given source actually supports):

- **SEC EDGAR client** — XBRL company-facts API for fundamentals, full-text search / filing index for filings. No API key required, but SEC requires a real, identifying `User-Agent` header on every request (a contact name + email, e.g. `"Ale <email@example.com>"`) — read this from environment variable `SEC_EDGAR_USER_AGENT`, never hardcode it. SEC actively rate-limits or blocks requests with a missing or generic User-Agent, so this is a functional requirement, not a courtesy. Be a well-behaved client (reasonable request pacing) — SEC does not publish a generous free-tier number the way the others do, so don't hammer it.
- **Finnhub client** — free tier, 60 requests/minute. Requires an API key, read from environment variable `FINNHUB_API_KEY`. Financials-as-reported, earnings surprise endpoint, company-news endpoint, price/volume.
- **yfinance client** — no key required, last-resort fallback for fundamentals/price-volume/news.

Each wrapper method must implement waterfall fallback where multiple sources apply (later phases will specify the exact order per use case — e.g. EDGAR-first for fundamentals, Finnhub-first for earnings surprise data). If every source in a waterfall is exhausted, the method must return a clear "no data" signal (not raise an unhandled exception) so callers can log a `_NO_DATA`-style outcome rather than crash. Every fallback attempt (which source was tried, which succeeded or failed) must be logged via the audit utility from item 3, tagged `subsystem="data_client"`.

### 5. Paper-trading harness
- `open_paper_position(ticker, direction, share_count, entry_price, initial_stop, take_profit, ...)` — writes a new `trades` document with `status="OPEN"`.
- `close_paper_position(trade_id, exit_price, exit_reason)` — computes `realized_pnl` (accounting for direction — a short's PnL sign is inverted relative to a long's), updates the `trades` document to `status="CLOSED"`.
- No broker integration of any kind, anywhere, ever — this is a structural constraint of the entire project, not just this phase. There must be no code path in this harness that could plausibly be pointed at a real brokerage API later without a deliberate, separate rewrite.

### 6. Deployment skeleton
Two GitHub Actions workflow files:
- **Trading Cycle** — scheduled ~5x during market hours (e.g. 9:45, 11:15, 12:45, 2:15, 3:45 ET). Invokes a placeholder entrypoint script that currently only logs "Trading Cycle: not yet implemented" and exits cleanly.
- **Learn** — scheduled weekly. Same placeholder pattern.

Both read all secrets from GitHub Secrets via environment variables — no other configuration mechanism.

## Boundaries for v1 (explicitly out of scope for this phase)

- No gating, scoring, discovery, or AI logic of any kind — this phase is plumbing only.
- No fixed candidate universe or watchlist — data clients fetch per-ticker on demand; nothing pre-populates a list of tickers to track.
- No real broker integration, now or ever, per the constraint above.
- No Gemini/AI client setup — that belongs to a later phase, which is the only consumer of it.

## Definition of Done

1. Running the project connects to MongoDB Atlas using `MONGODB_URI` and confirms all six collections exist (creating them if absent).
2. A dummy document can be written to and read back from each of the six collections.
3. `open_paper_position(...)` followed by `close_paper_position(...)` on a made-up long and a made-up short both produce a correctly-signed `realized_pnl`, and each writes a corresponding `audit_log` entry.
4. For at least one data-client method with a real waterfall (e.g. fundamentals: EDGAR → Finnhub → yfinance), demonstrate the fallback path actually engages when the primary source is forced to fail (e.g. via a bad ticker or mocked failure), and confirm the fallback attempt is logged.
5. Both GitHub Actions workflow files are present, pass YAML validation, and can be manually triggered (`workflow_dispatch`) to confirm they run their placeholder script end-to-end without error.
