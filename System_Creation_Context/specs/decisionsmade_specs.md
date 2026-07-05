# TBE Provisional Parameters & Decision Log
### Companion to all seven subsystem specs
**Version 1.1 — July 2026** (Scoring & Regime Filter and Execution Engine sections updated: the combined-score go/no-go issue has been resolved through discussion — see the new narrative section at the end of this document)

## Purpose of This Document

This is **not** a subsystem spec, and a coding agent should not treat it as a build instruction — it's a review document for Ale, and for isolating anything that might be hallucinated or AI-biased before code exists, while that's still cheap to fix. Every number and design decision below was made by Claude while writing the seven specs, without a dedicated back-and-forth the way the earlier locked decisions (long/short, evidence model, deployment shape) got. Items marked **RESOLVED** below have since gone through that back-and-forth explicitly and should be trusted; anything still marked PROVISIONAL or INVENTED SCALE has not, and should not be assumed correct just because it's written down with confidence elsewhere.

Categories, and they need different treatment:

- **PUBLISHED** — a fixed formula or widely-cited convention (Beneish, Altman, Chandelier Exit). Not something to "tune" — either the formula is being applied correctly or it isn't.
- **PROVISIONAL** — a number Claude picked to make a spec concrete, with no external validation. These are exactly what the Learning Aggregator (Phase 7) exists to eventually test against real trade outcomes.
- **RESOLVED** — discussed directly with Ale, with an explicit chain of reasoning behind the final value, the same way the kill-switch threshold was resolved previously.

---

## Hard-Gate Engine

| Item | Value | Type | Notes |
|---|---|---|---|
| Beneish M-Score threshold | > -1.78 | PUBLISHED | Standard academic threshold, not invented |
| Altman Z-Score threshold | < 1.81 | PUBLISHED | Standard "distress zone" threshold |
| Minimum ADV | $5,000,000 | PROVISIONAL | No sourcing beyond "reasonable-sounding" |
| Minimum share price | $5.00 | PROVISIONAL | Common penny-stock cutoff convention, not TBE-specific research |
| Auditor-change lookback | 12 months | PROVISIONAL | |
| Delinquent-filing lookback | 6 months | PROVISIONAL | |
| Adverse-opinion keyword list | 4 fixed phrases | PROVISIONAL, deliberately blunt | Will produce false positives by design; see spec Section 5.4 |

## Discovery Engine

| Item | Value | Type | Notes |
|---|---|---|---|
| EPS surprise threshold | ≥5% | PROVISIONAL | |
| EPS surprise, near-zero-consensus fallback | ≥$0.05 | PROVISIONAL | |
| 8-K qualifying item list | 1.01, 2.01, 2.05, 5.02, 8.01 | PROVISIONAL | Other items (e.g. bankruptcy, delisting) arguably belong here too — see spec Section 2.2 note |
| Filing price/volume confirmation | ≥3% move, ≥1.5x avg. volume | PROVISIONAL | This is also what sets the direction for filing-based triggers — an incorrect threshold here doesn't just misfire, it could assign the wrong direction |

## AI Reasoning Layer

| Item | Value | Type | Notes |
|---|---|---|---|
| Conviction scale | 5 categories (STRONG_SUPPORT → STRONG_CONTRADICTION) | DESIGN CHOICE | Could be simpler (3-category) — not revisited; the *numeric mapping* of this scale is now resolved (see Scoring & Regime Filter row below), but the category count itself was not part of that discussion |
| Retry policy | 1 retry on schema failure, 1 retry + key rotation on API failure | PROVISIONAL | |

## Scoring & Regime Filter

