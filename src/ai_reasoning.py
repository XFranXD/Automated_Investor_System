import json
import datetime
from src.db import get_db
from src.logger import write_audit_log
from src.data_client import (
    get_cik,
    get_filings,
    get_sec_document_text,
    get_company_news,
    clean_html
)
from src.gemini_client import call_gemini_api, QuotaExhaustedError, AIUnavailableError

# Structured output schema for Google Gemini
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "conviction": {
            "type": "STRING",
            "enum": ["STRONG_SUPPORT", "MODERATE_SUPPORT", "NEUTRAL", "MODERATE_CONTRADICTION", "STRONG_CONTRADICTION"]
        },
        "risk_flags": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            }
        },
        "information_sufficiency": {
            "type": "STRING",
            "enum": ["SUFFICIENT", "LIMITED", "INSUFFICIENT"]
        },
        "rationale": {
            "type": "STRING"
        }
      },
      "required": ["conviction", "risk_flags", "information_sufficiency", "rationale"]
}

def validate_response_schema(data):
    """Checks if the returned dictionary complies exactly with the structured schema rules."""
    if not isinstance(data, dict):
        return False
        
    for req in ["conviction", "risk_flags", "information_sufficiency", "rationale"]:
        if req not in data:
            return False
            
    if data["conviction"] not in ["STRONG_SUPPORT", "MODERATE_SUPPORT", "NEUTRAL", "MODERATE_CONTRADICTION", "STRONG_CONTRADICTION"]:
        return False
        
    if data["information_sufficiency"] not in ["SUFFICIENT", "LIMITED", "INSUFFICIENT"]:
        return False
        
    if not isinstance(data["risk_flags"], list) or not all(isinstance(f, str) for f in data["risk_flags"]):
        return False
        
    if not isinstance(data["rationale"], str):
        return False
        
    return True

def get_primary_text_evidence(ticker, trigger_type, filings, cik):
    """Retrieves and cleans primary text evidence from SEC EDGAR filings based on the trigger type."""
    if not filings or not cik:
        return ""
        
    # 1. Earnings Surprise (PEAD): Search for recent 8-K with Item 2.02 (earnings releases)
    if trigger_type == "EARNINGS_SURPRISE":
        for f in filings:
            if f.get("form") == "8-K":
                items = str(f.get("items", ""))
                if "2.02" in items:
                    acc_num = f.get("accessionNumber")
                    primary_doc = f.get("primaryDocument")
                    if acc_num and primary_doc:
                        try:
                            html_text = get_sec_document_text(cik, acc_num, primary_doc)
                            return clean_html(html_text)
                        except Exception as e:
                            print(f"Error fetching 8-K Item 2.02 text: {e}")
                            
    # 2. Material Filing (8-K): Find the 8-K matching the date/items from candidate details
    elif trigger_type == "MATERIAL_FILING":
        # Check filing from date in the last few days
        for f in filings:
            if f.get("form") == "8-K":
                acc_num = f.get("accessionNumber")
                primary_doc = f.get("primaryDocument")
                if acc_num and primary_doc:
                    try:
                        html_text = get_sec_document_text(cik, acc_num, primary_doc)
                        return clean_html(html_text)
                    except Exception as e:
                        print(f"Error fetching qualifying 8-K text: {e}")
                        
    return ""

