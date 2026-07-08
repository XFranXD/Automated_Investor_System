import os
import csv
import time
import datetime
import requests
import re
import yfinance
import collections
import threading
from src.config import FINNHUB_API_KEY, SEC_EDGAR_USER_AGENT, TWELVEDATA_API_KEY
from src.logger import write_audit_log

# Global cache for ticker to CIK mapping
_CIK_MAP = None

def _get_cik_from_sec(ticker):
    """Fetches the CIK lookup table from SEC EDGAR and returns the CIK for the ticker."""
    global _CIK_MAP
    ticker = ticker.upper().strip()
    
    if _CIK_MAP is None:
        try:
            headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
            response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            _CIK_MAP = {}
            for item in data.values():
                _CIK_MAP[item["ticker"].upper()] = str(item["cik_str"]).zfill(10)
        except Exception as e:
            # Do not raise, allow fallback to other methods or yfinance CIK retrieval
            print(f"Warning: Failed to fetch CIK list from SEC EDGAR: {e}")
            _CIK_MAP = {}
            
    return _CIK_MAP.get(ticker)

def get_cik(ticker):
    """Retrieves CIK, trying the SEC mapper first, then falling back to yfinance."""
    cik = _get_cik_from_sec(ticker)
    if not cik:
        try:
            yt = yfinance.Ticker(ticker)
            val = yt.info.get("cik")
            if val:
                cik = str(val).zfill(10)
        except Exception:
            pass
    return cik

def log_attempt(ticker, source, success, details=None):
    """Helper to log internal data-client fetch attempts."""
    decision = "SUCCESS" if success else "FAILED"
    reasoning = f"Attempted to fetch data from {source}."
    if details:
        reasoning += f" Context: {details}"
    
    write_audit_log(
        subsystem="data_client",
        action="fetch_data",
        decision=decision,
        reasoning=reasoning,
        ticker=ticker,
        data_sources_consulted=[source]
    )

# --- SEC EDGAR Source Implementations ---

def get_sec_fundamentals(ticker):
    """Fetches raw XBRL company facts from SEC EDGAR."""
    cik = get_cik(ticker)
    if not cik:
        raise ValueError(f"No CIK found for ticker '{ticker}'")
        
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_sec_filings(ticker, item_types=None):
    """Fetches filings index from SEC EDGAR and returns list of recent filings."""
    cik = get_cik(ticker)
    if not cik:
        raise ValueError(f"No CIK found for ticker '{ticker}'")
        
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    recent = data.get("filings", {}).get("recent", {})
    keys = list(recent.keys())
    if not keys:
        return []
        
    filings = []
    num_filings = len(recent[keys[0]])
    for i in range(num_filings):
        filing = {k: recent[k][i] for k in keys}
        # If item_types is provided, filter by it (8-K specific items)
        if item_types:
            items_str = str(filing.get("items", ""))
            # Check if any specified item is in this filing
            matched = any(item in items_str for item in item_types)
            if not matched:
                continue
        filings.append(filing)
        
    return filings

# --- Finnhub Source Implementations ---

def get_finnhub_fundamentals(ticker):
    """Fetches reported financials from Finnhub."""
    url = f"https://finnhub.io/api/v1/stock/financials-reported?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if data and data.get("data"):
        return data
    return None

class TwelveDataRateLimiter:
    def __init__(self, max_calls=7, period=60.0, max_wait=65.0):
        self.max_calls = max_calls
        self.period = period
        self.max_wait = max_wait
        self.calls = collections.deque(maxlen=max_calls)
        self.lock = threading.Lock()

    def wait_for_slot(self):
        start_time = time.time()
        while True:
            with self.lock:
                now = time.time()
                elapsed = now - start_time
                if elapsed > self.max_wait:
                    return False
                
                while self.calls and now - self.calls[0] >= self.period:
                    self.calls.popleft()
                
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return True
                
                oldest = self.calls[0]
                wait_time = self.period - (now - oldest)
                
                if elapsed + wait_time > self.max_wait:
                    return False
            
            time.sleep(wait_time)

