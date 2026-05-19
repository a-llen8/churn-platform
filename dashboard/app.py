import streamlit as st
import duckdb
import json

st.set_page_config(
    page_title="Churn Prevention Dashboard",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] { background: #0d1117; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    con = duckdb.connect('duckdb/churn_airflow.db')
    df = con.execute("SELECT * FROM churn_features").df()
    con.close()
    return df


df = load_data()

records = df[[
    'customer_id', 'is_high_risk',
    'avg_monthly_charges', 'avg_tenure_months',
    'avg_support_tickets', 'churn_rate'
]].to_dict(orient='records')

data_json = json.dumps(records)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e2e8f0; font-size: 13px; }}

.topbar {{ display: flex; align-items: center; justify-content: space-between; padding: 13px 24px; background: #0a0e16; border-bottom: 1px solid #1e2a3a; }}
.logo {{ font-size: 15px; font-weight: 700; color: #e2e8f0; }}
.logo span {{ color: #00d4ff; }}
.badge-live {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 600; background: rgba(0,212,255,0.12); color: #00d4ff; }}
.pulse {{ width: 7px; height: 7px; border-radius: 50%; background: #00d4ff; animation: blink 1.5s infinite; flex-shrink: 0; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.2}} }}

.content {{ padding: 20px 24px; }}

.kpi-row {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }}
.kpi {{ background: #111827; border: 1px solid #1e2a3a; border-radius: 8px; padding: 16px 18px; position: relative; overflow: hidden; }}
.kpi::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px; }}
.kpi.cyan::before    {{ background: #00d4ff; }}
.kpi.magenta::before {{ background: #e040fb; }}
.kpi.green::before   {{ background: #00e676; }}
.kpi.amber::before   {{ background: #ffd740; }}
.kpi-label {{ font-size: 10px; letter-spacing: 0.08em; color: #4a5568; text-transform: uppercase; margin-bottom: 8px; }}
.kpi-value {{ font-size: 26px; font-weight: 700; color: #e2e8f0; font-variant-numeric: tabular-nums; }}
.kpi-delta {{ font-size: 11px; margin-top: 5px; }}

.charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }}
.card {{ background: #111827; border: 1px solid #1e2a3a; border-radius: 8px; padding: 16px 18px; margin-bottom: 20px; }}
.card-title {{ font-size: 12px; font-weight: 600; color: #a0aec0; margin-bottom: 12px; letter-spacing: 0.03em; display: flex; align-items: center; gap: 7px; }}
.legend-row {{ display: flex; gap: 14px; margin-bottom: 10px; }}
.leg {{ display: flex; align-items: center; gap: 5px; font-size: 11px; color: #718096; }}
.leg-dot {{ width: 9px; height: 9px; border-radius: 2px; }}

table {{ width: 100%; border-collapse: collapse; }}
th {{ text-align: left; font-size: 10px; letter-spacing: 0.08em; color: #4a5568; text-transform: uppercase; padding: 7px 10px; border-bottom: 1px solid #1e2a3a; }}
td {{ padding: 9px 10px; font-size: 12px; color: #a0aec0; border-bottom: 1px solid rgba(30,42,58,0.4); font-variant-numeric: tabular-nums; }}
tr:hover td {{ background: rgba(0,212,255,0.03); }}
.risk-badge {{ display: inline-flex; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; background: rgba(224,64,251,0.15); color: #e040fb; }}

.predict-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 18px; }}
.slider-group {{ display: flex; flex-direction: column; gap: 7px; }}
.slider-label {{ display: flex; justify-content: space-between; font-size: 11px; color: #718096; }}
.slider-label span {{ color: #00d4ff; font-weight: 700; }}
input[type=range] {{ width: 100%; accent-color: #00d4ff; cursor: pointer; }}

.predict-btn {{ display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px; background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.35); color: #00d4ff; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; letter-spacing: 0.05em; font-family: 'Segoe UI', sans-serif; transition: background 0.15s; }}
.predict-btn:hover {{ background: rgba(0,212,255,0.2); }}
.predict-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

.result-box {{ padding: 12px 16px; border-radius: 6px; font-size: 12px; margin-top: 14px; display: none; line-height: 1.7; }}
.result-high {{ background: rgba(224,64,251,0.1); border: 1px solid rgba(224,64,251,0.3); color: #e040fb; }}
.result-low  {{ background: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3); color: #00e676; }}
.result-err  {{ background: rgba(255,100,100,0.08); border: 1px solid rgba(255,100,100,0.25); color: #fc8181; padding: 12px 16px; border-radius: 6px; font-size: 11px; margin-top: 14px; display: none; }}
.spinner {{ display: none; width: 14px; height: 14px; border: 2px solid rgba(0,212,255,0.3); border-top-color: #00d4ff; border-radius: 50%; animation: spin 0.7s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-thumb {{ background: #1e2a3a; border-radius: 4px; }}
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">Churn<span>Guard</span> &nbsp;<span style="font-size:11px;font-weight:400;color:#4a5568">Customer Churn Prevention Platform</span></div>
  <div class="badge-live"><div class="pulse"></div> Live</div>
</div>

<div class="content">

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi cyan">
      <div class="kpi-label">Total Customers</div>
      <div class="kpi-value" id="kpi-total">—</div>
      <div class="kpi-delta" style="color:#4a5568">All segments</div>
    </div>
    <div class="kpi magenta">
      <div class="kpi-label">High Risk</div>
      <div class="kpi-value" id="kpi-high">—</div>
      <div class="kpi-delta" style="color:#e040fb" id="kpi-high-pct">—</div>
    </div>
    <div class="kpi green">
      <div class="kpi-label">Low Risk</div>
      <div class="kpi-value" id="kpi-low">—</div>
      <div class="kpi-delta" style="color:#00e676">Stable retention</div>
    </div>
    <div class="kpi amber">
      <div class="kpi-label">Avg Monthly Charges</div>
      <div class="kpi-value" id="kpi-charges">—</div>
      <div class="kpi-delta" style="color:#4a5568">Per customer</div>
    </div>
  </div>

  <!-- Charts row 1 -->
  <div class="charts-row">
    <div class="card" style="margin-bottom:0">
      <div class="card-title">Churn Risk Distribution</div>
      <div class="legend-row">
        <div class="leg"><div class="leg-dot" style="background:#e040fb"></div> High Risk</div>
        <div class="leg"><div class="leg-dot" style="background:#00d4ff"></div> Low Risk</div>
      </div>
      <div style="position:relative;width:100%;height:240px;">
        <canvas id="pieChart"></canvas>
      </div>
    </div>
    <div class="card" style="margin-bottom:0">
      <div class="card-title">Monthly Charges vs Churn Rate</div>
      <div class="legend-row">
        <div class="leg"><div class="leg-dot" style="background:#e040fb"></div> High Risk</div>
        <div class="leg"><div class="leg-dot" style="background:#00d4ff"></div> Low Risk</div>
      </div>
      <div style="position:relative;width:100%;height:240px;">
        <canvas id="scatterChart"></canvas>
      </div>
    </div>
  </div>

  <!-- Charts row 2 -->
  <div class="charts-row">
    <div class="card" style="margin-bottom:0">
      <div class="card-title">Avg Tenure by Risk Level</div>
      <div class="legend-row">
        <div class="leg"><div class="leg-dot" style="background:#e040fb"></div> High Risk</div>
        <div class="leg"><div class="leg-dot" style="background:#00d4ff"></div> Low Risk</div>
      </div>
      <div style="position:relative;width:100%;height:220px;">
        <canvas id="tenureChart"></canvas>
      </div>
    </div>
    <div class="card" style="margin-bottom:0">
      <div class="card-title">Avg Support Tickets by Risk Level</div>
      <div class="legend-row">
        <div class="leg"><div class="leg-dot" style="background:#e040fb"></div> High Risk</div>
        <div class="leg"><div class="leg-dot" style="background:#00d4ff"></div> Low Risk</div>
      </div>
      <div style="position:relative;width:100%;height:220px;">
        <canvas id="ticketsChart"></canvas>
      </div>
    </div>
  </div>

  <!-- High Risk Table -->
  <div class="card">
    <div class="card-title" style="color:#e040fb">
      High Risk Customers — Intervention Required
    </div>
    <table>
      <thead>
        <tr>
          <th>Customer ID</th>
          <th>Monthly Charges</th>
          <th>Tenure (mo)</th>
          <th>Support Tickets</th>
          <th>Churn Rate</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody id="risk-table">
        <tr><td colspan="6" style="color:#4a5568;text-align:center;padding:20px">Loading...</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Predict -->
  <div class="card" style="margin-bottom:0">
    <div class="card-title" style="color:#00d4ff">
      Predict Single Customer Churn Risk
    </div>
    <div class="predict-grid">
      <div class="slider-group">
        <div class="slider-label">Monthly Charges <span id="v-charges">85</span></div>
        <input type="range" min="20" max="120" value="85" step="1" id="sl-charges"
               oninput="document.getElementById('v-charges').textContent=this.value">
      </div>
      <div class="slider-group">
        <div class="slider-label">Tenure Months <span id="v-tenure">6</span></div>
        <input type="range" min="1" max="60" value="6" step="1" id="sl-tenure"
               oninput="document.getElementById('v-tenure').textContent=this.value">
      </div>
      <div class="slider-group">
        <div class="slider-label">Support Tickets <span id="v-tickets">4</span></div>
        <input type="range" min="0" max="10" value="4" step="1" id="sl-tickets"
               oninput="document.getElementById('v-tickets').textContent=this.value">
      </div>
      <div class="slider-group">
        <div class="slider-label">Days Since Last Login <span id="v-login">45</span></div>
        <input type="range" min="0" max="90" value="45" step="1" id="sl-login"
               oninput="document.getElementById('v-login').textContent=this.value">
      </div>
      <div class="slider-group">
        <div class="slider-label">Number of Products <span id="v-products">1</span></div>
        <input type="range" min="1" max="5" value="1" step="1" id="sl-products"
               oninput="document.getElementById('v-products').textContent=this.value">
      </div>
      <div class="slider-group">
        <div class="slider-label">Total Events <span id="v-events">10</span></div>
        <input type="range" min="1" max="100" value="10" step="1" id="sl-events"
               oninput="document.getElementById('v-events').textContent=this.value">
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <button class="predict-btn" id="pred-btn" onclick="predictChurn()">
        Predict Churn Risk
      </button>
      <div class="spinner" id="spinner"></div>
    </div>

    <div class="result-box result-high" id="result-high"></div>
    <div class="result-box result-low"  id="result-low"></div>
    <div class="result-err" id="result-err">
      Could not reach FastAPI. Make sure it is running:<br>
      <code style="background:rgba(255,255,255,0.07);padding:2px 6px;border-radius:3px;font-family:monospace;">uvicorn api.main:app --reload</code>
    </div>
  </div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const allData  = {data_json};
const total    = allData.length;
const highRisk = allData.filter(d => d.is_high_risk === 1);
const lowRisk  = allData.filter(d => d.is_high_risk === 0);
const avgCh    = allData.reduce((s,d) => s + d.avg_monthly_charges, 0) / total;

document.getElementById('kpi-total').textContent    = total.toLocaleString();
document.getElementById('kpi-high').textContent     = highRisk.length.toLocaleString();
document.getElementById('kpi-high-pct').textContent = (highRisk.length/total*100).toFixed(1)+'% of base';
document.getElementById('kpi-low').textContent      = lowRisk.length.toLocaleString();
document.getElementById('kpi-charges').textContent  = '\u20b9' + avgCh.toFixed(2);

const sortedHigh = [...highRisk].sort((a,b) => b.churn_rate - a.churn_rate).slice(0,10);
document.getElementById('risk-table').innerHTML = sortedHigh.map(d => `
  <tr>
    <td style="color:#e2e8f0;font-weight:600">${{d.customer_id}}</td>
    <td>\u20b9${{d.avg_monthly_charges.toFixed(2)}}</td>
    <td>${{d.avg_tenure_months.toFixed(1)}}</td>
    <td>${{d.avg_support_tickets.toFixed(1)}}</td>
    <td>${{(d.churn_rate*100).toFixed(1)}}%</td>
    <td><span class="risk-badge">High Risk</span></td>
  </tr>
`).join('');

const gC = '#1e2a3a', tC = '#4a5568', tF = {{size:10}};
const baseScales = {{
  x: {{grid:{{color:gC}}, ticks:{{color:tC,font:tF}}}},
  y: {{grid:{{color:gC}}, ticks:{{color:tC,font:tF}}}}
}};

new Chart(document.getElementById('pieChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['High Risk','Low Risk'],
    datasets: [{{
      data: [highRisk.length, lowRisk.length],
      backgroundColor: ['#e040fb','#00d4ff'],
      borderColor: '#111827', borderWidth: 4, hoverOffset: 8
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false, cutout: '70%',
    plugins: {{
      legend: {{display:false}},
      tooltip: {{callbacks: {{label: c => ' '+c.label+': '+c.raw+' ('+(c.raw/total*100).toFixed(1)+'%)'}}}}
    }}
  }}
}});

new Chart(document.getElementById('scatterChart'), {{
  type: 'scatter',
  data: {{datasets: [
    {{
      label: 'High Risk',
      data: highRisk.slice(0,80).map(d => ({{x:+d.avg_monthly_charges.toFixed(2), y:+d.churn_rate.toFixed(3)}})),
      backgroundColor: 'rgba(224,64,251,0.65)', pointRadius: 4, pointStyle: 'triangle'
    }},
    {{
      label: 'Low Risk',
      data: lowRisk.slice(0,80).map(d => ({{x:+d.avg_monthly_charges.toFixed(2), y:+d.churn_rate.toFixed(3)}})),
      backgroundColor: 'rgba(0,212,255,0.55)', pointRadius: 4, pointStyle: 'circle'
    }}
  ]}},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{legend:{{display:false}}}},
    scales: {{
      x: {{...baseScales.x, title:{{display:true,text:'Avg Monthly Charges',color:tC,font:tF}}}},
      y: {{...baseScales.y, title:{{display:true,text:'Churn Rate',color:tC,font:tF}}}}
    }}
  }}
}});

const avgTH = +(highRisk.reduce((s,d)=>s+d.avg_tenure_months,0)/highRisk.length).toFixed(1);
const avgTL = +(lowRisk.reduce((s,d)=>s+d.avg_tenure_months,0)/lowRisk.length).toFixed(1);
new Chart(document.getElementById('tenureChart'), {{
  type: 'bar',
  data: {{
    labels: ['High Risk','Low Risk'],
    datasets: [{{
      label:'Avg Tenure (mo)',
      data:[avgTH,avgTL],
      backgroundColor:['rgba(224,64,251,0.7)','rgba(0,212,255,0.7)'],
      borderRadius:5, borderSkipped:false
    }}]
  }},
  options: {{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:baseScales}}
}});

const avgKH = +(highRisk.reduce((s,d)=>s+d.avg_support_tickets,0)/highRisk.length).toFixed(2);
const avgKL = +(lowRisk.reduce((s,d)=>s+d.avg_support_tickets,0)/lowRisk.length).toFixed(2);
new Chart(document.getElementById('ticketsChart'), {{
  type: 'bar',
  data: {{
    labels: ['High Risk','Low Risk'],
    datasets: [{{
      label:'Avg Support Tickets',
      data:[avgKH,avgKL],
      backgroundColor:['rgba(224,64,251,0.7)','rgba(0,212,255,0.7)'],
      borderRadius:5, borderSkipped:false
    }}]
  }},
  options: {{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:baseScales}}
}});

async function predictChurn() {{
  const btn     = document.getElementById('pred-btn');
  const spinner = document.getElementById('spinner');
  const rh      = document.getElementById('result-high');
  const rl      = document.getElementById('result-low');
  const err     = document.getElementById('result-err');
  rh.style.display = rl.style.display = err.style.display = 'none';
  btn.disabled = true; spinner.style.display = 'block';
  const payload = {{
    avg_monthly_charges: parseFloat(document.getElementById('sl-charges').value),
    avg_tenure_months:   parseFloat(document.getElementById('sl-tenure').value),
    avg_support_tickets: parseFloat(document.getElementById('sl-tickets').value),
    avg_last_login_days: parseFloat(document.getElementById('sl-login').value),
    avg_num_products:    parseFloat(document.getElementById('sl-products').value),
    total_events:        parseFloat(document.getElementById('sl-events').value)
  }};
  try {{
    const res  = await fetch('http://127.0.0.1:8000/predict', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload)
    }});
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    if (data.risk_level === 'HIGH') {{
      rh.innerHTML = '<strong>HIGH RISK</strong> — Churn Probability: ' +
                     (data.churn_probability * 100).toFixed(1) + '% | ' + data.recommendation;
      rh.style.display = 'block';
    }} else {{
      rl.innerHTML = '<strong>LOW RISK</strong> — Churn Probability: ' +
                     (data.churn_probability * 100).toFixed(1) + '% | ' + data.recommendation;
      rl.style.display = 'block';
    }}
  }} catch(e) {{
    err.style.display = 'block';
  }} finally {{
    btn.disabled = false; spinner.style.display = 'none';
  }}
}}
</script>
</body>
</html>"""

import streamlit.components.v1 as components
components.html(html, height=2200, scrolling=True)