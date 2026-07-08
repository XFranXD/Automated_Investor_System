import sys
import datetime
from bson import ObjectId
from unittest.mock import patch, MagicMock
from src.db import get_verify_db
import src.db
src.db.get_db = get_verify_db

from src.execution import execute_trade

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_ticker(ticker):
    db = get_verify_db()
    db.trades.delete_many({"ticker": ticker})
    db.candidates.delete_many({"ticker": ticker})
    db.audit_log.delete_many({"ticker": ticker})

# --- MOCK CONTEXTS ---

# Mock 25 candles to compute ATR(22)
# High - Low = 2, Close - Prior Close = 1. TR is always max(2, 1, 1) = 2.0
# So ATR(22) = 2.0
MOCK_HISTORY = []
base_date = datetime.date.today() - datetime.timedelta(days=30)
for i in range(25):
    MOCK_HISTORY.append({
        "date": (base_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.0,
        "volume": 1000000.0 # 1M shares ADV
    })

MOCK_PV_DATA = {
    "source": "yfinance",
    "data": {
        "current_price": 100.0,
        "avg_daily_volume": 1000000.0,
        "avg_daily_dollar_volume": 100000000.0,
        "market_cap": 1000000000.0,
        "history": MOCK_HISTORY
    }
}

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_size_strong_score():
    print("\n--- TEST: Sizing & SL/TP for combined_score = 2.0 ---")
    ticker = "T_EX_STRONG"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7601")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 2.0, # max score
            "confidence_tier": "STRONG",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        # Portfolio State
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": []
        }
        
        # Sizing verification:
        # risk_pct = 0.75 + (2.0 - 0.5)/1.5 * 0.75 = 1.5%
        # Risk allocation: 1.5% of 100,000 = $1,500
        # stop distance = 3 * ATR(22) = 3 * 2.0 = 6.0
        # Shares = floor(1500 / 6.0) = 250 shares
        # Stop-Loss: 100.0 - 6.0 = 94.0
        # Take-Profit: 100.0 + 12.0 = 112.0
        
        with patch("src.execution.get_price_volume", return_value=MOCK_PV_DATA), \
             patch("src.execution.get_company_sector", return_value="Technology"):
             
            trade_id = execute_trade(cand, port_state, {"regime": "RISK_ON"})
            
        trade = db.trades.find_one({"_id": trade_id})
        
        success = (
            isinstance(trade_id, ObjectId) and
            trade is not None and
            trade["risk_pct_used"] == 1.5 and
            trade["share_count"] == 250 and
            trade["initial_stop"] == 94.0 and
            trade["take_profit"] == 112.0
        )
        print_test_result("Sizing for combined_score = 2.0 (1.5% Risk)", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_size_weak_score():
    print("\n--- TEST: Sizing & SL/TP for combined_score = 0.5 ---")
    ticker = "T_EX_WEAK"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7602")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 0.5, # min score
            "confidence_tier": "MODERATE",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": []
        }
        
        # Sizing verification:
        # risk_pct = 0.75 + (0.5 - 0.5)/1.5 * 0.75 = 0.75%
        # Risk allocation: 0.75% of 100,000 = $750
        # Stop distance = 3 * ATR(22) = 6.0
        # Shares = floor(750 / 6.0) = 125 shares (exactly half of 250!)
        
        with patch("src.execution.get_price_volume", return_value=MOCK_PV_DATA), \
             patch("src.execution.get_company_sector", return_value="Technology"):
             
            trade_id = execute_trade(cand, port_state, {"regime": "RISK_ON"})
            
        trade = db.trades.find_one({"_id": trade_id})
        
        success = (
            isinstance(trade_id, ObjectId) and
            trade is not None and
            trade["risk_pct_used"] == 0.75 and
            trade["share_count"] == 125
        )
        print_test_result("Sizing for combined_score = 0.5 (0.75% Risk)", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_kill_switch_active():
    print("\n--- TEST: Kill Switch Block ---")
    ticker = "T_EX_KILL"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7603")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 2.0,
            "confidence_tier": "STRONG",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        # Portfolio State has kill_switch_active = True
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": True,
            "correlation_cap_current": 0.6,
            "open_positions": []
        }
        
        res = execute_trade(cand, port_state, {"regime": "RISK_ON"})
        
        trade = db.trades.find_one({"ticker": ticker})
        logs = list(db.audit_log.find({"ticker": ticker}))
        
        success = (
            res == "ABSTAIN_KILL_SWITCH_ACTIVE" and
            trade is None and
            any("ABSTAIN_KILL_SWITCH_ACTIVE" in l["reason_code"] for l in logs)
        )
        print_test_result("Kill Switch Block", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_existing_position_block():
    print("\n--- TEST: Existing Position Block ---")
    ticker = "T_EX_EXIST"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7604")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 2.0,
            "confidence_tier": "STRONG",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        # Portfolio State already has a position in this ticker
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": [{"ticker": ticker, "share_count": 100, "value": 10000.0}]
        }
        
        res = execute_trade(cand, port_state, {"regime": "RISK_ON"})
        
        # Verify no new trade is opened and no existing trades document is modified
        count = db.trades.count_documents({"ticker": ticker})
        
        success = (
            res == "ABSTAIN_EXISTING_POSITION" and
            count == 0
        )
        print_test_result("Existing Position Block", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_correlation_cap_block():
    print("\n--- TEST: Correlation Cap Block ---")
    ticker = "T_EX_CORR"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7605")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 2.0,
            "confidence_tier": "STRONG",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": [{"ticker": "AAPL", "share_count": 100, "value": 15000.0}]
        }
        
        # 1. RISK_ON: Cap is 0.6, Mock correlation to AAPL = 0.7
        with patch("src.execution.compute_correlation", return_value=0.7):
            res_on = execute_trade(cand, port_state, {"regime": "RISK_ON"})
            
        # 2. RISK_OFF: Cap is 0.4, Mock correlation to AAPL = 0.5 (above tightened cap)
        port_state_off = port_state.copy()
        port_state_off["correlation_cap_current"] = 0.4
        with patch("src.execution.compute_correlation", return_value=0.5):
            res_off = execute_trade(cand, port_state_off, {"regime": "RISK_OFF"})
            
        success = (
            res_on == "ABSTAIN_CORRELATION_CAP" and
            res_off == "ABSTAIN_CORRELATION_CAP"
        )
        print_test_result("Correlation Cap Block", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_liquidity_cap_downsize():
    print("\n--- TEST: Liquidity Capacity Cap Sizing Down ---")
    ticker = "T_EX_LIQUID"
    clean_db_for_ticker(ticker)
    try:
        db = get_verify_db()
        cand_id = ObjectId("6a49b6110105d061e8ba7606")
        cand = {
            "_id": cand_id,
            "ticker": ticker,
            "direction": "LONG",
            "combined_score": 2.0,
            "confidence_tier": "STRONG",
            "gate_result": "PASSED"
        }
        db.candidates.insert_one(cand)
        
        # Mock price/volume with low ADV = 1,000 shares
        # So max 10% of ADV is 100 shares.
        # Normal ATR sizing would compute 250 shares.
        # Scaled down size should be exactly 100 shares!
        mock_low_adv_pv = {
            "source": "yfinance",
            "data": {
                "current_price": 100.0,
                "avg_daily_volume": 1000.0, # low ADV
                "avg_daily_dollar_volume": 100000.0,
                "market_cap": 1000000.0,
                "history": MOCK_HISTORY
            }
        }
        
        port_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": []
        }
        
        with patch("src.execution.get_price_volume", return_value=mock_low_adv_pv), \
             patch("src.execution.get_company_sector", return_value="Technology"):
             
            trade_id = execute_trade(cand, port_state, {"regime": "RISK_ON"})
            
        trade = db.trades.find_one({"_id": trade_id})
        
        success = (
            isinstance(trade_id, ObjectId) and
            trade is not None and
            trade["share_count"] == 100 and # Sized down to 10% ADV
            trade["reasoning_chain"]["is_sized_down"] == True
        )
        print_test_result("Liquidity ADV Sizing Down", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def run_all_tests():
    print("=== STARTING PHASE 5 EXECUTION ENGINE VERIFICATION ===")
    results = [
        test_size_strong_score(),
        test_size_weak_score(),
        test_kill_switch_active(),
        test_existing_position_block(),
        test_correlation_cap_block(),
        test_liquidity_cap_downsize()
    ]
    
    success = all(results)
    print("\n=== PHASE 5 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
