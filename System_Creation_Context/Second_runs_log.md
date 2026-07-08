# trading cycle workflow logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AIDG: No earnings dates found, symbol may be delisted
CEV: No earnings dates found, symbol may be delisted
CHBH: No earnings dates found, symbol may be delisted
CHSCP: No earnings dates found, symbol may be delisted
FPF: No earnings dates found, symbol may be delisted
MHI: No earnings dates found, symbol may be delisted
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260707-160846
Step 1: Running Portfolio Monitor...
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
[T_DASH_3] Could not retrieve price volume data for monitoring. Skipping.
AUDIT LOG: [portfolio_monitor] monitor_cycle -> MONITORED: Completed portfolio monitoring cycle. Equity: $90500.00, Cash: $90500.00, Drawdown: 0.00% (HWM: $90500.00), Kill Switch: False, Correlation Cap: 0.6 (Regime: RISK_ON).
Portfolio monitor finished. Equity: $90500.00 | Drawdown: 0.00% | Kill Switch: False
Step 2: Running Candidate Discovery...
=== STARTING CANDIDATE DISCOVERY ===

Scanning Earnings Calendar...
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 55 earnings calendar entries from 2026-07-06 to 2026-07-07.
AUDIT LOG: [data_client] for AIDG fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AIDG fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AIDG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CEV fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CEV fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CEV get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CHBH fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CHBH fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CHBH get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CHSCP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CHSCP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CHSCP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for EPAC fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for FPF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FPF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FPF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[KRUS] Discovered earnings trigger (LONG): surprise 12.39%
AUDIT LOG: [data_client] for MHI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for MHI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for MHI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NRIX fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[PENG] Discovered earnings trigger (LONG): surprise 20.65%
AUDIT LOG: [data_client] for SAR fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[SAR] Discovered earnings trigger (SHORT): surprise -128.60%
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ADN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for AREC fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[AREC] Discovered earnings trigger (LONG): surprise 1008.15%
AUDIT LOG: [data_client] for ASII fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ASII fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ASII get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for AUSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AUSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AUSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for AXG fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AXG fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AXG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for BANX fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for BTM fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[BTM] Discovered earnings trigger (SHORT): surprise -1652.23%
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
FTRS: No earnings dates found, symbol may be delisted
HBSI: No earnings dates found, symbol may be delisted
HIX: No earnings dates found, symbol may be delisted
HUBC: No earnings dates found, symbol may be delisted
IAF: No earnings dates found, symbol may be delisted
IXAQF: No earnings dates found, symbol may be delisted
NAD: No earnings dates found, symbol may be delisted
NEA: No earnings dates found, symbol may be delisted
NIMU: No earnings dates found, symbol may be delisted
NMZ: No earnings dates found, symbol may be delisted
NUV: No earnings dates found, symbol may be delisted
NVG: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRMT fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[CRMT] Discovered earnings trigger (SHORT): surprise -445.45%
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ENLV fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[ENLV] Discovered earnings trigger (SHORT): surprise -25553.59%
AUDIT LOG: [data_client] for FAX fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FAX fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FAX get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for FCO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FCO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FCO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for FLYE fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FLYE fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FLYE get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for FTII fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FTII fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FTII get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for FTRS fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for FTRS fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for FTRS get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for HIRU fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[HIRU] Discovered earnings trigger (SHORT): surprise -92.16%
AUDIT LOG: [data_client] for HIX fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HIX fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HIX get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for HUBC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HUBC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HUBC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for IAF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for IAF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for IAF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for IXAQF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for IXAQF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for IXAQF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for KOAN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for NAD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NAD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for NAD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NEA fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NEA fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for NEA get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NIMU fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NIMU fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for NIMU get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NMZ fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NMZ fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for NMZ get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NUV fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NUV fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for NUV get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVG fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for NVG fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for NVG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVVE fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for OLOX fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[OLOX] Discovered earnings trigger (LONG): surprise 37.36%
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for SANW fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[SANW] Discovered earnings trigger (LONG): surprise 48.73%
AUDIT LOG: [data_client] for SNRG fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for SNRG fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for SNRG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for SRKE fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for SRKE fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for SRKE get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for SRKE fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for SRKE fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for SRKE get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for TTRX fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for WTER fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[WTER] Discovered earnings trigger (LONG): surprise 26.47%
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> SUCCESS: Successfully fetched and parsed 100 CIKs from SEC EDGAR 8-K feed.
AUDIT LOG: [data_client] for LAZ fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for LAZ fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for ECHO fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ECHO fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for GETY fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GETY fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for EWSB fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for EWSB fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[EWSB] Discovered 8-K filing trigger (LONG): items ['5.02'], move 4.74% on 14.44x avg volume
AUDIT LOG: [data_client] for SPWR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SPWR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for UPLD fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for UPLD fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for VAVX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for VAVX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for POLA fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for RWT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[CMPS] Discovered 8-K filing trigger (SHORT): items ['8.01'], move 11.47% on 2.68x avg volume
AUDIT LOG: [data_client] for ALUR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ALUR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[ESI] Discovered 8-K filing trigger (SHORT): items ['1.01', '5.02'], move 7.89% on 3.95x avg volume
AUDIT LOG: [data_client] for PMNT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for HTB fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for HTB fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for AX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for AX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for USAC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for USAC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for GGRP fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GGRP fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for DMLP fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for DMLP fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for VRTX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for VRTX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[SOLS] Discovered 8-K filing trigger (SHORT): items ['1.01', '8.01'], move 13.39% on 2.79x avg volume
AUDIT LOG: [data_client] for TVRD fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for BHRB fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for BHRB fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for PRPL fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for PRPL fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for SVC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for LPAA fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for LPAA fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for SMTC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SMTC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for AITX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for AITX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for CURI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for NUVB fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for NUVB fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for COPR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for COPR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for RDZN fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for MBOT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for MBOT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for SMNR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SMNR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for RIVN fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GRTX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GRTX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for TTRX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for OSTX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for PRGO fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for PRGO fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for CGEH fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for EVTV fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for EVTV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for EVTV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[EVTV] Discovered 8-K filing trigger (LONG): items ['1.01', '2.01', '5.02'], move 20.00% on 1.59x avg volume
AUDIT LOG: [data_client] for MGTX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for MGTX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for CPPTL fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CPPTL fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for MVIS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for LSF fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SABS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CLMB fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ZPTA fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for QUCY fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for QUCY fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for AUID fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for TMHC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for TMHC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for CETX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CETX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for WHLR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for WHLR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for PIII fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for PIII fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[PIII] Discovered 8-K filing trigger (SHORT): items ['1.01'], move 30.93% on 2.29x avg volume
AUDIT LOG: [data_client] for CRNX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CRNX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[CRNX] Discovered 8-K filing trigger (SHORT): items ['1.01', '8.01'], move 6.57% on 3.46x avg volume
AUDIT LOG: [data_client] for SKYH fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SKYH fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for DGICA fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for DGICA fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for SVCO fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SVCO fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for VXRT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for VXRT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for DMRC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for DMRC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for TOVX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for TOVX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[TOVX] Discovered 8-K filing trigger (SHORT): items ['8.01'], move 29.44% on 1.97x avg volume
AUDIT LOG: [data_client] for ABTC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ABTC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for GRDX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GRDX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for BAM fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for BAM fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for VRM fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for VRM fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for ZCAR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ZCAR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for PMI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ABR fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for ABR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for O fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for O fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for EXYN fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for BIAF fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for BIAF fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[BIAF] Discovered 8-K filing trigger (LONG): items ['8.01'], move 3.16% on 2.75x avg volume
AUDIT LOG: [data_client] for PCMC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for PCMC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for MGTI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for MGTI fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for BKYI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for QBTS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for DOCN fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for DGXX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SSII fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SSII fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for GCAN fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for GCAN fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for CLVT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for CLVT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[CLVT] Discovered 8-K filing trigger (SHORT): items ['1.01', '5.02'], move 12.55% on 2.64x avg volume
AUDIT LOG: [data_client] for LQDT fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for LQDT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for NWSA fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for NWSA fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for NWSA fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for RMCF fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for RMCF fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for VANI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for VANI fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[VANI] Discovered 8-K filing trigger (SHORT): items ['1.01', '8.01'], move 8.66% on 13.97x avg volume
AUDIT LOG: [data_client] for SEV fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for SEV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for OLPX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for OLPX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [data_client] for FXAC fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [data_client] for FXAC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.

