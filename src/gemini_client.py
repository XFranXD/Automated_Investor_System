import os
import datetime
import requests
from src.db import get_db
from src.logger import write_audit_log

PRIMARY_MODEL = "gemini-3.1-flash-lite"
FALLBACK_MODEL = "gemini-1.5-flash-8b"

class QuotaExhaustedError(Exception):
    """Raised when all primary keys and fallback models are exhausted."""
    pass

class AIUnavailableError(Exception):
    """Raised when the Gemini service is completely unavailable due to network/server errors."""
    pass

def get_gemini_keys():
    """Reads GEMINI_API_KEY_1, _2, _3 from environment variables."""
    keys = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ]
    return [k for k in keys if k]

def get_active_key_state():
    """
    Retrieves the persistent key rotation state from MongoDB system_state collection.
    Initializes or resets the state if it is a new calendar day.
    """
    db = get_db()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    state = db.system_state.find_one({"_id": "gemini_key_state"})
    available_keys = get_gemini_keys()
    
    if not state or state.get("calendar_day") != today_str:
        state = {
            "_id": "gemini_key_state",
            "calendar_day": today_str,
            "current_key_idx": 0,
            "exhausted_keys": []
        }
        db.system_state.replace_one({"_id": "gemini_key_state"}, state, upsert=True)
        
    return state, available_keys

def _make_raw_request(api_key, model, prompt, schema=None):
    """Helper to perform the actual HTTP POST request to the Google Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    if schema:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
        
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    
    res_json = response.json()
    try:
        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected response structure from Gemini API: {e}. Full response: {res_json}")

def call_gemini_api(prompt, schema=None, use_fallback=False):
    """
    Invokes the Gemini generateContent API, managing key rotation, retries, and fallback model pools.
    
    - Immediate key rotation on quota (429) errors.
    - Single retry on active key for general network/timeout failures before rotating.
    - Engages FALLBACK_MODEL if all primary keys are exhausted.
    - Throws QuotaExhaustedError if fallback model fails or keys are exhausted.
    """
    db = get_db()
    
    if use_fallback:
        keys = get_gemini_keys()
        if not keys:
            raise ValueError("No Gemini API keys found in environment.")
        return _make_raw_request(keys[0], FALLBACK_MODEL, prompt, schema)
        
    while True:
        state, keys = get_active_key_state()
        if not keys:
            raise ValueError("No Gemini API keys found in environment.")
            
        current_idx = state.get("current_key_idx", 0)
        
        # If all primary keys are exhausted
        if current_idx >= len(keys):
            print("All primary Gemini API keys are exhausted for today.")
            exhausted = state.get("exhausted_keys", [])
            # If all primary keys failed on connection/network issues, raise AIUnavailableError directly
            if len(exhausted) == 0:
                raise AIUnavailableError("All primary keys failed due to connection/network issues.")
                
            write_audit_log(
                subsystem="gemini_client",
                action="call_api",
                decision="FALLBACK",
                reasoning="All primary keys exhausted. Engaging fallback model pool."
            )
            try:
                # Call fallback model using first available key
                return _make_raw_request(keys[0], FALLBACK_MODEL, prompt, schema)
            except requests.exceptions.RequestException as e:
                is_quota = False
                if e.response is not None and e.response.status_code == 429:
                    is_quota = True
                else:
                    try:
                        err_json = e.response.json()
                        err_msg = err_json.get("error", {}).get("message", "").lower()
                        if "quota" in err_msg or "rate limit" in err_msg or "exhausted" in err_msg:
                            is_quota = True
                    except Exception:
                        pass
                if is_quota:
                    raise QuotaExhaustedError(f"All primary keys and fallback model are exhausted due to quota limit: {e}")
                else:
                    raise AIUnavailableError(f"Gemini API is unavailable due to connection/server issues: {e}")
            except Exception as e:
                raise AIUnavailableError(f"Gemini API is unavailable: {e}")
                
        active_key = keys[current_idx]
        
        try:
            # Try active key (first attempt)
            return _make_raw_request(active_key, PRIMARY_MODEL, prompt, schema)
        except requests.exceptions.RequestException as e:
            is_quota_error = False
            if e.response is not None:
                status_code = e.response.status_code
                if status_code == 429:
                    is_quota_error = True
                else:
                    try:
                        err_json = e.response.json()
                        err_msg = err_json.get("error", {}).get("message", "").lower()
                        if "quota" in err_msg or "rate limit" in err_msg or "exhausted" in err_msg:
                            is_quota_error = True
                    except Exception:
                        pass
                        
            if is_quota_error:
                print(f"Gemini Key {current_idx+1} exhausted (daily cap/rate limit). Rotating to next key...")
                db.system_state.update_one(
                    {"_id": "gemini_key_state"},
                    {
                        "$inc": {"current_key_idx": 1},
                        "$push": {"exhausted_keys": current_idx}
                    }
                )
                continue # Retry loop with next key
                
            # General network/timeout error: retry once on the same key
            print(f"Network error on Gemini Key {current_idx+1}: {e}. Retrying once on same key...")
            try:
                return _make_raw_request(active_key, PRIMARY_MODEL, prompt, schema)
            except Exception as retry_err:
                print(f"Second attempt failed on Gemini Key {current_idx+1}: {retry_err}. Rotating key...")
                db.system_state.update_one(
                    {"_id": "gemini_key_state"},
                    {"$inc": {"current_key_idx": 1}}
                )
                # Continue loop to try next key
