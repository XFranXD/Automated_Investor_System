# TBE Subsystem Spec: Hard-Gate Engine
### Phase 1 of the Roadmap - Architecture Section 4
**Version 1.0 — July 2026**

## 1. Purpose

Given a ticker, determine whether it is disqualified outright before any evidence scoring, AI reasoning, or capital is ever considered for it. This is the first step a candidate faces after Discovery finds it, and gates run before anything else in the Trading Cycle's Discover phase. A candidate that fails any gate here never reaches AI-score or Execute — no score is computed, no AI call is made.

This subsystem is 100% deterministic. No AI involvement anywhere in this spec.

## 2. Inputs

- A ticker symbol, freshly identified by Discovery in the current Trading Cycle run.
- No inputs carried over from previous cycles — see Section 6 (Refresh Policy).

## 3. Data Source Strategy

Multiple free sources are used in a fixed waterfall order per data category. If a source fails, times out, or lacks the needed field, the next source in the list is tried. A gate is only marked "cannot verify" (see Section 7) after every source in its relevant waterfall has been exhausted.

**Fundamentals (Beneish M-Score / Altman Z-Score inputs — balance sheet, income statement fields):**
1. SEC EDGAR XBRL company-facts API (official, free, most authoritative — primary source)
2. Finnhub free tier (financials-as-reported)
3. yfinance (last resort — unofficial, no key required)

**Filings (auditor change, delinquent-filing status):**
- SEC EDGAR only. This is inherently EDGAR's domain (8-K filings, NT 10-K/NT 10-Q notices) — no other free source reliably covers this, so there is no waterfall here, only EDGAR.

