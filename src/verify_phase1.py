import sys
import datetime
from unittest.mock import patch, MagicMock
from src.db import get_db
from src.hard_gate import evaluate_gates

def print_test_result(name, success):
    status = "PASSED" if success else "FAILED"
    print(f"TEST [{name}]: {status}")

def clean_db_for_ticker(ticker):
    db = get_db()
    db.candidates.delete_many({"ticker": ticker})
    db.audit_log.delete_many({"ticker": ticker})

# --- MOCK DATA FOR GATES ---

MOCK_PRICE_VOLUME = {
    "source": "yfinance",
    "data": {
        "current_price": 150.0,
        "avg_daily_volume": 1000000.0,
        "avg_daily_dollar_volume": 150000000.0, # $150M
        "market_cap": 20000000000.0, # $20B
        "history": []
    }
}

MOCK_FILINGS = {
    "source": "SEC_EDGAR",
    "data": [
        {
            "form": "10-K",
            "filingDate": "2025-12-15",
            "accessionNumber": "0000123456-25-000100",
            "primaryDocument": "doc10k.htm",
            "fy": "2025"
        },
        {
            "form": "10-Q",
            "filingDate": "2026-03-15",
            "accessionNumber": "0000123456-26-000050",
            "primaryDocument": "doc10q.htm",
            "fy": "2026"
        }
    ]
}

# Healthy financials to pass Beneish & Altman Z-Score
# t = 2025 (current), t-1 = 2024 (prior)
MOCK_FUNDAMENTALS = {
    "source": "yfinance",
    "data": {
        "balance_sheet": {
            "2025-12-15": {
                "Total Assets": 10000.0,
                "Total Current Assets": 5000.0,
                "Total Current Liabilities": 2000.0,
                "Retained Earnings": 4000.0,
                "Total Liabilities": 3000.0,
                "Net PPE": 4000.0,
                "Accounts Receivable": 1000.0,
                "Cash Cash Equivalents And Short Term Investments": 1000.0
            },
            "2024-12-15": {
                "Total Assets": 9000.0,
                "Total Current Assets": 4500.0,
                "Total Current Liabilities": 1800.0,
                "Retained Earnings": 3500.0,
                "Total Liabilities": 2800.0,
                "Net PPE": 3800.0,
                "Accounts Receivable": 900.0,
                "Cash Cash Equivalents And Short Term Investments": 900.0
            }
        },
        "financials": {
            "2025-12-15": {
                "Total Revenue": 12000.0,
                "Cost Of Revenue": 6000.0,
                "Selling General And Administrative": 2000.0,
                "Depreciation And Amortization": 500.0,
                "Net Income": 2000.0,
                "EBIT": 2500.0,
                "Cash Flow From Operating Activities": 2200.0
            },
            "2024-12-15": {
                "Total Revenue": 10000.0,
                "Cost Of Revenue": 5000.0,
                "Selling General And Administrative": 1800.0,
                "Depreciation And Amortization": 400.0,
                "Net Income": 1500.0,
                "EBIT": 2000.0,
                "Cash Flow From Operating Activities": 1700.0
            }
        }
    }
}

# =====================================================================
# --- TEST SUITE CASES ---
# =====================================================================

def test_passed_candidate():
    print("\n--- TEST: Passed Candidate (All 6 Gates Pass) ---")
    ticker = "T_PASS"
    clean_db_for_ticker(ticker)
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value={"sanctioned_entity_xyz"}), \
         patch("src.hard_gate.get_company_name", return_value="Healthy Corporation"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value="Clean auditor report. No doubts."), \
         patch("src.hard_gate.get_fundamentals", return_value=MOCK_FUNDAMENTALS):
         
        res = evaluate_gates(ticker, "cycle-run-passed")
        
    db = get_db()
    # Check that candidate is stored as PASSED
    cand = db.candidates.find_one({"ticker": ticker})
    logs = list(db.audit_log.find({"ticker": ticker}))
    
    success = (
        res["gate_result"] == "PASSED" and
        cand is not None and
        cand["gate_result"] == "PASSED" and
        any("All six hard gates passed" in l["reasoning"] for l in logs)
    )
    print_test_result("Passed Candidate", success)
    return success

