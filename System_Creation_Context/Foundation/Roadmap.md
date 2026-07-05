# TBE Roadmap
### Automated Investor Bot — Build Sequence
**Version 1.0 — July 2026**

This roadmap sequences *what gets built and in what order*, not how each piece works internally (that's Architecture and Subsystem Specs, which follow this document). Each phase has an explicit definition of done and an explicit exclusion list, to prevent the scope drift that ended TBS. Phases are milestone-gated, not calendar-gated — a phase is "done" when its definition of done is met, whether that takes three days or three weeks. There are no fixed dates in this document on purpose.

## Governing Constraints (recap)

- Capital preservation over profit; portfolio-level optimization, not per-trade.
- Two-tier evidence model: hard gates first, equal-weighted scoring for survivors.
- AI is qualitative-only; all math, sizing, and execution logic is deterministic code.
- Learning is observational (aggregated stats from closed trades), never reinforcement-style.
- Paper trading only — no live capital anywhere in this roadmap.
- **v1 excludes any subsystem requiring manual calibration or a trusted historical lookback window.** Only fixed published formulas (Beneish M-Score, Altman Z-Score) and self-contained deterministic math (ATR, Chandelier Exit, correlation caps) are in scope. Absorption Ratio, Turbulence Index, and Conformal Risk Control are explicitly deferred — not scheduled, not promised, only reconsidered later if they can self-calibrate from TBE's own accumulated paper-trading history with zero manual tuning.
- The six architectural "never" rules (kill switch required, position never exceeds liquidity capacity, stop-loss never loosens live, never average down, never assume historical correlation holds in a crisis, never trade live capital to explore/learn) are locked and apply from Phase 0 onward — they are not a later addition, they constrain every phase below.

---

## Phase 0 — Foundations & Infrastructure

**Goal:** A skeleton that can pull data, simulate a trade, and record everything, before any intelligence is added.

**Builds:**
- Market data ingestion (price, volume, fundamentals, filings) for a candidate universe.
- Paper trading execution harness — simulates fills, tracks open/closed positions, no real broker connection.
- Storage schema for trades, candidates, and decisions, including the mergeable sum/count aggregation pattern for stats that must scale without storing every record forever.
- Audit-trail logging: every decision (including rejections and abstentions) is recorded with its reasoning, per the explainability principle.

**Definition of done:** A ticker can be pulled, a simulated trade can be opened and closed on paper, and the full lifecycle is queryable from storage with an audit trail.

**Excluded:** Any scoring, gating, or AI logic. This phase is plumbing only.

---

## Phase 1 — Deterministic Hard-Gate Engine

**Goal:** The disqualifier layer that eliminates unacceptable candidates before anything else touches them.

**Builds:**
- Beneish M-Score (fraud detection) and Altman Z-Score (insolvency detection) — both fixed formulas, zero calibration.
- Auditor resignation / adverse opinion detection, delayed-filing detection.
- Liquidity minimums (ADV threshold, spread threshold).
- Sanctions/OFAC screening.

**Definition of done:** Given a ticker, the system outputs a pass/fail per gate with the specific reason for any failure, and a candidate that fails any gate never proceeds further in the pipeline.

**Excluded:** Scored (non-gate) evidence, AI involvement, sizing logic.

---

## Phase 2 — Candidate Discovery (External Trigger Engine)

**Goal:** A deterministic scanner that finds candidates worth evaluating at all, so the system never generates a hypothesis out of thin air.

**Builds:**
- Detection of quantified, external triggers appropriate to the 2–20 day horizon (earnings surprises / PEAD-type signals, material filings such as 8-Ks, and comparable quantified events).
- Candidates with a valid trigger are passed to Phase 1's gates.

**Definition of done:** The system can independently identify a list of tickers with a live, quantified trigger, and route only gate-surviving candidates onward. No trigger, no candidate — the system does not go looking for reasons to trade.

**Excluded:** Any AI-generated hypothesis without a prior deterministic trigger — this ordering is intentional and non-negotiable per the AI/code boundary.

---

## Phase 3 — AI Reasoning Layer

**Goal:** Qualitative interpretation, strictly bounded to candidates that already cleared Phases 1 and 2.

**Builds:**
- Structured AI evaluation (schema-constrained output, not free text) of news, filings, and available qualitative context for a gated, triggered candidate.
- Output: a qualitative conviction label and any flagged risks — never a raw number the deterministic layer has to interpret loosely.

**Definition of done:** For any gated, triggered candidate, the AI produces a structured, schema-validated qualitative assessment that deterministic code can consume without parsing free-form prose.

**Excluded:** Any math, scoring, or position sizing performed by the AI. The AI never touches a number that controls capital.

---

## Phase 4 — Scoring, Confidence, and Simple Regime Filter

**Goal:** Combine deterministic and AI evidence into a decision, with the ability to say "not enough to decide."

**Builds:**
- Equal-weighted scoring across surviving evidence (deterministic metrics + AI qualitative output).
- A **simple** regime signal (e.g., a volatility index level plus a basic trend filter) that toggles a risk-on/risk-off posture — deliberately not the Absorption Ratio/Turbulence Index machinery, per the v1 constraint.
- Confidence handling: produce a valid score when evidence supports one; explicitly skip and log the reason when data is missing, conflicting, or untrustworthy, rather than forcing a number.

**Definition of done:** A gated, triggered, AI-evaluated candidate produces a final score, a confidence level, and a proceed/abstain decision, with the regime state factored into the threshold.

**Excluded:** Any statistical regime model requiring a trusted historical window.

---

## Phase 5 — Deterministic Execution & Position-Level Risk

**Goal:** Turn an approved candidate into a correctly sized, correctly protected paper position.

**Builds:**
- ATR-based position sizing (capital risk capped per trade, e.g. 1–2% of portfolio equity).
- Chandelier Exit trailing stop — ratchets only in the trade's favor, never loosens.
- Pre-trade correlation check against existing holdings (rolling correlation, reduce or reject above a defined threshold) and sector exposure cap.
- Kill-switch and output-reconciliation logic per the never-list (Knight Capital lesson) active from this phase onward.

**Definition of done:** The system can size, open (paper), manage, and close a single position end-to-end with every position-level risk rule enforced automatically, with no path for AI to intervene on the stop.

**Excluded:** Portfolio-wide (multi-position) risk aggregation — that's Phase 6.

---

## Phase 6 — Portfolio-Level Monitoring & Circuit Breakers

**Goal:** Risk management across the whole book, not just one trade at a time.

**Builds:**
- Aggregate exposure tracking (sector caps, correlation caps across the full open book).
- A simple, deterministic portfolio-level drawdown circuit breaker (e.g., halt new entries and tighten existing stops if the portfolio breaches a defined drawdown threshold) — the simplified stand-in for the report's Conformal-Risk-Control-based circuit breaker.
- The "never assume historical correlation holds in a crisis" rule enforced structurally (no leverage, correlation assumptions treated as void once the regime filter flags risk-off).

**Definition of done:** The system can detect a portfolio-wide risk condition and autonomously reduce new exposure and tighten existing protections without a per-trade trigger being the only thing standing in the way.

**Excluded:** Any lookback-window-dependent systemic risk model.

---

## Phase 7 — Observational Learning Loop

**Goal:** Closed trades become durable statistics without unbounded storage growth or manual review requirements.

**Builds:**
- Aggregation of closed trades into running statistics using the sum/count pattern (mergeable batch records), enabling win rate, average return, expectancy, and drawdown stats without storing every trade forever.
- Periodic performance reporting.

**Definition of done:** After a batch of closed paper trades, the system produces accurate aggregate performance statistics, and this aggregation never requires Ale to manually review or recalibrate anything for it to keep functioning.

**Excluded:** Automatic parameter rewriting or strategy changes based on this data — this loop informs, it does not self-modify decision logic in v1.

---

## Phase 8 — End-to-End Paper Trading Validation

**Goal:** Prove the whole pipeline runs unattended, on paper, for real.

**Builds:** Nothing new — this phase is operating the system built in Phases 0–7 continuously on paper trading, with Ale checking in periodically rather than supervising continuously (matching the target autonomy level, scaled to what v1 can actually support).

**Definition of done:** A sustained run of autonomous paper trading (a defined number of trades or weeks, TBD when this phase is reached) producing a full audit trail for every decision, including abstentions, with no manual intervention required to keep the system running correctly.

---

## Explicitly Deferred — Not Part of This Roadmap

These are not "Phase 9." They are candidates only, revisited exclusively if TBE is still alive and generating its own data after Phase 8:

- Absorption Ratio / Turbulence Index-based regime detection.
- Conformal Risk Control / Regime-Weighted Conformal calibration for VaR.
- Any self-calibration engine for the above — and only if it can calibrate from TBE's own accumulated paper-trading history, with zero manual tuning time from Ale.
- Live/real-money trading and broker integration.
- Any AI-generated hypothesis path that doesn't originate from an external deterministic trigger.

## Sequencing Logic (why this order)

Gates come before AI because cheap, deterministic rejection should filter the pool before anything expensive or interpretive touches a candidate — consistent with the constitution's "biased toward rejecting" stance. AI comes before scoring because scoring needs both deterministic and qualitative inputs to exist first. Execution is isolated into its own phase, after scoring, because sizing and stops must never be influenced by anything upstream once a decision is made — that separation is the AI/code boundary made physical. Portfolio-level monitoring comes after single-position execution works, because you can't manage a book before you can correctly manage one position. Learning comes last because it needs a body of closed trades to aggregate — there's nothing to learn from before Phase 5 produces trade history. Validation is the final gate before any conversation about advanced statistics, self-calibration, or real capital — none of which are part of this roadmap.