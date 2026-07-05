# TBE Subsystem Spec: Scoring & Regime Filter
### Phase 4 of the Roadmap - Architecture Section 4
**Version 1.1 — July 2026** (Section 9 updated: sizing hand-off to Execution Engine is now a real, specified mechanism, not a placeholder)

## 1. Purpose

Combine the deterministic trigger (from Discovery) and the qualitative assessment (from the AI Reasoning Layer) into a final proceed/abstain decision, using the locked equal-weighted scoring model, modulated by a simple market-regime signal. This is the last step before a candidate either reaches Execute or is logged as an abstention.

Within a Trading Cycle run, this subsystem is the second half of the "AI score" step in the Architecture diagram — it runs immediately after the AI Reasoning Layer for the same candidate, the same way Hard-Gate Engine runs immediately after Discovery within the "Discover" step. It is 100% deterministic — no AI call happens here; it only consumes the AI Reasoning Layer's already-produced structured output.

## 2. Inputs

- The candidate's trigger details from Discovery (type, direction, magnitude — surprise % or price/volume confirmation strength).
- The candidate's `evaluations` record from the AI Reasoning Layer (conviction, information_sufficiency), or an ABSTAIN status if that subsystem failed to produce one.
- Current regime state (Section 4).

## 3. Trigger Strength Scoring

Discovery's trigger already has a direction (locked); this step scores its *magnitude* on a simple 2-point scale, independent of direction:

- **Earnings trigger:** `|surprise%| ≥ 10%` → STRONG (+2); `5% ≤ |surprise%| < 10%` → MODERATE (+1).
- **Filing trigger:** price move `≥ 6%` on the qualifying volume → STRONG (+2); `3% ≤ price move < 6%` → MODERATE (+1).

This score is always positive — it measures how strong the deterministic evidence is, not whether it's contested. Contest comes from the AI side.

## 4. AI Conviction Scoring

Maps directly from the AI Reasoning Layer's `conviction` field onto a comparable scale:

| Conviction | Score |
|---|---|
| STRONG_SUPPORT | +2 |
| MODERATE_SUPPORT | +1 |
| NEUTRAL | 0 |
| MODERATE_CONTRADICTION | -1 |
| STRONG_CONTRADICTION | -2 |

Unlike trigger strength, this score can be negative — it represents whether the qualitative evidence agrees or disagrees with the direction Discovery already set.

**Why ±2, matching trigger strength's range:** this scale is deliberately kept symmetric and range-matched to the trigger-strength score (Section 3), rather than given a wider or asymmetric range. Because the combined score (Section 5) is a simple average of the two, any mismatch in range would silently break the locked equal-weighted evidence model — a wider AI-conviction range would let qualitative evidence dominate the average regardless of the word "equal" in the formula. Matching ranges is what makes equal-weighting actually true in practice, not just in the formula's name. See the Provisional Parameters & Decision Log for the fuller discussion, including why the scale was deliberately kept symmetric (contradiction weighted no more heavily than equivalent support) rather than biased toward rejection at this stage — that bias is instead expressed downstream, as reduced position size, not as a further-narrowed gate.

## 5. Combined Score & Decision

**Combined score = average(trigger strength score, AI conviction score).** This is genuinely equal-weighted — both pillars contribute identically, per the locked evidence model. Averaging a positive-only value against a possibly-negative one is what naturally produces abstention when the two disagree, without needing a special-case override: a STRONG trigger (+2) against STRONG_CONTRADICTION (-2) averages to 0, reading as "conflicting evidence," exactly as it should.

**Information sufficiency modifier**, applied before the bucket lookup below:
- `INSUFFICIENT` → forces ABSTAIN regardless of the combined score. Reason code: `ABSTAIN_AI_INSUFFICIENT_INFO`. Scoring on evidence the AI itself flagged as too thin to assess would contradict the whole point of that field existing.
- `LIMITED` → subtract 0.5 from the combined score before the bucket lookup (a real penalty, not a disqualifier).
- `SUFFICIENT` → no adjustment.

