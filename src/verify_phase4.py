import sys
import datetime
from bson import ObjectId
from src.db import get_verify_db
import src.db
src.db.get_db = get_verify_db

from src.scoring import score_candidate

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_candidate(cand_id):
    db = get_verify_db()
    db.candidates.delete_many({"_id": cand_id})
    db.audit_log.delete_many({"trading_cycle_run_id": "run-scoring-test"})

# --- MOCK CONTEXTS ---

REGIME_ON = {"vix": 15.0, "spy_close": 510.0, "spy_sma_50": 500.0, "regime": "RISK_ON"}
REGIME_OFF = {"vix": 35.0, "spy_close": 510.0, "spy_sma_50": 500.0, "regime": "RISK_OFF"}

# =====================================================================
# --- TEST CASES ---
# =====================================================================

def test_strong_trigger_strong_support_riskon():
    print("\n--- TEST: Strong Trigger + Strong Support, RISK_ON ---")
    db = get_verify_db()
    cand_id = ObjectId("6a49b6110105d061e8ba7501")
    clean_db_for_candidate(cand_id)
    try:
        cand = {
            "_id": cand_id,
            "ticker": "T_SC_1",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 12.0}, # Strong trigger (+2)
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand)
        
        evaluation = {
            "candidate_id": cand_id,
            "ticker": "T_SC_1",
            "conviction": "STRONG_SUPPORT", # +2
            "information_sufficiency": "SUFFICIENT"
        }
        
        res = score_candidate(cand, evaluation, REGIME_ON)
        
        # Combined score = (2.0 + 2.0) / 2.0 = 2.0
        # Outcomes: PROCEED, Strong, combined_score = 2.0
        success = (
            res["trigger_strength_score"] == 2.0 and
            res["ai_conviction_score"] == 2.0 and
            res["combined_score"] == 2.0 and
            res["final_outcome"] == "PROCEED" and
            res["confidence_tier"] == "STRONG" and
            res["regime_state_at_decision"] == "RISK_ON"
        )
        print_test_result("Strong Trigger + Strong Support, RISK_ON", success)
        return success
    finally:
        clean_db_for_candidate(cand_id)

def test_strong_trigger_moderate_contradiction():
    print("\n--- TEST: Strong Trigger + Moderate Contradiction ---")
    db = get_verify_db()
    cand_id = ObjectId("6a49b6110105d061e8ba7502")
    clean_db_for_candidate(cand_id)
    try:
        cand = {
            "_id": cand_id,
            "ticker": "T_SC_2",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 15.0}, # Strong trigger (+2)
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand)
        
        evaluation = {
            "candidate_id": cand_id,
            "ticker": "T_SC_2",
            "conviction": "MODERATE_CONTRADICTION", # -1
            "information_sufficiency": "SUFFICIENT"
        }
        
        res = score_candidate(cand, evaluation, REGIME_ON)
        
        # Combined score = (2.0 + -1.0) / 2.0 = 0.5
        # Outcomes: PROCEED, Moderate, combined_score = 0.5 (not blocked)
        success = (
            res["trigger_strength_score"] == 2.0 and
            res["ai_conviction_score"] == -1.0 and
            res["combined_score"] == 0.5 and
            res["final_outcome"] == "PROCEED" and
            res["confidence_tier"] == "MODERATE"
        )
        print_test_result("Strong Trigger + Moderate Contradiction", success)
        return success
    finally:
        clean_db_for_candidate(cand_id)

def test_moderate_trigger_strong_contradiction():
    print("\n--- TEST: Moderate Trigger + Strong Contradiction ---")
    db = get_verify_db()
    cand_id = ObjectId("6a49b6110105d061e8ba7503")
    clean_db_for_candidate(cand_id)
    try:
        cand = {
            "_id": cand_id,
            "ticker": "T_SC_3",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 6.0}, # Moderate trigger (+1)
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand)
        
        evaluation = {
            "candidate_id": cand_id,
            "ticker": "T_SC_3",
            "conviction": "STRONG_CONTRADICTION", # -2
            "information_sufficiency": "SUFFICIENT"
        }
        
        res = score_candidate(cand, evaluation, REGIME_ON)
        
        # Combined score = (1.0 + -2.0) / 2.0 = -0.5
        # Outcomes: ABSTAIN, ABSTAIN_NEUTRAL_OR_CONFLICTING, combined_score = -0.5
        success = (
            res["trigger_strength_score"] == 1.0 and
            res["ai_conviction_score"] == -2.0 and
            res["combined_score"] == -0.5 and
            res["final_outcome"] == "ABSTAIN" and
            res["abstain_reason_code"] == "ABSTAIN_NEUTRAL_OR_CONFLICTING"
        )
        print_test_result("Moderate Trigger + Strong Contradiction", success)
        return success
    finally:
        clean_db_for_candidate(cand_id)

