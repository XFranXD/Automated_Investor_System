# Warning on every trade workflow, dashboard workflow and learner workflow: 
Annotations
1 warning
run-trading-cycle
Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-python@v5. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners

# First run (trading_cycle.yml) logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260706-164346
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
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 46 earnings calendar entries from 2026-07-03 to 2026-07-06.
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
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
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
AUDIT LOG: [data_client] for GLMD fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[GLMD] Discovered earnings trigger (SHORT): surprise -53.79%
AUDIT LOG: [data_client] for SEGG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> FAILED [RECENT_8K_CIKS_FAILED]: Failed to fetch recent 8-K CIKs: name 're' is not defined
Error fetching SEC 8-K CIKs: name 're' is not defined

Discovered 9 candidates in total. Routing to Hard-Gate Engine...
[AREC] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] fetch_ofac_sdn -> SUCCESS: Successfully downloaded and parsed 9780 entity entries from OFAC SDN list.
AUDIT LOG: [data_client] for AREC fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[AREC] Gate 1 PASSED.
[AREC] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for AREC fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for AREC evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $1.94 is below $5.00 floor.
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
AUDIT LOG: [hardgate] for CRMT evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $2.86 is below $5.00 floor.
[ENLV] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for ENLV fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[ENLV] Gate 1 PASSED.
[ENLV] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for ENLV fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for ENLV evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.52 is below $5.00 floor.
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
AUDIT LOG: [hardgate] for OLOX evaluate_gates -> REJECTED [GATE_LIQUIDITY_ADV]: Average daily dollar volume $143,511.17 is below $5,000,000 threshold.
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
[GLMD] Running Gate 1: OFAC Sanctions...
AUDIT LOG: [data_client] for GLMD fetch_data -> SUCCESS: Attempted to fetch data from yfinance_name.
[GLMD] Gate 1 PASSED.
[GLMD] Running Gate 2: Liquidity Minimums...
AUDIT LOG: [data_client] for GLMD fetch_data -> SUCCESS: Attempted to fetch data from yfinance.
AUDIT LOG: [hardgate] for GLMD evaluate_gates -> REJECTED [GATE_LIQUIDITY_PRICE]: Share price $0.56 is below $5.00 floor.
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 9) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260706-164346
Trading Cycle completed successfully.

# Second run (trading_cycle.yml) logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
FTRS: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260706-175007
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
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 46 earnings calendar entries from 2026-07-03 to 2026-07-06.
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ADN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[AREC] Earnings trigger already evaluated today, skipping discovery.
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
[BTM] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[CRMT] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[ENLV] Earnings trigger already evaluated today, skipping discovery.
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
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[HIRU] Earnings trigger already evaluated today, skipping discovery.
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
AUDIT LOG: [data_client] for NVG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVVE fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[OLOX] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[SANW] Earnings trigger already evaluated today, skipping discovery.
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
[WTER] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[GLMD] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for SEGG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> FAILED [RECENT_8K_CIKS_FAILED]: Failed to fetch recent 8-K CIKs: name 're' is not defined
Error fetching SEC 8-K CIKs: name 're' is not defined

Discovered 0 candidates in total. Routing to Hard-Gate Engine...
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 0) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260706-175007
Trading Cycle completed successfully.

# Third run (trading_cycle.yml) logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
FTRS: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260706-183243
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
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 46 earnings calendar entries from 2026-07-03 to 2026-07-06.
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ADN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[AREC] Earnings trigger already evaluated today, skipping discovery.
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
[BTM] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[CRMT] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[ENLV] Earnings trigger already evaluated today, skipping discovery.
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
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[HIRU] Earnings trigger already evaluated today, skipping discovery.
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
AUDIT LOG: [data_client] for NVG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVVE fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[OLOX] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[SANW] Earnings trigger already evaluated today, skipping discovery.
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
[WTER] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[GLMD] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for SEGG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> FAILED [RECENT_8K_CIKS_FAILED]: Failed to fetch recent 8-K CIKs: name 're' is not defined
Error fetching SEC 8-K CIKs: name 're' is not defined

Discovered 0 candidates in total. Routing to Hard-Gate Engine...
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 0) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260706-183243
Trading Cycle completed successfully.


# Fourth run (trading_cycle.yml) logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
FTRS: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260706-201601
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
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 46 earnings calendar entries from 2026-07-03 to 2026-07-06.
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ADN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[AREC] Earnings trigger already evaluated today, skipping discovery.
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
[BTM] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[CRMT] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[ENLV] Earnings trigger already evaluated today, skipping discovery.
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
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[HIRU] Earnings trigger already evaluated today, skipping discovery.
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
AUDIT LOG: [data_client] for NVG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVVE fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[OLOX] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[SANW] Earnings trigger already evaluated today, skipping discovery.
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
[WTER] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[GLMD] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for SEGG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> FAILED [RECENT_8K_CIKS_FAILED]: Failed to fetch recent 8-K CIKs: HTTPSConnectionPool(host='www.sec.gov', port=443): Read timed out. (read timeout=10)
Error fetching SEC 8-K CIKs: HTTPSConnectionPool(host='www.sec.gov', port=443): Read timed out. (read timeout=10)