def test_liquidity_price_fail():
    print("\n--- TEST: Liquidity Price Floor Fail ---")
    ticker = "T_LQ_PRICE"
    clean_db_for_ticker(ticker)
    
    # Mock price to be $4.50 (below $5.00 floor)
    bad_price_vol = {
        "source": "yfinance",
        "data": {
            "current_price": 4.50,
            "avg_daily_dollar_volume": 150000000.0,
            "market_cap": 20000000000.0
        }
    }
    
    # Mock filings/10k to spy on calls to verify short-circuiting
    mock_get_filings = MagicMock(return_value=MOCK_FILINGS)
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Low Price Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=bad_price_vol), \
         patch("src.hard_gate.get_filings", mock_get_filings):
         
        res = evaluate_gates(ticker, "cycle-run-lq-price")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    # Checks:
    # 1. Candidate is REJECTED with GATE_LIQUIDITY_PRICE
    # 2. subsequent data client functions like get_filings were NOT called (short-circuiting verified)
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_LIQUIDITY_PRICE" and
        cand is not None and
        cand["gate_result"] == "REJECTED" and
        cand["gate_reason_code"] == "GATE_LIQUIDITY_PRICE" and
        not mock_get_filings.called
    )
    print_test_result("Liquidity Price Fail & Short-Circuit", success)
    return success

def test_liquidity_adv_fail():
    print("\n--- TEST: Liquidity ADV Fail ---")
    ticker = "T_LQ_ADV"
    clean_db_for_ticker(ticker)
    
    # Mock ADV to be $4.5M (below $5M floor)
    bad_price_vol = {
        "source": "yfinance",
        "data": {
            "current_price": 10.0,
            "avg_daily_dollar_volume": 4500000.0,
            "market_cap": 20000000000.0
        }
    }
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Low Volume Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=bad_price_vol):
         
        res = evaluate_gates(ticker, "cycle-run-lq-adv")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_LIQUIDITY_ADV" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_LIQUIDITY_ADV"
    )
    print_test_result("Liquidity ADV Fail", success)
    return success

def test_ofac_sanctions_fail():
    print("\n--- TEST: OFAC Sanctions Fail ---")
    ticker = "T_SANCTIONS"
    clean_db_for_ticker(ticker)
    
    # Mock OFAC SDN list to contain "gasprom"
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value={"gasprom", "rosneft"}), \
         patch("src.hard_gate.get_company_name", return_value="Gasprom PJSC"):
         
        res = evaluate_gates(ticker, "cycle-run-sanctions")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_SANCTIONS" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_SANCTIONS"
    )
    print_test_result("OFAC Sanctions Match Fail", success)
    return success

def test_delinquent_filing_fail():
    print("\n--- TEST: Delinquent Filing Fail ---")
    ticker = "T_DELINQUENT"
    clean_db_for_ticker(ticker)
    
    # Mock filings to show NT 10-K filed 10 days ago (delinquent) and no subsequent 10-K
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    late_filings = {
        "source": "SEC_EDGAR",
        "data": [
            {
                "form": "NT 10-K",
                "filingDate": today_str,
                "accessionNumber": "0000123456-26-000200",
                "primaryDocument": "nt10k.htm"
            }
        ]
    }
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Late Filing Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=late_filings):
         
        res = evaluate_gates(ticker, "cycle-run-delinquent")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_DELINQUENT_FILING" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_DELINQUENT_FILING"
    )
    print_test_result("Delinquent Filing Fail", success)
    return success

def test_auditor_change_fail():
    print("\n--- TEST: Auditor Change Fail ---")
    ticker = "T_AUDITOR_CHANGE"
    clean_db_for_ticker(ticker)
    
    # Mock filings to show 8-K with Item 4.01 filed 20 days ago (auditor change)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    auditor_filings = {
        "source": "SEC_EDGAR",
        "data": [
            {
                "form": "8-K",
                "items": "4.01,5.02",
                "filingDate": today_str,
                "accessionNumber": "0000123456-26-000210",
                "primaryDocument": "form8k.htm"
            }
        ]
    }
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Auditor Changer Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=auditor_filings):
         
        res = evaluate_gates(ticker, "cycle-run-auditor")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_AUDITOR_CHANGE" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_AUDITOR_CHANGE"
    )
    print_test_result("Auditor Change 8-K Fail", success)
    return success

def test_adverse_opinion_fail():
    print("\n--- TEST: Adverse Opinion Fail ---")
    ticker = "T_ADVERSE"
    clean_db_for_ticker(ticker)
    
    # Mock 10-K text to contain "substantial doubt" keyword
    bad_10k_text = "Management report: There is substantial doubt about our ability to continue as a going concern."
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Going Concern Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value=bad_10k_text):
         
        res = evaluate_gates(ticker, "cycle-run-adverse")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_ADVERSE_OPINION" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_ADVERSE_OPINION"
    )
    print_test_result("Adverse Opinion Keyword Match Fail", success)
    return success

