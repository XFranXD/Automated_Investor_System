import sys
import datetime
from bson import ObjectId
from unittest.mock import patch, MagicMock
from src.db import get_db
from src.portfolio_monitor import monitor_portfolio

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_verify():
    db = get_db()
    db.trades.delete_many({"trading_cycle_run_id": "run-monitor-test"})
    db.portfolio_state.delete_one({"_id": "current_state"})
    db.audit_log.delete_many({"trading_cycle_run_id": "run-monitor-test"})

# --- MOCK ATR RETRIEVER ---

MOCK_HISTORY = []
base_date = datetime.date.today() - datetime.timedelta(days=30)
for i in range(25):
    MOCK_HISTORY.append({
        "date": (base_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.0,
        "volume": 1000000.0
    })

# ATR(22) is always 2.0 (High - Low = 2.0)
MOCK_PV_BASE = {
    "source": "yfinance",
    "data": {
        "current_price": 100.0,
        "avg_daily_volume": 1000000.0,
        "history": MOCK_HISTORY
    }
}

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_chandelier_stop_ratcheting():
    print("\n--- TEST: Trailing Stop Ratcheting ---")
    clean_db_for_verify()
    db = get_db()
    
    # 1. Initialize Portfolio State
    port_state = {
        "_id": "current_state",
        "equity": 100000.0,
        "cash": 90000.0,
        "kill_switch_active": False,
        "correlation_cap_current": 0.6,
        "open_positions": []
    }
    db.portfolio_state.insert_one(port_state)
    
    # 2. Open Long Trade: entry 100.0, initial stop 94.0, highest high 100.0
    trade_id = ObjectId("6a49b6110105d061e8ba7701")
    trade = {
        "_id": trade_id,
        "ticker": "T_MON_RATCH",
        "direction": "LONG",
        "entry_price": 100.0,
        "share_count": 100,
        "combined_score": 2.0,
        "risk_pct_used": 1.5,
        "initial_stop": 94.0,
        "current_stop": 94.0,
        "take_profit": 120.0,
        "status": "OPEN",
        "entry_timestamp": datetime.datetime.utcnow(),
        "highest_high_since_entry": 100.0,
        "trading_cycle_run_id": "run-monitor-test"
    }
    db.trades.insert_one(trade)
    
    # Associate position in portfolio state
    db.portfolio_state.update_one(
        {"_id": "current_state"},
        {"$push": {
            "open_positions": {
                "ticker": "T_MON_RATCH",
                "direction": "LONG",
                "share_count": 100,
                "entry_price": 100.0,
                "value": 10000.0,
                "sector": "Technology",
                "trade_id": trade_id
            }
        }}
    )
    
    # A. Execute cycle when price rises to 110.0
    # Highest high -> 110.0. ATR = 2.0.
    # New stop = 110.0 - 3 * 2 = 104.0 (ratchets up from 94.0)
    pv_1 = MOCK_PV_BASE.copy()
    pv_1["data"] = pv_1["data"].copy()
    pv_1["data"]["current_price"] = 110.0
    
    with patch("src.portfolio_monitor.get_price_volume", return_value=pv_1), \
         patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_ON"}):
        monitor_portfolio("run-monitor-test")
        
    t_doc_1 = db.trades.find_one({"_id": trade_id})
    stop_ratcheted_up = t_doc_1["current_stop"] == 104.0
    
    # B. Execute cycle when price drops back to 102.0
    # Highest high is still 110.0. New calculated stop is 110.0 - 6 = 104.0.
    # Stop should NOT move down to 102 - 6 = 96.0! It should stay at 104.0.
    pv_2 = MOCK_PV_BASE.copy()
    pv_2["data"] = pv_2["data"].copy()
    pv_2["data"]["current_price"] = 102.0
    
    with patch("src.portfolio_monitor.get_price_volume", return_value=pv_2), \
         patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_ON"}):
        monitor_portfolio("run-monitor-test")
        
    t_doc_2 = db.trades.find_one({"_id": trade_id})
    stop_held_high = t_doc_2["current_stop"] == 104.0
    
    success = stop_ratcheted_up and stop_held_high
    print_test_result("Trailing Stop Ratcheting", success)
    return success

def test_stop_loss_priority():
    print("\n--- TEST: Stop Loss Priority Exit ---")
    clean_db_for_verify()
    db = get_db()
    
    # Initialize State
    port_state = {
        "_id": "current_state",
        "equity": 100000.0,
        "cash": 90000.0,
        "kill_switch_active": False,
        "correlation_cap_current": 0.6,
        "open_positions": []
    }
    db.portfolio_state.insert_one(port_state)
    
    # Create trade where price moves to 80.0
    # This is below stop (94.0) AND take_profit is mocked to 75.0 (for short or long tp breach)
    # We construct a LONG position where stop is 94.0 and TP is 75.0 (TP is technically lower than stop, simulating a cross check anomaly)
    trade_id = ObjectId("6a49b6110105d061e8ba7702")
    trade = {
        "_id": trade_id,
        "ticker": "T_MON_PRIO",
        "direction": "LONG",
        "entry_price": 100.0,
        "share_count": 100,
        "combined_score": 2.0,
        "risk_pct_used": 1.5,
        "initial_stop": 94.0,
        "current_stop": 94.0,
        "take_profit": 75.0, # TP is also hit when price drops to 70.0
        "status": "OPEN",
        "entry_timestamp": datetime.datetime.utcnow(),
        "highest_high_since_entry": 100.0,
        "trading_cycle_run_id": "run-monitor-test"
    }
    db.trades.insert_one(trade)
    
    db.portfolio_state.update_one(
        {"_id": "current_state"},
        {"$push": {
            "open_positions": {
                "ticker": "T_MON_PRIO",
                "direction": "LONG",
                "share_count": 100,
                "entry_price": 100.0,
                "value": 10000.0,
                "sector": "Technology",
                "trade_id": trade_id
            }
        }}
    )
    
    # Price is 70.0 (both Stop 94.0 and TP 75.0 are breached)
    pv = MOCK_PV_BASE.copy()
    pv["data"] = pv["data"].copy()
    pv["data"]["current_price"] = 70.0
    
    with patch("src.portfolio_monitor.get_price_volume", return_value=pv), \
         patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_ON"}):
        monitor_portfolio("run-monitor-test")
        
    t_closed = db.trades.find_one({"_id": trade_id})
    
    # Verify exit_reason is STOP, not TAKE_PROFIT
    success = (
        t_closed["status"] == "CLOSED" and
        t_closed["exit_reason"] == "STOP"
    )
    print_test_result("Stop Loss Priority Exit", success)
    return success

def test_drawdown_kill_switch():
    print("\n--- TEST: Drawdown Kill Switch Trip ---")
    clean_db_for_verify()
    db = get_db()
    
    # Set high-water mark to 100,000
    # Portfolio equity drops to 85,000 (15% drawdown -> trips switch)
    port_state = {
        "_id": "current_state",
        "equity": 100000.0,
        "cash": 85000.0, # cash + open positions = 85,000
        "high_water_mark": 100000.0,
        "kill_switch_active": False,
        "correlation_cap_current": 0.6,
        "open_positions": []
    }
    db.portfolio_state.insert_one(port_state)
    
    # Run cycle with no open positions (equity stays 85,000)
    with patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_ON"}), \
         patch("src.portfolio_monitor.send_kill_switch_notification") as mock_notify:
        monitor_portfolio("run-monitor-test")
        
    updated_state = db.portfolio_state.find_one({"_id": "current_state"})
    
    success = (
        updated_state["kill_switch_active"] == True and
        updated_state["drawdown_pct"] == 15.0 and
        mock_notify.called
    )
    print_test_result("Drawdown Kill Switch Trip", success)
    return success

def test_regime_correlation_caps():
    print("\n--- TEST: Regime-Dependent Correlation Cap ---")
    clean_db_for_verify()
    db = get_db()
    
    # 1. RISK_OFF -> Cap should be 0.4
    db.portfolio_state.insert_one({
        "_id": "current_state",
        "equity": 100000.0,
        "cash": 100000.0,
        "kill_switch_active": False,
        "correlation_cap_current": 0.6,
        "open_positions": []
    })
    
    with patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_OFF"}):
        monitor_portfolio("run-monitor-test")
    state_off = db.portfolio_state.find_one({"_id": "current_state"})
    
    # 2. RISK_ON -> Cap should be 0.6
    with patch("src.portfolio_monitor.get_regime_state", return_value={"regime": "RISK_ON"}):
        monitor_portfolio("run-monitor-test")
    state_on = db.portfolio_state.find_one({"_id": "current_state"})
    
    success = (
        state_off["correlation_cap_current"] == 0.4 and
        state_on["correlation_cap_current"] == 0.6
    )
    print_test_result("Regime-Dependent Correlation Cap", success)
    return success

def run_all_tests():
    print("=== STARTING PHASE 6 PORTFOLIO MONITOR VERIFICATION ===")
    results = [
        test_chandelier_stop_ratcheting(),
        test_stop_loss_priority(),
        test_drawdown_kill_switch(),
        test_regime_correlation_caps()
    ]
    
    success = all(results)
    print("\n=== PHASE 6 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
