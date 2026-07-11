import os
import sys

# Auto-detect and re-execute within the project's virtual environment if not already inside it
venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "python"))
if os.path.exists(venv_python) and sys.executable != venv_python and not os.environ.get("VIRTUAL_ENV"):
    os.execv(venv_python, [venv_python] + sys.argv)

# Add the project root to sys.path so the script can find src.db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Ensure MONGODB_URI is set before doing anything else
if not os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_URI").strip() == "":
    print("CRITICAL ERROR: MONGODB_URI environment variable is not set.", file=sys.stderr)
    sys.exit(1)

# This is a READ-ONLY diagnostic script. No writes are performed anywhere below.
from src.db import get_db


def run_diagnosis():
    print("=== DIAGNOSING equity_at_entry ON OPEN TRADES ===")

    db = get_db()
    db_name = db.name
    print(f"Connected database name: {db_name}\n")

    if db_name == "tbe_test":
        print("WARNING: Connected to 'tbe_test', not production. Results may not reflect live trades.\n")

    open_trades = list(db.trades.find({"status": "OPEN"}))

    if not open_trades:
        print("No OPEN trades found in this database.")
        return

    print(f"Found {len(open_trades)} OPEN trade(s):\n")

    missing_count = 0
    for t in open_trades:
        ticker = t.get("ticker")
        equity_at_entry = t.get("equity_at_entry")
        entry_price = t.get("entry_price")
        entry_ts = t.get("entry_timestamp")
        share_count = t.get("share_count")

        status_flag = "OK" if (equity_at_entry is not None and equity_at_entry != 0) else "MISSING/INVALID"
        if status_flag != "OK":
            missing_count += 1

        print(f"  [{ticker}] entry_timestamp={entry_ts} | entry_price={entry_price} | shares={share_count}")
        print(f"          equity_at_entry={equity_at_entry!r}  -->  {status_flag}")
        print(f"          _id={t.get('_id')}")
        print()

    print("=== SUMMARY ===")
    print(f"Total OPEN trades checked: {len(open_trades)}")
    print(f"Trades with missing/invalid equity_at_entry: {missing_count}")

    if missing_count > 0:
        print(
            "\nThis confirms the dashboard's 'Open Unrealized P&L (Equity Impact)' bug: "
            "these trades cannot contribute a percentage figure, so the displayed total "
            "silently falls back to +0.00% instead of indicating missing data."
        )
    else:
        print(
            "\nAll open trades have a valid equity_at_entry. If the dashboard still shows "
            "+0.00%, the bug is elsewhere (e.g. in how trades_data is built or summed) "
            "and needs a different diagnostic."
        )


if __name__ == "__main__":
    run_diagnosis()