def test_beneish_fail():
    print("\n--- TEST: Beneish M-Score Fail ---")
    ticker = "T_BENEISH_FAIL"
    clean_db_for_ticker(ticker)
    
    # Manufacture financials that skew Beneish:
    # Set Receivables in 2025 to be huge relative to 2024 sales/receivables
    # to force high DSRI -> M-Score > -1.78
    bad_fundamentals = {
        "source": "yfinance",
        "data": {
            "balance_sheet": {
                "2025-12-15": {
                    "Total Assets": 10000.0,
                    "Total Current Assets": 5000.0,
                    "Total Current Liabilities": 2000.0,
                    "Retained Earnings": 4000.0,
                    "Total Liabilities": 3000.0,
                    "Net PPE": 4000.0,
                    "Accounts Receivable": 9000.0, # Massive receivables
                    "Cash Cash Equivalents And Short Term Investments": 100.0
                },
                "2024-12-15": {
                    "Total Assets": 9000.0,
                    "Total Current Assets": 4500.0,
                    "Total Current Liabilities": 1800.0,
                    "Retained Earnings": 3500.0,
                    "Total Liabilities": 2800.0,
                    "Net PPE": 3800.0,
                    "Accounts Receivable": 100.0, # Tiny receivables
                    "Cash Cash Equivalents And Short Term Investments": 100.0
                }
            },
            "financials": {
                "2025-12-15": {
                    "Total Revenue": 10000.0,
                    "Cost Of Revenue": 5000.0,
                    "Selling General And Administrative": 2000.0,
                    "Depreciation And Amortization": 500.0,
                    "Net Income": 2000.0,
                    "EBIT": 2500.0,
                    "Cash Flow From Operating Activities": 2200.0
                },
                "2024-12-15": {
                    "Total Revenue": 10000.0,
                    "Cost Of Revenue": 5000.0,
                    "Selling General And Administrative": 1800.0,
                    "Depreciation And Amortization": 400.0,
                    "Net Income": 1500.0,
                    "EBIT": 2000.0,
                    "Cash Flow From Operating Activities": 1700.0
                }
            }
        }
    }
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Manipulator Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value="Clean auditor report"), \
         patch("src.hard_gate.get_fundamentals", return_value=bad_fundamentals):
         
        res = evaluate_gates(ticker, "cycle-run-beneish")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_BENEISH" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_BENEISH"
    )
    print_test_result("Beneish M-Score Threshold Fail", success)
    return success

def test_altman_fail():
    print("\n--- TEST: Altman Z-Score Fail ---")
    ticker = "T_ALTMAN_FAIL"
    clean_db_for_ticker(ticker)
    
    # Manufacture financials that skew Altman Z-Score:
    # Set high Liabilities, low Sales, negative EBIT, negative Working Capital (ca - cl)
    # to force Z-Score < 1.81
    bad_fundamentals = {
        "source": "yfinance",
        "data": {
            "balance_sheet": {
                "2025-12-15": {
                    "Total Assets": 10000.0,
                    "Total Current Assets": 100.0, # low
                    "Total Current Liabilities": 5000.0, # high
                    "Retained Earnings": -4000.0, # negative
                    "Total Liabilities": 9500.0, # very high
                    "Net PPE": 4000.0,
                    "Accounts Receivable": 100.0,
                    "Cash Cash Equivalents And Short Term Investments": 100.0
                },
                "2024-12-15": {
                    "Total Assets": 9000.0,
                    "Total Current Assets": 4500.0,
                    "Total Current Liabilities": 1800.0,
                    "Retained Earnings": 3500.0,
                    "Total Liabilities": 2800.0,
                    "Net PPE": 3800.0,
                    "Accounts Receivable": 900.0,
                    "Cash Cash Equivalents And Short Term Investments": 900.0
                }
            },
            "financials": {
                "2025-12-15": {
                    "Total Revenue": 100.0, # low sales
                    "Cost Of Revenue": 5000.0,
                    "Selling General And Administrative": 2000.0,
                    "Depreciation And Amortization": 500.0,
                    "Net Income": -6000.0,
                    "EBIT": -4000.0, # negative ebit
                    "Cash Flow From Operating Activities": -3000.0
                },
                "2024-12-15": {
                    "Total Revenue": 10000.0,
                    "Cost Of Revenue": 5000.0,
                    "Selling General And Administrative": 1800.0,
                    "Depreciation And Amortization": 400.0,
                    "Net Income": 1500.0,
                    "EBIT": 2000.0,
                    "Cash Flow From Operating Activities": 1700.0
                }
            }
        }
    }
    
    bad_price_vol = {
        "source": "yfinance",
        "data": {
            "current_price": 10.0,
            "avg_daily_volume": 1000000.0,
            "avg_daily_dollar_volume": 10000000.0,
            "market_cap": 5000.0, # low market cap
            "history": []
        }
    }
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Distressed Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=bad_price_vol), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value="Clean auditor report"), \
         patch("src.hard_gate.get_fundamentals", return_value=bad_fundamentals):
         
        res = evaluate_gates(ticker, "cycle-run-altman")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_ALTMAN" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_ALTMAN"
    )
    print_test_result("Altman Z-Score Distress Fail", success)
    return success

