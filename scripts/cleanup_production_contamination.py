import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Ensure MONGODB_URI is set before doing anything else
if not os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_URI").strip() == "":
    print("CRITICAL ERROR: MONGODB_URI environment variable is not set.", file=sys.stderr)
    sys.exit(1)

# Import src.db to get the production database connection
# Note that we do NOT import get_verify_db or patch get_db because this script
# is specifically designed to clean up the production database.
from src.db import get_db

def run_cleanup():
    print("=== STARTING PRODUCTION DATABASE CLEANUP ===")
    
    db = get_db()
    prod_db_name = db.name
    print(f"Connected database name: {prod_db_name}")
    
    # Safety Check: Do NOT clean up if the database name is "tbe_test"
    if prod_db_name == "tbe_test":
        print("CRITICAL ERROR: Connected database is 'tbe_test'. This script is only for cleaning up production.", file=sys.stderr)
        sys.exit(1)
        
    # 1. Audit/clean trade contamination
    target_tickers = ["T_DASH_1", "T_DASH_2", "T_DASH_3"]
    print(f"Checking trade documents for tickers: {target_tickers}")
    
    trades_col = db.trades
    initial_count = trades_col.count_documents({"ticker": {"$in": target_tickers}})
    print(f"Found {initial_count} matching contaminated trades before cleanup.")
    
    if initial_count > 0:
        delete_trades_result = trades_col.delete_many({"ticker": {"$in": target_tickers}})
        print(f"Deleted {delete_trades_result.deleted_count} trade documents.")
    else:
        print("No contaminated trade documents found.")
        
    final_trade_count = trades_col.count_documents({"ticker": {"$in": target_tickers}})
    print(f"Contaminated trades remaining: {final_trade_count}")
    
    # 2. Audit/clean corrupted portfolio state
    portfolio_col = db.portfolio_state
    print("Deleting current_state document to allow clean regeneration.")
    delete_portfolio_result = portfolio_col.delete_one({"_id": "current_state"})
    print(f"Deleted {delete_portfolio_result.deleted_count} portfolio state document(s).")
        
    final_portfolio_doc = portfolio_col.find_one({"_id": "current_state"})
    if final_portfolio_doc:
        print("Portfolio state current_state document exists (is clean).")
    else:
        print("Portfolio state current_state document does not exist (will be regenerated with clean default values).")
        
    print("=== PRODUCTION DATABASE CLEANUP COMPLETED ===")

if __name__ == "__main__":
    try:
        run_cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR during cleanup execution: {e}", file=sys.stderr)
        sys.exit(1)
