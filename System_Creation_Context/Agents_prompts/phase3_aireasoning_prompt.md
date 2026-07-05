[Build — new module, Phase 3 of 8]

# TBE — Phase 3: AI Reasoning Layer

## Goal

Provide qualitative interpretation for a candidate that has already cleared the Hard-Gate Engine and already has a deterministic trigger and direction from Discovery. This is the *only* subsystem in the entire system permitted to call an AI model — it never originates a candidate, never assigns direction, and never outputs a number that controls capital.

This is Phase 3 of an 8-phase build, same repo as Phases 0-2. Use the audit-logging utility and shared data-source client module from Phase 0. This is the first phase to need a Gemini API client — build it here, since this is its only consumer.

## Precondition Enforcement (build this as a hard gate in code, not a comment)

The entrypoint into this subsystem must accept *only* a `candidates` record with `gate_result = "PASSED"`. There must be no code path that allows a call into this subsystem for anything else — reject/refuse at the function boundary if this precondition isn't met, don't just trust the caller.

## Gemini Client Setup

- **Primary model:** Gemini 3.1 Flash-Lite, three separate API keys (separate Google Cloud projects), read from environment variables `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3` — used in sequence: if the active key hits its daily cap, the next key takes over for the rest of that day. Track which key is "current" and its usage.
- **Fallback pool:** the reserved lower-RPD preview-tier models, used only when all three primary keys are exhausted or failing that day. Do not build this as routine capacity — it's a genuine-overflow-only path, and should be easy to remove/disable without touching the primary logic.
- **Structured output:** use Gemini's native structured-output/response-schema mode — the schema (below) is passed directly in the API request, never parsed from free text after the fact.

## Input Assembly (per gate-passed candidate)

- Trigger context from Discovery: type, direction, details (surprise % or filing item + price/volume confirmation).
- Primary text evidence: for earnings triggers, the earnings press release (often an 8-K Item 2.02 exhibit, via EDGAR) if available; for filing triggers, the qualifying filing's own text.
- Supplementary news: Finnhub company-news endpoint (primary) → yfinance news feature (fallback). Never Alpha Vantage.
- If no text evidence can be assembled at all, still proceed to the model call — this is a legitimate input state, not an error. The prompt must explicitly tell the model evidence is minimal, and the model communicates this back via `information_sufficiency`, not by guessing.

## Output Schema (enforced via structured output, not post-hoc parsing)

```json
{
  "conviction": "STRONG_SUPPORT | MODERATE_SUPPORT | NEUTRAL | MODERATE_CONTRADICTION | STRONG_CONTRADICTION",
  "risk_flags": ["short string", "..."],
  "information_sufficiency": "SUFFICIENT | LIMITED | INSUFFICIENT",
  "rationale": "1-3 sentence plain-language explanation"
}
```

Any response failing schema validation is never partially accepted or repaired — treat it exactly per the Failure Handling section below.

## Prompt Construction Requirements (every call must state, explicitly)

- Its role is limited to qualitative assessment of the evidence provided — no assumed access to price data or technical indicators.
- It must not suggest a direction different from the one already given — it evaluates the *existing* direction's supporting evidence, never second-guesses Discovery's trigger.
- It must not invent facts absent from the assembled context — gaps are noted via `information_sufficiency` or a risk flag, never filled from general knowledge.
- Output must conform exactly to the schema — no commentary outside the structured fields.

## Failure & Retry Handling

- **Schema validation failure:** retry once. If it fails again, record `ABSTAIN`, reason `AI_SCHEMA_VALIDATION_FAILED` — this must never be confused downstream with an actual `STRONG_CONTRADICTION` result.
- **API/network failure or timeout:** retry once on the same key; if it fails again, rotate to the next key before giving up. Only after all three primary keys are exhausted/failing does this candidate get `ABSTAIN`, reason `AI_UNAVAILABLE`.
- **All three keys' daily caps hit:** fall back to the reserved overflow pool only in this case. If that's unavailable too, record `ABSTAIN`, reason `AI_QUOTA_EXHAUSTED` — this is a legitimate, expected outcome, not a bug to fix.

## Output

Write one `evaluations` document per candidate processed (Phase 0 schema), linked to its `candidates` record: full schema output on success, or the abstain code on failure. Write the corresponding `audit_log` entry via the Phase 0 utility either way.

## Boundaries for v1 (explicitly out of scope)

- No position sizing, scoring math, or confidence-score computation of any kind — `conviction` is a label, nothing more; combining it with deterministic evidence is Phase 4's job entirely.
- No direction-setting or second-guessing Discovery's trigger.
- No memory or conversation history between calls — every call is a single, stateless turn.
- No routine use of the fallback/preview model pool.

## Definition of Done

1. Attempting to call this subsystem's entrypoint with a candidate that has `gate_result != "PASSED"` is refused at the function boundary (raises/returns an explicit error), not silently processed.
2. Given a real gate-passed candidate with available filing text and news, a call produces a schema-valid `evaluations` document with all four fields populated sensibly, and an `audit_log` entry is written.
3. Given a candidate with no retrievable text evidence at all, the model call still proceeds, and `information_sufficiency` reflects that (`LIMITED` or `INSUFFICIENT`) rather than the call being skipped.
4. Force a schema-validation failure (e.g. mock a malformed response) and confirm exactly one retry happens before it's recorded as `ABSTAIN` / `AI_SCHEMA_VALIDATION_FAILED` — and confirm this is stored distinctly from a real `STRONG_CONTRADICTION` result.
5. Force the primary key's API call to fail twice and confirm the system rotates to the second key rather than immediately failing the candidate.
6. Force all three primary keys to report their daily cap exhausted and confirm the system either engages the fallback pool or records `ABSTAIN` / `AI_QUOTA_EXHAUSTED` — never an unhandled exception.