_twelvedata_limiter = TwelveDataRateLimiter()

def get_twelvedata_candles(ticker, days=45):
    """Fetches daily candles from Twelve Data, with sliding-window rate limiting."""
    if not _twelvedata_limiter.wait_for_slot():
        log_attempt(ticker, "TwelveData", False, "Rate limit wait time exceeded (65s cap)")
        return None
        
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={ticker.upper()}&interval=1day&outputsize={days}&order=asc&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        res_data = response.json()
        
        if res_data.get("status") == "error":
            message = res_data.get("message", "Unknown Twelve Data error")
            log_attempt(ticker, "TwelveData", False, f"Twelve Data API returned error: {message}")
            return None
            
        values = res_data.get("values", [])
        if not values:
            log_attempt(ticker, "TwelveData", False, "Twelve Data returned empty values array")
            return None
            
        history_list = []
        for item in values:
            dt_str = item["datetime"][:10]
            history_list.append({
                "date": dt_str,
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item["volume"])
            })
            
        closes = [float(x["close"]) for x in history_list]
        volumes = [float(x["volume"]) for x in history_list]
        
        avg_volume = 0.0
        avg_dollar_volume = 0.0
        last_20_closes = closes[-20:]
        last_20_volumes = volumes[-20:]
        if last_20_volumes:
            avg_volume = sum(last_20_volumes) / len(last_20_volumes)
            avg_dollar_volume = sum(c * v for c, v in zip(last_20_closes, last_20_volumes)) / len(last_20_volumes)
            
        log_attempt(ticker, "TwelveData", True)
        return {
            "history": history_list,
            "avg_volume": avg_volume,
            "avg_dollar_volume": avg_dollar_volume
        }
    except Exception as e:
        log_attempt(ticker, "TwelveData", False, str(e))
        return None

def get_finnhub_price_volume(ticker):
    """Fetches price, 20-day ADV and history from Finnhub quote & metric, and Twelve Data candles."""
    # 1. Current Price
    url_quote = f"https://finnhub.io/api/v1/quote?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
    r_q = requests.get(url_quote, timeout=10)
    r_q.raise_for_status()
    quote = r_q.json()
    if not quote or quote.get("c") is None or quote.get("c") == 0:
        return None
    current_price = float(quote["c"])
    
    # 2. Metrics (Market Cap)
    url_metric = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker.upper()}&metric=all&token={FINNHUB_API_KEY}"
    r_m = requests.get(url_metric, timeout=10)
    r_m.raise_for_status()
    metric = r_m.json().get("metric", {})
    market_cap = metric.get("marketCapitalization")
    if market_cap:
        market_cap = market_cap * 1000000 # convert from millions
        
    # 3. Candles (from Twelve Data fallback instead of Finnhub candle endpoint)
    candles_data = get_twelvedata_candles(ticker, days=45)
    if not candles_data:
        return None
        
    return {
        "current_price": current_price,
        "avg_daily_volume": candles_data["avg_volume"],
        "avg_daily_dollar_volume": candles_data["avg_dollar_volume"],
        "market_cap": market_cap,
        "history": candles_data["history"]
    }

def get_finnhub_earnings(ticker):
    """Fetches EPS surprise records from Finnhub."""
    url = f"https://finnhub.io/api/v1/stock/earnings?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        return data
    return None

