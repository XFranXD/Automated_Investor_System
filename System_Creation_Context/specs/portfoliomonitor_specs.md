# TBE Subsystem Spec: Portfolio Monitor
### Phase 6 of the Roadmap - Architecture Section 4
**Version 1.0 — July 2026**

## 1. Purpose

Runs **first** in every Trading Cycle, before Discover, AI-score, or Execute — protecting what's already at risk always comes before looking for anything new, a direct expression of the capital-preservation-first objective, not an implementation convenience. This subsystem owns the entire lifecycle of an *existing* open position (stop ratcheting, exit execution) and all portfolio-wide aggregate risk checks, including the kill switch. It is 100% deterministic.

## 2. Position-Level Management

For every currently open position, every cycle:

1. Recompute current ATR(22) and track the highest high (long) or lowest low (short) reached since entry.
2. Recompute the Chandelier stop: `highest_high_since_entry - 3×ATR(22)` for a long, `lowest_low_since_entry + 3×ATR(22)` for a short. **The stop is only updated if the new value is more favorable than the current one** (higher for a long, lower for a short) — this is the concrete, structural implementation of "stop-loss never loosens live." Because the formula anchors to the highest-high/lowest-low since entry (a value that only ever moves favorably), there is no code path by which this calculation could produce a less protective stop than what's already set.
3. Check whether price has hit either the stop or the take-profit level since the last check. **If both could plausibly have triggered, the stop takes priority** — capital preservation over profit-taking, consistent with the Constitution's primary objective.
4. If triggered, execute the paper exit: record realized P&L, close the position in `trades`, write the full reasoning trace to `audit_log`.

## 3. Portfolio-Level Aggregate Checks

Recomputed every cycle across all open positions:

- **Sector exposure snapshot** — current % of portfolio equity per sector, feeding the 25% cap Execution checks on its next run.
- **Correlation snapshot** — rolling 30-day pairwise correlations among open positions, feeding the correlation cap Execution checks on its next run.
- **Drawdown tracking** — current portfolio equity compared against its trailing high-water mark, expressed as a drawdown percentage.

## 4. Kill Switch / Circuit Breaker

- **Threshold:** portfolio drawdown ≥ 14% from the high-water mark → `kill_switch_active = true`.
- **Effect:** Execution Engine blocks all new entries while this is true (Section 3 of that spec). This subsystem's own position management (Section 2) is unaffected — protecting and exiting existing positions never pauses, only new risk-taking does.
- **Reset:** never automatic. Once tripped, `kill_switch_active` stays true until Ale manually resets it. This is deliberate — a circuit breaker that can reset itself isn't really a circuit breaker, and it directly implements the never-list's "kill switch required" rule as something with real teeth, not a soft suggestion.

## 5. Regime-Dependent Correlation Tightening

Re-reads the current regime state from Scoring & Regime Filter's most recent determination. During `RISK_OFF`, the correlation cap tightens from 0.6 to 0.4, written into `portfolio_state` for Execution's next pre-trade check to consume. This is the concrete implementation of the never-list's "never assume historical correlation holds in a crisis" rule — correlation assumptions are treated as less trustworthy exactly when the regime signal says conditions have shifted.

## 6. Notification

If `kill_switch_active` transitions from `false` to `true` during this cycle's checks, a notification must fire — this is the "way to contact me" requirement already locked in the Constitution, not a new capability being added here.

- Content: a plain-language explanation of what triggered it (e.g., current drawdown %, which positions contributed). The AI Reasoning Layer's existing schema-constrained, explain-only capability may optionally be reused to phrase this more readably, but the notification **must** fire even if that step is unavailable — fall back to a plain templated message with the raw numbers rather than blocking the alert on an AI call succeeding.
- Delivery mechanism (email, or otherwise) is an implementation detail, not an architectural one.
- No notification fires on ordinary position exits (stop or take-profit hit) — those are normal operation, not an exceptional situation requiring Ale's attention.

## 7. Output

Updates to `trades` (any exits this cycle), updates to `portfolio_state` (sector/correlation snapshot, drawdown, kill-switch status), and `audit_log` entries for every check performed and every action taken — including checks that resulted in no action, consistent with every other subsystem's explainability requirement.

## 8. Explicitly Out of Scope for This Subsystem

- No new position entry — that's Execution Engine, and it runs after this subsystem, not before.
- No AI-driven decisions of any kind — the optional AI use in Section 6 is text-formatting only, never a factor in whether the kill switch trips or a position exits.
- No automatic kill-switch reset, ever.