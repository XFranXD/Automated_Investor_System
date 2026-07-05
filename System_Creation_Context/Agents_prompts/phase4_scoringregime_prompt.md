[Build — new module, Phase 4 of 8]

# TBE — Phase 4: Scoring & Regime Filter

## Goal

Combine the deterministic trigger (Discovery) and the qualitative assessment (AI Reasoning Layer) into a final proceed/abstain decision, using an equal-weighted scoring model, modulated by a simple regime signal. 100% deterministic — no AI call happens here; this only consumes the AI Reasoning Layer's already-produced structured output.

This is Phase 4 of an 8-phase build, same repo as Phases 0-3. Use the audit-logging utility and shared data-source client module from Phase 0.

## Inputs

- Candidate's trigger details from Discovery (type, direction, magnitude).
- Candidate's `evaluations` record from Phase 3 (conviction, information_sufficiency), or its `ABSTAIN` status if that subsystem failed to produce one.
- Current regime state (computed fresh each run — see below).

## Trigger Strength Scoring (magnitude only, always positive — direction is already locked from Discovery)

- **Earnings trigger:** `|surprise%| ≥ 10%` → STRONG (+2); `5% ≤ |surprise%| < 10%` → MODERATE (+1).
- **Filing trigger:** price move `≥ 6%` on qualifying volume → STRONG (+2); `3% ≤ move < 6%` → MODERATE (+1).

## AI Conviction Scoring

| Conviction | Score |
|---|---|
| STRONG_SUPPORT | +2 |
| MODERATE_SUPPORT | +1 |
| NEUTRAL | 0 |
| MODERATE_CONTRADICTION | -1 |
| STRONG_CONTRADICTION | -2 |

**This scale must stay exactly ±2, symmetric.** It is deliberately range-matched to trigger strength's ±2 scale — this is what makes the combined-score average genuinely equal-weighted between the two evidence pillars, not just nominally so. Do not widen, narrow, or make this scale asymmetric under any circumstance without this being a deliberate, separately-discussed change.

## Combined Score & Decision

`combined_score = average(trigger_strength_score, ai_conviction_score)`.

**Information sufficiency modifier**, applied before the bucket lookup:
- `INSUFFICIENT` → force `ABSTAIN` regardless of score. Reason: `ABSTAIN_AI_INSUFFICIENT_INFO`.
- `LIMITED` → subtract 0.5 from the combined score before lookup.
- `SUFFICIENT` → no adjustment.

**Bucket lookup** (after the modifier):

| Combined score | Outcome |
|---|---|
| ≥ 1.5 | STRONG conviction → proceed |
| 0.5 to < 1.5 | MODERATE conviction → proceed |
| -0.5 to < 0.5 | ABSTAIN — `ABSTAIN_NEUTRAL_OR_CONFLICTING` |
| < -0.5 | ABSTAIN — `ABSTAIN_EVIDENCE_CONTRADICTS_TRIGGER` |

**If Phase 3 itself returned `ABSTAIN`** (schema failure, unavailable, quota exhausted), there is no conviction score to combine — automatically abstain here too, reason `ABSTAIN_UPSTREAM_AI_FAILURE`.

**These bucket cutoffs are correct as written and must not be changed to "fix" the fact that a strong deterministic trigger can outweigh a real AI contradiction** (e.g. a STRONG trigger + MODERATE_CONTRADICTION averages to exactly 0.5, clearing MODERATE). That specific scenario is handled downstream, in Phase 5, via conviction-proportional position sizing — not by narrowing this gate. Do not add any special-case override here for that scenario.

## Regime Filter

- **Volatility:** CBOE VIX. `VIX > 30` → elevated.
- **Trend:** S&P 500 vs. its 50-day SMA. Below → downtrend.
- **Regime state:** `RISK_OFF` if either condition is true; `RISK_ON` otherwise (either signal alone is sufficient to flip regime — do not require both).
- **Effect:** during `RISK_OFF`, only STRONG-conviction candidates proceed; MODERATE candidates that would otherwise proceed are instead abstained, reason `ABSTAIN_RISK_OFF_REGIME`. During `RISK_ON`, both STRONG and MODERATE proceed per the table above.
- Regime state does **not** independently affect position sizing (that's entirely Phase 5's formula, operating on the combined score) — do not add a separate regime-based size adjustment here or in Phase 5. This is deliberate: `RISK_OFF` already restricts the reachable score range to the upper half (≥1.5), so sizing follows naturally without a second mechanism.
- Source waterfall: yfinance (primary) → Finnhub (fallback), same pattern as elsewhere. No Absorption Ratio, Turbulence Index, or any regime signal requiring a trusted historical calibration window — this VIX + SMA check is the entire extent of regime detection in v1.

## Same-Day Handling

A candidate is scored once per calendar day. If it reappears in a later Trading Cycle run the same day, its existing decision stands — do not re-score it even if regime state has since changed intraday.

## Output

Update the candidate's `candidates` record (Phase 0 schema) with: `combined_score`, `trigger_strength_score`, `ai_conviction_score`, `information_sufficiency_modifier` applied (if any), `regime_state_at_decision`, `final_outcome` (`PROCEED`/`ABSTAIN`), `confidence_tier` (if `PROCEED`), abstain reason code (if `ABSTAIN`). Write the corresponding `audit_log` entry regardless of outcome. **Pass the numeric `combined_score` forward to Phase 5 for every `PROCEED` outcome** — Phase 5's position sizing needs the exact value, not just the tier label.

## Boundaries for v1 (explicitly out of scope)

- No AI calls of any kind — purely arithmetic and lookup on already-produced inputs.
- No stop/target or position-sizing math — that's entirely Phase 5, including any use of the confidence tier or combined score for sizing.
- No Absorption Ratio, Turbulence Index, or any lookback-calibrated regime signal.
- No re-scoring of a candidate already decided earlier the same day.
- No regime-based sizing adjustment (see Regime Filter section above).

## Definition of Done

1. Given a STRONG trigger (+2) and STRONG_SUPPORT (+2), combined score = 2.0, `SUFFICIENT` info, `RISK_ON` → outcome `PROCEED`, tier `STRONG`.
2. Given a STRONG trigger (+2) and MODERATE_CONTRADICTION (-1), combined score = 0.5 → outcome `PROCEED`, tier `MODERATE` (confirm this is **not** blocked here — it must reach Phase 5 with `combined_score = 0.5` intact).
3. Given a MODERATE trigger (+1) and STRONG_CONTRADICTION (-2), combined score = -0.5 → outcome `ABSTAIN`, reason `ABSTAIN_NEUTRAL_OR_CONFLICTING` (confirm the boundary value -0.5 lands in this bucket, not the one below it).
4. Given a combined score that would be 1.6 with `LIMITED` info sufficiency, confirm the 0.5 penalty is applied *before* the bucket lookup (final score 1.1 → `MODERATE`, not `STRONG`).
5. Given a MODERATE-tier result during a manufactured `RISK_OFF` regime, confirm it is abstained with `ABSTAIN_RISK_OFF_REGIME`, and confirm the same evidence during `RISK_ON` proceeds normally.
6. Given Phase 3 returning `ABSTAIN`, confirm this phase immediately abstains with `ABSTAIN_UPSTREAM_AI_FAILURE` without attempting any score computation.
