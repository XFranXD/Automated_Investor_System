import datetime
import re
from src.db import get_db
from src.logger import write_audit_log
from src.data_client import (
    get_fundamentals,
    get_price_volume,
    get_filings,
    get_ofac_sdn_entities,
    get_company_name,
    get_sec_10k_text
)

# Extractor Mappings for SEC EDGAR and Finnhub (US-GAAP tags)
SEC_TAGS = {
    "revenue": ["Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueGoodsNet"],
    "receivables": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent", "AccountsReceivableNet"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfRevenue"],
    "current_assets": ["AssetsCurrent"],
    "total_assets": ["Assets"],
    "ppe": ["PropertyPlantAndEquipmentNet"],
    "depreciation": ["DepreciationDepletionAndAmortization", "Depreciation"],
    "sga": ["SellingGeneralAndAdministrativeExpense", "SellingAndAdministrativeExpense"],
    "liabilities": ["Liabilities", "LiabilitiesCurrent"],
    "net_income": ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "securities": ["MarketableSecuritiesCurrent", "ShortTermInvestments", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit"],
    "ebit": ["OperatingIncomeLoss", "EBIT", "EarningsBeforeInterestAndTaxes"]
}

# Extractor Mappings for yfinance (Standard row labels)
YF_KEYS = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "receivables": ["Accounts Receivable", "Receivables"],
    "cogs": ["Cost Of Revenue", "Cost Of Goods Sold"],
    "current_assets": ["Total Current Assets", "Current Assets"],
    "total_assets": ["Total Assets"],
    "ppe": ["Net PPE", "Property Plant And Equipment Net", "Net Property Plant Equipment"],
    "depreciation": ["Depreciation And Amortization", "Depreciation", "Depreciation Amortization Depletion"],
    "sga": ["Selling General And Administrative", "SG&A", "Selling General And Administrative Expense"],
    "liabilities": ["Total Liabilities Net External", "Total Liabilities", "Liabilities"],
    "net_income": ["Net Income", "Net Income Loss"],
    "cfo": ["Cash Flow From Operating Activities", "Operating Cash Flow"],
    "securities": ["Cash Cash Equivalents And Short Term Investments", "Short Term Investments", "Marketable Securities"],
    "current_liabilities": ["Total Current Liabilities", "Current Liabilities"],
    "retained_earnings": ["Retained Earnings"],
    "ebit": ["EBIT", "Operating Income"]
}

def _normalize_name(name):
    """Normalizes names by lowercasing, stripping punctuation, and removing common suffixes."""
    if not name:
        return ""
    name = name.lower()
    # Replace non-alphanumeric with spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    # Common company suffixes pattern
    suffixes = [
        r'\binc\b', r'\bco\b', r'\bltd\b', r'\bcorp\b', r'\bcorporation\b',
        r'\blimited\b', r'\bgroup\b', r'\bholdings\b', r'\bplc\b'
    ]
    for s in suffixes:
        name = re.sub(s, ' ', name)
    # Remove extra spaces
    name = ' '.join(name.split())
    return name

def _check_sanctions(company_name, sdn_list):
    """Checks if the company name matches any name in the sanctioned entity list using word boundaries."""
    norm_company = _normalize_name(company_name)
    if not norm_company:
        return False
        
    for sdn_name in sdn_list:
        norm_sdn = _normalize_name(sdn_name)
        if not norm_sdn:
            continue
        # Use word boundaries to search for sdn name in company name
        if re.search(r'\b' + re.escape(norm_sdn) + r'\b', norm_company):
            return True
    return False

# --- Helper extraction functions ---

