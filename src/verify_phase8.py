import os
import sys
import datetime
from bson import ObjectId
from unittest.mock import patch, MagicMock
from src.db import get_db
from src.dashboard_builder import generate_dashboard

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_verify():
    db = get_db()
    db.trades.delete_many({})
    db.stats_aggregates.delete_many({})
    db.portfolio_state.delete_one({"_id": "current_state"})
    db.candidates.delete_many({})
    db.evaluations.delete_many({})

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_file_generation_and_sanitization():
    print("\n--- TEST: File Generation & Credential Sanitization ---")
    clean_db_for_verify()
    
    # Run compiler
    generate_dashboard()
    
    # Check files exist
    idx_exists = os.path.exists("docs/index.html")
    sys_exists = os.path.exists("docs/system.html")
    css_exists = os.path.exists("docs/styles.css")
    
    # Scan for connection string leaks
    leaks_found = False
    for filename in ["docs/index.html", "docs/system.html", "docs/styles.css"]:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
                if "mongodb+srv" in content or "AIzaSy" in content:
                    print(f"CRITICAL ERROR: Leak found in {filename}!")
                    leaks_found = True
                    
    success = idx_exists and sys_exists and css_exists and not leaks_found
    print_test_result("File Generation & Credential Sanitization", success)
    return success

def test_summary_and_stat_accuracy():
    print("\n--- TEST: Summary & Stat Accuracy ---")
    clean_db_for_verify()
    db = get_db()
    
    # Setup mock trades:
    # 1. LONG, Entry 100, Exit 110, 100 shares -> PnL +1000 (Win)
    # 2. SHORT, Entry 100, Exit 105, 100 shares -> PnL -500 (Loss)
    # 3. LONG, Open position, Entry 100, 100 shares. Current price is 105 -> PnL +500 (Unrealized)
    base_time = datetime.datetime.utcnow()
    
    t1 = {
        "ticker": "T_DASH_1",
        "direction": "LONG",
        "entry_price": 100.0,
        "exit_price": 110.0,
        "share_count": 100,
        "realized_pnl": 1000.0,
        "status": "CLOSED",
        "entry_timestamp": base_time - datetime.timedelta(days=2),
        "exit_timestamp": base_time - datetime.timedelta(days=1),
        "reasoning_chain": {"trigger_type": "EARNINGS_SURPRISE"}
    }
    
    t2 = {
        "ticker": "T_DASH_2",
        "direction": "SHORT",
        "entry_price": 100.0,
        "exit_price": 105.0,
        "share_count": 100,
        "realized_pnl": -500.0,
        "status": "CLOSED",
        "entry_timestamp": base_time - datetime.timedelta(days=2),
        "exit_timestamp": base_time - datetime.timedelta(days=1),
        "reasoning_chain": {"trigger_type": "MATERIAL_FILING"}
    }
    
    t3 = {
        "ticker": "T_DASH_3",
        "direction": "LONG",
        "entry_price": 100.0,
        "share_count": 100,
        "status": "OPEN",
        "entry_timestamp": base_time - datetime.timedelta(days=1),
        "reasoning_chain": {"trigger_type": "EARNINGS_SURPRISE"}
    }
    
    db.trades.insert_many([t1, t2, t3])
    
    # Portfolio State
    db.portfolio_state.insert_one({
        "_id": "current_state",
        "equity": 100500.0,
        "cash": 90500.0,
        "kill_switch_active": False,
        "correlation_cap_current": 0.6,
        "open_positions": [{"ticker": "T_DASH_3", "direction": "LONG", "share_count": 100, "value": 10000.0, "sector": "Technology"}]
    })
    
    # Mock price volume for open trade: current price = 105.0 (PnL = +500)
    mock_pv = {
        "source": "yfinance",
        "data": {
            "current_price": 105.0,
            "avg_daily_volume": 1000000.0,
            "history": []
        }
    }
    
    # Compile
    with patch("src.dashboard_builder.get_price_volume", return_value=mock_pv):
        generate_dashboard()
        
    # Open files and inspect compiled numbers
    with open("docs/index.html", "r") as f:
        content = f.read()
        
    # Win rate should be: wins/closed = 1 / 2 = 50.0%
    # Realized PnL: +1000 - 500 = +500.00
    # Closed: 2
    # Open: 1
    total_pnl_ok = "$+500.00" in content
    win_rate_ok = "50.0%" in content
    closed_ok = "2" in content
    open_ok = "1" in content
    
    success = total_pnl_ok and win_rate_ok and closed_ok and open_ok
    print_test_result("Summary & Stat Accuracy", success)
    return success

def test_no_database_writes():
    print("\n--- TEST: No Database Writes ---")
    
    # Read dashboard_builder.py
    builder_path = "src/dashboard_builder.py"
    with open(builder_path, "r") as f:
        code = f.read()
        
    # Check for pymongo write patterns: insert_one, insert_many, update_one, update_many, delete_one, delete_many, replace_one
    write_patterns = [
        "insert_one", "insert_many",
        "update_one", "update_many",
        "delete_one", "delete_many",
        "replace_one"
    ]
    
    violations = []
    for pattern in write_patterns:
        if pattern in code:
            violations.append(pattern)
            
    success = len(violations) == 0
    if not success:
        print(f"Violations found in dashboard_builder: {violations}")
        
    print_test_result("No Database Writes", success)
    return success


def run_all_tests():
    print("=== STARTING PHASE 8 WEB DASHBOARD VERIFICATION ===")
    results = [
        test_file_generation_and_sanitization(),
        test_summary_and_stat_accuracy(),
        test_no_database_writes()
    ]
    
    success = all(results)
    print("\n=== PHASE 8 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
