import sys
import datetime
from unittest.mock import patch, MagicMock
from src.db import get_verify_db
import src.db
src.db.get_db = get_verify_db

from src.discovery import discover_candidates

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_ticker(ticker):
    db = get_verify_db()
    db.candidates.delete_many({"ticker": ticker})
    db.audit_log.delete_many({"ticker": ticker})

# --- MOCK STRUCTURES ---

# 1. Earnings Surprise mock data: normal 6% beat
MOCK_EARNINGS_NORMAL_BEAT = {
    "source": "Finnhub",
    "data": [
        {
            "actual": 1.06,
            "estimate": 1.00,
            "period": "2026-03-31",
            "symbol": "T_ER_BEAT"
        }
    ]
}

# 2. Earnings Surprise mock data: near-zero consensus ($0.00 consensus, actual $0.06)
MOCK_EARNINGS_NEAR_ZERO = {
    "source": "yfinance",
    "data": [
        {
            "actual": 0.06,
            "estimate": 0.00,
            "period": "2026-03-31",
            "symbol": "T_ER_ZERO"
        }
    ]
}

# 3. Filings mock data: Item 8.01 (Material Filing)
MOCK_FILINGS_8K_801 = {
    "source": "SEC_EDGAR",
    "data": [
        {
            "form": "8-K",
            "items": "8.01",
            "filingDate": datetime.date.today().strftime("%Y-%m-%d"),
            "accessionNumber": "0000123456-26-000300"
        }
    ]
}

# 4. Filings mock data: Item 4.01 (Disqualifying 8-K)
MOCK_FILINGS_8K_401 = {
    "source": "SEC_EDGAR",
    "data": [
        {
            "form": "8-K",
            "items": "4.01",
            "filingDate": datetime.date.today().strftime("%Y-%m-%d"),
            "accessionNumber": "0000123456-26-000310"
        }
    ]
}

# 5. Price/Volume mock data: +4% move on 2x average volume
MOCK_PV_CONFIRMED = {
    "source": "yfinance",
    "data": {
        "current_price": 104.0,
        "avg_daily_volume": 100000.0,
        "avg_daily_dollar_volume": 10000000.0,
        "market_cap": 10000000.0,
        "history": [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 100000.0
            },
            {
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "open": 100.0,
                "high": 105.0,
                "low": 100.0,
                "close": 104.0, # +4% close-to-close
                "volume": 200000.0 # 2x average volume
            }
        ]
    }
}