def _extract_edgar_fact(data, tags, year, period="FY"):
    """Extracts a fact from SEC EDGAR facts data for a specific year and period."""
    us_gaap = data.get("facts", {}).get("us-gaap", {})
    dei = data.get("facts", {}).get("dei", {})
    
    for tag in tags:
        tag_data = us_gaap.get(tag) or dei.get(tag)
        if not tag_data:
            continue
        units = tag_data.get("units", {})
        unit_keys = list(units.keys())
        if not unit_keys:
            continue
        entries = units[unit_keys[0]]
        
        matches = []
        for entry in entries:
            if entry.get("fy") == year and entry.get("fp") == period and "10-K" in entry.get("form", ""):
                matches.append(entry)
                
        if matches:
            # Sort by filing date descending
            matches.sort(key=lambda x: x.get("filed", ""), reverse=True)
            return float(matches[0]["val"])
            
    return None

def _extract_finnhub_fact(data, tags, year):
    """Extracts a fact from Finnhub reported financials for a specific fiscal year."""
    reports = data.get("data", [])
    target_report = None
    for r in reports:
        if r.get("year") == year and r.get("quarter") == 0 and "10-K" in r.get("form", ""):
            target_report = r
            break
            
    if not target_report:
        return None
        
    report_sections = target_report.get("report", {})
    for section in ["bs", "ic", "cf"]:
        items = report_sections.get(section, [])
        for item in items:
            concept = item.get("concept")
            if concept in tags:
                return float(item.get("value"))
                
    return None

def _extract_yfinance_fact(data, keys, year):
    """Extracts a fact from yfinance fundamentals data for a specific year."""
    for section in ["balance_sheet", "financials"]:
        section_dict = data.get(section, {})
        for col_date, metrics in section_dict.items():
            if str(year) in col_date:
                for k in keys:
                    if k in metrics:
                        val = metrics[k]
                        # Check for None and NaN
                        if val is not None and not (isinstance(val, float) and val != val):
                            return float(val)
    return None

def extract_financial_concept(fundamentals, concept, year):
    """Extracts the value of a specific financial concept from the fundamentals wrapper."""
    source = fundamentals.get("source")
    data = fundamentals.get("data")
    if not data:
        return None
        
    if source == "SEC_EDGAR":
        tags = SEC_TAGS.get(concept, [])
        return _extract_edgar_fact(data, tags, year)
    elif source == "Finnhub":
        tags = SEC_TAGS.get(concept, [])
        return _extract_finnhub_fact(data, tags, year)
    elif source == "yfinance":
        keys = YF_KEYS.get(concept, [])
        return _extract_yfinance_fact(data, keys, year)
    return None

def get_recent_fiscal_years(fundamentals):
    """Finds the two most recent fiscal years in the fundamentals data."""
    source = fundamentals.get("source")
    data = fundamentals.get("data")
    years = []
    
    if source == "SEC_EDGAR":
        us_gaap = data.get("facts", {}).get("us-gaap", {})
        dei = data.get("facts", {}).get("dei", {})
        for tag_dict in [us_gaap, dei]:
            for tag, tag_data in tag_dict.items():
                units = tag_data.get("units", {})
                for unit_key, entries in units.items():
                    for entry in entries:
                        if "10-K" in entry.get("form", ""):
                            fy = entry.get("fy")
                            if fy:
                                try:
                                    years.append(int(fy))
                                except ValueError:
                                    pass
    elif source == "Finnhub":
        reports = data.get("data", [])
        for r in reports:
            if r.get("quarter") == 0 and "10-K" in r.get("form", ""):
                fy = r.get("year")
                if fy:
                    years.append(int(fy))
    elif source == "yfinance":
        bs = data.get("balance_sheet", {})
        for col_date in bs.keys():
            try:
                yr = int(col_date.split("-")[0])
                years.append(yr)
            except (ValueError, IndexError):
                pass
                
    unique_years = sorted(list(set(years)), reverse=True)
    if len(unique_years) >= 2:
        return unique_years[0], unique_years[1]
    return None

# --- Core Gate Calculations ---

