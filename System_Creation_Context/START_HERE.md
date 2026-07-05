# TBE — Start Here (Read This First)

## What This Is

TBE (Automated Investor Bot) is an autonomous investment *decision-making* system — not a trading bot. It automates judgment (observe → reason → gather evidence → evaluate risk → decide → monitor → learn), optimizing for capital preservation over profit maximization. It trades both long and short on a 2-20 day swing horizon using PEAD (post-earnings-drift) and material-filing triggers, paper trading only, built to run unattended with minimal human oversight (weekly/biweekly check-ins, not daily supervision).

## Folder Contents & Reading Order

**Read these three in full, in this order, before writing any code:**
1. `Constitution.md` — the governing philosophy. Everything else must serve this; nothing overrides it.
2. `Architecture.md` — how the pieces fit together: deployment model, data layer, scheduler design, the AI/deterministic boundary, the never-list.
3. `Roadmap.md` — the build sequence and why it's ordered this way.

**Not for the agent — `decisionsmade_specs.md` (the Provisional Parameters & Decision Log) is a human-facing review document, not build input.** It says so explicitly in its own opening line. Every piece of it that actually matters for implementation — which numbers must not be changed, and why — has already been folded into the v1.1 specs and the relevant build prompts (Phase 4, Phase 5) directly, with explicit "do not deviate" instructions. This file exists for Ale's own future review once the Learning Aggregator has real data; it isn't part of what the agent needs to read.

**Subsystem specs — full design rationale for each phase, read once for context:**
- `hardgateengine_specs.md`, `discoveryengine_specs.md`, `AIreasoning_specs.md`, `scoreandregimefilter_specs.md`, `executionengine_specs.md`, `portfoliomonitor_specs.md`, `learningaggregator_specs.md`

**Important — two of these specs have been revised since they were first written:** `scoreandregimefilter_specs.md` and `executionengine_specs.md` are both **version 1.1**, updated to add conviction-proportional position sizing (resolving an edge case in the original go/no-go scoring logic). If your folder somehow contains an older copy of either file, discard it — only the v1.1 version (check the header) is current.

**Background only — not required to implement anything, skip unless you want the "why" behind a recommendation that isn't otherwise explained in the docs above:**
- The Deep Research prompt and its raw output (Gemini's research report). Every actionable conclusion from these has already been distilled into the Constitution, Architecture, and specs above — there is nothing in the raw research that should change what you build.

**Build prompts — execute these one at a time, strictly in this order, in the same repo/session throughout:**
1. `phase0_foundations_prompt.md`
2. `phase1_hardgate_prompt.md`
3. `phase2_discovery_prompt.md`
4. `phase3_aireasoning_prompt.md`
5. `phase4_scoringregime_prompt.md`
6. `phase5_execution_prompt.md`
7. `phase6_portfoliomonitor_prompt.md`
8. `phase7_learningaggregator_prompt.md`
9. `dashboard_prompt.md` — build this **last**, only once Phases 0-7 exist and have real data flowing through them.

## Rules for Working Through This

- Do not start a phase until the previous phase's Definition of Done is fully, verifiably satisfied. If it isn't, stop and fix it before moving on — do not carry a half-working phase forward and hope it gets fixed later.
- The subsystem specs are the full rationale behind each build prompt. If a build prompt is ever ambiguous, consult the matching spec. **If a build prompt and its spec ever conflict, trust the build prompt** — it reflects decisions resolved after the specs were originally written (this applies specifically to Execution Engine's position sizing and Scoring & Regime Filter's conviction scale).
- Do not re-derive, second-guess, or "improve" the combined-score bucket cutoffs, the ±2 AI-conviction scale, the conviction-proportional sizing formula, or the 14% kill-switch threshold — each build prompt already states explicitly where this applies and why. These went through deliberate discussion and are meant to be trusted, not re-optimized while implementing.
- Numbers not called out this way (liquidity floors, lookback windows, the LIMITED-info penalty, etc.) are placeholders picked for concreteness, not externally validated — implement them exactly as given, but there's no need to defend or improve them either; they're intentionally left as-is for now, to be revisited later with real output from the Learning Aggregator.
- Every build prompt reuses Phase 0's schema, audit-logging utility, and shared data-source client module by reference rather than re-specifying them. Don't reimplement fallback/waterfall logic locally in a later phase — extend the Phase 0 module if a new method is needed.

## Expected Secrets

See the accompanying secrets list (or the message this file was delivered alongside) for the full set of environment variables/GitHub Secrets this project needs before Phase 0 can run end-to-end.