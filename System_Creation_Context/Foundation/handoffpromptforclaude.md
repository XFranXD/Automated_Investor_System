# TBE — Handoff to New Chat
**Written July 2026, end of the design phase, start of implementation**

Paste this as the opening message in a new chat, along with the files listed in Section 1 attached.

---

## 0. Why This Handoff Exists

This conversation went long enough that continuing it costs more quota per turn than a fresh one. Everything below is either (a) already in Claude's memory from this project, or (b) written into the attached documents themselves — this handoff is the connective narrative between them, not a replacement for either. If Claude's memory of this project seems to conflict with anything written here, trust this document and the attached files — they're more precise than a compressed memory summary.

## 1. Required Attachments

**Before continuing, attach these files to the new chat** — they exist only in the old conversation's sandbox, not in memory:

1. `TBE_Constitution.md`
2. `TBE_Gemini_Deep_Research_Prompt.md`
3. `Autonomous_Investment_System_Framework.md` (Gemini's research output)
4. `TBE_Roadmap.md`
5. `TBE_Architecture.md` (already revised once — v2, merged Trading Cycle design)
6. `TBE_Spec_HardGateEngine.md`
7. `TBE_Spec_DiscoveryEngine.md`
8. `TBE_Spec_AIReasoningLayer.md`
9. `TBE_Spec_ScoringRegimeFilter.md`
10. `TBE_Spec_ExecutionEngine.md`
11. `TBE_Spec_PortfolioMonitor.md`
12. `TBE_Spec_LearningAggregator.md`
13. `TBE_ProvisionalParameters_DecisionLog.md`

## 2. What TBE Is (one paragraph, for orientation)

TBE (Automated Investor Bot) is a from-scratch redesign replacing a retired prior project (TBS) — nothing from TBS carries forward except one abstracted technique (sum/count aggregation for unbounded stats). TBE is an autonomous investment *decision-making* system, not a trading bot: it automates judgment (observe → reason → gather evidence → evaluate risk → decide → monitor → learn). Primary objective is capital preservation over profit maximization. It trades both long and short on a 2-20 day swing horizon, using PEAD (post-earnings-drift) and material-filing triggers, paper trading only, targeting Level 4 autonomy, built for Ale's actual constraint: a weekday schedule with almost no attention available for the system during market hours.

## 3. The Full Decision Trail, In Order

This is the narrative the 13 attached documents don't spell out explicitly — how we got from philosophy to locked engineering decisions.

1. **Constitution** established the philosophy: capital preservation first, portfolio-level (not per-trade) optimization, two-tier evidence model (hard gates then equal-weighted scoring), AI restricted to qualitative reasoning only, observational (non-RL) learning, uncertainty allowed to produce "I don't know."
2. **Deep Research** (via Gemini) recommended PEAD as the primary trigger methodology (not the originally-imagined macro/event-driven approach), a hard-gate list (Beneish, Altman, auditor/filing checks, liquidity, OFAC), and six historically-grounded "never" rules — all locked as-is.
3. **A v1 scope constraint got locked before the Roadmap was written**: no subsystem may require manual calibration or a trusted historical lookback window (this is why Absorption Ratio, Turbulence Index, and Conformal Risk Control from the research report are explicitly excluded from v1 — they assume the past year represents the present, which is fragile exactly when it matters most, and Ale doesn't have time to babysit a calibration process).
4. **Roadmap** sequenced 9 build phases with hard definitions of done, specifically to avoid the scope drift that killed TBS (which ran ~4 months before being shut down).
5. **Architecture v1** originally split the pipeline into 5 separately-scheduled jobs. **This was revised (v2) after Ale flagged real-world GitHub Actions delays (70-140 min, confirmed by GitHub's own docs as documented, expected behavior, not a fluke)** — the fix was merging Discovery, Gates, AI-score, and Execute into one self-contained, idempotent "Trading Cycle" job run ~5x/day, with Monitor (existing-position management) as a separate first-in-cycle step. This also fixed a second problem Ale identified: same-day opportunities were being missed by a once-daily discovery design.
6. **Deployment decisions**, made together: MongoDB Atlas (state must live externally, never on GitHub Actions' ephemeral disk), Gemini 3.1 Flash-Lite as the primary AI model (3 API keys = 1500 RPD combined, well above realistic candidate volume), SEC EDGAR + Finnhub + yfinance as data sources (**Alpha Vantage was removed entirely** after Ale caught that its real free-tier limit — confirmed at 25 requests/day — was far too low for how it had initially been used, including as the *primary* news source in one spec).
7. **Seven subsystem specs were written**, each translating one Roadmap phase into implementation-precise detail. Two design calls of note: (a) shorting was explicitly enabled (PEAD works in both directions, so long-only would have ignored half the evidence base) — this required designing a deterministic direction-assignment mechanism for filing-based triggers (a required price/volume confirmation, since a filing has no inherent numeric sign the way an earnings surprise does); (b) Execution Engine and Portfolio Monitor's boundary was decided independently (not pre-specified in Architecture) — Monitor owns the entire lifecycle of *existing* positions (stop-ratcheting, exits), Execution only ever opens *new* ones, specifically so "protect capital before seeking new trades" is structurally true, not just a stated intention.
8. **A companion Provisional Parameters & Decision Log** was written specifically because most of the numeric thresholds across the specs were invented by Claude without dedicated discussion — the log distinguishes PUBLISHED formulas (Beneish, Altman, Chandelier Exit — not really "decisions," just verify correct transcription) from PROVISIONAL numbers (genuinely arbitrary, meant to be revisited once the Learning Aggregator has real paper-trading data) from **INVENTED-SCALE items** (the AI-conviction-to-number mapping and the combined-score decision buckets in Scoring & Regime Filter — these don't correspond to anything external, so no amount of research fixes them; only design discussion or real trade data can).
9. **Two flagged high-stakes numbers got resolved through direct discussion, not research:**
   - **Kill-switch drawdown threshold: locked at 14%** (not the original 8%, not even the first recommendation of 12%). Reasoning: ~1.5% is lost per stopped-out trade by design; a normal (non-crisis) losing streak given ~50% win rate can plausibly reach 6-7 losses in a year, i.e. ~9-10.5% drawdown from pure variance — so 8% was set to fire on ordinary bad luck, not real emergencies. 14% sits above that noise floor while staying below the ~15-20% range where CTA convention says a strategy should be considered to have failed. Widened past 12% specifically because Ale's limited availability means a false-positive halt could sit undiagnosed for days or weeks — better to tolerate a deeper real drawdown than to freeze the system on noise he can't immediately address.
   - **Deterministic-vs-AI evidence weighting: stays exactly as originally specified (genuinely equal-weighted), not changed.** Ale initially wanted to weight deterministic evidence more heavily, worried that requiring strong signals on both sides would make trades too rare. Resolution: this concern is already solved by the existing STRONG/MODERATE two-tier proceed structure — a MODERATE trigger plus merely-neutral AI (not even agreement) already clears the bar to trade under normal regime conditions, so "both pillars must be strong" was a misreading, not a real design gap. No spec change was needed once this was clarified.
10. **One item remains explicitly open**: the combined-score decision bucket cutoffs in Scoring & Regime Filter (the -2 to +2 AI-conviction mapping, the 1.5/0.5/-0.5 thresholds). This is flagged as the single highest-consequence unresolved number in the whole system — it's the literal go/no-go gate for every trade — and was deliberately left for a dedicated design conversation rather than resolved as a side effect of the weighting discussion.

## 4. What's Genuinely Open Right Now

- The combined-score decision buckets (Section 3, item 10 above) — the one item worth resolving before Implementation, not just noting for later.
- Everything else in the Decision Log marked PROVISIONAL (not INVENTED-SCALE, not PUBLISHED) is fine to carry into Implementation as-is — these are meant to be revisited once the Learning Aggregator has real data, not before.

## 5. Next Step

Ale's intent, stated explicitly: once the open item above is resolved (or deliberately deferred), move to **Implementation** — using Ale's own **agent-prompt-architect** skill (already built, Path B: building new systems from scratch) to turn each of the 7 subsystem specs into a precise, ready-to-paste prompt for a coding agent (e.g. Claude Code). This is translation into working code, not further design — no new architectural decisions should get made at this stage; if one seems to be needed, that's a signal something upstream wasn't actually resolved and needs to go back to a spec, not be decided inline while writing a prompt.

## 6. Instruction for Claude in the New Chat

Read all 13 attached files first. Confirm you understand the full decision trail in Section 3 before proceeding — don't re-litigate anything already resolved there unless Ale explicitly reopens it. Then either (a) help resolve the open scoring-bucket question from Section 4, or (b) if Ale says it's fine to defer, move directly into building the first agent-prompt-architect prompt, starting with whichever subsystem Ale wants built first.