import sys
import datetime
from unittest.mock import patch
from src.db import init_db, get_db, COLLECTIONS
from src.trading_harness import open_paper_position, close_paper_position
from src.data_client import get_earnings

def run_tests():
    print("=== STARTING FOUNDATION VERIFICATION ===")
    
    # 1. DB Init & Collections Check
    print("\n1. Verifying Database Initialization...")
    try:
        init_db()
    except Exception as e:
        print(f"FAILED: Database initialization failed: {e}", file=sys.stderr)
        return False
        
    db = get_db()
    existing_collections = db.list_collection_names()
    for col in COLLECTIONS:
        if col not in existing_collections:
            print(f"FAILED: Required collection '{col}' is missing in database.", file=sys.stderr)
            return False
    print("SUCCESS: Database initialization check passed.")
    
    # 2. Write & Read Dummy Documents for All Collections
    print("\n2. Verifying Write & Read for all collections...")
    try:
        test_id = str(datetime.datetime.utcnow().timestamp())
        for col in COLLECTIONS:
            collection = db[col]
            dummy_doc = {"_verify_test_id": test_id, "test_field": "hello"}
            res = collection.insert_one(dummy_doc)
            inserted_id = res.inserted_id
            
            # Read back
            found = collection.find_one({"_id": inserted_id})
            if not found or found["test_field"] != "hello":
                print(f"FAILED: Write/read validation failed for collection '{col}'", file=sys.stderr)
                return False
                
            # Clean up dummy document
            collection.delete_one({"_id": inserted_id})
            print(f"SUCCESS: Write/read/delete verified for collection '{col}'.")
    except Exception as e:
        print(f"FAILED: Exception during write/read verification: {e}", file=sys.stderr)
        return False
        
    # 3. Verify Paper Trading Harness (PnL & Open/Close workflow)
    print("\n3. Verifying Paper Trading Harness (Long and Short)...")
    try:
        # A. Long Trade Test
        print("Testing LONG trade...")
        long_id = open_paper_position(
            ticker="AAPL",
            direction="LONG",
            share_count=100,
            entry_price=150.0,
            initial_stop=140.0,
            take_profit=170.0,
            combined_score=1.5,
            risk_pct_used=1.5,
            confidence_tier="STRONG",
            reasoning_chain={"test": True}
        )
        
        # Verify it is in DB
        trade = db.trades.find_one({"_id": long_id})
        if not trade or trade["status"] != "OPEN" or trade["direction"] != "LONG":
            print("FAILED: Opened LONG trade not found or has incorrect data in DB.", file=sys.stderr)
            return False
            
        # Close LONG trade at 160.0 (Expected Profit: (160 - 150) * 100 = 1000)
        closed_long = close_paper_position(long_id, exit_price=160.0, exit_reason="TAKE_PROFIT")
        if closed_long["status"] != "CLOSED" or closed_long["realized_pnl"] != 1000.0:
            print(f"FAILED: Closed LONG trade P&L calculation is incorrect: {closed_long.get('realized_pnl')}", file=sys.stderr)
            return False
        print("SUCCESS: LONG trade open/close P&L calculation passed.")
        
        # B. Short Trade Test
        print("Testing SHORT trade...")
        short_id = open_paper_position(
            ticker="TSLA",
            direction="SHORT",
            share_count=50,
            entry_price=200.0,
            initial_stop=210.0,
            take_profit=180.0,
            combined_score=1.0,
            risk_pct_used=0.75,
            confidence_tier="MODERATE",
            reasoning_chain={"test": True}
        )
        
        # Verify it is in DB
        trade = db.trades.find_one({"_id": short_id})
        if not trade or trade["status"] != "OPEN" or trade["direction"] != "SHORT":
            print("FAILED: Opened SHORT trade not found or has incorrect data in DB.", file=sys.stderr)
            return False
            
        # Close SHORT trade at 215.0 (Expected Loss: (200 - 215) * 50 = -750)
        closed_short = close_paper_position(short_id, exit_price=215.0, exit_reason="STOP")
        if closed_short["status"] != "CLOSED" or closed_short["realized_pnl"] != -750.0:
            print(f"FAILED: Closed SHORT trade P&L calculation is incorrect: {closed_short.get('realized_pnl')}", file=sys.stderr)
            return False
        print("SUCCESS: SHORT trade open/close P&L calculation passed.")
        
        # Check audit log entries for trades
        log_open = db.audit_log.find_one({"action": "open_position", "ticker": "AAPL"})
        log_close = db.audit_log.find_one({"action": "close_position", "ticker": "TSLA"})
        if not log_open or not log_close:
            print("FAILED: Audit logs for open/close positions were not written correctly.", file=sys.stderr)
            return False
        print("SUCCESS: Audit logs check for trades passed.")
        
    except Exception as e:
        print(f"FAILED: Exception during paper-trading harness verification: {e}", file=sys.stderr)
        return False
        
    # 4. Mocked Fallback Fetch Waterfall Test
    print("\n4. Verifying Waterfall Fallback Mechanics...")
    try:
        # Count audit logs for data_client and ticker MSFT before the run
        pre_count = db.audit_log.count_documents({"subsystem": "data_client", "ticker": "MSFT"})
        
        # Mock Finnhub earnings to fail, forcing it to fall back to yfinance
        with patch('src.data_client.get_finnhub_earnings', side_effect=Exception("Finnhub simulated failure")):
            res = get_earnings("MSFT")
            
        if not res:
            print("FAILED: Waterfall get_earnings returned None, expected fallback to yfinance to succeed.", file=sys.stderr)
            return False
            
        if res["source"] != "yfinance":
            print(f"FAILED: Waterfall resolved from source '{res['source']}', expected 'yfinance' fallback.", file=sys.stderr)
            return False
            
        # Retrieve logs created during the fallback attempt
        logs = list(db.audit_log.find({"subsystem": "data_client", "ticker": "MSFT"}).sort("timestamp", 1))
        new_logs = logs[pre_count:]
        
        # Verify that we logged a FAILED attempt (for the primary source failure)
        # and a SUCCESS check (for the fallback source success)
        has_failed = any(l["decision"] == "FAILED" for l in new_logs)
        has_success = any(l["decision"] == "SUCCESS" for l in new_logs)
        
        if not has_failed or not has_success:
            print("FAILED: Waterfall fallback attempts were not logged correctly in audit_log.", file=sys.stderr)
            for l in new_logs:
                print(f"  Logged Action: {l['action']} | Decision: {l['decision']} | Reasoning: {l['reasoning']}", file=sys.stderr)
            return False
            
        print("SUCCESS: Waterfall fallback mechanics verified.")
        
    except Exception as e:
        print(f"FAILED: Exception during waterfall verification: {e}", file=sys.stderr)
        return False
        
    print("\n=== ALL VERIFICATIONS PASSED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
