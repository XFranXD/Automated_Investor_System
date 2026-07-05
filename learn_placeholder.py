import sys
from src.config import validate_config
from src.db import init_db
from src.logger import write_audit_log
from src.learning_aggregator import run_weekly_aggregation

def main():
    print("Starting Learn Cycle...")
    try:
        # Enforce config validation
        validate_config()
        
        # Initialize database and collections
        init_db()
        
        # Execute Weekly Learning Aggregation
        processed_count = run_weekly_aggregation()
        
        # Log the execution to the audit log
        write_audit_log(
            subsystem="learning_aggregator",
            action="learn_run",
            decision="PASSED",
            reasoning=f"Successfully completed weekly learning aggregation. Processed {processed_count} closed trades."
        )
        print("Learn Cycle completed successfully.")
    except Exception as e:
        print(f"Error in Learn Cycle: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
