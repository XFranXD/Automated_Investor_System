[Build — new module, Phase 5 of 8]

# TBE — Phase 5: Execution Engine

## Goal

Turn a `PROCEED` decision from Phase 4 into a correctly sized, correctly protected paper position. This is the only subsystem permitted to open a new position — it runs last in each Trading Cycle, after Monitor, Discover, and AI-score. 100% deterministic.

This is Phase 5 of an 8-phase build, same repo as Phases 0-4. Use the paper-trading harness, audit-logging utility, and `portfolio_state`/`trades` schema from Phase 0.

Existing-position management (stop ratcheting, exits) is **not** this subsystem's job — that's Phase 6, which runs first each cycle. This subsystem only ever creates new positions; there must be no code path here that modifies an existing open position.

## Inputs

- A `PROCEED` decision from Phase 4: ticker, direction, confidence tier, **and the numeric `combined_score`**.
- Current `portfolio_state` (open positions, sector exposure, kill-switch status).

## Pre-Trade Checks (run in this order; any failure blocks entry — do not proceed past a failed check)

1. **Kill switch.** If `portfolio_state.kill_switch_active == true`, block all new entries. Reason: `ABSTAIN_KILL_SWITCH_ACTIVE`.
2. **One position per ticker.** If a position is already open on this ticker, block. Reason: `ABSTAIN_EXISTING_POSITION`. There must be no code path that adds to or resizes an existing position from this subsystem — a repeat signal on an open ticker is never treated as "add to it."
3. **Correlation cap.** Rolling 30-day correlation between the candidate and every existing open position; if any exceeds 0.6 (0.4 during `RISK_OFF` — read the current cap from `portfolio_state.correlation_cap_current`, set by Phase 6), block. Reason: `ABSTAIN_CORRELATION_CAP`.
4. **Sector exposure cap.** If adding this position would push its sector above 25% of total portfolio equity, block. Reason: `ABSTAIN_SECTOR_CAP`.

## Position Sizing (ATR-based, conviction-proportional)

- ATR period: 22 trading days.
- **Risk per trade is conviction-proportional, not flat:**
  ```
  risk_pct = 0.75 + (combined_score - 0.5) / (2.0 - 0.5) * (1.5 - 0.75)
  ```
  (expressed in percent; `combined_score` is always in `[0.5, 2.0]` here since only `PROCEED` decisions reach this subsystem). A score of exactly 0.5 → `risk_pct = 0.75%`. A score of exactly 2.0 → `risk_pct = 1.5%`. Linear in between. **Do not deviate from this formula or its two constants (0.75, 1.5) without this being a deliberate, separately-discussed change** — `1.5%` is load-bearing for the kill-switch threshold's own math in Phase 6, and `0.75%` (half of it) is the deliberately-chosen floor for the weakest evidence this system will still act on.
- Initial stop distance (per share) = `3 × ATR(22)`.
- Shares = `floor((portfolio_equity × risk_pct/100) / stop_distance_per_share)`.
- **Liquidity capacity cap:** position value must not exceed 10% of the candidate's 20-day ADV. If the sizing above would exceed this, size the position *down* to the cap rather than rejecting it outright — this is the one check in this list that adjusts instead of blocking.

## Stop-Loss (Chandelier Exit, initial value only — set at entry, never touched again by this subsystem)

- Long: `entry_price - 3×ATR(22)`.
- Short: `entry_price + 3×ATR(22)`.

## Take-Profit

- Long: `entry_price + 2×(3×ATR(22))`.
- Short: `entry_price - 2×(3×ATR(22))`.

## Output

Use Phase 0's `open_paper_position(...)` to write the `trades` document: ticker, direction, entry price, share count, `risk_pct_used`, `combined_score`, initial stop, take-profit, confidence tier, and the full reasoning chain (candidate → gate result → evaluation → scoring decision). Write an `audit_log` entry via Phase 0's utility for **every** attempted entry — a blocked entry (any of the four checks above) is exactly as auditable as an executed one.

## Boundaries for v1 (explicitly out of scope)

- No stop ratcheting after entry, no exit execution — both are Phase 6.
- No kill-switch or drawdown computation — Phase 6 computes `kill_switch_active`; this subsystem only reads it.
- No AI involvement of any kind.
- No sizing or entry logic for anything other than a `PROCEED` decision already produced by Phase 4.
- No admitting a trade that Phase 4 marked `ABSTAIN` — this subsystem never re-evaluates the go/no-go decision, only sizes and executes what Phase 4 already approved.

## Definition of Done

1. Given a `PROCEED` with `combined_score = 2.0` and a clean portfolio state (no blocks), the resulting trade's `risk_pct_used` is exactly 1.5%, with correctly computed stop and take-profit.
2. Given a `PROCEED` with `combined_score = 0.5`, the resulting trade's `risk_pct_used` is exactly 0.75% — confirm the share count is proportionally smaller than in test 1 for the same portfolio equity and ATR.
3. Given `portfolio_state.kill_switch_active = true`, confirm no trade is opened regardless of how strong the candidate is, and `ABSTAIN_KILL_SWITCH_ACTIVE` is logged.
4. Given an already-open position on the same ticker, confirm the new signal is blocked (`ABSTAIN_EXISTING_POSITION`) and confirm no existing `trades` document was modified.
5. Given a candidate whose correlation to an open position is 0.7 during `RISK_ON` (cap 0.6), confirm it's blocked; given the same 0.7 correlation but the cap is 0.6 (not yet tightened), confirm it's still blocked; given `RISK_OFF` with a 0.5 correlation (above the tightened 0.4 cap), confirm it's blocked too.
6. Given a position that would exceed the 10% ADV liquidity cap at its formula-computed size, confirm it is sized down to the cap rather than rejected.
