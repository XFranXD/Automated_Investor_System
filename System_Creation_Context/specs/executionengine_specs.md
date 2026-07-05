# TBE Subsystem Spec: Execution Engine
### Phase 5 of the Roadmap - Architecture Section 4
**Version 1.1 — July 2026** (Sections 2 and 4 updated: conviction-proportional position sizing added to resolve the combined-score go/no-go edge case flagged in the Provisional Parameters & Decision Log)

## 1. Purpose

Turn a `PROCEED` decision from Scoring into a correctly sized, correctly protected paper position. This is the only subsystem permitted to open a new position — it runs last in each Trading Cycle, after Monitor, Discover, and AI-score have all completed. It is 100% deterministic.

Existing-position management (stop ratcheting, exit execution) is **not** this subsystem's job — that belongs to Portfolio Monitor, which runs first each cycle specifically so protecting existing capital is never delayed by new-entry logic. This subsystem only ever creates new positions.

## 2. Inputs

- A `PROCEED` decision from Scoring & Regime Filter (ticker, direction, confidence tier, **and the underlying numeric `combined_score`**). The numeric score is required, not just the STRONG/MODERATE label — Section 4's sizing formula needs the precise value to scale risk proportionally rather than by a fixed tier.
- Current `portfolio_state` (open positions, sector exposure, kill-switch status).

## 3. Pre-Trade Checks (in order, any failure blocks entry)

