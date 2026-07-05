import sys
import json
import datetime
from bson import ObjectId
from unittest.mock import patch, MagicMock
import requests
from src.db import get_db
from src.ai_reasoning import evaluate_qualitative_evidence
from src.gemini_client import call_gemini_api, QuotaExhaustedError

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_ticker(ticker):
    db = get_db()
    db.evaluations.delete_many({"ticker": ticker})
    db.audit_log.delete_many({"ticker": ticker})

# --- MOCK CANDIDATE DOCUMENTS ---

CAND_PASSED = {
    "_id": ObjectId("6a49b6110105d061e8ba7401"),
    "ticker": "T_AI_PASS",
    "trigger_type": "EARNINGS_SURPRISE",
    "direction": "LONG",
    "trigger_details": {"surprise_pct": 8.5},
    "gate_result": "PASSED",
    "trading_cycle_run_id": "run-ai-pass"
}

CAND_FAILED_GATE = {
    "_id": ObjectId("6a49b6110105d061e8ba7402"),
    "ticker": "T_AI_FAIL_GATE",
    "trigger_type": "EARNINGS_SURPRISE",
    "direction": "LONG",
    "trigger_details": {"surprise_pct": 2.5},
    "gate_result": "REJECTED",
    "trading_cycle_run_id": "run-ai-fail-gate"
}

# --- MOCK GEMINI RESPONSES ---

MOCK_SUCCESS_RESPONSE = json.dumps({
    "conviction": "STRONG_SUPPORT",
    "risk_flags": ["High competition"],
    "information_sufficiency": "SUFFICIENT",
    "rationale": "Company reported exceptionally strong earnings exceeding all market consensus expectations."
})

MOCK_LIMITED_RESPONSE = json.dumps({
    "conviction": "NEUTRAL",
    "risk_flags": ["No recent news available"],
    "information_sufficiency": "LIMITED",
    "rationale": "Evidence provided is extremely minimal with no press release or news."
})

MOCK_MALFORMED_RESPONSE = json.dumps({
    "bad_key": "some value",
    "conviction": "UNKNOWN" # violates enum
})

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_precondition_enforcement():
    print("\n--- TEST: Precondition Enforcement ---")
    ticker = CAND_FAILED_GATE["ticker"]
    clean_db_for_ticker(ticker)
    
    raised_error = False
    try:
        evaluate_qualitative_evidence(CAND_FAILED_GATE)
    except ValueError as e:
        print(f"Precondition check raised expected error: {e}")
        raised_error = True
        
    db = get_db()
    eval_doc = db.evaluations.find_one({"ticker": ticker})
    
    success = raised_error and eval_doc is None
    print_test_result("Precondition Enforcement", success)
    return success

def test_schema_valid_evaluation():
    print("\n--- TEST: Schema-Valid Output Generation ---")
    ticker = CAND_PASSED["ticker"]
    clean_db_for_ticker(ticker)
    
    with patch("src.ai_reasoning.get_primary_text_evidence", return_value="Earnings press release: Sales grew 20%"), \
         patch("src.ai_reasoning.get_company_news", return_value={"source": "Finnhub", "data": []}), \
         patch("src.ai_reasoning.call_gemini_api", return_value=MOCK_SUCCESS_RESPONSE):
         
        res = evaluate_qualitative_evidence(CAND_PASSED)
        
    db = get_db()
    eval_doc = db.evaluations.find_one({"ticker": ticker})
    logs = list(db.audit_log.find({"ticker": ticker}))
    
    success = (
        res is not None and
        res["conviction"] == "STRONG_SUPPORT" and
        res["information_sufficiency"] == "SUFFICIENT" and
        eval_doc is not None and
        eval_doc["conviction"] == "STRONG_SUPPORT" and
        any("STRONG_SUPPORT" in l["decision"] for l in logs)
    )
    print_test_result("Schema-Valid Output Generation", success)
    return success

def test_no_text_evidence_handling():
    print("\n--- TEST: No Text Evidence Handling ---")
    ticker = "T_AI_NO_TEXT"
    clean_db_for_ticker(ticker)
    
    cand = CAND_PASSED.copy()
    cand["ticker"] = ticker
    
    # Mocking filing/news text retrieval to return empty string
    with patch("src.ai_reasoning.get_primary_text_evidence", return_value=""), \
         patch("src.ai_reasoning.get_company_news", return_value=None), \
         patch("src.ai_reasoning.call_gemini_api", return_value=MOCK_LIMITED_RESPONSE) as mock_call:
         
        res = evaluate_qualitative_evidence(cand)
        
    success = (
        mock_call.called and
        res["conviction"] == "NEUTRAL" and
        res["information_sufficiency"] == "LIMITED"
    )
    print_test_result("No Text Evidence Handling", success)
    return success

