import datetime
from src.db import get_db
from src.logger import write_audit_log
from src.trading_harness import close_paper_position
from src.data_client import get_price_volume, get_company_sector
from src.scoring import get_regime_state
from src.execution import compute_atr_22, compute_correlation

def send_kill_switch_notification(drawdown_pct, open_positions):
    """Fires a notification when the kill switch triggers, using AI if available."""
    msg = f"CRITICAL DRAWDOWN ALERT: System Kill Switch Activated!\n"
    msg += f"Current Drawdown: {drawdown_pct:.2f}% (Threshold: 14.00%)\n"
    msg += f"Timestamp: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    msg += "Active positions at drawdown event:\n"
    for pos in open_positions:
        msg += f"- {pos.get('ticker')} ({pos.get('direction')}): Entry ${pos.get('entry_price'):.2f}, Shares: {pos.get('share_count')}, Current Value: ${pos.get('value'):.2f}\n"
        
    print(f"NOTIFICATION OUT: {msg}")
    
    # Optional AI enhancement
    email_body = msg
    try:
        from src.gemini_client import call_gemini_api
        prompt = f"Format the following drawdown alert into a readable and formal hedge fund manager update email. Present all raw numbers accurately:\n{msg}"
        ai_msg = call_gemini_api(prompt)
        email_body = ai_msg
        print(f"AI enhanced message:\n{ai_msg}")
    except Exception as e:
        print(f"AI phrasing skipped/failed: {e}")
        
    # Send secure email alert
    from src.notifications import send_email_alert
    send_email_alert(
        subject=f"CRITICAL: TBE Kill Switch Activated ({drawdown_pct:.2f}% Drawdown)",
        body=email_body
    )