def compute_beneish_m_score(fundamentals, current_year, prior_year):
    """Computes the 8-variable Beneish M-Score for given years, or None if incomputable."""
    sales_t = extract_financial_concept(fundamentals, "revenue", current_year)
    sales_t1 = extract_financial_concept(fundamentals, "revenue", prior_year)
    
    rec_t = extract_financial_concept(fundamentals, "receivables", current_year)
    rec_t1 = extract_financial_concept(fundamentals, "receivables", prior_year)
    
    cogs_t = extract_financial_concept(fundamentals, "cogs", current_year)
    cogs_t1 = extract_financial_concept(fundamentals, "cogs", prior_year)
    
    ca_t = extract_financial_concept(fundamentals, "current_assets", current_year)
    ca_t1 = extract_financial_concept(fundamentals, "current_assets", prior_year)
    
    ta_t = extract_financial_concept(fundamentals, "total_assets", current_year)
    ta_t1 = extract_financial_concept(fundamentals, "total_assets", prior_year)
    
    ppe_t = extract_financial_concept(fundamentals, "ppe", current_year)
    ppe_t1 = extract_financial_concept(fundamentals, "ppe", prior_year)
    
    dep_t = extract_financial_concept(fundamentals, "depreciation", current_year)
    dep_t1 = extract_financial_concept(fundamentals, "depreciation", prior_year)
    
    sga_t = extract_financial_concept(fundamentals, "sga", current_year)
    sga_t1 = extract_financial_concept(fundamentals, "sga", prior_year)
    
    liab_t = extract_financial_concept(fundamentals, "liabilities", current_year)
    liab_t1 = extract_financial_concept(fundamentals, "liabilities", prior_year)
    
    ni_t = extract_financial_concept(fundamentals, "net_income", current_year)
    cfo_t = extract_financial_concept(fundamentals, "cfo", current_year)
    
    sec_t = extract_financial_concept(fundamentals, "securities", current_year) or 0.0
    sec_t1 = extract_financial_concept(fundamentals, "securities", prior_year) or 0.0
    
    required = [
        sales_t, sales_t1, rec_t, rec_t1, cogs_t, cogs_t1,
        ca_t, ca_t1, ta_t, ta_t1, ppe_t, ppe_t1,
        dep_t, dep_t1, sga_t, sga_t1, liab_t, liab_t1,
        ni_t, cfo_t
    ]
    if any(val is None for val in required):
        return None
        
    try:
        dsri = (rec_t / sales_t) / (rec_t1 / sales_t1)
        
        margin_t1 = (sales_t1 - cogs_t1) / sales_t1
        margin_t = (sales_t - cogs_t) / sales_t
        gmi = margin_t1 / margin_t
        
        aqi_t = 1.0 - (ca_t + ppe_t + sec_t) / ta_t
        aqi_t1 = 1.0 - (ca_t1 + ppe_t1 + sec_t1) / ta_t1
        aqi = aqi_t / aqi_t1
        
        sgi = sales_t / sales_t1
        
        depi_t1 = dep_t1 / (dep_t1 + ppe_t1)
        depi_t = dep_t / (dep_t + ppe_t)
        depi = depi_t1 / depi_t
        
        sgai = (sga_t / sales_t) / (sga_t1 / sales_t1)
        
        lvgi = (liab_t / ta_t) / (liab_t1 / ta_t1)
        
        tata = (ni_t - cfo_t) / ta_t
        
        m_score = (
            -4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
            + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi
        )
        return m_score
    except ZeroDivisionError:
        return None

def compute_altman_z_score(fundamentals, market_cap, current_year):
    """Computes the Altman Z-Score, or None if incomputable."""
    ca = extract_financial_concept(fundamentals, "current_assets", current_year)
    cl = extract_financial_concept(fundamentals, "current_liabilities", current_year)
    ta = extract_financial_concept(fundamentals, "total_assets", current_year)
    retained_earnings = extract_financial_concept(fundamentals, "retained_earnings", current_year)
    ebit = extract_financial_concept(fundamentals, "ebit", current_year)
    tl = extract_financial_concept(fundamentals, "liabilities", current_year)
    sales = extract_financial_concept(fundamentals, "revenue", current_year)
    
    required = [ca, cl, ta, retained_earnings, ebit, tl, sales, market_cap]
    if any(val is None for val in required):
        return None
        
    try:
        working_capital = ca - cl
        a = working_capital / ta
        b = retained_earnings / ta
        c = ebit / ta
        d = market_cap / tl
        e = sales / ta
        
        z_score = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e
        return z_score
    except ZeroDivisionError:
        return None


