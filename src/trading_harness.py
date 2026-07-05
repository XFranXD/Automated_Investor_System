import datetime
from bson import ObjectId
from src.db import get_db
from src.logger import write_audit_log

def open_paper_position(ticker, direction, share_count, entry_price, initial_stop, take_profit, combined_score, risk_pct_used, confidence_tier, reasoning_chain=None):
    """
    Creates a new paper position in the trades collection.
    
    Parameters:
    - ticker (str): Ticker symbol of the asset.
    - direction (str): 'LONG' or 'SHORT'.
    - share_count (int): Number of shares simulated.
    - entry_price (float): Simulated fill price.
    - initial_stop (float): Initial stop-loss level.
    - take_profit (float): Take-profit (limit exit) level.
    - combined_score (float): Score assigned by the decision engine (0.5 to 2.0).
    - risk_pct_used (float): Risk percentage of portfolio equity allocated.
    - confidence_tier (str): 'STRONG' or 'MODERATE'.
    - reasoning_chain (dict, optional): Context containing candidate/evaluation IDs and scoring snapshot.
    
    Returns:
    - ObjectId: The unique DB ID of the newly opened trade.
    """
    db = get_db()
    ticker = ticker.upper().strip()
    direction = direction.upper().strip()
    confidence_tier = confidence_tier.upper().strip()
    
    if direction not in ["LONG", "SHORT"]:
        raise ValueError(f"Invalid trade direction: {direction}. Must be LONG or SHORT.")
        
    trade_doc = {
        "ticker": ticker,
        "direction": direction,
        "entry_price": float(entry_price),
        "share_count": int(share_count),
        "combined_score": float(combined_score),
        "risk_pct_used": float(risk_pct_used),
        "initial_stop": float(initial_stop),
        "current_stop": float(initial_stop), # Starts equal to initial stop
        "take_profit": float(take_profit),
        "confidence_tier": confidence_tier,
        "status": "OPEN",
        "entry_timestamp": datetime.datetime.utcnow(),
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None,
        "realized_pnl": None,
        "highest_high_since_entry": float(entry_price),
        "lowest_low_since_entry": float(entry_price),
        "reasoning_chain": reasoning_chain or {}
    }
    
    result = db.trades.insert_one(trade_doc)
    trade_id = result.inserted_id
    
    reasoning = (
        f"Opened simulated {direction} position for {ticker}: {share_count} shares "
        f"@ ${entry_price:.2f}. SL: ${initial_stop:.2f}, TP: ${take_profit:.2f}."
    )
    write_audit_log(
        subsystem="execution",
        action="open_position",
        decision="OPENED",
        reasoning=reasoning,
        ticker=ticker
    )
    
    return trade_id

def close_paper_position(trade_id, exit_price, exit_reason):
    """
    Closes an open paper position, computing realized P&L.
    
    Parameters:
    - trade_id (ObjectId or str): Unique ID of the trade record.
    - exit_price (float): Simulated exit price.
    - exit_reason (str): Reason for closing ('STOP', 'TAKE_PROFIT', or 'MANUAL').
    
    Returns:
    - dict: The updated closed trade document.
    """
    db = get_db()
    
    if isinstance(trade_id, str):
        trade_id = ObjectId(trade_id)
        
    trade = db.trades.find_one({"_id": trade_id})
    if not trade:
        raise ValueError(f"Trade with ID '{trade_id}' not found.")
        
    if trade.get("status") == "CLOSED":
        print(f"Warning: Trade '{trade_id}' is already closed.")
        return trade
        
    direction = trade["direction"]
    entry_price = trade["entry_price"]
    share_count = trade["share_count"]
    
    # Compute realized PnL
    # Long: PnL = (exit_price - entry_price) * shares
    # Short: PnL = (entry_price - exit_price) * shares
    if direction == "LONG":
        realized_pnl = (float(exit_price) - entry_price) * share_count
    elif direction == "SHORT":
        realized_pnl = (entry_price - float(exit_price)) * share_count
    else:
        raise ValueError(f"Invalid direction in DB trade record: {direction}")
        
    db.trades.update_one(
        {"_id": trade_id},
        {
            "$set": {
                "status": "CLOSED",
                "exit_price": float(exit_price),
                "exit_timestamp": datetime.datetime.utcnow(),
                "exit_reason": exit_reason.upper().strip(),
                "realized_pnl": realized_pnl
            }
        }
    )
    
    updated_trade = db.trades.find_one({"_id": trade_id})
    
    reasoning = (
        f"Closed simulated {direction} position for {trade['ticker']}: {share_count} shares "
        f"@ ${exit_price:.2f} (Entry: ${entry_price:.2f}). Realized PnL: ${realized_pnl:+.2f}."
    )
    write_audit_log(
        subsystem="portfolio_monitor",
        action="close_position",
        decision="CLOSED",
        reasoning=reasoning,
        ticker=trade["ticker"],
        reason_code=exit_reason.upper().strip()
    )
    
    return updated_trade