**Price / volume / market cap (liquidity gate, and market value of equity needed for Altman Z-Score's Component D):**
1. yfinance (free, no key, generous informal access, reliable historical OHLCV)
2. Finnhub free tier

**Sanctions:**
- OFAC Specially Designated Nationals (SDN) list, published free by the U.S. Treasury (CSV/XML download). No waterfall needed — single authoritative source.

*Note: Alpha Vantage is deliberately excluded from every waterfall in this spec. Its free tier is confirmed at 25 requests/day, 5/minute — too low to serve as a working fallback here, since fundamentals for even one candidate can require several calls across multiple fields. Finnhub (60 requests/minute free tier) and yfinance carry the fallback role instead. Exact current limits for Finnhub should still be re-verified at implementation time, since third-party API limits change without much notice.*

## 4. Gate Evaluation Order (short-circuit on first failure)

Gates run in this order specifically to avoid pulling expensive multi-field financial data for a candidate that would have been rejected anyway on a cheaper check:

1. **OFAC / Sanctions screening** — single list lookup, cheapest possible check, runs first.
2. **Liquidity minimums** — one price/volume fetch.
3. **Delinquent filing check** — one EDGAR filing-index lookup.
4. **Auditor change / adverse opinion check** — one EDGAR filing-index lookup, same call family as #3.
5. **Beneish M-Score** — requires two years of detailed financials across up to four fallback sources; most expensive, runs last among the "cheap" checks.
6. **Altman Z-Score** — requires financials already pulled for Beneish plus market cap; runs after Beneish since it can reuse the same fetched financial statement data.

The moment any gate fails, evaluation stops — remaining gates are not run, and the candidate is rejected with the reason code from whichever gate failed first.

## 5. Gate Definitions

### 5.1 OFAC / Sanctions Screening
Match the company name and any known associated entities against the current OFAC SDN list. Any match → reject. Reason code: `GATE_SANCTIONS`.

### 5.2 Liquidity Minimums
Two independent checks, both must pass:
- **Average daily dollar volume (ADV)**, trailing 20 trading days, must be ≥ $5,000,000. Below this → reject. Reason code: `GATE_LIQUIDITY_ADV`.
- **Share price** must be ≥ $5.00. Below this → reject. Reason code: `GATE_LIQUIDITY_PRICE`.

*(A live bid-ask spread gate is deliberately excluded from v1 — reliable free real-time quote data isn't consistently available across the fallback sources, and ADV + price floor together already screen out the illiquid/manipulable names this gate exists to catch. Revisit only if data availability improves.)*

### 5.3 Delinquent Filing Check
Query EDGAR's filing index for the ticker's CIK. If a Form NT 10-K or NT 10-Q (Notification of Late Filing) appears within the trailing 6 months **and** no subsequent 10-K/10-Q has been filed since, the company is currently delinquent → reject. Reason code: `GATE_DELINQUENT_FILING`.

### 5.4 Auditor Change / Adverse Opinion Check
Two deterministic sub-checks, either one triggers rejection:
- **Auditor change:** any 8-K filing with Item 4.01 (Changes in Registrant's Certifying Accountant) within the trailing 12 months → reject. Reason code: `GATE_AUDITOR_CHANGE`.
- **Adverse opinion language:** using EDGAR full-text search against the company's most recent 10-K, search for a fixed keyword list in the auditor's report section — phrases including "substantial doubt," "going concern," "adverse opinion," "did not express an opinion." A match → reject. Reason code: `GATE_ADVERSE_OPINION`.

*(This keyword approach is a deliberate simplification — full NLP-based opinion classification is out of scope for v1. It's deterministic and keyword-based, consistent with the "no calibration" constraint, even though it will occasionally be too blunt. False positives here just mean an extra rejected candidate, which fits the system's bias toward rejection; false negatives are a known limitation to revisit later, not a v1 blocker.)*

### 5.5 Beneish M-Score
Standard 8-variable formula using two years of financials (current vs. prior fiscal year):

```
M = -4.84 + 0.92(DSRI) + 0.528(GMI) + 0.404(AQI) + 0.892(SGI)
    + 0.115(DEPI) - 0.172(SGAI) + 4.679(TATA) - 0.327(LVGI)
```

Where DSRI, GMI, AQI, SGI, DEPI, SGAI, TATA, and LVGI are the standard published ratios (Days Sales in Receivables Index, Gross Margin Index, Asset Quality Index, Sales Growth Index, Depreciation Index, SG&A Index, Total Accruals to Total Assets, Leverage Index respectively), computed from the two years of balance sheet and income statement data pulled per Section 3's waterfall.

**Threshold: M-Score > -1.78 → reject** (published threshold indicating likely earnings manipulation). Reason code: `GATE_BENEISH`.

### 5.6 Altman Z-Score
Standard public-company (manufacturing/general) formula:

```
Z = 1.2(A) + 1.4(B) + 3.3(C) + 0.6(D) + 1.0(E)
```

Where: A = Working Capital / Total Assets, B = Retained Earnings / Total Assets, C = EBIT / Total Assets, D = Market Value of Equity / Total Liabilities, E = Sales / Total Assets. Market value of equity comes from the price/market-cap source waterfall in Section 3; the rest from the same financials pulled for Beneish.

**Threshold: Z < 1.81 → reject** (published "distress zone" threshold). Reason code: `GATE_ALTMAN`.

## 6. Refresh Policy

No cross-day caching in v1, per the locked decision to keep things simple. A candidate is gated fresh the first time it's seen on a given trading day. If the same candidate reappears in a later Trading Cycle run on the *same* day (e.g., it was gated and AI-scored earlier but Execute abstained on it, and Discovery surfaces it again later), it is **not** re-gated within that same day — gate results, once computed for a given calendar day, are reused for the rest of that day. This mirrors the same-day dedup rule already established for AI-score, and for the same reason: fraud/insolvency/liquidity status doesn't materially change within a single trading day, so recomputing it repeatedly only burns API budget for no benefit.

## 7. Missing / Incomplete Data Handling

If, after exhausting every source in a gate's waterfall, the data needed to compute that gate still isn't available, **the gate is treated as failed and the candidate is rejected** — fail-safe, per the locked decision. This is recorded with a distinct reason code from an actual failed check, so the audit trail can tell the difference between "verified and disqualified" and "could not verify":

- Actual failure: e.g. `GATE_BENEISH` (computed, exceeded threshold)
- Could not verify: e.g. `GATE_BENEISH_NO_DATA` (all sources exhausted, insufficient data to compute)

This distinction matters operationally — if `_NO_DATA` rejections start showing up disproportionately for a particular gate, that's a signal the data source waterfall needs attention, not that the candidate pool is unusually fraud-prone.

## 8. Output

For every candidate that enters gate evaluation, write one record to `candidates` and corresponding entries to `audit_log`, regardless of outcome:

- Ticker, evaluation timestamp, which Trading Cycle run triggered it.
- Final result: `PASSED` (all six gates cleared) or `REJECTED`.
- If rejected: the specific reason code from Section 5/7 that caused rejection, and which data source(s) were consulted before the result was reached.
- If passed: confirmation that all six gates were checked and cleared, ready to proceed to AI-score.

Rejected candidates are not deleted or hidden — the audit trail requirement from the Constitution applies to rejections exactly as much as approvals.

## 9. Explicitly Out of Scope for This Subsystem

- No scoring, weighting, or AI involvement of any kind — gates are binary pass/fail.
- No position sizing, no execution logic.
- No handling of *scored* (non-gate) evidence — that's the Scoring & Regime Filter subsystem, downstream.
- No live bid-ask spread checking (see 5.2 note).
- No adverse-opinion NLP beyond the fixed keyword list in 5.4.