def monitor_portfolio(trading_cycle_run_id=None):
    """
    Monitors portfolio risk, trailing stops (stop ratcheting), checks exits,
    and updates sector/correlation/drawdown metrics and the global kill switch status.
    """
    db = get_db()
    
    # 1. Fetch current portfolio state
    state = db.portfolio_state.find_one({"_id": "current_state"})
    if not state:
        state = {
            "_id": "current_state",
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": []
        }
        db.portfolio_state.replace_one({"_id": "current_state"}, state, upsert=True)
        
    # 2. Update regime-dependent correlation cap
    regime_state = get_regime_state()
    regime = regime_state.get("regime", "RISK_OFF")
    correlation_cap = 0.4 if regime == "RISK_OFF" else 0.6
    
    # 3. Process each open trade
    open_trades = list(db.trades.find({"status": "OPEN"}))
    updated_positions = []
    
    for trade in open_trades:
        ticker = trade["ticker"]
        direction = trade["direction"]
        entry_price = trade["entry_price"]
        shares = trade["share_count"]
        trade_id = trade["_id"]
        
        # Fetch current price metrics
        pv_res = get_price_volume(ticker)
        if not pv_res:
            print(f"[{ticker}] Could not retrieve price volume data for monitoring. Skipping.")
            # Keep original position in state
            pos_in_state = next((p for p in state.get("open_positions", []) if str(p.get("trade_id")) == str(trade_id)), None)
            if pos_in_state:
                updated_positions.append(pos_in_state)
            continue
            
        pv_data = pv_res["data"]
        current_price = pv_data.get("current_price", entry_price)
        history = pv_data.get("history", [])
        
        # Determine highest/lowest seen since entry
        highest_high = max(trade.get("highest_high_since_entry", entry_price), current_price)
        lowest_low = min(trade.get("lowest_low_since_entry", entry_price), current_price)
        
        # Compute current ATR(22)
        atr = compute_atr_22(history)
        if atr is None or atr == 0.0:
            # Fallback to a small percentage of price if ATR cannot be computed
            atr = current_price * 0.02
            
        current_stop = trade.get("current_stop")
        if current_stop is None:
            current_stop = trade.get("initial_stop")
        if current_stop is None:
            current_stop = entry_price
        
        # Compute Chandelier stops and ratchet only favorably (never loosen)
        if direction == "LONG":
            new_stop = highest_high - 3.0 * atr
            if new_stop > current_stop:
                current_stop = new_stop
        else:
            new_stop = lowest_low + 3.0 * atr
            if new_stop < current_stop:
                current_stop = new_stop
                
        # Check Exits (SL / TP)
        # Note: If both could trigger, STOP takes priority
        exit_triggered = False
        exit_price = None
        exit_reason = None
        
        if direction == "LONG":
            if current_price <= current_stop:
                exit_triggered = True
                exit_price = current_stop
                exit_reason = "STOP"
            elif current_price >= trade["take_profit"]:
                exit_triggered = True
                exit_price = trade["take_profit"]
                exit_reason = "TAKE_PROFIT"
        else:
            if current_price >= current_stop:
                exit_triggered = True
                exit_price = current_stop
                exit_reason = "STOP"
            elif current_price <= trade["take_profit"]:
                exit_triggered = True
                exit_price = trade["take_profit"]
                exit_reason = "TAKE_PROFIT"
                
        if exit_triggered:
            # Execute exit
            close_paper_position(trade_id, exit_price, exit_reason)
            
            # Calculate cash proceeds to return to portfolio state
            if direction == "LONG":
                proceeds = shares * exit_price
            else:
                proceeds = shares * (2.0 * entry_price - exit_price)
                
            db.portfolio_state.update_one(
                {"_id": "current_state"},
                {"$inc": {"cash": proceeds}}
            )
            print(f"[{ticker}] Exit triggered ({exit_reason}) @ ${exit_price:.2f}. Position closed.")
        else:
            # Update stop/high/low in trades collection
            db.trades.update_one(
                {"_id": trade_id},
                {
                    "$set": {
                        "highest_high_since_entry": highest_high,
                        "lowest_low_since_entry": lowest_low,
                        "current_stop": current_stop
                    }
                }
            )
            
            # Calculate current value of position for portfolio snapshot
            if direction == "LONG":
                pos_val = shares * current_price
            else:
                pos_val = shares * (2.0 * entry_price - current_price)
                
            # Find candidate's sector from open positions or fetch it
            sector = next((p.get("sector") for p in state.get("open_positions", []) if str(p.get("trade_id")) == str(trade_id)), None)
            if not sector:
                sector = get_company_sector(ticker)
                
            updated_positions.append({
                "ticker": ticker,
                "direction": direction,
                "share_count": shares,
                "entry_price": entry_price,
                "value": pos_val,
                "sector": sector,
                "trade_id": trade_id
            })

    # 4. Refresh Cash after cash updates
    state = db.portfolio_state.find_one({"_id": "current_state"})
    cash = float(state.get("cash", 100000.0))
    
    total_pos_value = sum(pos["value"] for pos in updated_positions)
    equity = cash + total_pos_value
    
    # Update High-Water Mark and Drawdown
    hwm = float(state.get("high_water_mark", equity))
    hwm = max(hwm, equity)
    
    drawdown_pct = 0.0
    if hwm > 0:
        drawdown_pct = ((hwm - equity) / hwm) * 100.0
        
    kill_switch_active = state.get("kill_switch_active", False)
    transitioned_to_kill = False
    
    if drawdown_pct >= 14.0 and not kill_switch_active:
        kill_switch_active = True
        transitioned_to_kill = True
        send_kill_switch_notification(drawdown_pct, updated_positions)
        
    # 5. Snapshots
    # Sector exposure % of equity
    sector_exposure = {}
    for pos in updated_positions:
        sec = pos.get("sector", "Unknown")
        val = pos.get("value", 0.0)
        sector_exposure[sec] = sector_exposure.get(sec, 0.0) + val
        
    sector_exposure_pct = {}
    for sec, val in sector_exposure.items():
        sector_exposure_pct[sec] = (val / equity) * 100.0 if equity > 0.0 else 0.0
        
    # Correlation snapshot
    correlation_snapshot = {}
    for i in range(len(updated_positions)):
        for j in range(i+1, len(updated_positions)):
            t1 = updated_positions[i]["ticker"]
            t2 = updated_positions[j]["ticker"]
            corr = compute_correlation(t1, t2)
            correlation_snapshot[f"{t1}_{t2}"] = corr
            
    # 6. Save updated portfolio state
    state_updates = {
        "equity": equity,
        "high_water_mark": hwm,
        "drawdown_pct": drawdown_pct,
        "kill_switch_active": kill_switch_active,
        "correlation_cap_current": correlation_cap,
        "sector_exposure": sector_exposure_pct,
        "correlation_snapshot": correlation_snapshot,
        "open_positions": updated_positions,
        "regime_snapshot": {
            "vix": regime_state.get("vix"),
            "spy_close": regime_state.get("spy_close"),
            "spy_sma_50": regime_state.get("spy_sma_50"),
            "source": regime_state.get("source"),
            "regime": regime
        }
    }
    
    db.portfolio_state.update_one(
        {"_id": "current_state"},
        {"$set": state_updates}
    )
    
    reasoning = (
        f"Completed portfolio monitoring cycle. Equity: ${equity:.2f}, Cash: ${cash:.2f}, "
        f"Drawdown: {drawdown_pct:.2f}% (HWM: ${hwm:.2f}), Kill Switch: {kill_switch_active}, "
        f"Correlation Cap: {correlation_cap} (Regime: {regime})."
    )
    write_audit_log(
        subsystem="portfolio_monitor",
        action="monitor_cycle",
        decision="MONITORED",
        reasoning=reasoning,
        trading_cycle_run_id=trading_cycle_run_id
    )
    print(f"Portfolio monitor finished. Equity: ${equity:.2f} | Drawdown: {drawdown_pct:.2f}% | Kill Switch: {kill_switch_active}")
    return db.portfolio_state.find_one({"_id": "current_state"})