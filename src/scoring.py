import datetime
import time
import requests
import yfinance
from src.db import get_db
from src.logger import write_audit_log
from src.data_client import FINNHUB_API_KEY, get_twelvedata_candles

def get_regime_state():
    """
    Computes current regime state fresh for the run:
    - RISK_OFF if VIX > 30 OR SPY < 50-day SMA.
    - RISK_ON otherwise.
    Uses yfinance (primary) -> Finnhub (fallback).
    """
    vix = None
    spy_close = None
    spy_sma_50 = None
    
    # 1. Primary: yfinance
    try:
        vix_t = yfinance.Ticker("^VIX")
        vix_hist = vix_t.history(period="1d")
        if not vix_hist.empty:
            vix = float(vix_hist["Close"].iloc[-1])
            
        spy_t = yfinance.Ticker("SPY")
        spy_hist = spy_t.history(period="3mo")
        if not spy_hist.empty and len(spy_hist) >= 50:
            spy_close = float(spy_hist["Close"].iloc[-1])
            spy_sma_50 = float(spy_hist["Close"].tail(50).mean())
            
        if vix is not None and spy_close is not None and spy_sma_50 is not None:
            vix_elevated = vix > 30
            spy_downtrend = spy_close < spy_sma_50
            regime = "RISK_OFF" if (vix_elevated or spy_downtrend) else "RISK_ON"
            return {
                "source": "yfinance",
                "vix": vix,
                "spy_close": spy_close,
                "spy_sma_50": spy_sma_50,
                "regime": regime
            }
    except Exception as e:
        print(f"yfinance regime fetch failed: {e}")
        
    # 2. Fallback: Finnhub + Twelve Data
    try:
        url_vix = f"https://finnhub.io/api/v1/quote?symbol=^VIX&token={FINNHUB_API_KEY}"
        r_vix = requests.get(url_vix, timeout=10)
        r_vix.raise_for_status()
        vix_data = r_vix.json()
        if vix_data and vix_data.get("c") is not None:
            vix = float(vix_data["c"])
            
        candles_data = get_twelvedata_candles("SPY", days=60)
        if candles_data:
            closes = [float(day["close"]) for day in candles_data["history"]]
            if len(closes) >= 50:
                spy_close = closes[-1]
                spy_sma_50 = sum(closes[-50:]) / 50.0
                
        if vix is not None and spy_close is not None and spy_sma_50 is not None:
            vix_elevated = vix > 30
            spy_downtrend = spy_close < spy_sma_50
            regime = "RISK_OFF" if (vix_elevated or spy_downtrend) else "RISK_ON"
            return {
                "source": "Finnhub+TwelveData",
                "vix": vix,
                "spy_close": spy_close,
                "spy_sma_50": spy_sma_50,
                "regime": regime
            }
    except Exception as e:
        print(f"Twelve Data regime fetch failed: {e}")
        
    # Safe default
    print("Regime detection failed completely. Defaulting to RISK_OFF safe mode.")
    return {
        "source": "DEFAULT_FALLBACK",
        "vix": 35.0,
        "spy_close": 400.0,
        "spy_sma_50": 450.0,
        "regime": "RISK_OFF"
    }