def test_limited_info_modifier():
    print("\n--- TEST: Info Sufficiency LIMITED Modifier ---")
    db = get_verify_db()
    cand_id = ObjectId("6a49b6110105d061e8ba7504")
    clean_db_for_candidate(cand_id)
    try:
        # Strong trigger (+2) + Strong support (+2) -> Base combined score = 2.0
        # Limited info -> Subtracts 0.5 -> Final combined score = 1.5 -> MODERATE lookup?
        # Wait: 1.5 in bucket lookup is:
        # ">= 1.5 -> STRONG conviction -> proceed"
        # Wait, what if we use Strong (+2) + Moderate Support (+1)?
        # Base combined score = (2 + 1)/2 = 1.5.
        # Limited info -> Subtracts 0.5 -> Final combined score = 1.0.
        # 1.0 lands in 0.5 to < 1.5 -> MODERATE conviction (originally was 1.5 -> STRONG).
        # This verifies the penalty before lookup!
        cand = {
            "_id": cand_id,
            "ticker": "T_SC_4",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 12.0}, # Strong trigger (+2)
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand)
        
        evaluation = {
            "candidate_id": cand_id,
            "ticker": "T_SC_4",
            "conviction": "MODERATE_SUPPORT", # +1
            "information_sufficiency": "LIMITED"
        }
        
        res = score_candidate(cand, evaluation, REGIME_ON)
        
        success = (
            res["combined_score"] == 1.0 and # (2.0 + 1.0)/2 - 0.5
            res["final_outcome"] == "PROCEED" and
            res["confidence_tier"] == "MODERATE" and # Originally was STRONG (1.5)
            res["information_sufficiency_modifier"] == -0.5
        )
        print_test_result("Limited Info Sufficiency Modifier", success)
        return success
    finally:
        clean_db_for_candidate(cand_id)

def test_regime_modulation_moderate():
    print("\n--- TEST: Regime Modulation Moderate in RISK_OFF ---")
    db = get_verify_db()
    
    cand_id_1 = ObjectId("6a49b6110105d061e8ba7505")
    cand_id_2 = ObjectId("6a49b6110105d061e8ba7506")
    clean_db_for_candidate(cand_id_1)
    clean_db_for_candidate(cand_id_2)
    try:
        # Moderate candidate setup: Strong trigger (+2) + Neutral support (0) -> combined score = 1.0 (MODERATE)
        # 1. Verify in RISK_OFF it is ABSTAINED with ABSTAIN_RISK_OFF_REGIME
        cand_1 = {
            "_id": cand_id_1,
            "ticker": "T_SC_5A",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 12.0},
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand_1)
        evaluation_1 = {
            "candidate_id": cand_id_1,
            "ticker": "T_SC_5A",
            "conviction": "NEUTRAL",
            "information_sufficiency": "SUFFICIENT"
        }
        res_1 = score_candidate(cand_1, evaluation_1, REGIME_OFF)
        
        # 2. Verify in RISK_ON it PROCEEDS as MODERATE
        cand_2 = {
            "_id": cand_id_2,
            "ticker": "T_SC_5B",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 12.0},
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand_2)
        evaluation_2 = {
            "candidate_id": cand_id_2,
            "ticker": "T_SC_5B",
            "conviction": "NEUTRAL",
            "information_sufficiency": "SUFFICIENT"
        }
        res_2 = score_candidate(cand_2, evaluation_2, REGIME_ON)
        
        success = (
            res_1["final_outcome"] == "ABSTAIN" and
            res_1["abstain_reason_code"] == "ABSTAIN_RISK_OFF_REGIME" and
            res_2["final_outcome"] == "PROCEED" and
            res_2["confidence_tier"] == "MODERATE"
        )
        print_test_result("Regime Modulation (RISK_OFF blocks MODERATE)", success)
        return success
    finally:
        clean_db_for_candidate(cand_id_1)
        clean_db_for_candidate(cand_id_2)

def test_upstream_ai_failure():
    print("\n--- TEST: Upstream AI Failure ---")
    db = get_verify_db()
    cand_id = ObjectId("6a49b6110105d061e8ba7507")
    clean_db_for_candidate(cand_id)
    try:
        cand = {
            "_id": cand_id,
            "ticker": "T_SC_6",
            "trigger_type": "EARNINGS_SURPRISE",
            "trigger_details": {"surprise_pct": 12.0},
            "gate_result": "PASSED",
            "trading_cycle_run_id": "run-scoring-test",
            "calendar_day": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.candidates.insert_one(cand)
        
        # AI reasoned abstained
        evaluation = {
            "candidate_id": cand_id,
            "ticker": "T_SC_6",
            "conviction": "ABSTAIN",
            "abstain_reason": "AI_QUOTA_EXHAUSTED"
        }
        
        res = score_candidate(cand, evaluation, REGIME_ON)
        
        success = (
            res["final_outcome"] == "ABSTAIN" and
            res["abstain_reason_code"] == "ABSTAIN_UPSTREAM_AI_FAILURE"
        )
        print_test_result("Upstream AI Failure Abstaining", success)
        return success
    finally:
        clean_db_for_candidate(cand_id)

def run_all_tests():
    print("=== STARTING PHASE 4 SCORING & REGIME FILTER VERIFICATION ===")
    results = [
        test_strong_trigger_strong_support_riskon(),
        test_strong_trigger_moderate_contradiction(),
        test_moderate_trigger_strong_contradiction(),
        test_limited_info_modifier(),
        test_regime_modulation_moderate(),
        test_upstream_ai_failure()
    ]
    
    success = all(results)
    print("\n=== PHASE 4 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