| Item | Value | Type | Notes |
|---|---|---|---|
| Trigger strength thresholds | 10%/6% = STRONG, 5%/3% = MODERATE | PROVISIONAL | Reuses Discovery's thresholds as the MODERATE floor |
| AI conviction → number mapping | +2 to -2, symmetric | **RESOLVED** — kept as originally specified, now with real justification | Discussed directly: should contradiction be weighted more heavily than support, given the Constitution's rejection bias? Decided **no** — the range must match trigger-strength's ±2 scale for the equal-weighted evidence model to hold in practice, not just in the formula's name; a wider or asymmetric AI range would let qualitative evidence silently dominate the average. The system's rejection bias is instead expressed through position sizing (see Execution Engine row below), not through further-skewing the gate itself. Granularity (5 categories) was not reopened — only the numeric spacing was. |
| LIMITED-info penalty | -0.5 | INVENTED SCALE | **Still open, deliberately deferred.** Discussed briefly; decided this is lower-priority than the bucket cutoffs since a LIMITED-penalized borderline trade is now automatically sized smaller anyway (see Execution Engine row) — the sizing fix absorbs most of the risk this number posed. Revisit once real trade data exists. |
| Combined-score decision buckets | ≥1.5 STRONG, 0.5–1.5 MODERATE, -0.5–0.5 ABSTAIN, <-0.5 ABSTAIN | **RESOLVED** — kept exactly as originally specified | This was the single most consequential open item in the whole system. Resolved not by changing the cutoffs themselves, but by fixing the actual problem they exposed (see the full narrative at the end of this document): a strong deterministic trigger could outweigh a real AI contradiction and still produce a PROCEED. Rather than narrowing the gate (which would risk repeating TBS's failure mode of long trade-free stretches later found to have been missed opportunities), the fix makes the *consequence* of a borderline PROCEED proportional to how contested the evidence was, via conviction-proportional position sizing in Execution Engine. The bucket boundaries themselves remain unvalidated by real data and should still be revisited once the Learning Aggregator has enough closed trades to check them against. |
| VIX regime threshold | >30 = elevated | PROVISIONAL, grounded in convention | Could be sharpened with a quick targeted check, not a full research pass — flagged previously as "worth a look," not done |
| Trend filter | Below 50-day SMA = downtrend | PROVISIONAL, grounded in convention | |
| Regime effect on position sizing | None — RISK_OFF affects the gate only, not sizing directly | **RESOLVED** — deliberate, not an oversight | Discussed directly: should RISK_OFF also independently shrink position size, on top of already restricting PROCEED to STRONG-tier candidates? Decided no — RISK_OFF already only allows through the upper half of the score range (≥1.5), so conviction-proportional sizing already lands those trades in the upper half of the sizing range by construction. A second, independent regime-based size reduction was judged to be solving the same concern twice. |

## Execution Engine

| Item | Value | Type | Notes |
|---|---|---|---|
| Risk per trade | Conviction-proportional: `0.75% + (combined_score − 0.5)/(2.0 − 0.5) × (1.5% − 0.75%)` | **RESOLVED** — replaces the original flat 1.5% | New mechanism added specifically to resolve the combined-score go/no-go issue. `max_risk = 1.5%` was deliberately kept unchanged from the original flat rate, since the kill-switch's 14% threshold math was built on a ~1.5%-per-trade-loss assumption — changing the ceiling would have silently invalidated that already-resolved reasoning. `min_risk = 0.75%` (half of max) was chosen because a combined score of exactly 0.5 is, by definition, the weakest evidence the system will act on at all; half-size keeps the trade meaningful while ensuring the weakest-conviction trades never risk as much as the strongest ones. See full narrative at the end of this document. |
| ATR period | 22 days | PUBLISHED | Chandelier Exit's standard period |
| Stop multiplier | 3×ATR | PUBLISHED | Chandelier Exit's standard multiplier |
| Take-profit ratio | 2:1 reward:risk | PROVISIONAL | |
| Correlation cap | 0.6 (0.4 in RISK_OFF) | PROVISIONAL | |
| Sector exposure cap | 25% | PROVISIONAL | |
| Liquidity capacity cap | 10% of 20-day ADV | PROVISIONAL | |

## Portfolio Monitor

| Item | Value | Type | Notes |
|---|---|---|---|
| Kill-switch drawdown threshold | 14% from high-water mark | **RESOLVED** — reasoned from math + convention; reasoning strengthened further by the sizing change above | Original reasoning: ~1.5% lost per stopped-out trade; normal-variance losing streaks (no real crisis, just bad luck) land around 10-11% given a ~50% win rate. 14% sits above that noise floor while staying below the 15-20% range where a strategy is conventionally considered to have failed. Widened past the original 12% recommendation specifically because a false-positive halt could sit unresolved for days/weeks given Ale's schedule. **Update:** now that most PROCEED trades risk somewhere between 0.75% and 1.5% rather than a flat 1.5%, an ordinary losing streak will typically consume equity more slowly than the original math assumed — a given string of losses now generally costs less than it would have under flat sizing. The 14% threshold itself does not need to change; its existing safety margin is simply somewhat wider than originally estimated, meaning reaching 14% is now a slightly stronger signal of genuine trouble rather than ordinary variance. |

---

## How These Get Resolved

1. **PUBLISHED items** — verify the formula is transcribed and applied correctly; nothing to "decide."
2. **PROVISIONAL items grounded in convention** (VIX, SMA, liquidity floors) — a quick targeted check could sharpen these before implementation, if you want it; not worth a full Deep Research pass, per the earlier discussion.
3. **INVENTED-SCALE items still open** (the LIMITED-info penalty) — no external research fixes this, because the scale itself doesn't exist outside this project. This is exactly what the Learning Aggregator's dimension-bucketed stats (by confidence tier, by regime, etc.) are specifically built to eventually test against real outcomes — see that spec's Section 6.
4. **RESOLVED items** — the kill-switch threshold, the AI-conviction scale, the combined-score buckets, and the new conviction-proportional sizing mechanism — have each gone through direct discussion with an explicit chain of reasoning, and should be treated as locked for implementation, not re-litigated without a specific new reason to reopen them.

---

## Narrative: How the Combined-Score Go/No-Go Issue Was Resolved

This section exists because the resolution wasn't a single number change — it was a chain of reasoning worth preserving so a future reader (including Ale, months from now) understands *why* the buckets look unchanged despite this having been the most heavily discussed open item in the system.

**The problem, restated precisely:** the combined score is built from two stacked, unvalidated scales (the AI conviction mapping and the LIMITED penalty) feeding into bucket cutoffs that were also unvalidated — and no external research or formula could fix any of it, because none of these scales correspond to anything outside this project (unlike Beneish or Altman, there's no textbook to check them against). The sharpest concrete symptom: a STRONG trigger (+2) combined with the AI expressing MODERATE_CONTRADICTION (-1) still averages to +0.5 — clearing the PROCEED threshold even though the AI is actively arguing against the trade, not merely staying neutral.

**Two ways to fix an unvalidated threshold were considered:** narrow the gate itself (raise the bar, or weight contradiction more heavily), or change what happens once a trade already clears the gate. Narrowing was rejected deliberately, for a reason grounded in TBS's own history: TBS went through long stretches with no trades, and multiple opportunities from those stretches were later reviewed and confirmed (with contrasted data and AI review) as trades that should have been taken. Not trading feels safe but isn't free — it has a real cost (missed compounding), and over-narrowing the gate risks repeating that exact failure mode. The Constitution's capital-preservation objective is about controlling losses, not eliminating trades altogether.

**The resolution:** rather than making the gate stricter, position sizing was made proportional to how strong the combined evidence actually was, within the PROCEED range that already exists (Execution Engine, Section 4). A borderline PROCEED — like the STRONG-trigger-vs-MODERATE-contradiction case above — now still executes, but at close to half size rather than full size. If the AI's objection was right, less money is lost. If the deterministic trigger was right, a smaller win is still a win. This also directly reflects a broader point raised in discussion: TBE isn't meant to avoid losing, it's meant to make losing controlled and bounded rather than unpredictable — "embracing" loss as part of the equation rather than treating any loss as a system failure.

**Why the AI-conviction scale was kept symmetric rather than weighted toward contradiction:** a related question was whether AI-flagged contradictions should count for more than equivalent support, given the system's stated bias toward rejection and the fact that the deterministic trigger has no real mechanism to sanity-check the AI's read, only vice versa. Decided against, for two reasons. First, mechanically: the combined score is a straight average, so the AI-conviction range has to match the trigger-strength range (±2) for "equal-weighted" to be true in more than name — an asymmetric or wider AI range would let qualitative evidence silently dominate every decision. Second, philosophically: the AI Reasoning Layer already only reasons over specific, assembled text evidence (filing text, earnings releases, targeted news) rather than open-ended market sentiment, which limits (though doesn't eliminate) its exposure to the kind of sentiment-driven noise or manipulation that was raised as the underlying worry. The sizing mechanism above already responds proportionally to AI disagreement without needing to additionally distort the scale that produces it — stacking both changes would solve the same concern twice and narrow the trading window further than intended, without any real trade data yet showing the symmetric scale is too permissive.

**What remains genuinely open:** the LIMITED-info penalty (-0.5) was not part of this resolution and stays deferred, on the reasoning that the sizing fix already reduces its practical impact. The bucket cutoffs (1.5 / 0.5 / -0.5) and the ±2 conviction scale are now justified by explicit reasoning rather than convenience, but they are still not *validated* by real outcomes — that validation can only come from the Learning Aggregator once enough paper trades have closed. Nothing in this resolution should be read as claiming these numbers are correct, only that they are now deliberately chosen and their consequences are bounded and understood.