**Bucket lookup** (after the modifier above):

| Combined score | Outcome |
|---|---|
| ≥ 1.5 | STRONG conviction → proceed |
| 0.5 to < 1.5 | MODERATE conviction → proceed |
| -0.5 to < 0.5 | ABSTAIN — reason: `ABSTAIN_NEUTRAL_OR_CONFLICTING` |
| < -0.5 | ABSTAIN — reason: `ABSTAIN_EVIDENCE_CONTRADICTS_TRIGGER` |

**If the AI Reasoning Layer itself returned an ABSTAIN status** (schema failure, API unavailable, quota exhausted — Section 7 of that spec), there is no conviction score to combine, so this subsystem automatically abstains too. Reason code: `ABSTAIN_UPSTREAM_AI_FAILURE`.

## 6. Regime Filter

**Signal:** two deterministic checks, both sourced from yfinance (primary) / Finnhub (fallback), same waterfall pattern used elsewhere:
- **Volatility:** CBOE VIX level. `VIX > 30` → elevated.
- **Trend:** S&P 500 price relative to its 50-day simple moving average. Below the SMA → downtrend.

**Regime state:** `RISK_OFF` if either condition is true (VIX elevated OR index below its 50-day SMA); `RISK_ON` otherwise. This is intentionally conservative — either signal alone is enough to flip the regime, not requiring both.

**Effect on the decision in Section 5:** during `RISK_OFF`, the bar is raised — only STRONG conviction candidates proceed; MODERATE conviction candidates that would otherwise proceed are instead abstained, reason code `ABSTAIN_RISK_OFF_REGIME`. During `RISK_ON`, both STRONG and MODERATE proceed as normal per Section 5's table.

This is the full extent of regime detection in v1 — deliberately not the Absorption Ratio / Turbulence Index approach from the research report, per the locked v1 constraint against techniques requiring a trusted historical calibration window. A 50-day moving average and a VIX threshold are both self-contained, published, deterministic checks, not calibrated models.

Note: regime state is not separately factored into position sizing (Execution Engine Section 4) — since `RISK_OFF` already restricts `PROCEED` to STRONG-tier candidates only, sizing under `RISK_OFF` follows naturally from the conviction-proportional formula operating on an already-elevated score range. This was a deliberate choice, not an oversight — see the Decision Log.

## 7. Same-Day Handling

Consistent with every upstream subsystem: a candidate is scored once per day. If it reappears in a later Trading Cycle run the same day, its existing decision from earlier that day stands — this subsystem does not re-score it, even if the regime state has since changed. Regime state is only applied at the moment a *new* candidate is being decided, not retroactively to earlier decisions made the same day.

## 8. Output

Update the candidate's record with: combined score, trigger-strength and AI-conviction components that produced it, information-sufficiency modifier applied (if any), regime state at decision time, and final outcome — `PROCEED` (with confidence tier STRONG or MODERATE) or `ABSTAIN` (with the specific reason code from Sections 5 or 6). Written to `audit_log` regardless of outcome, same as every other subsystem — an abstention's reasoning is exactly as auditable as an approval's.

Only `PROCEED` outcomes are passed to the Execution Engine — and the **numeric combined score is passed along with the tier**, not just the STRONG/MODERATE label, since Execution Engine's position sizing (Section 4 of that spec) now scales continuously with the exact score rather than by tier alone.

## 9. Explicitly Out of Scope for This Subsystem

- No AI calls of any kind — purely arithmetic and lookup on already-produced inputs.
- No stop/target calculation — that stays entirely in the Execution Engine spec.
- Position sizing math itself is computed in Execution Engine, not here; this subsystem's only responsibility toward sizing is to pass forward the combined score and confidence tier it already produces as part of its normal output (Section 8) — it does not compute a risk percentage or dollar amount itself.
- No Absorption Ratio, Turbulence Index, or any regime signal requiring a trusted historical lookback window (see Section 6).
- No re-scoring of a candidate already decided earlier the same day, even if regime state changes intraday.