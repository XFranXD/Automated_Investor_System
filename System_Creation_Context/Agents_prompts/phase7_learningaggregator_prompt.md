[Build — new module, Phase 7 of 8]

# TBE — Phase 7: Learning Aggregator

## Goal

Convert closed trades into durable, queryable statistics without storing every trade forever, using a mergeable sum/count aggregation pattern. Runs weekly, independent of the Trading Cycle. This subsystem is purely informational in v1 — it produces numbers for human review and never rewrites any other subsystem's parameters automatically, per the locked observational (not reinforcement-style) learning philosophy.

This is Phase 7 of an 8-phase build, same repo as Phases 0-6 — the final phase. Use the audit-logging utility and `trades`/`stats_aggregates` schema from Phase 0.

## Aggregation Dimensions

Every closed trade contributes to five buckets simultaneously — one overall total plus one bucket from each of four dimensions:

- **Overall** — every closed trade.
- **By direction** — `LONG` vs. `SHORT`.
- **By trigger type** — `EARNINGS_SURPRISE` vs. `MATERIAL_FILING`.
- **By confidence tier** — `STRONG` vs. `MODERATE` (from the trade's stored `confidence_tier`, set by Phase 5).
- **By regime state at entry** — `RISK_ON` vs. `RISK_OFF` (from the trade's stored regime state at the time it was opened).

## Mergeable Fields (per bucket)

`tradeCount`, `wins`, `losses`, `sumPnL`, `sumPnLSquared` (for variance/standard deviation), `grossProfit`, `grossLoss`, `maxWin`, `maxLoss`. These must be **additive/mergeable** — each new batch of closed trades updates a bucket by adding to its existing values, never by re-deriving from the full trade history. Do not build this by re-reading all historical trades on every run; only new closes since the last run are processed, and their contributions are added to whatever the bucket already holds.

From these fields, win rate, average return, expectancy, profit factor, and standard deviation must all be derivable on demand for any bucket, without re-reading individual `trades` records.

## Refresh Policy

Weekly. Track a `last_processed_timestamp` (per the `stats_aggregates` schema from Phase 0) and process only trades closed since that timestamp on each run — never the full trade history.

## Output

One document per dimension-bucket in `stats_aggregates` (Phase 0 schema), merged into on each run (fields incremented), not overwritten. Write an `audit_log` entry summarizing what was processed (how many trades, which buckets updated) via the Phase 0 utility.

## Boundaries for v1 (explicitly out of scope)

- No automatic parameter changes to any other subsystem, under any circumstance — this subsystem's output is for a human to read and decide from, never for the system to act on itself.
- No reinforcement-style feedback into live trading decisions.
- No AI involvement — purely arithmetic aggregation.

## Definition of Done

1. Given a batch of newly-closed trades spanning both directions, both trigger types, both confidence tiers, and both regime states, confirm each trade updates exactly five buckets (overall + one per dimension), and confirm the resulting `tradeCount` across buckets is internally consistent (e.g. sum of `LONG` + `SHORT` tradeCounts equals the overall tradeCount for that same batch).
2. Run the aggregator twice in a row with no new closed trades between runs, and confirm the second run makes no changes to any bucket (idempotent on empty input) and does not re-process trades already covered by `last_processed_timestamp`.
3. Given an existing bucket with prior accumulated values, confirm a new batch's contributions are **added** to those values, not used to overwrite them — verify this explicitly by checking the bucket's `tradeCount` before and after equals prior + new.
4. From a bucket's stored fields, compute win rate, average return, expectancy, profit factor, and standard deviation, and confirm each formula is derived correctly from `wins`/`losses`/`sumPnL`/`sumPnLSquared`/`grossProfit`/`grossLoss` alone — without needing to query any individual `trades` document.
5. Confirm this subsystem contains no code path, function, or hook that writes to any collection other than `stats_aggregates` and `audit_log` — specifically, confirm it never writes to any other subsystem's parameters, thresholds, or the `candidates`/`portfolio_state` collections.
