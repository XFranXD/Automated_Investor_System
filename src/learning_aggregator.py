import math
import datetime
from src.db import get_db
from src.logger import write_audit_log

def get_derived_metrics(bucket_doc):
    """
    Computes derived metrics from aggregated statistics:
    - win_rate: wins / tradeCount
    - avg_return (average return/PnL): sumPnL / tradeCount
    - expectancy: (win_rate * avg_win) - (loss_rate * avg_loss)
    - profit_factor: grossProfit / grossLoss (returns grossProfit if grossLoss is 0)
    - std_dev: standard deviation computed as sqrt((sumPnLSquared / tradeCount) - avg_return^2)
    """
    tc = bucket_doc.get("tradeCount", 0)
    if tc == 0:
        return {
            "win_rate": 0.0,
            "avg_return": 0.0,
            "expectancy": 0.0,
            "profit_factor": 1.0,
            "std_dev": 0.0
        }
        
    wins = bucket_doc.get("wins", 0)
    losses = bucket_doc.get("losses", 0)
    sum_pnl = bucket_doc.get("sumPnL", 0.0)
    sum_pnl_sq = bucket_doc.get("sumPnLSquared", 0.0)
    gp = bucket_doc.get("grossProfit", 0.0)
    gl = bucket_doc.get("grossLoss", 0.0)
    
    win_rate = wins / tc
    avg_return = sum_pnl / tc
    
    avg_win = gp / wins if wins > 0 else 0.0
    avg_loss = gl / losses if losses > 0 else 0.0
    loss_rate = losses / tc
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    
    profit_factor = gp / gl if gl > 0.0 else gp
    
    variance = max(0.0, (sum_pnl_sq / tc) - (avg_return ** 2))
    std_dev = math.sqrt(variance)
    
    return {
        "win_rate": win_rate,
        "avg_return": avg_return,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "std_dev": std_dev
    }

def update_bucket(dimension, value, pnl):
    """
    Increments metrics in a single aggregates document using MongoDB additive updates.
    """
    db = get_db()
    bucket_id = {"dimension": dimension, "value": value}
    
    # Check/Initialize bucket if not present to ensure $max/$min run on active floats
    doc = db.stats_aggregates.find_one({"_id": bucket_id})
    if not doc:
        db.stats_aggregates.insert_one({
            "_id": bucket_id,
            "tradeCount": 0,
            "wins": 0,
            "losses": 0,
            "sumPnL": 0.0,
            "sumPnLSquared": 0.0,
            "grossProfit": 0.0,
            "grossLoss": 0.0,
            "maxWin": 0.0,
            "maxLoss": 0.0
        })
        
    is_win = pnl > 0
    is_loss = pnl < 0
    
    wins_inc = 1 if is_win else 0
    losses_inc = 1 if is_loss else 0
    gp = pnl if is_win else 0.0
    gl = abs(pnl) if is_loss else 0.0
    
    db.stats_aggregates.update_one(
        {"_id": bucket_id},
        {
            "$inc": {
                "tradeCount": 1,
                "wins": wins_inc,
                "losses": losses_inc,
                "sumPnL": pnl,
                "sumPnLSquared": pnl ** 2,
                "grossProfit": gp,
                "grossLoss": gl
            },
            "$max": {
                "maxWin": max(0.0, pnl)
            },
            "$min": {
                "maxLoss": min(0.0, pnl)
            }
        }
    )

def run_weekly_aggregation():
    """
    Weekly learning aggregator. Aggregates all closed trades since last run
    into stats_aggregates collection across 5 dimensions.
    Purely informational (no feedback updates are written to other subsystems).
    """
    db = get_db()
    
    # 1. Fetch persistent last processed timestamp
    state = db.system_state.find_one({"_id": "learning_aggregator_state"})
    if not state:
        state = {
            "_id": "learning_aggregator_state",
            "last_processed_timestamp": datetime.datetime.min
        }
        db.system_state.replace_one({"_id": "learning_aggregator_state"}, state, upsert=True)
        
    last_processed = state.get("last_processed_timestamp", datetime.datetime.min)
    
    # 2. Query closed trades after last_processed sorted ascending
    closed_trades = list(db.trades.find({
        "status": "CLOSED",
        "exit_timestamp": {"$gt": last_processed}
    }).sort("exit_timestamp", 1))
    
    if not closed_trades:
        print("Weekly Aggregator: No new closed trades found since last run. Skipping.")
        return 0
        
    print(f"Weekly Aggregator: Found {len(closed_trades)} new closed trades to aggregate.")
    
    # 3. Process each trade
    last_exit_time = last_processed
    for trade in closed_trades:
        direction = trade.get("direction", "LONG").upper()
        
        # Pull details from reasoning_chain if present, with defaults
        r_chain = trade.get("reasoning_chain") or {}
        trigger_type = r_chain.get("trigger_type") or "EARNINGS_SURPRISE"
        confidence_tier = trade.get("confidence_tier") or r_chain.get("confidence_tier") or "STRONG"
        
        # Regime state at entry (default RISK_ON)
        regime_state = r_chain.get("regime_state_at_decision") or "RISK_ON"
        
        # Calculate realized P&L if not explicitly saved
        pnl = trade.get("realized_pnl")
        if pnl is None:
            entry = float(trade.get("entry_price", 0.0))
            exit = float(trade.get("exit_price", 0.0))
            shares = int(trade.get("share_count", 0))
            if direction == "LONG":
                pnl = shares * (exit - entry)
            else:
                pnl = shares * (entry - exit)
        else:
            pnl = float(pnl)
            
        # Update 5 buckets
        # Bucket 1: Overall
        update_bucket("overall", "total", pnl)
        # Bucket 2: By direction
        update_bucket("direction", direction, pnl)
        # Bucket 3: By trigger type
        update_bucket("trigger_type", trigger_type, pnl)
        # Bucket 4: By confidence tier
        update_bucket("confidence_tier", confidence_tier, pnl)
        # Bucket 5: By regime state at entry
        update_bucket("regime_state", regime_state, pnl)
        
        # Keep track of latest exit timestamp
        exit_ts = trade.get("exit_timestamp")
        if exit_ts and exit_ts > last_exit_time:
            last_exit_time = exit_ts
            
    # 4. Save progress
    db.system_state.update_one(
        {"_id": "learning_aggregator_state"},
        {"$set": {"last_processed_timestamp": last_exit_time}}
    )
    
    reasoning = (
        f"Executed weekly aggregation. Processed {len(closed_trades)} new closed trades. "
        f"Updated aggregates up to timestamp: {last_exit_time.isoformat()}."
    )
    write_audit_log(
        subsystem="learning_aggregator",
        action="weekly_aggregation",
        decision="AGGREGATED",
        reasoning=reasoning
    )
    print(f"Weekly Aggregator: Completed. Processed {len(closed_trades)} trades.")
    return len(closed_trades)
