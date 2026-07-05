import math
import datetime
from src.db import get_db
from src.logger import write_audit_log
from src.trading_harness import open_paper_position
from src.data_client import get_price_volume, get_company_sector
from src.scoring import get_regime_state

def compute_atr_22(history):
    """
    Computes ATR over a 22-day period using history candles.
    TR = max(high - low, |high - prior_close|, |low - prior_close|)
    """
    if len(history) < 23:
        return None
        
    tr_values = []
    for i in range(1, len(history)):
        high = history[i]["high"]
        low = history[i]["low"]
        prior_close = history[i-1]["close"]
        
        tr = max(
            high - low,
            abs(high - prior_close),
            abs(low - prior_close)
        )
        tr_values.append(tr)
        
    if len(tr_values) < 22:
        return None
        
    return sum(tr_values[-22:]) / 22.0

def compute_correlation(ticker1, ticker2):
    """
    Computes rolling 30-day Pearson correlation of daily returns between two tickers.
    """
    pv1 = get_price_volume(ticker1)
    pv2 = get_price_volume(ticker2)
    if not pv1 or not pv2:
        return 0.0
        
    hist1 = pv1["data"].get("history", [])
    hist2 = pv2["data"].get("history", [])
    
    dates1 = {c["date"]: c["close"] for c in hist1}
    dates2 = {c["date"]: c["close"] for c in hist2}
    
    common_dates = sorted(list(set(dates1.keys()) & set(dates2.keys())))
    if len(common_dates) < 31: # Need 31 closes for 30 daily returns
        return 0.0
        
    common_dates = common_dates[-31:]
    
    returns1 = []
    returns2 = []
    for i in range(1, len(common_dates)):
        d_curr = common_dates[i]
        d_prev = common_dates[i-1]
        
        ret1 = (dates1[d_curr] - dates1[d_prev]) / dates1[d_prev]
        ret2 = (dates2[d_curr] - dates2[d_prev]) / dates2[d_prev]
        
        returns1.append(ret1)
        returns2.append(ret2)
        
    n = len(returns1)
    mean1 = sum(returns1) / n
    mean2 = sum(returns2) / n
    
    var1 = sum((x - mean1) ** 2 for x in returns1)
    var2 = sum((y - mean2) ** 2 for y in returns2)
    
    cov = sum((x - mean1) * (y - mean2) for x, y in zip(returns1, returns2))
    
    if var1 == 0.0 or var2 == 0.0:
        return 0.0
        
    return cov / math.sqrt(var1 * var2)

