[Build — new module, Phase 2 of 8]

# TBE — Phase 2: Discovery Engine

## Goal

Find candidates worth evaluating at all, fresh, on every Trading Cycle run — no maintained watchlist, no fixed universe. A ticker becomes eligible because something quantifiable happened to it since the last check. This is the *only* entry point for a candidate into the pipeline; nothing downstream may originate a candidate on its own. 100% deterministic, no AI involvement.

This is Phase 2 of an 8-phase build, same repo as Phases 0-1. Use the shared data-source client module and audit-logging utility from Phase 0. Output feeds directly into Phase 1's Hard-Gate Engine — call it immediately for every raw candidate this phase produces, before anything else touches the candidate.

## Trigger Types (either one qualifies a ticker; both produce a required direction)

### 1. Earnings Surprise (PEAD)
- **Data source waterfall:** Finnhub `/stock/earnings` (provides surprise % directly) → yfinance (fallback; compute surprise manually from actual EPS vs. consensus). SEC EDGAR is not part of this waterfall — it has no consensus-estimate data. Alpha Vantage is excluded here too.
- **Window:** any earnings report published since the prior trading day's market close through the current run.
- **Threshold:** `|actual EPS - consensus EPS| / |consensus EPS| ≥ 5%`. **Edge case:** if `|consensus EPS| < $0.01`, use an absolute-dollar fallback instead: `|actual EPS - consensus EPS| ≥ $0.05`.
- **Direction:** beat → `LONG`, miss → `SHORT`. Directly from the sign of the surprise — no separate confirmation needed.
- **Do not build:** revenue-surprise triggers, or any standardized/statistically-normalized surprise measure (SUE) requiring a trailing standard-deviation window — that's a calibration-against-history technique, out of scope for v1.

### 2. Material Filing (8-K)
- **Data source:** SEC EDGAR only, no fallback.
- **Window:** 8-K filings submitted since the prior trading day's market close through the current run.
- **Qualifying items:** 1.01, 2.01, 2.05, 5.02, 8.01. (Not 2.02 — that's the earnings trigger's domain. Not 4.01 — that's a Hard-Gate disqualifier, not an opportunity signal, and must never be treated as a trigger here.)
- **Direction — requires a price/volume confirmation, since a filing has no inherent sign:** within 1 trading day of the filing, the stock must move ≥3% (close-to-close or intraday) on volume ≥1.5x its trailing 20-day average. If both conditions hold, it's a valid trigger and direction follows the move (up → `LONG`, down → `SHORT`). If not, the filing is not a trigger at all — discard it as noise, do not create a candidate. Never use AI or any qualitative judgment to infer direction here — it is always this deterministic confirmation or nothing.

## Output

For every ticker producing a valid trigger, write a raw `candidates` document (Phase 0 schema) with: ticker, `trigger_type`, `direction`, `trigger_details` (surprise %/dollar amount + report date, OR qualifying item number(s) + filing date + the price/volume figures that confirmed it), `discovery_timestamp`, `trading_cycle_run_id`. Immediately pass this record into Phase 1's Hard-Gate Engine.

## Same-Day Handling

A ticker that already has a `candidates` record for the current calendar day from the *same* trigger type is not re-discovered in a later cycle that day. A *new, different* trigger type on the same ticker the same day (e.g. an 8-K after an earlier earnings trigger) is a distinct event and should be evaluated separately.

## Boundaries for v1 (explicitly out of scope)

- No gating, scoring, or AI involvement — this subsystem only finds candidates and assigns direction.
- No fixed universe or watchlist of any kind, ever.
- No revenue-surprise trigger, no SUE calculation.
- No AI-inferred direction for filings — always the deterministic price/volume confirmation, or no trigger at all.

## Definition of Done

1. Given a mocked earnings report with a 6% EPS beat against a normal (non-near-zero) consensus, a `LONG` candidate is created with the correct surprise % recorded.
2. Given a mocked earnings report with `|consensus EPS| < $0.01` and an actual-vs-consensus gap of $0.06, the dollar-fallback threshold fires correctly and produces a candidate (confirm the percentage-based path is *not* used here).
3. Given a mocked 8-K with Item 8.01 and a same-day +4% move on 2x average volume, a `LONG` candidate is created with the price/volume figures recorded in `trigger_details`.
4. Given the same mocked 8-K but with only a 1% move (confirmation threshold not met), confirm **no** candidate is created.
5. Given a mocked 8-K with Item 4.01, confirm it is never treated as a trigger under any circumstance.
6. Run discovery twice for the same ticker/trigger-type on the same calendar day and confirm the second run does not produce a duplicate candidate.