def test_schema_failure_retry():
    print("\n--- TEST: Schema Failure Retry (Abstain) ---")
    ticker = "T_AI_SCHEMA_FAIL"
    clean_db_for_ticker(ticker)
    
    cand = CAND_PASSED.copy()
    cand["ticker"] = ticker
    
    # Call Gemini will return malformed output twice
    mock_call = MagicMock(return_value=MOCK_MALFORMED_RESPONSE)
    
    with patch("src.ai_reasoning.get_primary_text_evidence", return_value="some text"), \
         patch("src.ai_reasoning.get_company_news", return_value=None), \
         patch("src.ai_reasoning.call_gemini_api", mock_call):
         
        res = evaluate_qualitative_evidence(cand)
        
    db = get_db()
    eval_doc = db.evaluations.find_one({"ticker": ticker})
    
    # Verify:
    # 1. Exactly 2 attempts (initial + 1 retry) were made
    # 2. Evaluations document records ABSTAIN / AI_SCHEMA_VALIDATION_FAILED
    success = (
        mock_call.call_count == 2 and
        res["conviction"] == "ABSTAIN" and
        res["abstain_reason"] == "AI_SCHEMA_VALIDATION_FAILED" and
        eval_doc is not None and
        eval_doc["abstain_reason"] == "AI_SCHEMA_VALIDATION_FAILED"
    )
    print_test_result("Schema Failure Retry", success)
    return success

def test_api_key_rotation():
    print("\n--- TEST: API Key Rotation on Failure ---")
    
    # Clean system state first to make sure indices start clean
    db = get_db()
    db.system_state.delete_one({"_id": "gemini_key_state"})
    
    # Mock three API keys
    with patch("src.gemini_client.get_gemini_keys", return_value=["KEY1", "KEY2", "KEY3"]):
        # Stub the raw request post
        # First call on Key 1: raise HTTPError 429 (quota hit)
        # Second call on Key 2: return success response
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 429
        mock_response_1.json.return_value = {"error": {"message": "Resource has been exhausted (e.g. queries per minute quota)"}}
        
        err_429 = requests.exceptions.HTTPError(response=mock_response_1)
        
        mock_post = MagicMock(side_effect=[err_429, MagicMock(json=lambda: {"candidates": [{"content": {"parts": [{"text": MOCK_SUCCESS_RESPONSE}]}}]})])
        
        with patch("requests.post", mock_post):
            res_text = call_gemini_api("Test prompt", schema={})
            
        state = db.system_state.find_one({"_id": "gemini_key_state"})
        
        # Verify:
        # 1. Key 1 was rotated (index incremented to 1)
        # 2. Request was retried on Key 2 and succeeded
        success = (
            res_text == MOCK_SUCCESS_RESPONSE and
            state["current_key_idx"] == 1 and
            0 in state["exhausted_keys"]
        )
        print_test_result("API Key Rotation", success)
        return success

def test_quota_exhausted_abstain():
    print("\n--- TEST: Quota Exhausted (Abstain) ---")
    ticker = "T_AI_QUOTA"
    clean_db_for_ticker(ticker)
    
    cand = CAND_PASSED.copy()
    cand["ticker"] = ticker
    
    db = get_db()
    db.system_state.delete_one({"_id": "gemini_key_state"})
    
    # Mock three keys and force all to fail with QuotaExhaustedError
    with patch("src.gemini_client.get_gemini_keys", return_value=["KEY1", "KEY2", "KEY3"]):
        # Mock requests.post to return 429 for all calls
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        err_429 = requests.exceptions.HTTPError(response=mock_resp)
        
        with patch("requests.post", side_effect=err_429), \
             patch("src.ai_reasoning.get_primary_text_evidence", return_value="some text"), \
             patch("src.ai_reasoning.get_company_news", return_value=None):
             
            res = evaluate_qualitative_evidence(cand)
            
        eval_doc = db.evaluations.find_one({"ticker": ticker})
        
        success = (
            res["conviction"] == "ABSTAIN" and
            res["abstain_reason"] == "AI_QUOTA_EXHAUSTED" and
            eval_doc is not None and
            eval_doc["abstain_reason"] == "AI_QUOTA_EXHAUSTED"
        )
        print_test_result("Quota Exhausted Abstain", success)
        return success

def run_all_tests():
    print("=== STARTING PHASE 3 AI REASONING LAYER VERIFICATION ===")
    results = [
        test_precondition_enforcement(),
        test_schema_valid_evaluation(),
        test_no_text_evidence_handling(),
        test_schema_failure_retry(),
        test_api_key_rotation(),
        test_quota_exhausted_abstain()
    ]
    
    success = all(results)
    print("\n=== PHASE 3 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
