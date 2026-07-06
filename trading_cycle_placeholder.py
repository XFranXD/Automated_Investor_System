import sys
import datetime
from src.config import validate_config
from src.db import init_db, get_db
from src.logger import write_audit_log
from src.portfolio_monitor import monitor_portfolio
from src.discovery import discover_candidates
from src.ai_reasoning import evaluate_qualitative_evidence
from src.scoring import score_candidate, get_regime_state
from src.execution import execute_trade

def main():
    print("Starting Trading Cycle...")
    try:
        # 1. Enforce config validation
        validate_config()
        
        # 2. Initialize database and collections
        init_db()
        db = get_db()
        
        # Generate unique trading cycle run ID
        run_id = "run-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        print(f"Trading Cycle Run ID: {run_id}")
        
        # 3. Step 1: Run Portfolio Monitor
        # Protecting what is already at risk always comes first.
        print("Step 1: Running Portfolio Monitor...")
        portfolio_state = monitor_portfolio(run_id)
        
        # Check if global drawdown kill switch has been activated
        if portfolio_state.get("kill_switch_active", False):
            print("Portfolio Kill Switch is ACTIVE. Halted new entries for this cycle.")
            write_audit_log(
                subsystem="orchestrator",
                action="trading_cycle_run",
                decision="BLOCKED",
                reasoning="Trading cycle execution blocked: Kill switch is currently active.",
                trading_cycle_run_id=run_id
            )
            return

        # Fetch current regime state (VIX + SPY relative trend)
        regime_state = get_regime_state()
        
        # 4. Step 2: Discover Candidates and run Hard-Gate checks
        print("Step 2: Running Candidate Discovery...")
        discover_candidates(run_id)
        
        # Find candidates from this run that successfully passed hard gates
        passed_candidates = list(db.candidates.find({
            "trading_cycle_run_id": run_id,
            "gate_result": "PASSED"
        }))
        print(f"Discovered {len(passed_candidates)} passed candidates.")
        
        # 5. Step 3: Run AI qualitative reasoning & Scoring on passed candidates
        for cand in passed_candidates:
            # Re-fetch portfolio_state from DB so that any positions opened earlier in this cycle are seen
            portfolio_state = db.portfolio_state.find_one({"_id": "current_state"})
            if not portfolio_state:
                portfolio_state = {
                    "equity": 100000.0,
                    "cash": 100000.0,
                    "kill_switch_active": False,
                    "correlation_cap_current": 0.6,
                    "open_positions": []
                }
                
            ticker = cand.get("ticker")
            print(f"Processing candidate: {ticker}")
            
            # A. Qualitative AI reasoning
            eval_doc = evaluate_qualitative_evidence(cand)
            
            # B. Decision scoring & regime modulation
            scored_cand = score_candidate(cand, eval_doc, regime_state)
            
            # C. Sizing and execution for proceed outcomes
            if scored_cand.get("final_outcome") == "PROCEED":
                print(f"Candidate {ticker} approved. Opening paper position...")
                execute_trade(scored_cand, portfolio_state, regime_state)
            else:
                print(f"Candidate {ticker} abstained from execution (Outcome: {scored_cand.get('final_outcome')}).")
                
        # Log successful completion of full trading cycle
        write_audit_log(
            subsystem="orchestrator",
            action="trading_cycle_run",
            decision="PASSED",
            reasoning=f"Successfully completed Trading Cycle orchestration. Run ID: {run_id}",
            trading_cycle_run_id=run_id
        )
        print("Trading Cycle completed successfully.")
    except Exception as e:
        print(f"Error in Trading Cycle: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