Discovered 0 candidates in total. Routing to Hard-Gate Engine...
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 0) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260706-201601
Trading Cycle completed successfully.
# Fifth run (trading_cycle.yml) logs
Run python trading_cycle_placeholder.py
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
ACP: No earnings dates found, symbol may be delisted
AOD: No earnings dates found, symbol may be delisted
ASII: No earnings dates found, symbol may be delisted
AUSI: No earnings dates found, symbol may be delisted
CET: No earnings dates found, symbol may be delisted
CRCW: No earnings dates found, symbol may be delisted
CYBL: No earnings dates found, symbol may be delisted
DMNIF: No earnings dates found, symbol may be delisted
FAX: No earnings dates found, symbol may be delisted
FCO: No earnings dates found, symbol may be delisted
FTII: No earnings dates found, symbol may be delisted
FTRS: No earnings dates found, symbol may be delisted
Starting Trading Cycle...
Database connection verified successfully via ping.
Collection 'candidates' already exists.
Collection 'evaluations' already exists.
Collection 'trades' already exists.
Collection 'portfolio_state' already exists.
Collection 'stats_aggregates' already exists.
Collection 'audit_log' already exists.
Database initialization complete.
Trading Cycle Run ID: run-20260706-211421
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
AUDIT LOG: [data_client] get_earnings_calendar -> SUCCESS: Successfully fetched 46 earnings calendar entries from 2026-07-03 to 2026-07-06.
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for ACP get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for ADN fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for AOD get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[AREC] Earnings trigger already evaluated today, skipping discovery.
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
[BTM] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CDT get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CET get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CRCW get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[CRMT] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for CYBL get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for DMNIF get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[ENLV] Earnings trigger already evaluated today, skipping discovery.
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
OWPC: No earnings dates found, symbol may be delisted
SNRG: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
SRKE: No earnings dates found, symbol may be delisted
XITO: No earnings dates found, symbol may be delisted
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for HBSI get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[HIRU] Earnings trigger already evaluated today, skipping discovery.
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
AUDIT LOG: [data_client] for NVG get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
AUDIT LOG: [data_client] for NVVE fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.
[OLOX] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for OWPC get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[SANW] Earnings trigger already evaluated today, skipping discovery.
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
[WTER] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for XITO get_earnings -> FAILED [EARNINGS_NO_DATA]: All earnings surprise sources in waterfall failed or returned no data.
[GLMD] Earnings trigger already evaluated today, skipping discovery.
AUDIT LOG: [data_client] for SEGG fetch_data -> SUCCESS: Attempted to fetch data from Finnhub.

Scanning SEC 8-K filings...
AUDIT LOG: [data_client] get_recent_8k_ciks -> FAILED [RECENT_8K_CIKS_FAILED]: Failed to fetch recent 8-K CIKs: name 're' is not defined
Error fetching SEC 8-K CIKs: name 're' is not defined

Discovered 0 candidates in total. Routing to Hard-Gate Engine...
=== CANDIDATE DISCOVERY COMPLETED (Evaluated: 0) ===
Discovered 0 passed candidates.
AUDIT LOG: [orchestrator] trading_cycle_run -> PASSED: Successfully completed Trading Cycle orchestration. Run ID: run-20260706-211421
Trading Cycle completed successfully.

# Second run (dashboard.yml) logs (first was the error you solved)
Run python -m src.dashboard_builder
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
Static Dashboard compiled successfully inside docs/ directory.


# Third run (dashboard.yml) logs
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
Static Dashboard compiled successfully inside docs/ directory.

# Fourth run (dashboard.yml) logs
Run python -m src.dashboard_builder
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
Static Dashboard compiled successfully inside docs/ directory.

# Fifth run (dashboard.yml) logs
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: T_DASH_3"}}}
$T_DASH_3: possibly delisted; no price data found  (period=2mo) (Yahoo error = "No data found, symbol may be delisted")
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from yfinance. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 fetch_data -> FAILED: Attempted to fetch data from Finnhub. Context: Returned empty data structure
AUDIT LOG: [data_client] for T_DASH_3 get_price_volume -> FAILED [PRICE_VOLUME_NO_DATA]: All price/volume sources in waterfall failed or returned no data.
Static Dashboard compiled successfully inside docs/ directory.