Discovered 22 candidates in total. Routing to Hard-Gate Engine...
[KRUS] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] fetch_ofac_sdn -> SUCCESS: Successfully downloaded and parsed 9780 entity entries from OFAC SDN list.
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[KRUS] Gate 1 PASSED.
[KRUS] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[KRUS] Gate 2 PASSED.
[KRUS] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[KRUS] Gate 3 PASSED.
[KRUS] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR_10K.
[KRUS] Gate 4 PASSED.
[KRUS] Running Gate 5: Beneish M-Score...
AUDIT LOG: [data_client] for KRUS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [hardgate] for KRUS evaluate_gates -> REJECTED [GATE_BENEISH_NO_DATA]: Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.
[PENG] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[PENG] Gate 1 PASSED.
[PENG] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[PENG] Gate 2 PASSED.
[PENG] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[PENG] Gate 3 PASSED.
[PENG] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR_10K.
[PENG] Gate 4 PASSED.
[PENG] Running Gate 5: Beneish M-Score...
AUDIT LOG: [data_client] for PENG fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [hardgate] for PENG evaluate_gates -> REJECTED [GATE_BENEISH_NO_DATA]: Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.
[SAR] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for SAR fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[SAR] Gate 1 PASSED.
[SAR] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for SAR fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for SAR evaluate_gates -> REJECTED [GATE_LIQUIDITY_ADV]: Average daily dollar volume $1,874,047.48 is below $5,000,000 threshold.
[AREC] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for AREC fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[AREC] Gate 1 PASSED.
[AREC] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for AREC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for AREC evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $1.85 is below $5.00 floor.
[BTM] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for BTM fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[BTM] Gate 1 PASSED.
[BTM] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for BTM fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for BTM evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.11 is below $5.00 floor.
[CRMT] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for CRMT fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[CRMT] Gate 1 PASSED.
[CRMT] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for CRMT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for CRMT evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $2.98 is below $5.00 floor.
[ENLV] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for ENLV fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[ENLV] Gate 1 PASSED.
[ENLV] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for ENLV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for ENLV evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.49 is below $5.00 floor.
[HIRU] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for HIRU fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[HIRU] Gate 1 PASSED.
[HIRU] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for HIRU fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for HIRU evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.00 is below $5.00 floor.
[OLOX] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for OLOX fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[OLOX] Gate 1 PASSED.
[OLOX] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for OLOX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for OLOX evaluate_gates -> REJECTED [GATE_LIQUIDITY_ADV]: Average daily dollar volume $194,211.65 is below $5,000,000 threshold.
[SANW] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for SANW fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[SANW] Gate 1 PASSED.
[SANW] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for SANW fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for SANW evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.00 is below $5.00 floor.
[WTER] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for WTER fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[WTER] Gate 1 PASSED.
[WTER] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for WTER fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for WTER evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.04 is below $5.00 floor.
[EWSB] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for EWSB fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[EWSB] Gate 1 PASSED.
[EWSB] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for EWSB fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for EWSB evaluate_gates -> REJECTED [GATE_LIQUIDITY_ADV]: Average daily dollar volume $530.30 is below $5,000,000 threshold.
[CMPS] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[CMPS] Gate 1 PASSED.
[CMPS] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[CMPS] Gate 2 PASSED.
[CMPS] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[CMPS] Gate 3 PASSED.
[CMPS] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR_10K.
[CMPS] Gate 4 PASSED.
[CMPS] Running Gate 5: Beneish M-Score...
AUDIT LOG: [data_client] for CMPS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [hardgate] for CMPS evaluate_gates -> REJECTED [GATE_BENEISH_NO_DATA]: Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.
[ESI] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[ESI] Gate 1 PASSED.
[ESI] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[ESI] Gate 2 PASSED.
[ESI] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[ESI] Gate 3 PASSED.
[ESI] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR_10K.
[ESI] Gate 4 PASSED.
[ESI] Running Gate 5: Beneish M-Score...
AUDIT LOG: [data_client] for ESI fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [hardgate] for ESI evaluate_gates -> REJECTED [GATE_BENEISH_NO_DATA]: Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.
[SOLS] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[SOLS] Gate 1 PASSED.
[SOLS] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[SOLS] Gate 2 PASSED.
[SOLS] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[SOLS] Gate 3 PASSED.
[SOLS] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR_10K.
[SOLS] Gate 4 PASSED.
[SOLS] Running Gate 5: Beneish M-Score...
AUDIT LOG: [data_client] for SOLS fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
AUDIT LOG: [hardgate] for SOLS evaluate_gates -> REJECTED [GATE_BENEISH_NO_DATA]: Could not compute Beneish M-Score: Insufficient fiscal years in fundamentals.
[EVTV] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for EVTV fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[EVTV] Gate 1 PASSED.
[EVTV] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for EVTV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for EVTV evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $1.88 is below $5.00 floor.
[PIII] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for PIII fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[PIII] Gate 1 PASSED.
[PIII] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for PIII fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for PIII evaluate_gates -> REJECTED [GATE_LIQUIDITY_ADV]: Average daily dollar volume $521,504.56 is below $5,000,000 threshold.
[CRNX] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for CRNX fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[CRNX] Gate 1 PASSED.
[CRNX] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for CRNX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
[CRNX] Gate 2 PASSED.
[CRNX] Running Gate 3: Delinquent Filing Check...
AUDIT LOG: [data_client] for CRNX fetch_data -> SUCCESS: Attempted to fetch data from SEC_EDGAR.
[CRNX] Gate 3 PASSED.
[CRNX] Running Gate 4: Auditor Change & Adverse Opinion...
AUDIT LOG: [hardgate] for CRNX evaluate_gates -> REJECTED [GATE_AUDITOR_CHANGE]: Registrant certifying accountant change (Item 4.01) reported on 8-K on 2026-03-03.
[TOVX] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for TOVX fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[TOVX] Gate 1 PASSED.
[TOVX] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for TOVX fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for TOVX evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.23 is below $5.00 floor.
[BIAF] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for BIAF fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[BIAF] Gate 1 PASSED.
[BIAF] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for BIAF fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for BIAF evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.82 is below $5.00 floor.
[CLVT] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for CLVT fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[CLVT] Gate 1 PASSED.
[CLVT] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for CLVT fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for CLVT evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $2.43 is below $5.00 floor.
[VANI] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for VANI fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[VANI] Gate 1 PASSED.
[VANI] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for VANI fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for VANI evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $1.27 is below $5.00 floor.
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 22) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260707-160846
Trading Cycle completed successfully.
# Dashboard update workflow
Run python -m src.dashboard_builder
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
Static Dashboard compiled successfully inside docs/ directory.