def get_finnhub_news(ticker):
    """Fetches company news from Finnhub and standardizes it."""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=7)
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker.upper()}&from={start_date.strftime('%Y-%m-%d')}&to={today.strftime('%Y-%m-%d')}&token={FINNHUB_API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        standard_news = []
        for item in data:
            standard_news.append({
                "title": item.get("headline", ""),
                "summary": item.get("summary", ""),
                "url": item.get("url", ""),
                "datetime": item.get("datetime", 0),
                "source": item.get("source", "Finnhub")
            })
        return standard_news
    return None

# --- yfinance Source Implementations ---

def get_yfinance_fundamentals(ticker):
    """Fetches fundamentals from yfinance."""
    yt = yfinance.Ticker(ticker)
    info = yt.info
    if not info:
        return None
    try:
        balance_sheet = yt.balance_sheet.to_dict() if not yt.balance_sheet.empty else {}
        financials = yt.financials.to_dict() if not yt.financials.empty else {}
    except Exception:
        balance_sheet = {}
        financials = {}
    return {
        "info": info,
        "balance_sheet": balance_sheet,
        "financials": financials
    }

def get_yfinance_price_volume(ticker):
    """Fetches price, volume metrics, and daily history from yfinance."""
    yt = yfinance.Ticker(ticker)
    hist = yt.history(period="2mo")
    if hist.empty:
        return None
        
    current_price = float(hist["Close"].iloc[-1])
    last_20 = hist.tail(20)
    avg_volume = float(last_20["Volume"].mean())
    avg_dollar_volume = float((last_20["Close"] * last_20["Volume"]).mean())
    
    market_cap = yt.info.get("marketCap")
    if not market_cap:
        shares = yt.info.get("sharesOutstanding")
        if shares:
            market_cap = current_price * shares
            
    history_list = []
    for idx, row in hist.iterrows():
        history_list.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"])
        })
        
    return {
        "current_price": current_price,
        "avg_daily_volume": avg_volume,
        "avg_daily_dollar_volume": avg_dollar_volume,
        "market_cap": market_cap,
        "history": history_list
    }

def get_yfinance_earnings(ticker):
    """Fetches earnings surprise records from yfinance."""
    yt = yfinance.Ticker(ticker)
    df = yt.earnings_dates
    if df is None or df.empty:
        return None
        
    df = df.dropna(subset=["EPS Estimate", "Reported EPS"])
    records = []
    for idx, row in df.iterrows():
        actual = float(row["Reported EPS"])
        estimate = float(row["EPS Estimate"])
        surprise = actual - estimate
        surprise_pct = float(row.get("Surprise(%)", 0.0))
        records.append({
            "period": idx.strftime("%Y-%m-%d"),
            "actual": actual,
            "estimate": estimate,
            "surprise": surprise,
            "surprisePercent": surprise_pct
        })
    return records

def get_yfinance_news(ticker):
    """Fetches and standardizes news from yfinance."""
    yt = yfinance.Ticker(ticker)
    news = yt.news
    if not news:
        return None
        
    standard_news = []
    for item in news:
        standard_news.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "url": item.get("link", ""),
            "datetime": item.get("providerPublishTime", 0),
            "source": item.get("publisher", "yfinance")
        })
    return standard_news


_OFAC_SDN_ENTITIES = None

def get_ofac_sdn_entities():
    """Fetches the CSV file from U.S. Treasury and returns a set of normalized sanctioned entity names."""
    global _OFAC_SDN_ENTITIES
    if _OFAC_SDN_ENTITIES is not None:
        return _OFAC_SDN_ENTITIES
        
    url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    try:
        headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        lines = response.text.splitlines()
        reader = csv.reader(lines)
        entities = set()
        for row in reader:
            if len(row) < 3:
                continue
            sdn_name = row[1].strip()
            sdn_type = row[2].strip().lower()
            
            # Filter out individuals, vessels, and aircrafts. Keep other types as entities.
            if sdn_type not in ["individual", "vessel", "aircraft"]:
                entities.add(sdn_name.lower())
                
        _OFAC_SDN_ENTITIES = entities
        write_audit_log(
            subsystem="data_client",
            action="fetch_ofac_sdn",
            decision="SUCCESS",
            reasoning=f"Successfully downloaded and parsed {len(entities)} entity entries from OFAC SDN list."
        )
    except Exception as e:
        write_audit_log(
            subsystem="data_client",
            action="fetch_ofac_sdn",
            decision="FAILED",
            reasoning=f"Failed to fetch OFAC SDN list: {e}",
            reason_code="OFAC_FETCH_FAILED"
        )
        raise e
        
    return _OFAC_SDN_ENTITIES