def evaluate_qualitative_evidence(candidate_doc):
    """
    Evaluates qualitative text evidence for a candidate ticker that has successfully PASSED the Hard-Gate Engine.
    
    Refuses execution at the function boundary if candidate_doc.gate_result != 'PASSED'.
    Returns:
    - dict: The generated evaluations document stored in MongoDB.
    """
    ticker = candidate_doc.get("ticker", "").upper().strip()
    gate_result = candidate_doc.get("gate_result")
    trading_cycle_run_id = candidate_doc.get("trading_cycle_run_id")
    
    # 1. Precondition Enforcement
    if gate_result != "PASSED":
        raise ValueError(
            f"Precondition failure: candidate {ticker} has gate_result = '{gate_result}', expected 'PASSED'."
        )
        
    print(f"[{ticker}] Running Qualitative AI Reasoning...")
    db = get_db()
    
    # Assembly contexts
    cik = get_cik(ticker)
    filings_res = get_filings(ticker)
    filings = filings_res["data"] if filings_res else []
    
    filing_text = get_primary_text_evidence(ticker, candidate_doc.get("trigger_type"), filings, cik)
    
    news_res = get_company_news(ticker)
    news_text = ""
    if news_res and news_res.get("data"):
        news_list = news_res["data"]
        news_text = "\n".join([
            f"Source: {n.get('source')} | Title: {n.get('headline')} | Summary: {n.get('summary')}"
            for n in news_list
        ])
        
    # Construct prompt
    prompt = f"""You are Antigravity, a professional qualitative assessment analyst for the Autonomous Investment System.
Your task is to qualitatively analyze the provided text evidence for candidate ticker: {ticker}.

PRE-SET STRATEGY SUMMARY:
- Trigger type: {candidate_doc.get('trigger_type')}
- Target direction: {candidate_doc.get('direction')}
- Trigger details: {candidate_doc.get('trigger_details')}

TEXT EVIDENCE AVAILABLE:
--- START FILING TEXT EVIDENCE ---
{filing_text if filing_text else "[NO FILING EVIDENCE AVAILABLE]"}
--- END FILING TEXT EVIDENCE ---

--- START NEWS EVIDENCE ---
{news_text if news_text else "[NO NEWS EVIDENCE AVAILABLE]"}
--- END NEWS EVIDENCE ---

INSTRUCTIONS:
1. Your role is STRICTLY limited to assessing whether the text evidence qualitatively supports or contradicts the target direction ({candidate_doc.get('direction')}) for {ticker}.
2. Do NOT suggest a direction different from the one already given.
3. Do NOT assume access to current price data or technical indicators.
4. Do NOT invent facts. If the evidence provided is minimal, note this in the output.
5. If the evidence is minimal, you must set "information_sufficiency" to "LIMITED" or "INSUFFICIENT".
6. Analyze risk factors present in the text and list them in the "risk_flags" array.
7. Provide a concise, 1-3 sentence rationale explaining your assessment in plain language.

Response must be formatted exactly as JSON matching the schema.
"""
    
    eval_doc = {
        "candidate_id": candidate_doc["_id"],
        "ticker": ticker,
        "evaluation_timestamp": datetime.datetime.utcnow(),
        "trading_cycle_run_id": trading_cycle_run_id,
        "conviction": "ABSTAIN",
        "risk_flags": [],
        "information_sufficiency": "INSUFFICIENT",
        "rationale": "",
        "abstain_reason": None
    }
    
    def save_and_log_evaluation(doc, status_msg):
        db.evaluations.insert_one(doc)
        write_audit_log(
            subsystem="ai_reasoning",
            action="evaluate_qualitative",
            decision=doc["conviction"],
            reasoning=status_msg,
            ticker=ticker,
            reason_code=doc["abstain_reason"],
            trading_cycle_run_id=trading_cycle_run_id
        )
        return doc

    # Gemini call retry loop
    for attempt in range(2): # 1 initial attempt + 1 schema retry
        try:
            res_text = call_gemini_api(prompt, RESPONSE_SCHEMA)
            
            # Clean response text formatting (if any markdown wrapper returned)
            res_text = res_text.strip()
            if res_text.startswith("```json"):
                res_text = res_text[7:]
            if res_text.endswith("```"):
                res_text = res_text[:-3]
            res_text = res_text.strip()
            
            parsed = json.loads(res_text)
            if validate_response_schema(parsed):
                eval_doc["conviction"] = parsed["conviction"]
                eval_doc["risk_flags"] = parsed["risk_flags"]
                eval_doc["information_sufficiency"] = parsed["information_sufficiency"]
                eval_doc["rationale"] = parsed["rationale"]
                
                print(f"[{ticker}] AI Assessment: {eval_doc['conviction']} | Sufficiency: {eval_doc['information_sufficiency']}")
                return save_and_log_evaluation(eval_doc, f"Successfully completed qualitative AI assessment: conviction={eval_doc['conviction']}.")
            else:
                print(f"[{ticker}] Schema validation failed on attempt {attempt+1} (output did not match responseSchema).")
                
        except json.JSONDecodeError as je:
            print(f"[{ticker}] JSON decode error on attempt {attempt+1}: {je}")
        except QuotaExhaustedError as qe:
            print(f"[{ticker}] Quota exhausted across all Gemini keys: {qe}")
            eval_doc["conviction"] = "ABSTAIN"
            eval_doc["abstain_reason"] = "AI_QUOTA_EXHAUSTED"
            return save_and_log_evaluation(eval_doc, "AI Qualitative Assessment Abstained: API quota exhausted.")
        except AIUnavailableError as ae:
            print(f"[{ticker}] Gemini service unavailable: {ae}")
            eval_doc["conviction"] = "ABSTAIN"
            eval_doc["abstain_reason"] = "AI_UNAVAILABLE"
            return save_and_log_evaluation(eval_doc, "AI Qualitative Assessment Abstained: AI service unavailable.")
        except Exception as e:
            print(f"[{ticker}] Gemini API error on attempt {attempt+1}: {e}")
            
    # If loop exits without returning, schema validation failed twice
    print(f"[{ticker}] Qualitative AI assessment failed schema validation twice. Abstaining.")
    eval_doc["conviction"] = "ABSTAIN"
    eval_doc["abstain_reason"] = "AI_SCHEMA_VALIDATION_FAILED"
    return save_and_log_evaluation(eval_doc, "AI Qualitative Assessment Abstained: Schema validation failed twice.")