def test_no_data_handling():
    print("\n--- TEST: Missing Data Handling (_NO_DATA Codes) ---")
    ticker = "T_NODATA"
    clean_db_for_ticker(ticker)
    
    # Mock get_fundamentals to return None (Waterfall failure)
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="No Data Corp"), \
         patch("src.hard_gate.get_price_volume", return_value=MOCK_PRICE_VOLUME), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value="Clean auditor report"), \
         patch("src.hard_gate.get_fundamentals", return_value=None): # Fail waterfall
         
        res = evaluate_gates(ticker, "cycle-run-nodata")
        
    db = get_db()
    cand = db.candidates.find_one({"ticker": ticker})
    
    success = (
        res["gate_result"] == "REJECTED" and
        res["gate_reason_code"] == "GATE_BENEISH_NO_DATA" and
        cand is not None and
        cand["gate_reason_code"] == "GATE_BENEISH_NO_DATA"
    )
    print_test_result("Waterfall No-Data Fallback", success)
    return success

def test_same_day_caching():
    print("\n--- TEST: Same-Day Caching ---")
    ticker = "T_CACHE"
    clean_db_for_ticker(ticker)
    
    mock_get_price_volume = MagicMock(return_value=MOCK_PRICE_VOLUME)
    
    with patch("src.hard_gate.get_ofac_sdn_entities", return_value=set()), \
         patch("src.hard_gate.get_company_name", return_value="Cached Corp"), \
         patch("src.hard_gate.get_price_volume", mock_get_price_volume), \
         patch("src.hard_gate.get_filings", return_value=MOCK_FILINGS), \
         patch("src.hard_gate.get_sec_10k_text", return_value="Clean auditor report"), \
         patch("src.hard_gate.get_fundamentals", return_value=MOCK_FUNDAMENTALS):
         
        # Run first time (populates cache)
        res1 = evaluate_gates(ticker, "cycle-run-cache1")
        # Run second time (should hit cache and NOT call get_price_volume again)
        res2 = evaluate_gates(ticker, "cycle-run-cache2")
        
    db = get_db()
    # Check that candidates has exactly 1 document for this ticker
    # (since the second run returned the cached document and did not insert a new one)
    count = db.candidates.count_documents({"ticker": ticker})
    
    success = (
        res1["gate_result"] == "PASSED" and
        res2["gate_result"] == "PASSED" and
        mock_get_price_volume.call_count == 1 and
        count == 1
    )
    print_test_result("Same-Day Cache Hits", success)
    return success

# --- Real-world integration test (optional / informative, tries MSFT) ---
def test_real_ticker_msft():
    print("\n--- TEST: Real-world Ticker MSFT (E2E Integration Check) ---")
    ticker = "MSFT"
    clean_db_for_ticker(ticker)
    
    try:
        res = evaluate_gates(ticker, "cycle-run-msft-real")
        print(f"MSFT Gate Result: {res['gate_result']} | Reason: {res.get('gate_reason_code')}")
        success = res["gate_result"] in ["PASSED", "REJECTED"] # should evaluate cleanly either way
    except Exception as e:
        print(f"Exception during MSFT real test: {e}")
        success = False
        
    print_test_result("Real-world MSFT Integration", success)
    return success

def run_all_tests():
    print("=== STARTING PHASE 1 HARD-GATE ENGINE VERIFICATION ===")
    results = [
        test_passed_candidate(),
        test_liquidity_price_fail(),
        test_liquidity_adv_fail(),
        test_ofac_sanctions_fail(),
        test_delinquent_filing_fail(),
        test_auditor_change_fail(),
        test_adverse_opinion_fail(),
        test_beneish_fail(),
        test_altman_fail(),
        test_no_data_handling(),
        test_same_day_caching(),
        test_real_ticker_msft()
    ]
    
    success = all(results)
    print("\n=== PHASE 1 VERIFICATION COMPLETED ===")
    if success:
        print("ALL SCENARIOS COMPLETED SUCCESSFULLY.")
    else:
        print("SOME SCENARIOS FAILED. Check stdout for logs.")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