def score_candidate(candidate_doc, evaluation_doc, regime_state=None):
    """
    Combines deterministic triggers and qualitative AI evaluations into a final proceed/abstain decision.
    Modulated by market regime filter.
    
    Returns:
    - dict: The updated candidate document from MongoDB.
    """
    ticker = candidate_doc.get("ticker", "").upper().strip()
    db = get_db()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 1. Caching check: if already scored today, return candidate doc as is
    if candidate_doc.get("final_outcome") is not None:
        print(f"[{ticker}] Candidate already scored today, skipping re-score.")
        return candidate_doc
        
    # Initialize score variables
    trigger_strength_score = 0.0
    ai_conviction_score = 0.0
    combined_score = 0.0
    info_sufficiency = "INSUFFICIENT"
    info_modifier_val = 0.0
    
    final_outcome = "ABSTAIN"
    confidence_tier = None
    abstain_reason = None
    
    # Resolve regime state if not provided
    if regime_state is None:
        regime_state = get_regime_state()
    regime = regime_state.get("regime", "RISK_OFF")
    
    # 2. Check for upstream AI abstention
    if not evaluation_doc or evaluation_doc.get("conviction") == "ABSTAIN":
        final_outcome = "ABSTAIN"
        abstain_reason = "ABSTAIN_UPSTREAM_AI_FAILURE"
        
        # Save to DB
        cand_updates = {
            "trigger_strength_score": 0.0,
            "ai_conviction_score": 0.0,
            "combined_score": 0.0,
            "information_sufficiency_modifier": 0.0,
            "regime_state_at_decision": regime,
            "final_outcome": final_outcome,
            "confidence_tier": None,
            "abstain_reason_code": abstain_reason
        }
        db.candidates.update_one(
            {"_id": candidate_doc["_id"]},
            {"$set": cand_updates}
        )
        updated_cand = db.candidates.find_one({"_id": candidate_doc["_id"]})
        
        write_audit_log(
            subsystem="scoring",
            action="score_candidate",
            decision=final_outcome,
            reasoning="Abstained due to upstream AI reasoning failure.",
            ticker=ticker,
            reason_code=abstain_reason,
            trading_cycle_run_id=candidate_doc.get("trading_cycle_run_id")
        )
        return updated_cand

    # 3. Calculate Trigger Strength Score
    trigger_type = candidate_doc.get("trigger_type")
    details = candidate_doc.get("trigger_details", {})
    
    if trigger_type == "EARNINGS_SURPRISE":
        surprise_pct = abs(details.get("surprise_pct", 0.0))
        if surprise_pct >= 10.0:
            trigger_strength_score = 2.0
        elif surprise_pct >= 5.0:
            trigger_strength_score = 1.0
        else:
            trigger_strength_score = 1.0 # default to MODERATE if trigger fired
            
    elif trigger_type == "MATERIAL_FILING":
        close_move = abs(details.get("close_move_pct", 0.0))
        intraday_move = abs(details.get("intraday_move_pct", 0.0))
        move = max(close_move, intraday_move)
        if move >= 6.0:
            trigger_strength_score = 2.0
        elif move >= 3.0:
            trigger_strength_score = 1.0
        else:
            trigger_strength_score = 1.0 # default to MODERATE if trigger fired

    # 4. Calculate AI Conviction Score
    conviction_map = {
        "STRONG_SUPPORT": 2.0,
        "MODERATE_SUPPORT": 1.0,
        "NEUTRAL": 0.0,
        "MODERATE_CONTRADICTION": -1.0,
        "STRONG_CONTRADICTION": -2.0
    }
    ai_conviction_score = conviction_map.get(evaluation_doc.get("conviction"), 0.0)
    
    # 5. Combined Score
    combined_score = (trigger_strength_score + ai_conviction_score) / 2.0
    
    # 6. Apply Information Sufficiency Modifier
    info_sufficiency = evaluation_doc.get("information_sufficiency", "INSUFFICIENT")
    
    if info_sufficiency == "INSUFFICIENT":
        final_outcome = "ABSTAIN"
        abstain_reason = "ABSTAIN_AI_INSUFFICIENT_INFO"
        info_modifier_val = "INSUFFICIENT"
    else:
        if info_sufficiency == "LIMITED":
            combined_score -= 0.5
            info_modifier_val = -0.5
        else:
            info_modifier_val = 0.0
            
        # 7. Bucket Lookup
        if combined_score >= 1.5:
            final_outcome = "PROCEED"
            confidence_tier = "STRONG"
        elif combined_score >= 0.5:
            final_outcome = "PROCEED"
            confidence_tier = "MODERATE"
        elif combined_score >= -0.5:
            final_outcome = "ABSTAIN"
            abstain_reason = "ABSTAIN_NEUTRAL_OR_CONFLICTING"
        else:
            final_outcome = "ABSTAIN"
            abstain_reason = "ABSTAIN_EVIDENCE_CONTRADICTS_TRIGGER"
            
    # 8. Regime Modulation
    if final_outcome == "PROCEED" and regime == "RISK_OFF" and confidence_tier == "MODERATE":
        final_outcome = "ABSTAIN"
        abstain_reason = "ABSTAIN_RISK_OFF_REGIME"
        
    # 9. Update DB & Log
    cand_updates = {
        "trigger_strength_score": trigger_strength_score,
        "ai_conviction_score": ai_conviction_score,
        "combined_score": combined_score,
        "information_sufficiency_modifier": info_modifier_val,
        "regime_state_at_decision": regime,
        "final_outcome": final_outcome,
        "confidence_tier": confidence_tier,
        "abstain_reason_code": abstain_reason
    }
    db.candidates.update_one(
        {"_id": candidate_doc["_id"]},
        {"$set": cand_updates}
    )
    updated_cand = db.candidates.find_one({"_id": candidate_doc["_id"]})
    
    reasoning_msg = (
        f"Scoring decision: {final_outcome} (tier: {confidence_tier}). "
        f"Trigger: {trigger_strength_score:.1f}, AI Conviction: {ai_conviction_score:.1f}, "
        f"Combined Score: {combined_score:.1f} (Info: {info_sufficiency}), Regime: {regime}."
    )
    write_audit_log(
        subsystem="scoring",
        action="score_candidate",
        decision=final_outcome,
        reasoning=reasoning_msg,
        ticker=ticker,
        reason_code=abstain_reason,
        trading_cycle_run_id=candidate_doc.get("trading_cycle_run_id")
    )
    print(f"[{ticker}] Scoring completed: {final_outcome} | Score: {combined_score:.2f} | Regime: {regime}")
    return updated_cand