1. **Kill switch.** If `portfolio_state.kill_switch_active = true`, no new entries at all. Reason: `ABSTAIN_KILL_SWITCH_ACTIVE`. This is the never-list's "kill switch required" rule, enforced by simply refusing to proceed past this check.
2. **One position per ticker.** If a position is already open on this ticker, the new signal is not executed — this is how "never average down" is enforced structurally: there is no code path that adds to or modifies an existing position's size from this subsystem. Reason: `ABSTAIN_EXISTING_POSITION`.
3. **Correlation cap.** Rolling 30-day price correlation between the candidate and every existing open position is checked; if any exceeds 0.6 (tightened to 0.4 during `RISK_OFF` regime, per Portfolio Monitor's regime handling), the entry is blocked. Reason: `ABSTAIN_CORRELATION_CAP`.
4. **Sector exposure cap.** If adding this position at its intended size would push that sector's share of total portfolio equity above 25%, the entry is blocked. Reason: `ABSTAIN_SECTOR_CAP`.

## 4. Position Sizing (ATR-based, conviction-proportional)

- ATR period: **22 trading days** (Chandelier Exit's standard published period — matches the stop calculation in Section 5, not an invented number).

- **Risk per trade is conviction-proportional, not flat.** A candidate that only just cleared the PROCEED threshold (combined score barely above 0.5) risks less capital than one with a near-maximal score. This directly addresses the edge case where a strong deterministic trigger can outweigh a real AI contradiction and still produce a `PROCEED`: the trade is still allowed to happen — the AI's objection isn't given veto power over deterministic evidence, consistent with the locked equal-weighted evidence model — but its size now reflects how contested the evidence actually was.

  ```
  risk% = min_risk + (combined_score − 0.5) / (2.0 − 0.5) × (max_risk − min_risk)
  ```

  Where:
  - `max_risk = 1.5%` — unchanged from the original flat rate. This is deliberately left untouched because the Portfolio Monitor's 14% kill-switch threshold was reasoned directly from a ~1.5% per-trade loss assumption; changing this ceiling would silently invalidate that already-resolved math. A candidate with the maximum possible combined score (2.0) is sized exactly as it always was.
  - `min_risk = 0.75%` — half of `max_risk`. A combined score of 0.5 is, by definition, the weakest evidence the system will still act on at all (anything below it is `ABSTAIN`). Sizing this floor at half the maximum keeps the trade meaningful (not so small that per-trade audit/monitoring overhead outweighs the position) while ensuring the system's weakest-conviction trades never risk as much as its strongest ones.
  - This formula only applies within the already-existing `PROCEED` range (0.5 to 2.0 inclusive). It does not change, widen, or narrow the ABSTAIN boundary in any way — the go/no-go gate itself (Scoring & Regime Filter Section 5) is untouched.
  - **Note on the kill-switch threshold:** because most `PROCEED` trades will now risk somewhat less than the original flat 1.5%, a losing streak of ordinary bad luck will typically consume equity more slowly than the math behind the 14% threshold assumed. The 14% figure itself does not need to change — this makes its existing safety margin somewhat more conservative than originally estimated, not less. See the Decision Log for the full note.

- Initial stop distance (per share) = **3 × ATR(22)**, unchanged.
- Shares = `(portfolio_equity × risk%) / stop_distance_per_share`, rounded down to a whole share count, where `risk%` is the conviction-proportional value computed above (no longer a fixed 1.5%).
- **Liquidity capacity cap:** position value must not exceed 10% of the candidate's 20-day average daily dollar volume (a stricter, size-aware check beyond the Hard-Gate Engine's binary liquidity floor, meant to avoid market-impact-scale positions even in a nominally liquid name). If conviction-proportional sizing would exceed this, the position is sized down to the cap rather than rejected outright — this is the one pre-trade check that adjusts rather than blocks.

## 5. Stop-Loss (Chandelier Exit, set at entry)

- **Long:** initial stop = `entry_price - 3×ATR(22)`.
- **Short:** initial stop = `entry_price + 3×ATR(22)`.

This subsystem only sets the *initial* stop at entry. Ongoing ratcheting (the ratchet-only-favorably rule that structurally implements "stop-loss never loosens live") happens every cycle in Portfolio Monitor, not here — see that spec for the update mechanics.

## 6. Take-Profit (Hit-Limit)

Fixed reward:risk ratio of **2:1** relative to the initial stop distance:
- **Long:** take-profit = `entry_price + 2×(3×ATR(22))`.
- **Short:** take-profit = `entry_price - 2×(3×ATR(22))`.

This is what satisfies the "assign a price to automatically exit and take the earnings" requirement — the trailing stop protects against loss, this fixed target locks in a defined win condition, and whichever level is reached first (checked in Portfolio Monitor) closes the trade.

## 7. Output

Write a new `trades` record: ticker, direction, entry price, share count, **the `risk%` and `combined_score` used to size this position**, initial stop, take-profit level, confidence tier from Scoring, and the full chain of reasoning it descended from (candidate → gate result → AI evaluation → scoring decision). Write the corresponding `audit_log` entry — this applies to every attempted entry, not just successful ones; a blocked entry (Section 3) is exactly as auditable as an executed one.

## 8. Never-List Enforcement Recap

| Rule | How this subsystem enforces it |
|---|---|
| Kill switch required | Section 3, check 1 — hard block, checked before anything else |
| Position never exceeds liquidity capacity | Section 4's liquidity capacity cap, on top of the Hard-Gate's binary floor |
| Never average down | Section 3, check 2 — one position per ticker, structurally, not by policy |
| Never trade live capital to explore | Structural — this entire subsystem only ever writes to a paper `trades` record; there is no broker integration anywhere in this spec |

## 9. Explicitly Out of Scope for This Subsystem

- No stop ratcheting after entry, no exit execution — both are Portfolio Monitor's job.
- No portfolio-level drawdown circuit breaker logic — Portfolio Monitor computes `kill_switch_active`; this subsystem only reads it.
- No AI involvement of any kind.
- No sizing or entry logic for anything other than a `PROCEED` decision already produced by Scoring.
- No changes to the go/no-go boundary itself — conviction-proportional sizing operates entirely within the `PROCEED` range already defined by Scoring & Regime Filter; it does not admit trades that would otherwise `ABSTAIN`.