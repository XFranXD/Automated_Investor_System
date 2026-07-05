[Build — new module, Phase 1 of 8]

# TBE — Phase 1: Hard-Gate Engine

## Goal

Given a ticker, deterministically decide whether it's disqualified before any evidence-scoring or AI reasoning ever considers it. Six binary gates, evaluated in a fixed cheap-to-expensive order, short-circuiting on the first failure. No AI involvement anywhere in this phase.

This is Phase 1 of an 8-phase build, in the same repo as Phase 0. Use the MongoDB connection, the `candidates` collection schema, the audit-logging utility, and the shared data-source client module already built in Phase 0 — do not reimplement fallback/waterfall logic locally; extend the Phase 0 client module with any new methods this phase needs (e.g. OFAC list lookup) instead of writing a parallel client.

## Context & Constraints

- 100% deterministic — no calibration, no historical-window dependency, no AI calls.
- Data source waterfalls (extend the Phase 0 client module rather than duplicating it):
  - **Fundamentals** (Beneish/Altman inputs): SEC EDGAR XBRL company-facts → Finnhub financials-as-reported → yfinance.
  - **Filings** (auditor change, delinquent filing): SEC EDGAR only, no fallback — this is EDGAR's exclusive domain.
  - **Price/volume/market cap**: yfinance → Finnhub.
  - **Sanctions**: OFAC SDN list (free CSV/XML from U.S. Treasury) — single source, no waterfall. This is a new client method not yet built in Phase 0; add it there or as a sibling module, following the same pattern.
- Alpha Vantage is excluded from every waterfall in this phase, full stop.

## Gate Order (short-circuit on first failure — do not run remaining gates once one fails)

1. **OFAC / Sanctions** — match company name/known entities against the current SDN list. Fail → reason code `GATE_SANCTIONS`.
2. **Liquidity minimums** — both must pass: 20-day trailing ADV ≥ $5,000,000 (fail → `GATE_LIQUIDITY_ADV`); share price ≥ $5.00 (fail → `GATE_LIQUIDITY_PRICE`).
3. **Delinquent filing check** — Form NT 10-K/NT 10-Q within trailing 6 months with no subsequent 10-K/10-Q filed since → `GATE_DELINQUENT_FILING`.
4. **Auditor change / adverse opinion** — either sub-check fails the gate: 8-K Item 4.01 within trailing 12 months → `GATE_AUDITOR_CHANGE`; OR EDGAR full-text search of the most recent 10-K's auditor report section matches any of these fixed phrases: "substantial doubt", "going concern", "adverse opinion", "did not express an opinion" → `GATE_ADVERSE_OPINION`. This keyword list is deliberately blunt and will produce false positives by design — do not attempt to make it smarter with NLP.
5. **Beneish M-Score** — standard 8-variable formula: `M = -4.84 + 0.92(DSRI) + 0.528(GMI) + 0.404(AQI) + 0.892(SGI) + 0.115(DEPI) - 0.172(SGAI) + 4.679(TATA) - 0.327(LVGI)`, computed from two fiscal years of financials. Threshold: `M > -1.78` → reject, `GATE_BENEISH`.
6. **Altman Z-Score** — `Z = 1.2(A) + 1.4(B) + 3.3(C) + 0.6(D) + 1.0(E)` where A=Working Capital/Total Assets, B=Retained Earnings/Total Assets, C=EBIT/Total Assets, D=Market Value of Equity/Total Liabilities, E=Sales/Total Assets. Threshold: `Z < 1.81` → reject, `GATE_ALTMAN`. Reuse the financials already pulled for Beneish; only market value of equity needs a fresh fetch.

## Missing-Data Handling

If every source in a gate's waterfall is exhausted and the gate still can't be computed, **treat it as a failure and reject** — fail-safe, not fail-open. Use a distinct reason code from an actual computed failure so the audit trail can tell "verified and disqualified" apart from "could not verify" (e.g. `GATE_BENEISH` vs. `GATE_BENEISH_NO_DATA`).

## Same-Day Caching

Gate results are computed once per calendar day per ticker. If the same ticker is gated again later the same day (e.g., Discovery resurfaces it in a later Trading Cycle run), reuse the existing result — do not recompute.

## Output

For every candidate evaluated, write one `candidates` document (per the Phase 0 schema): ticker, evaluation timestamp, `trading_cycle_run_id`, `gate_result` (`PASSED`|`REJECTED`), and if rejected, the specific reason code plus which data sources were consulted. Write a corresponding `audit_log` entry via the Phase 0 utility for every evaluation, pass or fail — rejections are exactly as auditable as passes, and are never deleted or hidden.

## Boundaries for v1 (explicitly out of scope)

- No scoring, weighting, or AI involvement — gates are strictly binary.
- No position sizing or execution logic.
- No live bid-ask spread check — ADV + price floor are the only liquidity gates in v1.
- No adverse-opinion detection beyond the fixed 4-phrase keyword list.

## Definition of Done

1. Given a ticker known to be liquid and financially sound, all six gates evaluate and the candidate is marked `PASSED`, with `audit_log` showing all six checks ran in order.
2. Given a ticker with a share price under $5 (or ADV under $5M), the pipeline stops at gate 2 with `GATE_LIQUIDITY_PRICE` (or `_ADV`), and gates 3-6 are confirmed **not** to have run (check the audit trail for their absence).
3. Given a ticker with a manufactured Beneish M-Score above -1.78 (mock the financials input), the candidate is rejected with `GATE_BENEISH` and the audit log shows the computed M-Score value.
4. Force every data source in one waterfall (e.g. fundamentals) to fail for a given ticker and confirm the result is `GATE_BENEISH_NO_DATA` (or the equivalent `_NO_DATA` code for whichever gate depends on that data), not an unhandled exception and not a silent pass.
5. Gate the same ticker twice in the same calendar day and confirm the second call returns the cached result without re-fetching any data source.