# =====================================================================
# --- Core Gates Engine ---
# =====================================================================

def evaluate_gates(ticker, trading_cycle_run_id=None):
    """
    Evaluates a ticker against all six deterministic hard gates in order.
    
    Short-circuits on the first failure. Reuses same-day cached candidate documents if found.
    Returns:
    - dict: The candidate document stored in MongoDB database.
    """
    ticker = ticker.upper().strip()
    db = get_db()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # Resolve trigger_type by checking if there is a PENDING candidate for this ticker today.
    # This keeps same-day multiple triggers caching working correctly.
    pending_cand = db.candidates.find_one({
        "ticker": ticker,
        "calendar_day": today_str,
        "gate_result": "PENDING"
    })
    if pending_cand:
        trigger_type = pending_cand.get("trigger_type")
    else:
        # Fallback to any existing candidate today, or default to "EARNINGS_SURPRISE"
        exist_cand = db.candidates.find_one({"ticker": ticker, "calendar_day": today_str})
        if exist_cand:
            trigger_type = exist_cand.get("trigger_type")
        else:
            trigger_type = "EARNINGS_SURPRISE"
            
    query_filter = {"ticker": ticker, "calendar_day": today_str, "trigger_type": trigger_type}
    
    # 1. Same-Day Caching check
    cached = db.candidates.find_one(query_filter)
    if cached and cached.get("gate_result") in ["PASSED", "REJECTED"]:
        write_audit_log(
            subsystem="hardgate",
            action="evaluate_gates_cached",
            decision=cached["gate_result"],
            reasoning=f"Retrieved same-day cached gate evaluation result.",
            ticker=ticker,
            reason_code=cached.get("gate_reason_code"),
            trading_cycle_run_id=trading_cycle_run_id
        )
        return cached

    sources_consulted = []
    
    # Initialize candidate payload
    cand_doc = {
        "ticker": ticker,
        "trigger_type": trigger_type,
        "discovery_timestamp": datetime.datetime.utcnow(),
        "trading_cycle_run_id": trading_cycle_run_id,
        "calendar_day": today_str,
        "gate_result": "PASSED",
        "gate_reason_code": None,
        "gate_data_sources_consulted": []
    }
    
    def fail_candidate(reason_code, details):
        cand_doc["gate_result"] = "REJECTED"
        cand_doc["gate_reason_code"] = reason_code
        cand_doc["gate_data_sources_consulted"] = list(set(sources_consulted))
        
        # Save/update in DB to preserve any trigger fields set by discovery
        db.candidates.update_one(
            query_filter,
            {"$set": cand_doc},
            upsert=True
        )
        final_doc = db.candidates.find_one(query_filter)
        
        write_audit_log(
            subsystem="hardgate",
            action="evaluate_gates",
            decision="REJECTED",
            reasoning=details,
            ticker=ticker,
            data_sources_consulted=cand_doc["gate_data_sources_consulted"],
            reason_code=reason_code,
            trading_cycle_run_id=trading_cycle_run_id
        )
        return final_doc

    # --- GATE 1: OFAC / Sanctions ---
    print(f"[{ticker}] Running Gate 1: OFAC Sanctions...")
    try:
        sdn_entities = get_ofac_sdn_entities()
        sources_consulted.append("OFAC")
    except Exception as e:
        return fail_candidate("GATE_SANCTIONS_NO_DATA", f"Could not verify sanctions status: {e}")
        
    company_name = get_company_name(ticker)
    if not company_name:
        return fail_candidate("GATE_SANCTIONS_NO_DATA", "Could not verify sanctions: Company name could not be resolved.")
        
    if _check_sanctions(company_name, sdn_entities):
        return fail_candidate("GATE_SANCTIONS", f"Company name '{company_name}' matched OFAC sanctions list.")
    print(f"[{ticker}] Gate 1 PASSED.")

    # --- GATE 2: Liquidity Minimums ---
    print(f"[{ticker}] Running Gate 2: Liquidity Minimums...")
    price_vol_res = get_price_volume(ticker)
    if not price_vol_res:
        return fail_candidate("GATE_LIQUIDITY_PRICE_NO_DATA", "Could not verify liquidity: Failed to fetch price/volume data.")
        
    sources_consulted.append(price_vol_res["source"])
    pv_data = price_vol_res["data"]
    
    current_price = pv_data.get("current_price")
    avg_dollar_volume = pv_data.get("avg_daily_dollar_volume")
    
    if current_price is None:
        return fail_candidate("GATE_LIQUIDITY_PRICE_NO_DATA", "Could not verify share price: Missing price field.")
    if current_price < 5.00:
        return fail_candidate("GATE_LIQUIDITY_PRICE", f"Share price ${current_price:.2f} is below $5.00 floor.")
        
    if avg_dollar_volume is None:
        return fail_candidate("GATE_LIQUIDITY_ADV_NO_DATA", "Could not verify average daily volume: Missing ADV field.")
    if avg_dollar_volume < 5000000.0:
        return fail_candidate("GATE_LIQUIDITY_ADV", f"Average daily dollar volume ${avg_dollar_volume:,.2f} is below $5,000,000 threshold.")
    print(f"[{ticker}] Gate 2 PASSED.")

    # --- GATE 3: Delinquent Filing Check ---
    print(f"[{ticker}] Running Gate 3: Delinquent Filing Check...")
    filings_res = get_filings(ticker)
    if not filings_res:
        return fail_candidate("GATE_DELINQUENT_FILING_NO_DATA", "Could not verify filing delinquency: Failed to fetch filings.")
        
    sources_consulted.append(filings_res["source"])
    filings = filings_res["data"]
    
    six_months_ago = datetime.date.today() - datetime.timedelta(days=180)
    
    # Check for NT 10-K or NT 10-Q filings
    for f in filings:
        form = f.get("form", "")
        if form in ["NT 10-K", "NT 10-Q"]:
            f_date_str = f.get("filingDate", "")
            try:
                f_date = datetime.datetime.strptime(f_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
                
            if f_date >= six_months_ago:
                # We found a late filing notice. Check if a subsequent 10-K or 10-Q has been filed since
                subsequent_filed = False
                target_subsequent_form = "10-K" if "10-K" in form else "10-Q"
                
                for sub_f in filings:
                    sub_form = sub_f.get("form", "")
                    if sub_form == target_subsequent_form:
                        sub_date_str = sub_f.get("filingDate", "")
                        try:
                            sub_date = datetime.datetime.strptime(sub_date_str, "%Y-%m-%d").date()
                        except ValueError:
                            continue
                        if sub_date > f_date:
                            subsequent_filed = True
                            break
                            
                if not subsequent_filed:
                    return fail_candidate("GATE_DELINQUENT_FILING", f"Late filing notice '{form}' submitted on {f_date_str} with no subsequent {target_subsequent_form} filed.")
    print(f"[{ticker}] Gate 3 PASSED.")

    # --- GATE 4: Auditor Change & Adverse Opinion ---
    print(f"[{ticker}] Running Gate 4: Auditor Change & Adverse Opinion...")
    # Sub-check A: Auditor change in last 12 months
    twelve_months_ago = datetime.date.today() - datetime.timedelta(days=365)
    for f in filings:
        form = f.get("form", "")
        if form == "8-K":
            items = str(f.get("items", ""))
            if "4.01" in items:
                f_date_str = f.get("filingDate", "")
                try:
                    f_date = datetime.datetime.strptime(f_date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue
                if f_date >= twelve_months_ago:
                    return fail_candidate("GATE_AUDITOR_CHANGE", f"Registrant certifying accountant change (Item 4.01) reported on 8-K on {f_date_str}.")
                    
    # Sub-check B: Auditor adverse opinion check
    try:
        doc_text = get_sec_10k_text(ticker)
    except Exception as e:
        return fail_candidate("GATE_ADVERSE_OPINION_NO_DATA", f"Could not verify auditor opinion: Failed to fetch most recent 10-K document: {e}")
        
    if not doc_text:
        return fail_candidate("GATE_ADVERSE_OPINION_NO_DATA", "Could not verify auditor opinion: No 10-K filing document text retrieved.")
        
    sources_consulted.append("SEC_EDGAR_10K")
    doc_text_lower = doc_text.lower()
    
    adverse_phrases = ["substantial doubt", "going concern", "adverse opinion", "did not express an opinion"]
    for phrase in adverse_phrases:
        if phrase in doc_text_lower:
            return fail_candidate("GATE_ADVERSE_OPINION", f"Auditor adverse opinion/going concern keywords found in last 10-K: matched '{phrase}'.")
    print(f"[{ticker}] Gate 4 PASSED.")

    # --- GATE 5: Beneish M-Score ---
    print(f"[{ticker}] Running Gate 5: Beneish M-Score...")
    fundamentals_res = get_fundamentals(ticker)
    if not fundamentals_res:
        return fail_candidate("GATE_BENEISH_NO_DATA", "Could not compute Beneish M-Score: Failed to fetch fundamentals.")
        
    sources_consulted.append(fundamentals_res["source"])
    fundamentals = fundamentals_res["data"]
    
    years = get_recent_fiscal_years(fundamentals_res)
    if not years:
        return fail_candidate("GATE_BENEISH_NO_DATA", "Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.")
        
    current_yr, prior_yr = years
    m_score = compute_beneish_m_score(fundamentals_res, current_yr, prior_yr)
    if m_score is None:
        return fail_candidate("GATE_BENEISH_NO_DATA", f"Could not compute Beneish M-Score: Missing required accounting metrics for FY{current_yr} vs FY{prior_yr}.")
        
    if m_score > -1.78:
        return fail_candidate("GATE_BENEISH", f"Beneish M-Score of {m_score:.4f} is above the -1.78 manipulation threshold (FY{current_yr} vs FY{prior_yr}).")
    print(f"[{ticker}] Gate 5 PASSED (M-Score: {m_score:.4f}).")

    # --- GATE 6: Altman Z-Score ---
    print(f"[{ticker}] Running Gate 6: Altman Z-Score...")
    market_cap = pv_data.get("market_cap")
    z_score = compute_altman_z_score(fundamentals_res, market_cap, current_yr)
    if z_score is None:
        return fail_candidate("GATE_ALTMAN_NO_DATA", f"Could not compute Altman Z-Score: Missing required accounting metrics for FY{current_yr}.")
        
    if z_score < 1.81:
        return fail_candidate("GATE_ALTMAN", f"Altman Z-Score of {z_score:.4f} is below the 1.81 distress zone threshold (FY{current_yr}).")
    print(f"[{ticker}] Gate 6 PASSED (Z-Score: {z_score:.4f}).")

    # --- SUCCESSFUL PASS ---
    cand_doc["gate_data_sources_consulted"] = list(set(sources_consulted))
    
    db.candidates.update_one(
        query_filter,
        {"$set": cand_doc},
        upsert=True
    )
    final_doc = db.candidates.find_one(query_filter)
    
    write_audit_log(
        subsystem="hardgate",
        action="evaluate_gates",
        decision="PASSED",
        reasoning=(
            f"All six hard gates passed. M-Score: {m_score:.4f} (threshold: > -1.78), "
            f"Z-Score: {z_score:.4f} (threshold: < 1.81)."
        ),
        ticker=ticker,
        data_sources_consulted=cand_doc["gate_data_sources_consulted"],
        trading_cycle_run_id=trading_cycle_run_id
    )
    
    return final_doc
