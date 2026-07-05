import os
import json
import datetime
from bson import ObjectId
from src.db import get_db
from src.data_client import get_price_volume, get_company_sector
from src.learning_aggregator import get_derived_metrics

# Helper to serialize ObjectId and datetimes in inline data
class DashboardJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

def generate_dashboard():
    db = get_db()
    
    # 1. Fetch data from MongoDB
    trades = list(db.trades.find().sort("entry_timestamp", -1))
    portfolio_state = db.portfolio_state.find_one({"_id": "current_state"})
    if not portfolio_state:
        portfolio_state = {
            "equity": 100000.0,
            "cash": 100000.0,
            "kill_switch_active": False,
            "correlation_cap_current": 0.6,
            "open_positions": [],
            "drawdown_pct": 0.0,
            "high_water_mark": 100000.0,
            "sector_exposure": {},
            "correlation_snapshot": {}
        }
        
    candidates = list(db.candidates.find().sort("timestamp", -1))
    evaluations = list(db.evaluations.find())
    stats_aggregates = list(db.stats_aggregates.find())
    
    # 2. Summary stats calculations
    total_pnl = 0.0
    wins = 0
    losses = 0
    closed_count = 0
    open_count = 0
    
    for t in trades:
        if t.get("status") == "CLOSED":
            pnl = float(t.get("realized_pnl", 0.0))
            total_pnl += pnl
            closed_count += 1
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
        else:
            open_count += 1
            
    win_rate = (wins / closed_count * 100.0) if closed_count > 0 else 0.0
    
    # Reconstruct Equity Curve Points from closed trades
    closed_trades_chronological = sorted(
        [t for t in trades if t.get("status") == "CLOSED"], 
        key=lambda x: x.get("exit_timestamp") or datetime.datetime.min
    )
    
    equity_curve = []
    current_equity = 100000.0
    current_hwm = 100000.0
    
    # Starting point
    equity_curve.append({
        "date": "Initial",
        "equity": current_equity,
        "hwm": current_hwm,
        "drawdown": 0.0
    })
    
    for t in closed_trades_chronological:
        pnl = float(t.get("realized_pnl", 0.0))
        current_equity += pnl
        current_hwm = max(current_hwm, current_equity)
        dd = ((current_hwm - current_equity) / current_hwm * 100.0) if current_hwm > 0 else 0.0
        
        exit_ts = t.get("exit_timestamp")
        date_str = exit_ts.strftime("%Y-%m-%d %H:%M") if exit_ts else "Unknown"
        equity_curve.append({
            "date": date_str,
            "equity": current_equity,
            "hwm": current_hwm,
            "drawdown": dd
        })
        
    # 3. Calendar Data Mapping (group daily closed realized PnL)
    calendar_pnl = {}
    for t in trades:
        if t.get("status") == "CLOSED" and t.get("exit_timestamp"):
            exit_date = t["exit_timestamp"].date().isoformat()
            pnl = float(t.get("realized_pnl", 0.0))
            calendar_pnl[exit_date] = calendar_pnl.get(exit_date, 0.0) + pnl
            
    # 4. Rejection breakdown grouping
    rejections = {}
    for cand in candidates:
        if cand.get("gate_result") == "REJECTED":
            details = cand.get("gate_details", {})
            for gate, passed in details.items():
                if not passed:
                    code = f"REJECTED_{gate.upper()}"
                    rejections[code] = rejections.get(code, 0) + 1
        elif cand.get("final_outcome") == "ABSTAIN":
            reason = cand.get("abstain_reason_code")
            if reason:
                rejections[reason] = rejections.get(reason, 0) + 1
                
    # 5. Load current market indices from candidates/history
    # Let's inspect latest candidate details or default context
    latest_vix = 18.5
    latest_spy_rel = "+1.2%"
    if candidates:
        # Check if we can find VIX / SPY relative from audit log or regime state
        pass
    correlation_cap = portfolio_state.get("correlation_cap_current", 0.6)
    regime = "RISK_OFF" if correlation_cap == 0.4 else "RISK_ON"
    
    # Ensure docs/ directory exists
    os.makedirs("docs", exist_ok=True)
    
    # 6. Generate Styles CSS
    css_content = """
:root {
    --bg-dark: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.7);
    --border-color: rgba(255, 255, 255, 0.05);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-emerald: #10b981;
    --accent-rose: #f43f5e;
    --accent-indigo: #6366f1;
    --font-family: 'Outfit', 'Inter', sans-serif;
}

body {
    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: var(--font-family);
    margin: 0;
    padding: 0;
}

header {
    background: rgba(15, 23, 42, 0.9);
    border-bottom: 1px solid var(--border-color);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
}

header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

nav {
    display: flex;
    gap: 20px;
}

nav a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 15px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 8px;
    transition: all 0.2s ease;
}

nav a:hover, nav a.active {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
}

.container {
    max-width: 1400px;
    margin: 40px auto;
    padding: 0 20px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

.card-title {
    color: var(--text-secondary);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.card-val {
    font-size: 32px;
    font-weight: 700;
}

.val-green { color: var(--accent-emerald); }
.val-rose { color: var(--accent-rose); }
.val-indigo { color: var(--accent-indigo); }

.grid-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
    margin-bottom: 40px;
}

@media(max-width: 1024px) {
    .grid-layout {
        grid-template-columns: 1fr;
    }
}

/* Calendar styling */
.calendar-container {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-top: 15px;
}

.calendar-header {
    text-align: center;
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 600;
    padding: 8px 0;
}

.calendar-day {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    aspect-ratio: 1.2;
    padding: 8px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.2s ease;
}

.calendar-day:hover {
    background: rgba(255, 255, 255, 0.05);
}

.calendar-day.empty {
    opacity: 0.2;
    cursor: default;
}

.calendar-day-num {
    font-size: 12px;
    color: var(--text-secondary);
}

.calendar-day-pnl {
    font-size: 12px;
    font-weight: 600;
    text-align: right;
}

/* Table styling */
.table-container {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow-x: auto;
    backdrop-filter: blur(12px);
}

table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

th {
    background: rgba(15, 23, 42, 0.4);
    border-bottom: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 600;
    padding: 16px;
}

td {
    border-bottom: 1px solid var(--border-color);
    padding: 16px;
    font-size: 14px;
}

tr:hover {
    background: rgba(255, 255, 255, 0.01);
    cursor: pointer;
}

.badge {
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-open {
    background: rgba(99, 102, 241, 0.15);
    color: var(--accent-indigo);
}

.badge-closed {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
}

/* Modal styling */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(8px);
    z-index: 1000;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    max-width: 800px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    padding: 30px;
    position: relative;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.close-btn {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 24px;
    cursor: pointer;
    color: var(--text-secondary);
}

.close-btn:hover {
    color: var(--text-primary);
}

.flex-row {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 25px;
}

.meta-item {
    min-width: 120px;
}

.meta-label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
}

.meta-val {
    font-size: 16px;
    font-weight: 600;
    margin-top: 4px;
}
"""
    with open("docs/styles.css", "w") as f:
        f.write(css_content)

    # 7. Generate index.html (Trades Page)
    # Re-evaluate all open positions for current P&L
    trades_data = []
    for t in trades:
        t_copy = t.copy()
        if t_copy.get("status") == "OPEN":
            # For open positions, get current price and calculate unrealized P&L
            # For simplicity in static compilation, we use current_price
            ticker = t_copy["ticker"]
            direction = t_copy["direction"]
            entry = float(t_copy["entry_price"])
            shares = int(t_copy["share_count"])
            
            pv = get_price_volume(ticker)
            curr = pv["data"]["current_price"] if (pv and pv.get("data")) else entry
            
            if direction == "LONG":
                unrealized = shares * (curr - entry)
            else:
                unrealized = shares * (entry - curr)
            t_copy["realized_pnl"] = unrealized
            t_copy["exit_price"] = curr
        
        # Resolve associated evaluation details
        eval_doc = next((ev for ev in evaluations if str(ev.get("candidate_id")) == str(t_copy.get("reasoning_chain", {}).get("candidate_id"))), None)
        if eval_doc:
            t_copy["ai_conviction"] = eval_doc.get("conviction")
            t_copy["ai_rationale"] = eval_doc.get("rationale")
            t_copy["ai_risk_flags"] = eval_doc.get("risk_flags", [])
            
        trades_data.append(t_copy)

    # Compile calendar days
    calendar_days_html = ""
    # Render calendar for current month (e.g. July 2026)
    # July 2026 starts on a Wednesday (index 3 if Monday=0 or index 2)
    # We will generate 31 days
    for blank in range(3): # Wednesday start
        calendar_days_html += '<div class="calendar-day empty"></div>'
    for day in range(1, 32):
        date_str = f"2026-07-{day:02d}"
        pnl = calendar_pnl.get(date_str, 0.0)
        pnl_class = "val-green" if pnl > 0 else ("val-rose" if pnl < 0 else "")
        pnl_text = f"${pnl:+.2f}" if pnl != 0 else ""
        
        calendar_days_html += f"""
        <div class="calendar-day" onclick="filterDate('{date_str}')">
            <div class="calendar-day-num">{day}</div>
            <div class="calendar-day-pnl {pnl_class}">{pnl_text}</div>
        </div>
        """

    # Compile trades list HTML rows
    table_rows_html = ""
    for t in trades_data:
        pnl = float(t.get("realized_pnl", 0.0))
        pnl_class = "val-green" if pnl > 0 else ("val-rose" if pnl < 0 else "")
        status_badge = f'<span class="badge badge-open">Open</span>' if t["status"] == "OPEN" else f'<span class="badge badge-closed">Closed</span>'
        
        exit_date_str = "OPEN"
        if t["status"] == "CLOSED" and t.get("exit_timestamp"):
            exit_date_str = t["exit_timestamp"].strftime("%Y-%m-%d %H:%M")
            
        close_date_iso = t["exit_timestamp"].date().isoformat() if (t["status"] == "CLOSED" and t.get("exit_timestamp")) else ""
            
        table_rows_html += f"""
        <tr data-close-date="{close_date_iso}" onclick='showTradeDetail({json.dumps(t, cls=DashboardJSONEncoder)})'>
            <td><strong>{t['ticker']}</strong></td>
            <td class="{ "val-green" if t['direction'] == "LONG" else "val-rose" }">{t['direction']}</td>
            <td>{t['entry_timestamp'].strftime("%Y-%m-%d %H:%M")}</td>
            <td>{exit_date_str}</td>
            <td>${t['entry_price']:.2f}</td>
            <td>${t.get('exit_price', 0.0):.2f} if t.get('exit_price') else '-'</td>
            <td>{t['share_count']}</td>
            <td class="{pnl_class}">${pnl:+.2f}</td>
            <td>{status_badge}</td>
        </tr>
        """

    index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TBE — Trades Dashboard</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1>TBE — Autonomous Investment Dashboard</h1>
        <nav>
            <a href="index.html" class="active">Trades Log</a>
            <a href="system.html">System State</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="summary-grid">
            <div class="card">
                <div class="card-title">Total Realized P&L</div>
                <div class="card-val { "val-green" if total_pnl > 0 else "val-rose" }">${total_pnl:+.2f}</div>
            </div>
            <div class="card">
                <div class="card-title">Overall Win Rate</div>
                <div class="card-val val-indigo">{win_rate:.1f}%</div>
            </div>
            <div class="card">
                <div class="card-title">Closed Positions</div>
                <div class="card-val">{closed_count}</div>
            </div>
            <div class="card">
                <div class="card-title">Open Positions</div>
                <div class="card-val val-green">{open_count}</div>
            </div>
        </div>

        <div class="grid-layout">
            <div class="card">
                <div class="card-title" style="display:flex; justify-content:space-between; align-items:center;">
                    <span>July 2026 P&L Calendar</span>
                    <button onclick="filterDate('')" style="background:rgba(255,255,255,0.05); color:var(--text-primary); border:1px solid var(--border-color); padding:4px 8px; border-radius:4px; cursor:pointer; font-size:12px;">Show All</button>
                </div>
                <div class="calendar-container">
                    <div class="calendar-header">Mon</div>
                    <div class="calendar-header">Tue</div>
                    <div class="calendar-header">Wed</div>
                    <div class="calendar-header">Thu</div>
                    <div class="calendar-header">Fri</div>
                    <div class="calendar-header">Sat</div>
                    <div class="calendar-header">Sun</div>
                    {calendar_days_html}
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Market Context</div>
                <div class="meta-item" style="margin-bottom:20px;">
                    <div class="meta-label">VIX Level</div>
                    <div class="meta-val { "val-rose" if latest_vix > 30 else "val-green" }">{latest_vix} (Elevated: > 30)</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">SPY Relative to 50 SMA</div>
                    <div class="meta-val val-green">{latest_spy_rel} Above SMA</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Position Ledger</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Direction</th>
                            <th>Entry Timestamp</th>
                            <th>Exit Timestamp</th>
                            <th>Entry Price</th>
                            <th>Exit Price</th>
                            <th>Shares</th>
                            <th>Realized P&L</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="trades-table-body">
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Trade Detail Modal -->
    <div id="detail-modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <span class="close-btn" onclick="document.getElementById('detail-modal').style.display = 'none'">&times;</span>
            <h2 id="modal-ticker" style="margin-top:0;">AAPL - LONG</h2>
            
            <h3 style="border-bottom:1px solid var(--border-color); padding-bottom:8px; color:var(--text-secondary);">Execution Details</h3>
            <div class="flex-row">
                <div class="meta-item">
                    <div class="meta-label">Shares</div>
                    <div id="modal-shares" class="meta-val">0</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Entry Price</div>
                    <div id="modal-entry-price" class="meta-val">$0.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Exit Price</div>
                    <div id="modal-exit-price" class="meta-val">$0.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Realized PnL</div>
                    <div id="modal-pnl" class="meta-val">$0.00</div>
                </div>
            </div>
            
            <div class="flex-row">
                <div class="meta-item">
                    <div class="meta-label">Initial Stop</div>
                    <div id="modal-init-stop" class="meta-val">$0.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Current Stop</div>
                    <div id="modal-curr-stop" class="meta-val">$0.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Take Profit</div>
                    <div id="modal-tp" class="meta-val">$0.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Risk Allocated</div>
                    <div id="modal-risk" class="meta-val">0.00%</div>
                </div>
            </div>

            <h3 style="border-bottom:1px solid var(--border-color); padding-bottom:8px; color:var(--text-secondary);">Reasoning Chain</h3>
            <div class="flex-row">
                <div class="meta-item">
                    <div class="meta-label">Trigger Type</div>
                    <div id="modal-trigger-type" class="meta-val">PEAD</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Decision Score</div>
                    <div id="modal-score" class="meta-val">2.00</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Confidence Tier</div>
                    <div id="modal-tier" class="meta-val">STRONG</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">AI Conviction</div>
                    <div id="modal-ai-conv" class="meta-val">STRONG_SUPPORT</div>
                </div>
            </div>

            <div style="margin-bottom:20px;">
                <div class="meta-label">AI Rationale</div>
                <div id="modal-ai-rationale" class="meta-val" style="font-weight:400; font-size:14px; margin-top:8px;"></div>
            </div>
            
            <div>
                <div class="meta-label">Risk Flags Identified</div>
                <div id="modal-risk-flags" class="meta-val" style="font-weight:400; font-size:14px; margin-top:8px;"></div>
            </div>
        </div>
    </div>

    <script>
        function filterDate(dateStr) {{
            const rows = document.querySelectorAll("#trades-table-body tr");
            rows.forEach(r => {{
                if (!dateStr || r.getAttribute("data-close-date") === dateStr) {{
                    r.style.display = "";
                }} else {{
                    r.style.display = "none";
                }}
            }});
        }}

        function showTradeDetail(t) {{
            document.getElementById("modal-ticker").innerText = t.ticker + " - " + t.direction;
            document.getElementById("modal-shares").innerText = t.share_count;
            document.getElementById("modal-entry-price").innerText = "$" + parseFloat(t.entry_price).toFixed(2);
            document.getElementById("modal-exit-price").innerText = t.exit_price ? "$" + parseFloat(t.exit_price).toFixed(2) : "-";
            
            const pnl = parseFloat(t.realized_pnl || 0.0);
            const pnlEl = document.getElementById("modal-pnl");
            pnlEl.innerText = (pnl >= 0 ? "+" : "") + "$" + pnl.toFixed(2);
            pnlEl.className = "meta-val " + (pnl >= 0 ? "val-green" : "val-rose");
            
            document.getElementById("modal-init-stop").innerText = "$" + parseFloat(t.initial_stop).toFixed(2);
            document.getElementById("modal-curr-stop").innerText = "$" + parseFloat(t.current_stop).toFixed(2);
            document.getElementById("modal-tp").innerText = "$" + parseFloat(t.take_profit).toFixed(2);
            document.getElementById("modal-risk").innerText = parseFloat(t.risk_pct_used).toFixed(2) + "%";
            
            document.getElementById("modal-trigger-type").innerText = t.reasoning_chain.trigger_type || "EARNINGS_SURPRISE";
            document.getElementById("modal-score").innerText = parseFloat(t.combined_score).toFixed(2);
            document.getElementById("modal-tier").innerText = t.confidence_tier || "STRONG";
            document.getElementById("modal-ai-conv").innerText = t.ai_conviction || "ABSTAIN/UNKNOWN";
            document.getElementById("modal-ai-rationale").innerText = t.ai_rationale || "No AI rationale details available.";
            
            const flags = t.ai_risk_flags || [];
            document.getElementById("modal-risk-flags").innerText = flags.length > 0 ? flags.join(", ") : "No specific risk flags identified.";
            
            document.getElementById("detail-modal").style.display = "flex";
        }}

        function closeModal(e) {{
            if (e.target.id === "detail-modal") {{
                document.getElementById("detail-modal").style.display = "none";
            }}
        }}
    </script>