def get_sec_10k_text(ticker):
    """Fetches the raw document text/HTML of the most recent 10-K filing for the ticker."""
    cik = get_cik(ticker)
    if not cik:
        raise ValueError(f"No CIK found for ticker '{ticker}'")
        
    filings = get_sec_filings(ticker)
    if not filings:
        return None
        
    target_filing = None
    for f in filings:
        if f.get("form") == "10-K":
            target_filing = f
            break
            
    if not target_filing:
        return None
        
    acc_num = target_filing["accessionNumber"]
    acc_no_dashes = acc_num.replace("-", "")
    primary_doc = target_filing["primaryDocument"]
    
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_doc}"
    headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    log_attempt(ticker, "SEC_EDGAR_10K", True)
    return response.text

def get_company_name(ticker):
    """Retrieves the company name for a ticker, checking yfinance first then falling back to Finnhub."""
    # 1. yfinance
    try:
        yt = yfinance.Ticker(ticker)
        name = yt.info.get("longName") or yt.info.get("shortName")
        if name:
            log_attempt(ticker, "yfinance_name", True)
            return name
    except Exception:
        pass
        
    # 2. Finnhub
    try:
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        name = data.get("name")
        if name:
            log_attempt(ticker, "Finnhub_name", True)
            return name
    except Exception:
        pass
        
    log_attempt(ticker, "company_name_lookup", False, "Could not resolve company name from yfinance or Finnhub")
    return None

def get_company_sector(ticker):
    """Retrieves the industry/sector for a ticker, checking yfinance first then falling back to Finnhub."""
    # 1. yfinance
    try:
        yt = yfinance.Ticker(ticker)
        sector = yt.info.get("sector")
        if sector:
            log_attempt(ticker, "yfinance_sector", True)
            return sector
    except Exception:
        pass
        
    # 2. Finnhub
    try:
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        sector = data.get("finnhubIndustry")
        if sector:
            log_attempt(ticker, "Finnhub_sector", True)
            return sector
    except Exception:
        pass
        
    log_attempt(ticker, "company_sector_lookup", False, "Could not resolve company sector from yfinance or Finnhub")
    return "Unknown"


def get_finnhub_earnings_calendar(from_date, to_date):
    """Fetches scheduled earnings calendar entries from Finnhub for the date range."""
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        calendar = data.get("earningsCalendar", [])
        write_audit_log(
            subsystem="data_client",
            action="get_earnings_calendar",
            decision="SUCCESS",
            reasoning=f"Successfully fetched {len(calendar)} earnings calendar entries from {from_date} to {to_date}."
        )
        return calendar
    except Exception as e:
        write_audit_log(
            subsystem="data_client",
            action="get_earnings_calendar",
            decision="FAILED",
            reasoning=f"Failed to fetch earnings calendar from {from_date} to {to_date}: {e}",
            reason_code="CALENDAR_FETCH_FAILED"
        )
        raise e

def get_sec_recent_8k_ciks():
    """Fetches the SEC EDGAR RSS/Atom feed of the latest 100 8-K filings and returns CIKs."""
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&count=100&output=atom"
    headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse CIKs from feed HTML/XML using regular expressions to capture '/data/CIK/' URLs
        ciks = re.findall(r'/data/(\d+)/', response.text)
        cik_set = {c.zfill(10) for c in ciks}
        
        write_audit_log(
            subsystem="data_client",
            action="get_recent_8k_ciks",
            decision="SUCCESS",
            reasoning=f"Successfully fetched and parsed {len(cik_set)} CIKs from SEC EDGAR 8-K feed."
        )
        return list(cik_set)
    except Exception as e:
        write_audit_log(
            subsystem="data_client",
            action="get_recent_8k_ciks",
            decision="FAILED",
            reasoning=f"Failed to fetch recent 8-K CIKs: {e}",
            reason_code="RECENT_8K_CIKS_FAILED"
        )
        raise e

