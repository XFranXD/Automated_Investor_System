# TBE Subsystem Spec: AI Reasoning Layer
### Phase 3 of the Roadmap - Architecture Section 4/5
**Version 1.0 — July 2026**

## 1. Purpose

Provide qualitative interpretation for a candidate that has already cleared the Hard-Gate Engine and already has a deterministic trigger and direction from the Discovery Engine. This is the *only* subsystem in TBE permitted to call an AI model, and it is invoked under a strict precondition: no candidate reaches this subsystem without first passing gates and having a Discovery-assigned trigger and direction (Architecture Section 5). The AI never originates a candidate, never assigns direction, and never outputs a number that controls capital — it assesses and explains, nothing more.

## 2. Model & Capacity

**Primary model: Gemini 3.1 Flash-Lite** — stable release, frontier-class quality at low cost, matching the locked model-selection decision. Three separate API keys (separate Google Cloud projects) are used in sequence: if the active key hits its daily request cap, the next key takes over for the remainder of that day. Combined capacity across all three keys comfortably exceeds realistic daily candidate volume (estimated in the tens, not hundreds, per day given the trigger-first Discovery design).

**Fallback model pool** (the ~20 RPD preview-tier models mentioned earlier) is reserved for genuine overflow only — an unusually high-volume day that exhausts all three primary keys, or a primary-model outage. It is not baseline capacity and the spec should not be built assuming it's routinely available.

## 3. Precondition Enforcement

This subsystem's entrypoint accepts only a `candidates` record with `gate_result = PASSED`. There is no code path that allows a call into this subsystem for a candidate without that status — this is the concrete mechanism behind Architecture Section 5's "no reasoning without a prior deterministic trigger" rule, not a convention the calling code is expected to remember.

## 4. Input Assembly

For a gate-passed candidate, assemble the following context before calling the model:

- **Trigger context** (from Discovery): trigger type, direction, and trigger details (surprise %, or filing item + price/volume confirmation).
- **Primary text evidence:**
  - For earnings-triggered candidates: the earnings press release text (often filed as an 8-K Item 2.02 exhibit, retrievable via EDGAR) if available.
  - For filing-triggered candidates: the qualifying filing's text itself (already being retrieved for item classification in Discovery).
- **Supplementary news context:** recent news items for the ticker via Finnhub's company-news endpoint (free tier, 60 requests/minute — comfortably covers this). yfinance's news feature is the fallback if Finnhub is unavailable. *(Alpha Vantage's News & Sentiment API was the original candidate for this role, but its free tier is confirmed at only 25 requests/day — far too low to serve as the primary source for every AI-scored candidate, which is exactly what this step would have required.)*

If no text evidence can be assembled at all (filing text unavailable, no news found), the candidate still proceeds to the model call, but the prompt explicitly states evidence is minimal — this is a legitimate input state, not an error, and the model's `information_sufficiency` field (Section 5) is how that gets communicated downstream rather than silently guessing.

## 5. Output Schema

Enforced via Gemini's native structured-output mode (response schema passed directly in the API request, not parsed from free text after the fact). Any response that fails schema validation is treated as in Section 7 — it is never partially accepted or repaired.

```json
{
  "conviction": "STRONG_SUPPORT | MODERATE_SUPPORT | NEUTRAL | MODERATE_CONTRADICTION | STRONG_CONTRADICTION",
  "risk_flags": ["short string", "short string", "..."],
  "information_sufficiency": "SUFFICIENT | LIMITED | INSUFFICIENT",
  "rationale": "1-3 sentence plain-language explanation"
}
```

- **`conviction`** is assessed *relative to the direction Discovery already assigned* — the model is never asked "should this be long or short," only "does the qualitative evidence support or undercut the [long/short] case Discovery already made." This is the mechanism that keeps direction-setting entirely deterministic while still letting AI meaningfully weigh in.
- **`risk_flags`** is a short list of specific, concrete flags grounded in the evidence provided (e.g. "management tone notably cautious on guidance," "pending litigation mentioned in filing," "recent news sentiment mixed") — not a freeform paragraph, and not padded with generic boilerplate flags.
- **`information_sufficiency`** lets the model report when it genuinely didn't have much to work with, rather than manufacturing confidence from thin evidence. `INSUFFICIENT` here is a strong signal to the downstream Scoring & Regime Filter that this evaluation should weigh toward abstention.
- **`rationale`** is the human-readable record for the audit trail — this is what satisfies the Constitution's explainability requirement for this subsystem's contribution to a decision.

Nothing in this schema is a number that sizes a position, sets a stop, or otherwise controls capital — those stay entirely in the Execution Engine, untouched by anything produced here.

## 6. Prompt Construction Principles

The prompt (system instruction + assembled context from Section 4) must explicitly state, every call:

- Its role is limited to qualitative assessment of the evidence provided — it does not have, and should not assume, access to real-time price data, technical indicators, or anything the deterministic layers already compute.
- It must not suggest a trade direction different from the one already given — its job is to evaluate the *existing* direction's supporting evidence, not second-guess Discovery's deterministic trigger.
- It must not invent facts not present in the assembled context — if the provided text doesn't address something, that's a gap to note (via `information_sufficiency` or a risk flag), not something to fill in from general knowledge.
- Output must conform exactly to the schema in Section 5 — no additional commentary outside the structured fields.

## 7. Failure & Retry Handling

- **Schema validation failure:** retry the call once. If the retry also fails validation, the evaluation is recorded as `ABSTAIN`, reason code `AI_SCHEMA_VALIDATION_FAILED` — this is distinct from a `STRONG_CONTRADICTION` conviction (a real assessment that argues against the trade) and must not be confused with one downstream.
- **API/network failure or timeout:** retry once with the same key; if it fails again, fail over to the next API key in the rotation (Section 2) before giving up. Only after all three primary keys are exhausted or failing does this candidate's evaluation get recorded as `ABSTAIN`, reason code `AI_UNAVAILABLE`.
- **All-keys-exhausted (daily cap hit across all three):** fall back to the reserved overflow model pool (Section 2) only if this occurs; otherwise, remaining candidates for the day are recorded `ABSTAIN`, reason code `AI_QUOTA_EXHAUSTED` — this is a legitimate outcome (a no-trade day is acceptable per the Constitution), not a system failure requiring intervention.

## 8. Output

Write one record to `evaluations` per candidate processed, linked to its `candidates` record: the full schema output (Section 5) on success, or the abstain reason code (Section 7) on failure — either way, this and the reasoning behind it are written to `audit_log`, consistent with every other subsystem's explainability requirement.

## 9. Explicitly Out of Scope for This Subsystem

- No position sizing, scoring math, or confidence-score computation — `conviction` is a qualitative label, not a number the Scoring & Regime Filter treats as pre-computed; combining it with deterministic evidence happens entirely in that next subsystem.
- No direction-setting or second-guessing Discovery's deterministic trigger.
- No memory or conversation history between calls — every call is a single, stateless turn with no dependency on prior AI evaluations.
- No use of the fallback/preview model pool as routine capacity (Section 2).