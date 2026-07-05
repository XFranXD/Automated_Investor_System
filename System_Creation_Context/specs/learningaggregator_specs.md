# TBE Subsystem Spec: Learning Aggregator
### Phase 7 of the Roadmap - Architecture Section 4
**Version 1.0 — July 2026**

## 1. Purpose

Converts closed trades into durable, queryable statistics without storing every trade forever, using the mergeable sum/count aggregation pattern. Runs weekly, independent of the Trading Cycle. This subsystem is purely informational in v1 — it produces numbers for review, it never rewrites any other subsystem's parameters automatically, per the locked observational (not reinforcement-style) learning philosophy.

## 2. Aggregation Dimensions

Trades are aggregated into overlapping buckets, not just one overall total, specifically so the provisional parameters used throughout the other specs can eventually be evaluated against real outcomes:

- **Overall** — every closed trade.
- **By direction** — long vs. short.
- **By trigger type** — earnings surprise vs. material filing.
- **By confidence tier** — STRONG vs. MODERATE (from Scoring & Regime Filter).
- **By regime state at entry** — RISK_ON vs. RISK_OFF.

A single closed trade contributes to five buckets simultaneously (overall, plus one from each of the other four dimensions).

## 3. Mergeable Fields (per bucket)

`tradeCount`, `wins`, `losses`, `sumPnL`, `sumPnLSquared` (for variance/standard deviation), `grossProfit`, `grossLoss`, `maxWin`, `maxLoss`. From these, win rate, average return, expectancy, profit factor, and standard deviation can all be derived for any bucket or combination of batches, without ever needing to re-read individual trade records once they've been aggregated.

## 4. Refresh Policy

Weekly. Processes only trades closed since the last successful run (tracked via a last-processed timestamp), not the full trade history each time — consistent with the efficiency principle applied throughout the other specs.

## 5. Output

One document per dimension-bucket in `stats_aggregates`, merged (fields added to) rather than overwritten on each run.

## 6. Relationship to Provisional Parameters

This is the mechanism referenced throughout the other six specs' provisional thresholds. Once enough trades exist in a given bucket, questions like "do STRONG-tier trades actually outperform MODERATE-tier ones enough to justify where that cutoff was drawn" or "does RISK_OFF abstention actually protect capital, or does it just miss otherwise-good trades" become answerable from this subsystem's output — by Ale, reviewing the numbers, not by the system silently adjusting itself. See the companion Provisional Parameters document for the full list of what this is expected to eventually inform.

## 7. Explicitly Out of Scope for This Subsystem

- No automatic parameter changes to any other subsystem.
- No reinforcement-style feedback into live trading decisions.
- No AI involvement — purely arithmetic aggregation.