def execute_trade(candidate_doc, portfolio_state=None, regime_state=None):
    """
    Evaluates a candidate doc against pre-trade checks, sizes the position, and executes it.
    
    Pre-trade checks run in order:
    1. Kill switch active
    2. Already open ticker
    3. Correlation cap
    4. Sector cap
    
    Returns:
    - ObjectId: The trade_id if position was opened.
    - str: The block reason code if rejected.
    """
    ticker = candidate_doc.get("ticker", "").upper().strip()
    direction = candidate_doc.get("direction", "").upper().strip()
    combined_score = float(candidate_doc.get("combined_score", 0.5))
    confidence_tier = candidate_doc.get("confidence_tier")
    
    db = get_db()
    
    # 1. Load active portfolio state if not provided
    if portfolio_state is None:
        portfolio_state = db.portfolio_state.find_one({"_id": "current_state"})
        if not portfolio_state:
            # Fallback initialization if state doesn't exist
            portfolio_state = {
                "_id": "current_state",
                "equity": 100000.0,
                "cash": 100000.0,
                "kill_switch_active": False,
                "correlation_cap_current": 0.6,
                "open_positions": []
            }
            db.portfolio_state.replace_one({"_id": "current_state"}, portfolio_state, upsert=True)
            
    # Resolve regime if not provided
    if regime_state is None:
        regime_state = get_regime_state()
    regime = regime_state.get("regime", "RISK_OFF")
    
    def block_trade(reason_code, message):
        write_audit_log(
            subsystem="execution",
            action="open_position",
            decision="BLOCKED",
            reasoning=message,
            ticker=ticker,
            reason_code=reason_code,
            trading_cycle_run_id=candidate_doc.get("trading_cycle_run_id")
        )
        # Update candidate doc with decision
        db.candidates.update_one(
            {"_id": candidate_doc["_id"]},
            {"$set": {"final_outcome": "ABSTAIN", "abstain_reason_code": reason_code}}
        )
        return reason_code

    # --- CHECK 1: Kill Switch ---
    if portfolio_state.get("kill_switch_active", False):
        return block_trade("ABSTAIN_KILL_SWITCH_ACTIVE", "Trade blocked: Global kill switch is currently active.")
        
    # --- CHECK 2: One position per ticker ---
    open_positions = portfolio_state.get("open_positions", [])
    if any(pos["ticker"] == ticker for pos in open_positions):
        return block_trade("ABSTAIN_EXISTING_POSITION", f"Trade blocked: An open position already exists for {ticker}.")
        
    # --- CHECK 3: Correlation Cap ---
    # Retrieve current cap: use saved cap or fallback to 0.4 (RISK_OFF) / 0.6 (RISK_ON)
    default_cap = 0.4 if regime == "RISK_OFF" else 0.6
    correlation_cap = portfolio_state.get("correlation_cap_current", default_cap)
    
    for pos in open_positions:
        corr = compute_correlation(ticker, pos["ticker"])
        if corr > correlation_cap:
            return block_trade(
                "ABSTAIN_CORRELATION_CAP",
                f"Trade blocked: Correlation of {ticker} to open position {pos['ticker']} is {corr:.2f} (cap: {correlation_cap})."
            )
            
    # --- CHECK 4: Sector Exposure Cap ---
    candidate_sector = get_company_sector(ticker)
    
    # Calculate position details for sizing
    pv_res = get_price_volume(ticker)
    if not pv_res:
        return block_trade("ABSTAIN_ATR_FAILED", "Trade blocked: Price/volume data unavailable.")
        
    pv_data = pv_res["data"]
    history = pv_data.get("history", [])
    avg_daily_volume = pv_data.get("avg_daily_volume", 0.0)
    current_price = pv_data.get("current_price", 0.0)
    
    if not history or current_price == 0.0:
        return block_trade("ABSTAIN_ATR_FAILED", "Trade blocked: Price/volume history unavailable.")
        
    # Compute ATR(22)
    atr = compute_atr_22(history)
    if atr is None or atr == 0.0:
        return block_trade("ABSTAIN_ATR_FAILED", "Trade blocked: Failed to compute ATR(22) due to insufficient history.")
        
    # Sizing logic
    # risk_pct = 0.75 + (combined_score - 0.5) / 1.5 * 0.75
    risk_pct = 0.75 + ((combined_score - 0.5) / 1.5) * 0.75
    portfolio_equity = float(portfolio_state.get("equity", 100000.0))
    
    stop_distance = 3.0 * atr
    if stop_distance == 0.0:
        return block_trade("ABSTAIN_ATR_FAILED", "Trade blocked: Calculated stop distance is 0.0.")
        
    shares = math.floor((portfolio_equity * (risk_pct / 100.0)) / stop_distance)
    if shares <= 0:
        return block_trade("ABSTAIN_ZERO_SHARES", f"Trade blocked: Calculated share count is 0 (Equity: {portfolio_equity}, Risk%: {risk_pct:.2f}%, Stop: {stop_distance:.2f}).")
        
    # Liquidity capacity cap: position value must not exceed 10% of 20-day average daily dollar volume (ADV)
    avg_dollar_volume = pv_data.get("avg_daily_dollar_volume", 0.0)
    max_position_value = 0.1 * avg_dollar_volume
    is_sized_down = False
    original_shares = shares
    
    proposed_value = shares * current_price
    if proposed_value > max_position_value:
        shares = math.floor(max_position_value / current_price)
        is_sized_down = True
        
    if shares <= 0:
        return block_trade("ABSTAIN_ZERO_SHARES", f"Trade blocked: Position sized down to 0 due to 10% ADV liquidity cap (Dollar ADV: {avg_dollar_volume:,.2f}).")
        
    position_value = shares * current_price
    
    # Check Sector Cap (max 25% of total equity)
    current_sector_value = sum(pos.get("value", 0.0) for pos in open_positions if pos.get("sector") == candidate_sector)
    proposed_sector_value = current_sector_value + position_value
    
    if (proposed_sector_value / portfolio_equity) > 0.25:
        return block_trade(
            "ABSTAIN_SECTOR_CAP",
            f"Trade blocked: Proposed sector exposure for '{candidate_sector}' would be {(proposed_sector_value / portfolio_equity)*100:.1f}% (cap: 25.0%)."
        )
        
    # --- CALCULATE SL/TP ---
    if direction == "LONG":
        initial_stop = current_price - stop_distance
        take_profit = current_price + 2.0 * stop_distance
    else:
        initial_stop = current_price + stop_distance
        take_profit = current_price - 2.0 * stop_distance
        
    reasoning_chain = {
        "candidate_id": candidate_doc["_id"],
        "trigger_type": candidate_doc.get("trigger_type"),
        "confidence_tier": confidence_tier,
        "combined_score": combined_score,
        "atr_22": atr,
        "risk_pct_allocated": risk_pct,
        "is_sized_down": is_sized_down,
        "original_shares": original_shares,
        "regime_state_at_decision": candidate_doc.get("regime_state_at_decision")
    }
    
    trade_id = open_paper_position(
        ticker=ticker,
        direction=direction,
        share_count=shares,
        entry_price=current_price,
        initial_stop=initial_stop,
        take_profit=take_profit,
        combined_score=combined_score,
        risk_pct_used=risk_pct,
        confidence_tier=confidence_tier,
        reasoning_chain=reasoning_chain
    )
    
    # Update portfolio state document in MongoDB
    new_position = {
        "ticker": ticker,
        "direction": direction,
        "share_count": shares,
        "entry_price": current_price,
        "value": position_value,
        "sector": candidate_sector,
        "trade_id": trade_id
    }
    
    db.portfolio_state.update_one(
        {"_id": "current_state"},
        {
            "$push": {"open_positions": new_position},
            "$inc": {"cash": -position_value}
        }
    )
    
    print(f"[{ticker}] Trade executed successfully. Opened {direction} position with {shares} shares @ ${current_price:.2f}.")
    return trade_id
