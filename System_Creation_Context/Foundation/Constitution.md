# TBE Constitution
### Automated Investor Bot — Governing Document
**Version 1.0 — July 2026**

This document is the foundation for every decision made about TBE from this point forward. It is not an implementation detail — it is the philosophy the implementation must serve. Any future architecture, spec, or line of code that conflicts with this document is wrong by definition, not the document.

TBE succeeds a prior project (TBS). TBS is retired as an implementation. Nothing here inherits from it by default — every principle below stands on its own justification.

---

## 1. Mission

Build an autonomous investment system capable of operating with minimal human intervention while preserving capital and achieving sustainable long-term portfolio growth.

## 2. What TBE Is — and Is Not

TBE is **not** a trading bot. A trading bot automates a pipeline of *signal → trade*. TBE automates a pipeline of judgment:

```
Observe → Reason → Gather Evidence → Evaluate Risk → Decide → Monitor → Learn
```

TBE is an autonomous investor, not an execution engine. It is closer to automating how a disciplined, experienced human investor thinks than to automating a strategy.

## 3. Primary Optimization Objective

TBE optimizes **capital preservation and portfolio longevity — not profit, not return maximization.**

Money is treated as the resource that lets the system keep playing. Losing it ends the game; protecting it is what allows compounding to happen at all. Given a choice between a higher-return path with higher drawdown and a lower-return path with lower drawdown, TBE prefers the latter.

Reference example that defines "success" for this system:

| Profile | Return | Max Drawdown | Win Rate |
|---|---|---|---|
| Rejected | +80% | −55% | 61% |
| Rejected | +28% | −9% | 64% |
| **Target** | **+17%** | **−3%** | **76%** |

Consistency and survival beat magnitude.

## 4. Scope: What Gets Optimized

TBE optimizes **the portfolio, not the individual trade.** A lower-return opportunity that reduces overall portfolio risk can be preferable to a higher-return opportunity that increases it. No trade is evaluated in isolation from the book it would join.

## 5. Investment Horizon

Primary focus: **swing trading**, typical holding period 2–20 days. Intraday is not forbidden — if a stop-loss or take-profit triggers naturally within a day, the position closes that day. Time itself is never the objective; evidence and price action are.

## 6. Decision-Making Philosophy

TBE behaves like a disciplined human investor, not an algorithm chasing every opportunity available to it. The general reasoning flow:

```
Observe → Understand context → Generate hypotheses → Gather evidence →
Evaluate portfolio impact → Evaluate risk → Validate thesis →
Execute only if justified → Monitor → Learn
```

The system is not required to trade because markets are open. **No opportunities found = no trades, and this is a fully acceptable outcome, not a failure state.** TBE is biased toward rejecting opportunities, not toward finding reasons to accept them. The operative question is closer to "which trades should I refuse?" than "which trade should I take?"

There is no single rigid strategy. There is one investment decision framework, inside which different analytical methodologies (technical, fundamental, event-driven, momentum, sentiment, macro, future methods) act as interchangeable tools, not competing identities. Every methodology must justify its own complexity — nothing is added to the framework simply because it exists.

## 7. Evidence Evaluation Model

Evidence is not evaluated as one undifferentiated pool. TBE uses a **two-tier model**:

1. **Hard gates.** A small, deliberately short list of severe, binary disqualifiers (e.g., confirmed accounting fraud, insolvency risk, active regulatory action, delisting risk) reject a candidate outright. No score is computed once a gate fails — the candidate simply does not proceed.
2. **Equal-weighted scoring among survivors.** Once a candidate clears all gates, the remaining evidence (technical, momentum, fundamentals, sentiment, etc.) is scored with equal weighting, without arguing over which signal deserves more importance than another.

This mirrors how a human investor reasons: some facts don't get "outvoted" by good news elsewhere, they end the conversation.

## 8. Risk Philosophy

Risk precedes return. Every position uses defined stop-loss and take-profit (hit-limit) levels — capital protection is structural, not discretionary. High-risk opportunities are frequently rejected outright rather than sized down. A rejected-for-now candidate is not necessarily discarded — it may become a **watch candidate**, monitored without capital at risk until conditions change.

## 9. AI Philosophy

AI is used only where traditional software cannot do the job as well:

- **Use AI for:** reasoning, interpreting news and language, macroeconomic reasoning, connecting unrelated events, hypothesis generation, qualitative and ambiguous evidence evaluation, explaining decisions in natural language.
- **Do not use AI for:** mathematics, statistics, indicators, position sizing, sorting, filtering, database operations, or any task expressible as deterministic logic.

Rule of thumb: if a task can be written as deterministic math or code, it stays in code. If it requires interpreting uncertain or qualitative information, AI is the appropriate tool.

## 10. Learning Philosophy

TBE learns **observationally, not behaviorally.**

```
Trades → Statistics accumulate → Patterns emerge → Research improves → Future versions improve
```

This is explicitly **not** reinforcement learning. TBE never loses money in order to learn — learning supports future decisions, it never justifies a poor decision in the present. Statistics accumulate from closed trades using techniques that scale to unbounded history without storing every record (e.g., running sum + count rather than a growing list), but the learning loop is decoupled from any individual trade's execution logic.

## 11. Prediction Philosophy

Prediction does not control capital. A prediction/forecasting subsystem, if built, operates as a **research-only** track: it generates hypotheses, paper-trades them, measures its own accuracy, and improves — entirely separate from the live decision path. Production decisions react to evidence that has already emerged, not to forecasts of what might emerge.

## 12. Handling Uncertainty

TBE is allowed to produce a valid confidence score when the available evidence supports one. When key data is missing or untrustworthy, TBE states this explicitly and skips the opportunity rather than forcing a number. "Insufficient evidence to decide" is a first-class, valid outcome — not a failure of the system.

## 13. Automation & Target Autonomy

Target: **Level 4 autonomy** — fully autonomous except where legal, API, or security constraints require human involvement. Checking the system on a weekly or biweekly cadence is the intended human touchpoint, not daily supervision.

## 14. Explainability

Explainability is secondary to correctness, but every investment decision leaves an auditable record: the reasoning, the evidence, the conditions, and the risk assessment behind it are stored, even when the reasoning itself is AI-generated natural language.

## 15. Success Criteria

TBE is successful if, over time, it demonstrates:

- Capital preservation as the dominant outcome (low drawdown, high win rate) over raw return maximization.
- A willingness to sit out — no-trade periods are evidence of discipline, not malfunction.
- Decisions that are auditable and evidence-based, not speculative or forecast-driven.
- Progress toward Level 4 autonomy without loosening the capital-preservation objective to get there.

## 16. Research Objectives

The Deep Research phase that follows this constitution must operate **within** these principles, not invent new ones. Its objective is not "find the best trading strategy." Its objective is:

> Design the optimal autonomous investment decision framework for TBE — determining how expert investors reason under uncertainty, how they protect capital, how they adapt to changing market conditions, which methodologies complement or conflict with one another, how AI should participate in that reasoning, and what evidence hierarchy should govern decisions — given TBE's mission, constraints, and philosophy as defined above.

## 17. Deferred to Research

One category of decision is intentionally left open by this constitution rather than invented here: the specific list of architectural "never" rules (e.g., never average down automatically, never override a stop-loss, never risk more than X% on a single position). These are treated as candidates to be *discovered* — ideally converging from what independent, successful long-term investors treat as non-negotiable — rather than authored from personal preference. They will be locked down after the research phase, before architecture is finalized.

---

*This document supersedes any prior TBS-era philosophy. It is the reference point for the Deep Research prompt, the roadmap, the architecture, and every subsystem spec that follows.*