</body>
</html>
"""
    with open("docs/index.html", "w") as f:
        f.write(index_html)

    # 8. Generate system.html (System Page)
    # Render aggregate rejections list
    rejections_html = ""
    if rejections:
        for code, count in rejections.items():
            rejections_html += f"""
            <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid var(--border-color);">
                <span>{code}</span>
                <span style="font-weight:600;">{count}</span>
            </div>
            """
    else:
        rejections_html = '<div style="color:var(--text-secondary);">No rejections logged in the select window.</div>'

    # Sector Snapshot list
    sector_html = ""
    for sec, pct in portfolio_state.get("sector_exposure", {}).items():
        sector_html += f"""
        <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid var(--border-color);">
            <span>{sec}</span>
            <span style="font-weight:600;">{pct:.1f}%</span>
        </div>
        """
    if not sector_html:
        sector_html = '<div style="color:var(--text-secondary);">No active sector exposure.</div>'

    # Learning stats tables
    stats_rows_html = ""
    for agg in stats_aggregates:
        dim = agg["_id"]["dimension"]
        val = agg["_id"]["value"]
        
        metrics = get_derived_metrics(agg)
        
        stats_rows_html += f"""
        <tr>
            <td><strong>{dim.upper()}</strong></td>
            <td>{val}</td>
            <td>{agg['tradeCount']}</td>
            <td>{metrics['win_rate']*100:.1f}%</td>
            <td>${metrics['avg_return']:+.2f}</td>
            <td>{metrics['profit_factor']:.2f}</td>
            <td class="val-green">${agg.get('maxWin', 0.0):.2f}</td>
            <td class="val-rose">${agg.get('maxLoss', 0.0):.2f}</td>
        </tr>
        """

    # Drawdown switch details
    is_kill = portfolio_state.get("kill_switch_active", False)
    kill_switch_html = ""
    if is_kill:
        kill_switch_html = f"""
        <div style="background:rgba(244,63,94,0.1); border:1px solid var(--accent-rose); border-radius:8px; padding:15px; margin-top:15px;">
            <strong style="color:var(--accent-rose);">Circuit Breaker ACTIVE</strong>
            <p style="margin:5px 0 0 0; font-size:14px; color:var(--text-secondary);">
                Active Drawdown: {portfolio_state.get('drawdown_pct', 0.0):.2f}% (Threshold: 14.0%).
            </p>
        </div>
        """
    else:
        kill_switch_html = """
        <div style="background:rgba(16,185,129,0.1); border:1px solid var(--accent-emerald); border-radius:8px; padding:15px; margin-top:15px;">
            <strong style="color:var(--accent-emerald);">All Systems Nominal</strong>
            <p style="margin:5px 0 0 0; font-size:14px; color:var(--text-secondary);">
                Global kill switch is currently INACTIVE. New positions permitted.
            </p>
        </div>
        """

    # Charts configuration: Equity Curve data points
    equity_labels = [p["date"] for p in equity_curve]
    equity_vals = [p["equity"] for p in equity_curve]
    hwm_vals = [p["hwm"] for p in equity_curve]

    system_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TBE — System Health</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <h1>TBE — Autonomous Investment Dashboard</h1>
        <nav>
            <a href="index.html">Trades Log</a>
            <a href="system.html" class="active">System State</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="grid-layout">
            <div>
                <div class="card" style="margin-bottom:30px;">
                    <div class="card-title">Equity Curve & High-Water Mark</div>
                    <div style="height: 350px; position: relative;">
                        <canvas id="equityChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-title">Learning Aggregator Statistics</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Dimension</th>
                                    <th>Value</th>
                                    <th>Trades</th>
                                    <th>Win Rate</th>
                                    <th>Avg Return</th>
                                    <th>Profit Factor</th>
                                    <th>Max Win</th>
                                    <th>Max Loss</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats_rows_html if stats_rows_html else '<tr><td colspan="8" style="text-align:center;">No aggregate stats compiled yet.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div>
                <div class="card" style="margin-bottom:30px;">
                    <div class="card-title">Global Risk Circuit Breaker</div>
                    {kill_switch_html}
                </div>
                
                <div class="card" style="margin-bottom:30px;">
                    <div class="card-title">Regime and Correlation Rules</div>
                    <div class="meta-item" style="margin-bottom:20px; border-bottom:1px solid var(--border-color); padding-bottom:10px;">
                        <div class="meta-label">Regime State</div>
                        <div class="meta-val val-indigo">{regime}</div>
                    </div>
                    <div class="meta-item" style="margin-bottom:20px; border-bottom:1px solid var(--border-color); padding-bottom:10px;">
                        <div class="meta-label">Active Correlation Cap</div>
                        <div class="meta-val">{portfolio_state.get('correlation_cap_current', 0.6)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">High Water Mark</div>
                        <div class="meta-val">${hwm_vals[-1] if hwm_vals else 100000.0:,.2f}</div>
                    </div>
                </div>

                <div class="card" style="margin-bottom:30px;">
                    <div class="card-title">Sector Exposure Snapshots</div>
                    {sector_html}
                </div>

                <div class="card">
                    <div class="card-title">Rejection / Abstain Reasons</div>
                    {rejections_html}
                </div>
            </div>
        </div>
    </div>

    <script>
        // Setup Chart.js Equity Curve
        const ctx = document.getElementById('equityChart').getContext('2d');
        const chartData = {{
            labels: {json.dumps(equity_labels)},
            datasets: [
                {{
                    label: 'Portfolio Equity',
                    data: {json.dumps(equity_vals)},
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    fill: true,
                    tension: 0.1
                }},
                {{
                    label: 'High Water Mark',
                    data: {json.dumps(hwm_vals)},
                    borderColor: '#6366f1',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.1
                }}
            ]
        }};
        
        new Chart(ctx, {{
            type: 'line',
            data: chartData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255,255,255,0.02)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255,255,255,0.02)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: '#f8fafc' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open("docs/system.html", "w") as f:
        f.write(system_html)

    print("Static Dashboard compiled successfully inside docs/ directory.")

if __name__ == "__main__":
    generate_dashboard()
