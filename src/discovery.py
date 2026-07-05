import datetime
from src.db import get_db
from src.logger import write_audit_log
from src.hard_gate import evaluate_gates
from src.data_client import (
    get_finnhub_earnings_calendar,
    get_earnings,
    get_sec_recent_8k_ciks,
    get_ticker_from_cik,
    get_filings,
    get_price_volume
)

def get_prior_market_close():
    """
    Returns the UTC datetime corresponding to the prior trading day's market close (16:00 ET / 20:00 UTC).
    """
    now = datetime.datetime.utcnow()
    # Monday is 0, Sunday is 6
    today_weekday = now.weekday()
    if today_weekday == 0:  # Monday -> prior is Friday (3 days ago)
        days_back = 3
    elif today_weekday == 6:  # Sunday -> prior is Friday (2 days ago)
        days_back = 2
    elif today_weekday == 5:  # Saturday -> prior is Friday (1 day ago)
        days_back = 1
    else:  # Tuesday-Friday -> prior is yesterday (1 day ago)
        days_back = 1
        
    prior_date = now.date() - datetime.timedelta(days=days_back)
    prior_close = datetime.datetime.combine(prior_date, datetime.time(20, 0)) # 20:00 UTC (4 PM ET)
    return prior_close

def discover_candidates(trading_cycle_run_id=None):
    """
    Runs the deterministic scanner to discover earnings (PEAD) or 8-K trigger events
    since the prior market close. Discovered candidates are saved as PENDING and routed
    directly to the Hard-Gate Engine.
    
    Returns:
    - list: List of evaluated candidate documents.
    """
    print("=== STARTING CANDIDATE DISCOVERY ===")
    db = get_db()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    prior_close = get_prior_market_close()
    prior_date_str = prior_close.strftime("%Y-%m-%d")
    
    # 1. Earnings Surprise (PEAD)
    print("\nScanning Earnings Calendar...")
    calendar_entries = []
    try:
        calendar_entries = get_finnhub_earnings_calendar(prior_date_str, today_str)
    except Exception as e:
        print(f"Error fetching earnings calendar: {e}")
        
    discovered_pead = []
    for entry in calendar_entries:
        symbol = entry.get("symbol")
        if not symbol:
            continue
        symbol = symbol.upper().strip()
        
        # Check if already evaluated today for EARNINGS_SURPRISE
        existing = db.candidates.find_one({
            "ticker": symbol,
            "calendar_day": today_str,
            "trigger_type": "EARNINGS_SURPRISE"
        })
        if existing:
            print(f"[{symbol}] Earnings trigger already evaluated today, skipping discovery.")
            continue
            
        # Call get_earnings waterfall
        earnings_res = get_earnings(symbol)
        if not earnings_res:
            continue
            
        records = earnings_res["data"]
        if not records:
            continue
            
        # Find the most recent record (which corresponds to the report schedule)
        # Finnhub/yfinance lists are sorted chronologically or reverse
        # Let's inspect the latest one
        latest_record = records[0]
        actual = latest_record.get("actual")
        estimate = latest_record.get("estimate")
        if actual is None or estimate is None:
            continue
            
        actual = float(actual)
        estimate = float(estimate)
        surprise = actual - estimate
        
        is_surprise = False
        surprise_pct = 0.0
        
        if abs(estimate) < 0.01:
            # Near-zero consensus fallback: absolute difference >= $0.05
            if abs(surprise) >= 0.05:
                is_surprise = True
                # Mock surprise percentage to be meaningful
                surprise_pct = (surprise / 0.01) * 100.0
        else:
            surprise_pct = (surprise / abs(estimate)) * 100.0
            if abs(surprise_pct) >= 5.0:
                is_surprise = True
                
        if is_surprise:
            direction = "LONG" if surprise > 0 else "SHORT"
            
            trigger_details = {
                "surprise_pct": surprise_pct,
                "actual_eps": actual,
                "consensus_eps": estimate,
                "surprise_eps": surprise,
                "period": latest_record.get("period", ""),
                "source": earnings_res["source"]
            }
            
            cand_doc = {
                "ticker": symbol,
                "trigger_type": "EARNINGS_SURPRISE",
                "direction": direction,
                "trigger_details": trigger_details,
                "discovery_timestamp": datetime.datetime.utcnow(),
                "trading_cycle_run_id": trading_cycle_run_id,
                "calendar_day": today_str,
                "gate_result": "PENDING"
            }
            
            print(f"[{symbol}] Discovered earnings trigger ({direction}): surprise {surprise_pct:.2f}%")
            discovered_pead.append(cand_doc)
            
    # 2. Material Filing (8-K)
    print("\nScanning SEC 8-K filings...")
    recent_ciks = []
    try:
        recent_ciks = get_sec_recent_8k_ciks()
    except Exception as e:
        print(f"Error fetching SEC 8-K CIKs: {e}")
        
    discovered_8k = []
    for cik in recent_ciks:
        ticker = get_ticker_from_cik(cik)
        if not ticker:
            continue
        ticker = ticker.upper().strip()
        
        # Check if already evaluated today for MATERIAL_FILING
        existing = db.candidates.find_one({
            "ticker": ticker,
            "calendar_day": today_str,
            "trigger_type": "MATERIAL_FILING"
        })
        if existing:
            print(f"[{ticker}] 8-K trigger already evaluated today, skipping discovery.")
            continue
            
        filings_res = get_filings(ticker)
        if not filings_res:
            continue
            
        filings = filings_res["data"]
        # Check filings for 8-Ks within window
        for f in filings:
            if f.get("form") != "8-K":
                continue
            f_date_str = f.get("filingDate", "")
            try:
                f_date = datetime.datetime.strptime(f_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
                
            if f_date >= prior_close.date():
                items = str(f.get("items", ""))
                # Qualifying items: 1.01, 2.01, 2.05, 5.02, 8.01. Ignore 4.01.
                qualifying_items = [it for it in ["1.01", "2.01", "2.05", "5.02", "8.01"] if it in items]
                
                if qualifying_items and "4.01" not in items:
                    # Found a material 8-K! Check price/volume confirmation
                    pv_res = get_price_volume(ticker)
                    if not pv_res:
                        continue
                        
                    pv_data = pv_res["data"]
                    history = pv_data.get("history", [])
                    avg_volume = pv_data.get("avg_daily_volume")
                    
                    if not history or not avg_volume:
                        continue
                        
                    # Find T_trade (first trading candle on or after filing date)
                    t_trade_idx = -1
                    for idx, candle in enumerate(history):
                        c_date_str = candle["date"]
                        if c_date_str >= f_date_str:
                            t_trade_idx = idx
                            break
                            
                    if t_trade_idx == -1 or t_trade_idx == 0:
                        continue
                        
                    t_candle = history[t_trade_idx]
                    prior_candle = history[t_trade_idx - 1]
                    
                    close_val = t_candle["close"]
                    open_val = t_candle["open"]
                    high_val = t_candle["high"]
                    low_val = t_candle["low"]
                    volume_val = t_candle["volume"]
                    prior_close_val = prior_candle["close"]
                    
                    close_move = abs(close_val - prior_close_val) / prior_close_val
                    intraday_move = (high_val - low_val) / low_val
                    max_move = max(close_move, intraday_move)
                    
                    is_volume_confirmed = volume_val >= 1.5 * avg_volume
                    is_price_confirmed = max_move >= 0.03
                    
                    if is_price_confirmed and is_volume_confirmed:
                        direction = "LONG" if close_val > prior_close_val else "SHORT"
                        
                        trigger_details = {
                            "qualifying_items": qualifying_items,
                            "filing_date": f_date_str,
                            "trade_date": t_candle["date"],
                            "close_move_pct": close_move * 100.0,
                            "intraday_move_pct": intraday_move * 100.0,
                            "volume": volume_val,
                            "avg_volume": avg_volume,
                            "source": filings_res["source"]
                        }
                        
                        cand_doc = {
                            "ticker": ticker,
                            "trigger_type": "MATERIAL_FILING",
                            "direction": direction,
                            "trigger_details": trigger_details,
                            "discovery_timestamp": datetime.datetime.utcnow(),
                            "trading_cycle_run_id": trading_cycle_run_id,
                            "calendar_day": today_str,
                            "gate_result": "PENDING"
                        }
                        
                        print(f"[{ticker}] Discovered 8-K filing trigger ({direction}): items {qualifying_items}, move {max_move*100.0:.2f}% on {volume_val/avg_volume:.2f}x avg volume")
                        discovered_8k.append(cand_doc)
                        break  # Only evaluate the latest qualifying filing per ticker
                        
    # Route all discovered candidates to Hard Gates
    all_discovered = discovered_pead + discovered_8k
    print(f"\nDiscovered {len(all_discovered)} candidates in total. Routing to Hard-Gate Engine...")
    
    evaluated_candidates = []
    for cand in all_discovered:
        ticker = cand["ticker"]
        # Save to DB first with PENDING status so trigger details are saved
        db.candidates.update_one(
            {"ticker": ticker, "calendar_day": today_str, "trigger_type": cand["trigger_type"]},
            {"$set": cand},
            upsert=True
        )
        
        # Run hard gates (will update candidate document and return the updated version)
        try:
            evaluated_doc = evaluate_gates(ticker, trading_cycle_run_id)
            evaluated_candidates.append(evaluated_doc)
        except Exception as e:
            print(f"Error evaluating hard gates for {ticker}: {e}")
            
    print(f"=== CANDIDATE DISCOVERY COMPLETED (Evaluated: {len(evaluated_candidates)}) ===")
    return evaluated_candidates
