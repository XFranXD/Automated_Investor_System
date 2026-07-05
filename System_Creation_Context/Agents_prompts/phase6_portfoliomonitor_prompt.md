[Build — new module, Phase 6 of 8]

# TBE — Phase 6: Portfolio Monitor

## Goal

Runs **first** in every Trading Cycle, before Discover, AI-score, or Execute — protecting what's already at risk always comes before looking for anything new. Owns the entire lifecycle of *existing* open positions (stop ratcheting, exit execution) and all portfolio-wide aggregate risk checks, including the kill switch. 100% deterministic.

This is Phase 6 of an 8-phase build, same repo as Phases 0-5. Use the paper-trading harness (`close_paper_position`), audit-logging utility, and `trades`/`portfolio_state` schema from Phase 0.

## Position-Level Management (every open position, every cycle)

1. Recompute current ATR(22) and track the highest-high (long) / lowest-low (short) reached since entry, storing it on the `trades` document (`highest_high_since_entry` / `lowest_low_since_entry`).
2. Recompute the Chandelier stop: `highest_high_since_entry - 3×ATR(22)` (long) or `lowest_low_since_entry + 3×ATR(22)` (short). **Update `current_stop` only if the new value is more favorable** than what's already stored (higher for a long, lower for a short) — never loosen it. Because the anchor (`highest_high`/`lowest_low` since entry) only ever moves favorably, there must be no code path by which this computation produces a less protective stop than the current one. Do not add any override, manual reset, or "widen stop" capability anywhere in this subsystem.
3. Check whether price has hit either `current_stop` or `take_profit` since the last check. **If both could plausibly have triggered in the same check, the stop takes priority** — capital preservation over profit-taking.
4. If triggered, call `close_paper_position(...)` from Phase 0, recording `exit_reason` (`STOP` or `TAKE_PROFIT`) and the resulting `realized_pnl`. Write the full reasoning trace to `audit_log`.

## Portfolio-Level Aggregate Checks (recomputed every cycle, across all open positions)

- **Sector exposure snapshot** — current % of portfolio equity per sector, written to `portfolio_state.sector_exposure` for Phase 5's next run to read.
- **Correlation snapshot** — rolling 30-day pairwise correlations among open positions, written to `portfolio_state.correlation_snapshot`.
- **Drawdown tracking** — current portfolio equity vs. its trailing high-water mark, written to `portfolio_state.drawdown_pct`. Update `portfolio_state.high_water_mark` whenever equity exceeds the prior mark.

## Kill Switch / Circuit Breaker

- **Threshold:** `portfolio_state.drawdown_pct >= 14%` (from high-water mark) → set `kill_switch_active = true`.
- **Effect:** Phase 5 blocks all new entries while this is true. This subsystem's own position management (above) is **never** affected by the kill switch being active — protecting and exiting existing positions never pauses, only new risk-taking does.
- **Reset:** never automatic, under any circumstance. Once `kill_switch_active = true`, it stays true until manually reset outside this subsystem's code path entirely — do not build any reset mechanism, scheduled or conditional, anywhere in this phase.

## Regime-Dependent Correlation Tightening

Read the current regime state from Phase 4's most recent determination (stored on the relevant `candidates` record or wherever Phase 4 last wrote it — check Phase 4's actual output location). During `RISK_OFF`, set `portfolio_state.correlation_cap_current = 0.4`; during `RISK_ON`, `0.6`. This is what Phase 5's correlation check (pre-trade check 3) reads.

## Notification

If `kill_switch_active` transitions from `false` to `true` during this cycle's checks (not on every cycle it remains true), fire a notification.
- Content: plain-language explanation of what triggered it — current drawdown %, which positions contributed most.
- Optionally reuse Phase 3's AI Reasoning Layer to phrase this more readably, but **the notification must fire even if that call is unavailable or fails** — fall back to a plain templated message with the raw numbers. Never let the notification depend on an AI call succeeding.
- Delivery mechanism (email or otherwise) is an implementation detail — choose something reliable and low-maintenance given this runs unattended.
- No notification on ordinary stop/take-profit exits — those are normal operation, not something requiring attention.

## Output

Updates to `trades` (any exits this cycle), updates to `portfolio_state` (sector/correlation snapshot, drawdown, kill-switch status, correlation cap, high-water mark), and an `audit_log` entry via the Phase 0 utility for every check performed and every action taken — including checks that resulted in no action.

## Boundaries for v1 (explicitly out of scope)

- No new position entry — that's Phase 5, and it runs after this subsystem, never before.
- No AI-driven decisions of any kind — the optional AI use in Notification is text-formatting only, never a factor in whether the kill switch trips or a position exits.
- No automatic kill-switch reset, ever, under any condition.

## Definition of Done

1. Given an open long position where price has moved favorably since entry, confirm `current_stop` ratchets upward to the new Chandelier level, and confirm running the check again with a *less* favorable price does **not** move the stop back down.
2. Given an open position where price crosses both the stop and take-profit level within the same check (construct this deliberately), confirm the exit is recorded with `exit_reason = "STOP"`, not `"TAKE_PROFIT"`.
3. Given a portfolio drawdown that crosses 13.9% → 14.1% between two consecutive checks, confirm `kill_switch_active` flips to `true` exactly at that transition and a notification fires exactly once (not on every subsequent cycle it remains active).
4. Given `kill_switch_active = true`, confirm this subsystem still ratchets stops and executes exits normally on the same cycle.
5. Attempt to programmatically reset `kill_switch_active` to `false` from within this subsystem's own logic and confirm there is no code path that allows it — the only way it changes is manual, external intervention.
6. Force the optional AI notification-phrasing call to fail and confirm the notification still fires with the plain templated fallback message.
7. Given a manufactured `RISK_OFF` regime state, confirm `portfolio_state.correlation_cap_current` is set to 0.4, and 0.6 under `RISK_ON`.