def get_ticker_from_cik(cik):
    """Maps a CIK back to its ticker symbol."""
    global _CIK_MAP
    if _CIK_MAP is None:
        _get_cik_from_sec("AAPL")
        
    cik = str(cik).zfill(10)
    for ticker, c in _CIK_MAP.items():
        if c == cik:
            return ticker
    return None

def get_sec_document_text(cik, acc_num, primary_doc):
    """Fetches a specific SEC filing document text/HTML using standard SEC parameters."""
    acc_no_dashes = acc_num.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_doc}"
    headers = {"User-Agent": SEC_EDGAR_USER_AGENT}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

def get_company_news(ticker):
    """Fetches recent company news from Finnhub (primary) or yfinance (fallback)."""
    # 1. Finnhub news
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    seven_days_ago_str = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker.upper()}&from={seven_days_ago_str}&to={today_str}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json()
        if articles:
            formatted_news = []
            for art in articles[:10]:
                formatted_news.append({
                    "headline": art.get("headline", ""),
                    "summary": art.get("summary", ""),
                    "source": art.get("source", ""),
                    "datetime": datetime.datetime.utcfromtimestamp(art.get("datetime", 0)).strftime("%Y-%m-%d %H:%M:%S") if art.get("datetime") else ""
                })
            log_attempt(ticker, "Finnhub_news", True)
            return {"source": "Finnhub", "data": formatted_news}
    except Exception:
        pass
        
    # 2. yfinance news fallback
    try:
        yt = yfinance.Ticker(ticker)
        news = yt.news
        if news:
            formatted_news = []
            for art in news[:10]:
                formatted_news.append({
                    "headline": art.get("title", ""),
                    "summary": art.get("publisher", ""),
                    "source": art.get("publisher", ""),
                    "datetime": datetime.datetime.utcfromtimestamp(art.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M:%S") if art.get("providerPublishTime") else ""
                })
            log_attempt(ticker, "yfinance_news", True)
            return {"source": "yfinance", "data": formatted_news}
    except Exception:
        pass
        
    log_attempt(ticker, "company_news", False, "Could not fetch news from Finnhub or yfinance")
    return None

def clean_html(html_text):
    """Strips HTML tags, script/style content, and normalizes spacing. Limits output size."""
    if not html_text:
        return ""
    # Remove script and style elements
    text = re.sub(r'<(script|style).*?>.*?</\1>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', ' ', text)
    # Replace entities
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    # Normalize spaces
    text = ' '.join(text.split())
    # Limit character length to 20,000 chars to respect context limits
    return text[:20000]





# =====================================================================
# --- Unified Waterfall APIs ---
# =====================================================================

def get_fundamentals(ticker):
    """Waterfall: SEC_EDGAR -> Finnhub -> yfinance"""
    sources = ["SEC_EDGAR", "Finnhub", "yfinance"]
    
    # 1. SEC EDGAR
    try:
        data = get_sec_fundamentals(ticker)
        if data:
            log_attempt(ticker, "SEC_EDGAR", True)
            return {"source": "SEC_EDGAR", "data": data}
        log_attempt(ticker, "SEC_EDGAR", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "SEC_EDGAR", False, str(e))
        
    # 2. Finnhub
    try:
        data = get_finnhub_fundamentals(ticker)
        if data:
            log_attempt(ticker, "Finnhub", True)
            return {"source": "Finnhub", "data": data}
        log_attempt(ticker, "Finnhub", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "Finnhub", False, str(e))
        
    # 3. yfinance
    try:
        data = get_yfinance_fundamentals(ticker)
        if data:
            log_attempt(ticker, "yfinance", True)
            return {"source": "yfinance", "data": data}
        log_attempt(ticker, "yfinance", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "yfinance", False, str(e))
        
    write_audit_log(
        subsystem="data_client",
        action="get_fundamentals",
        decision="FAILED",
        reasoning="All fundamental sources in waterfall failed or returned no data.",
        ticker=ticker,
        data_sources_consulted=sources,
        reason_code="FUNDAMENTALS_NO_DATA"
    )
    return None

def get_price_volume(ticker):
    """Waterfall: yfinance -> Finnhub+TwelveData"""
    sources = ["yfinance", "Finnhub+TwelveData"]
    
    # 1. yfinance
    try:
        data = get_yfinance_price_volume(ticker)
        if data:
            log_attempt(ticker, "yfinance", True)
            return {"source": "yfinance", "data": data}
        log_attempt(ticker, "yfinance", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "yfinance", False, str(e))
        
    # 2. Finnhub + TwelveData
    try:
        data = get_finnhub_price_volume(ticker)
        if data:
            log_attempt(ticker, "Finnhub+TwelveData", True)
            return {"source": "Finnhub+TwelveData", "data": data}
        log_attempt(ticker, "Finnhub+TwelveData", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "Finnhub+TwelveData", False, str(e))
        
    write_audit_log(
        subsystem="data_client",
        action="get_price_volume",
        decision="FAILED",
        reasoning="All price/volume sources in waterfall failed or returned no data.",
        ticker=ticker,
        data_sources_consulted=sources,
        reason_code="PRICE_VOLUME_NO_DATA"
    )
    return None

def get_earnings(ticker):
    """Waterfall: Finnhub -> yfinance"""
    sources = ["Finnhub", "yfinance"]
    
    # 1. Finnhub
    try:
        data = get_finnhub_earnings(ticker)
        if data:
            log_attempt(ticker, "Finnhub", True)
            return {"source": "Finnhub", "data": data}
        log_attempt(ticker, "Finnhub", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "Finnhub", False, str(e))
        
    # 2. yfinance
    try:
        data = get_yfinance_earnings(ticker)
        if data:
            log_attempt(ticker, "yfinance", True)
            return {"source": "yfinance", "data": data}
        log_attempt(ticker, "yfinance", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "yfinance", False, str(e))
        
    write_audit_log(
        subsystem="data_client",
        action="get_earnings",
        decision="FAILED",
        reasoning="All earnings surprise sources in waterfall failed or returned no data.",
        ticker=ticker,
        data_sources_consulted=sources,
        reason_code="EARNINGS_NO_DATA"
    )
    return None

def get_news(ticker):
    """Waterfall: Finnhub -> yfinance"""
    sources = ["Finnhub", "yfinance"]
    
    # 1. Finnhub
    try:
        data = get_finnhub_news(ticker)
        if data:
            log_attempt(ticker, "Finnhub", True)
            return {"source": "Finnhub", "data": data}
        log_attempt(ticker, "Finnhub", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "Finnhub", False, str(e))
        
    # 2. yfinance
    try:
        data = get_yfinance_news(ticker)
        if data:
            log_attempt(ticker, "yfinance", True)
            return {"source": "yfinance", "data": data}
        log_attempt(ticker, "yfinance", False, "Returned empty data structure")
    except Exception as e:
        log_attempt(ticker, "yfinance", False, str(e))
        
    write_audit_log(
        subsystem="data_client",
        action="get_news",
        decision="FAILED",
        reasoning="All news sources in waterfall failed or returned no data.",
        ticker=ticker,
        data_sources_consulted=sources,
        reason_code="NEWS_NO_DATA"
    )
    return None

def get_filings(ticker, item_types=None):
    """Filing Waterfall: SEC_EDGAR only"""
    sources = ["SEC_EDGAR"]
    
    # 1. SEC EDGAR
    try:
        data = get_sec_filings(ticker, item_types)
        if data:
            log_attempt(ticker, "SEC_EDGAR", True)
            return {"source": "SEC_EDGAR", "data": data}
        log_attempt(ticker, "SEC_EDGAR", False, "Returned empty list or no matching items")
    except Exception as e:
        log_attempt(ticker, "SEC_EDGAR", False, str(e))
        
    write_audit_log(
        subsystem="data_client",
        action="get_filings",
        decision="FAILED",
        reasoning="SEC EDGAR filings query failed or returned no data.",
        ticker=ticker,
        data_sources_consulted=sources,
        reason_code="FILINGS_NO_DATA"
    )
    return None
