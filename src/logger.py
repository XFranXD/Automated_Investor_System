import datetime
from src.db import get_db

def write_audit_log(subsystem, action, decision, reasoning, ticker=None, data_sources_consulted=None, reason_code=None, trading_cycle_run_id=None):
    """
    Appends a log entry to the 'audit_log' collection.
    
    Parameters:
    - subsystem (str): Name of the subsystem calling this (e.g. 'data_client', 'hardgate', 'execution').
    - action (str): What was attempted or performed.
    - decision (str): The outcome (e.g. 'PASSED', 'REJECTED', 'ABSTAIN', 'OPENED', 'CLOSED').
    - reasoning (str): Descriptive text explaining why the decision was reached.
    - ticker (str, optional): Ticker symbol if specific to a stock candidate.
    - data_sources_consulted (list of str, optional): List of sources used (e.g. ['EDGAR', 'Finnhub']).
    - reason_code (str, optional): A structured string code representing the reason (e.g. 'GATE_LIQUIDITY_ADV', '_NO_DATA').
    - trading_cycle_run_id (str, optional): ID of the current Trading Cycle execution run.
    """
    db = get_db()
    
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "subsystem": subsystem,
        "trading_cycle_run_id": trading_cycle_run_id,
        "ticker": ticker,
        "action": action,
        "decision": decision,
        "reasoning": reasoning,
        "data_sources_consulted": data_sources_consulted,
        "reason_code": reason_code
    }
    
    db.audit_log.insert_one(log_entry)
    
    # Print to console for runtime visibility
    ticker_str = f" for {ticker}" if ticker else ""
    code_str = f" [{reason_code}]" if reason_code else ""
    print(f"AUDIT LOG: [{subsystem}]{ticker_str} {action} -> {decision}{code_str}: {reasoning}")