# 6. Price/Volume mock data: only 1% move on 2x volume (fails confirmation)
MOCK_PV_UNCONFIRMED = {
    "source": "yfinance",
    "data": {
        "current_price": 101.0,
        "avg_daily_volume": 100000.0,
        "avg_daily_dollar_volume": 10000000.0,
        "market_cap": 10000000.0,
        "history": [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 100000.0
            },
            {
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "open": 100.0,
                "high": 101.5,
                "low": 99.8,
                "close": 101.0, # only +1% move
                "volume": 200000.0 # 2x volume
            }
        ]
    }
}

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_earnings_beat_normal():
    print("\n--- TEST: Earnings Beat (Normal Consensus) ---")
    ticker = "T_ER_BEAT"
    clean_db_for_ticker(ticker)
    try:
        # Mock Finnhub calendar to return this symbol
        calendar_mock = [{"symbol": ticker, "date": datetime.date.today().strftime("%Y-%m-%d")}]
        
        # Stub evaluate_gates to return the document with PASSED status
        def mock_eval_gates(sym, run_id=None):
            db = get_verify_db()
            doc = db.candidates.find_one({"ticker": sym})
            doc["gate_result"] = "PASSED"
            db.candidates.update_one({"_id": doc["_id"]}, {"$set": {"gate_result": "PASSED"}})
            return doc
            
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=calendar_mock), \
             patch("src.discovery.get_earnings", return_value=MOCK_EARNINGS_NORMAL_BEAT), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=[]), \
             patch("src.discovery.evaluate_gates", side_effect=mock_eval_gates):
             
            res = discover_candidates("run-er-beat")
            
        db = get_verify_db()
        cand = db.candidates.find_one({"ticker": ticker})
        
        success = (
            len(res) == 1 and
            res[0]["ticker"] == ticker and
            res[0]["trigger_type"] == "EARNINGS_SURPRISE" and
            res[0]["direction"] == "LONG" and
            res[0]["gate_result"] == "PASSED" and
            cand is not None and
            abs(cand["trigger_details"]["surprise_pct"] - 6.0) < 1e-9
        )
        print_test_result("Earnings Beat Normal", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_earnings_near_zero_consensus():
    print("\n--- TEST: Earnings Beat (Near-Zero Consensus Fallback) ---")
    ticker = "T_ER_ZERO"
    clean_db_for_ticker(ticker)
    try:
        calendar_mock = [{"symbol": ticker, "date": datetime.date.today().strftime("%Y-%m-%d")}]
        
        def mock_eval_gates(sym, run_id=None):
            db = get_verify_db()
            doc = db.candidates.find_one({"ticker": sym})
            doc["gate_result"] = "PASSED"
            db.candidates.update_one({"_id": doc["_id"]}, {"$set": {"gate_result": "PASSED"}})
            return doc
            
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=calendar_mock), \
             patch("src.discovery.get_earnings", return_value=MOCK_EARNINGS_NEAR_ZERO), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=[]), \
             patch("src.discovery.evaluate_gates", side_effect=mock_eval_gates):
             
            res = discover_candidates("run-er-zero")
            
        db = get_verify_db()
        cand = db.candidates.find_one({"ticker": ticker})
        
        success = (
            len(res) == 1 and
            res[0]["ticker"] == ticker and
            res[0]["trigger_type"] == "EARNINGS_SURPRISE" and
            res[0]["direction"] == "LONG" and
            cand is not None and
            cand["trigger_details"]["actual_eps"] == 0.06 and
            cand["trigger_details"]["consensus_eps"] == 0.00
        )
        print_test_result("Earnings Near-Zero Fallback", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_filing_8k_confirmed():
    print("\n--- TEST: Material 8-K Confirmed Move ---")
    ticker = "T_8K_CONFIRMED"
    clean_db_for_ticker(ticker)
    try:
        # Mock SEC recent CIKs
        ciks_mock = ["0000999999"]
        
        def mock_eval_gates(sym, run_id=None):
            db = get_verify_db()
            doc = db.candidates.find_one({"ticker": sym})
            doc["gate_result"] = "PASSED"
            db.candidates.update_one({"_id": doc["_id"]}, {"$set": {"gate_result": "PASSED"}})
            return doc
            
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=[]), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=ciks_mock), \
             patch("src.discovery.get_ticker_from_cik", return_value=ticker), \
             patch("src.discovery.get_filings", return_value=MOCK_FILINGS_8K_801), \
             patch("src.discovery.get_price_volume", return_value=MOCK_PV_CONFIRMED), \
             patch("src.discovery.evaluate_gates", side_effect=mock_eval_gates):
             
            res = discover_candidates("run-8k-confirmed")
            
        db = get_verify_db()
        cand = db.candidates.find_one({"ticker": ticker})
        
        success = (
            len(res) == 1 and
            res[0]["ticker"] == ticker and
            res[0]["trigger_type"] == "MATERIAL_FILING" and
            res[0]["direction"] == "LONG" and
            cand is not None and
            "8.01" in cand["trigger_details"]["qualifying_items"] and
            cand["trigger_details"]["close_move_pct"] == 4.0
        )
        print_test_result("8-K Filing Confirmed", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_filing_8k_unconfirmed():
    print("\n--- TEST: Material 8-K Unconfirmed Move ---")
    ticker = "T_8K_UNCONFIRMED"
    clean_db_for_ticker(ticker)
    try:
        ciks_mock = ["0000999998"]
        
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=[]), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=ciks_mock), \
             patch("src.discovery.get_ticker_from_cik", return_value=ticker), \
             patch("src.discovery.get_filings", return_value=MOCK_FILINGS_8K_801), \
             patch("src.discovery.get_price_volume", return_value=MOCK_PV_UNCONFIRMED):
             
            res = discover_candidates("run-8k-unconfirmed")
            
        db = get_verify_db()
        cand = db.candidates.find_one({"ticker": ticker})
        
        # Checks:
        # 1. No candidate evaluated (returns empty list)
        # 2. No candidate stored in DB
        success = (
            len(res) == 0 and
            cand is None
        )
        print_test_result("8-K Filing Unconfirmed (Move too small)", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_filing_8k_disqualifying():
    print("\n--- TEST: Material 8-K with Item 4.01 (Disqualified) ---")
    ticker = "T_8K_401"
    clean_db_for_ticker(ticker)
    try:
        ciks_mock = ["0000999997"]
        
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=[]), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=ciks_mock), \
             patch("src.discovery.get_ticker_from_cik", return_value=ticker), \
             patch("src.discovery.get_filings", return_value=MOCK_FILINGS_8K_401), \
             patch("src.discovery.get_price_volume", return_value=MOCK_PV_CONFIRMED):
             
            res = discover_candidates("run-8k-401")
            
        db = get_verify_db()
        cand = db.candidates.find_one({"ticker": ticker})
        
        success = (
            len(res) == 0 and
            cand is None
        )
        print_test_result("8-K Filing Disqualified (Contains Item 4.01)", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def test_same_day_duplicate():
    print("\n--- TEST: Same-Day Duplicate Prevention ---")
    ticker = "T_DUP"
    clean_db_for_ticker(ticker)
    try:
        calendar_mock = [{"symbol": ticker, "date": datetime.date.today().strftime("%Y-%m-%d")}]
        
        def mock_eval_gates(sym, run_id=None):
            db = get_verify_db()
            doc = db.candidates.find_one({"ticker": sym})
            doc["gate_result"] = "PASSED"
            db.candidates.update_one({"_id": doc["_id"]}, {"$set": {"gate_result": "PASSED"}})
            return doc
            
        with patch("src.discovery.get_finnhub_earnings_calendar", return_value=calendar_mock), \
             patch("src.discovery.get_earnings", return_value=MOCK_EARNINGS_NORMAL_BEAT), \
             patch("src.discovery.get_sec_recent_8k_ciks", return_value=[]), \
             patch("src.discovery.evaluate_gates", side_effect=mock_eval_gates):
             
            # Run first time (discovers and saves candidate)
            res1 = discover_candidates("run-dup-1")
            # Run second time (should be skipped due to same-day duplicate prevention)
            res2 = discover_candidates("run-dup-2")
            
        db = get_verify_db()
        count = db.candidates.count_documents({"ticker": ticker, "trigger_type": "EARNINGS_SURPRISE"})
        
        success = (
            len(res1) == 1 and
            len(res2) == 0 and
            count == 1
        )
        print_test_result("Same-Day Duplicate Prevention", success)
        return success
    finally:
        clean_db_for_ticker(ticker)

def run_all_tests():
    print("=== STARTING PHASE 2 DISCOVERY ENGINE VERIFICATION ===")
    results = [
        test_earnings_beat_normal(),
        test_earnings_near_zero_consensus(),
        test_filing_8k_confirmed(),
        test_filing_8k_unconfirmed(),
        test_filing_8k_disqualifying(),
        test_same_day_duplicate()
    ]
    
    success = all(results)
    print("\n=== PHASE 2 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
