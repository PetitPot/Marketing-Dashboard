# Builds the Marketing Scorecard mockup (index.html) with made-up weekly data.
import json, random
random.seed(7)

weeks = ["2026-04-26","2026-05-03","2026-05-10","2026-05-17",
         "2026-05-24","2026-05-31","2026-06-07","2026-06-14"]

def series(n, base, growth, noise, rnd=0):
    out=[]; v=base
    for i in range(n):
        x = v*(1+random.uniform(-noise,noise))
        out.append(round(x,rnd) if rnd else int(round(x)))
        v *= (1+growth)
    return out

def build(channel, spend_b, spend_g, roas_b, impr_per_spend, ctr, cvr, upo):
    spend  = series(len(weeks), spend_b, spend_g, .05)
    rows=[]
    for i,wk in enumerate(weeks):
        sp = spend[i]
        roas = round(roas_b*(1+random.uniform(-.08,.08)),2)
        sales = int(round(sp*roas))
        impr = int(round(sp*impr_per_spend*(1+random.uniform(-.06,.06))))
        clicks = int(round(impr*ctr*(1+random.uniform(-.08,.08))))
        orders = int(round(clicks*cvr*(1+random.uniform(-.08,.08))))
        units = int(round(orders*upo*(1+random.uniform(-.05,.05))))
        rows.append({"wk":wk,"spend":sp,"sales":sales,"impr":impr,
                     "clicks":clicks,"orders":orders,"units":units})
    return rows

DATA = {
  "instacart": build("instacart", 1800, .04, 4.1, 95,  .028, .11, 1.8),
  "amazon":    build("amazon",    4600, .03, 3.4, 185, .004, .09, 1.7),
  "meta":      build("meta",      2900, .035,2.5, 250, .010, .045,1.6),
}
print(json.dumps({k:[r['wk']+f" spend {r['spend']} sales {r['sales']}" for r in v[-2:]] for k,v in DATA.items()}, indent=1))

def fmt_data(d):
    order=["wk","spend","sales","impr","clicks","orders","units"]
    lines=["const DATA = {"]
    chans=list(d.keys())
    for ci,ch in enumerate(chans):
        lines.append(f'  "{ch}": [')
        rows=d[ch]
        for ri,r in enumerate(rows):
            obj=", ".join((f'"{k}": "{r[k]}"' if k=="wk" else f'"{k}": {r[k]}') for k in order)
            comma="," if ri<len(rows)-1 else ""
            lines.append(f'    {{ {obj} }}{comma}')
        lines.append("  ]" + ("," if ci<len(chans)-1 else ""))
    lines.append("};")
    return "\n".join(lines)
data_js = fmt_data(DATA)

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Petit Pot — Marketing Scorecard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js"></script>
<style>
  :root{color-scheme:light;--bg:#fff;--surface:#fff;--border:#dde8f5;--text:#1a1a1a;--muted:#6b7280;
    --accent:#fd5000;--green:#1e7a3d;--red:#c62828;--header-bg:#1b69b3;--soft:#f4f8fd;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);font-size:13px}
  .header{background:var(--header-bg);color:#f0ebe0;padding:14px 24px;display:flex;align-items:center;justify-content:space-between}
  .header h1{font-size:17px;font-weight:600}
  .header .meta{font-size:12px;color:#c0b89a}
  .tabs{background:var(--surface);border-bottom:1px solid var(--border);display:flex;padding:0 24px;overflow-x:auto}
  .tab{padding:11px 18px;cursor:pointer;font-size:12.5px;font-weight:500;color:var(--muted);border-bottom:3px solid transparent;white-space:nowrap}
  .tab:hover{color:var(--text)}
  .tab.active{color:var(--accent);border-bottom-color:var(--accent)}
  .content{padding:20px 24px;max-width:1180px}
  .panel{display:none}.panel.active{display:block}
  .note{font-size:11.5px;color:var(--muted);background:#fff7f0;border:1px solid #ffd9bf;border-radius:6px;padding:7px 11px;margin-bottom:14px}
  .kpi-row{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap}
  .kpi{background:var(--soft);border:1px solid #cfe0f2;border-radius:8px;padding:12px 16px;min-width:150px;flex:1}
  .kpi .lbl{font-size:11px;color:var(--muted);font-weight:500;margin-bottom:4px;text-transform:uppercase;letter-spacing:.03em}
  .kpi .val{font-size:21px;font-weight:700}
  .kpi .chg{font-size:11px;margin-top:3px}
  .pos{color:var(--green)}.neg{color:var(--red)}
  .section-hd{display:flex;align-items:center;justify-content:space-between;margin:18px 0 10px}
  .section-hd h2{font-size:14px;font-weight:600}
  .badge{background:#ffecda;color:var(--accent);border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600}
  .tbl-wrap{overflow-x:auto;border-radius:8px;border:1px solid var(--border);display:inline-block;max-width:100%}
  table{border-collapse:collapse;font-size:12.5px;width:auto}
  thead th{background:#ffecda;padding:9px 13px;text-align:right;font-weight:600;font-size:11.5px;border-bottom:1px solid var(--border);white-space:nowrap;min-width:84px}
  thead th.left,td.left{text-align:left;min-width:120px}
  tbody tr:nth-child(even){background:#f8fbff}
  tbody tr:hover{background:#ffecda}
  td{padding:7px 13px;text-align:right;border-bottom:1px solid #f0ece6;white-space:nowrap}
  .grp td{background:#eef4fb!important;font-weight:700;color:#1b69b3;font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding:6px 13px}
  .chart-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:8px}
  .chart-box{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px}
  .chart-box h3{font-size:12px;font-weight:600;color:var(--muted);margin-bottom:12px}
  .chart-box canvas{max-height:240px}
  @media(max-width:760px){.chart-row{grid-template-columns:1fr}.kpi-row{flex-direction:column}}
</style>
</head>
<body>
<div class="header">
  <h1>Petit Pot — Marketing Scorecard</h1>
  <span class="meta">MOCK DATA · weekly by channel</span>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('overview')">Overview</div>
  <div class="tab" onclick="showTab('instacart')">Instacart</div>
  <div class="tab" onclick="showTab('amazon')">Amazon</div>
  <div class="tab" onclick="showTab('meta')">Meta / Facebook</div>
</div>
<div class="content">
  <div class="note">&#9888; This is a <b>mockup with placeholder numbers</b>. Replace the data in the <code>DATA</code> block near the top of this file each week &mdash; see the README for steps.</div>
  <div class="panel active" id="panel-overview"></div>
  <div class="panel" id="panel-instacart"></div>
  <div class="panel" id="panel-amazon"></div>
  <div class="panel" id="panel-meta"></div>
</div>

<script>
/* =====================================================================
   WEEKLY DATA  —  EDIT THIS EACH WEEK, THEN SAVE & UPLOAD TO GITHUB
   ---------------------------------------------------------------------
   - One line per week, inside each channel (instacart / amazon / meta).
   - To add a week: copy the LAST { ... } line in a channel, paste it
     below that line, then change the date + 6 numbers.
   - Enter only the 6 raw numbers from each ad portal:
       wk     = week-ending date "YYYY-MM-DD"
       spend  = ad spend ($)
       sales  = attributed sales / conversion value ($)
       impr   = impressions
       clicks = clicks
       orders = orders / purchases
       units  = units sold
   - Everything else (ROAS, CTR, CPC, conv rate, $/unit) is calculated
     for you. Keep the commas and curly braces exactly as shown.
   ===================================================================== */
__DATA__
/* ===================  END OF WEEKLY DATA  =========================== */

const CH = {instacart:{name:"Instacart",color:"#ff7a00"},
            amazon:{name:"Amazon",color:"#1b69b3"},
            meta:{name:"Meta / Facebook",color:"#6abc4b"}};
const ORDER = ["instacart","amazon","meta"];

const nf=(v,d=0)=>(+v).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const usd=(v,d=0)=>'$'+nf(v,d);
const pct=(v)=>nf(v,1)+'%';
const fwk=w=>{const p=w.split('-');return (+p[1])+'/'+(+p[2]);};

function derive(r){
  return {...r,
    roas: r.spend? r.sales/r.spend : 0,
    ctr:  r.impr?  r.clicks/r.impr*100 : 0,
    cpc:  r.clicks? r.spend/r.clicks : 0,
    cvr:  r.clicks? r.orders/r.clicks*100 : 0,
    ppu:  r.units? r.sales/r.units : 0,
  };
}
function rowsOf(ch){ return DATA[ch].map(derive); }
function delta(cur,prev,inv){ // returns {txt,cls}
  if(prev==null||prev===0) return {txt:'',cls:''};
  const d=(cur-prev)/Math.abs(prev)*100;
  const good = inv ? d<0 : d>0;
  const arrow = d>=0?'&#9650;':'&#9660;';
  return {txt:`${arrow} ${nf(Math.abs(d),1)}%`, cls: good?'pos':'neg'};
}
function kpi(lbl,val,dl){
  return `<div class="kpi"><div class="lbl">${lbl}</div><div class="val">${val}</div>`+
    (dl&&dl.txt?`<div class="chg ${dl.cls}">${dl.txt} vs last wk</div>`:`<div class="chg">&nbsp;</div>`)+`</div>`;
}

let charts=[];
function clearCharts(){ charts.forEach(c=>c.destroy()); charts=[]; }

function channelPanel(ch){
  const rows=rowsOf(ch); const last=rows[rows.length-1], prev=rows[rows.length-2];
  const c=CH[ch].color;
  const cards=
    kpi('Spend', usd(last.spend), delta(last.spend,prev&&prev.spend))+
    kpi('Attributed Sales', usd(last.sales), delta(last.sales,prev&&prev.sales))+
    kpi('ROAS', nf(last.roas,2)+'x', delta(last.roas,prev&&prev.roas))+
    kpi('Impressions', nf(last.impr), delta(last.impr,prev&&prev.impr))+
    kpi('Clicks', nf(last.clicks), delta(last.clicks,prev&&prev.clicks))+
    kpi('CTR', pct(last.ctr), delta(last.ctr,prev&&prev.ctr))+
    kpi('CPC', usd(last.cpc,2), delta(last.cpc,prev&&prev.cpc,true))+
    kpi('Orders', nf(last.orders), delta(last.orders,prev&&prev.orders))+
    kpi('Units (sold)', nf(last.units), delta(last.units,prev&&prev.units));
  // weeks-as-columns table
  const head=`<th class="left">Metric</th>`+rows.map(r=>`<th>${fwk(r.wk)}</th>`).join('');
  const mrow=(lbl,fn)=>`<tr><td class="left">${lbl}</td>`+rows.map(r=>`<td>${fn(r)}</td>`).join('')+`</tr>`;
  const body=
    `<tr class="grp"><td class="left" colspan="${rows.length+1}">Sales &amp; Spend</td></tr>`+
    mrow('Spend', r=>usd(r.spend))+
    mrow('Attributed Sales', r=>usd(r.sales))+
    mrow('ROAS', r=>nf(r.roas,2)+'x')+
    mrow('$ / Unit', r=>usd(r.ppu,2))+
    `<tr class="grp"><td class="left" colspan="${rows.length+1}">Funnel</td></tr>`+
    mrow('Impressions', r=>nf(r.impr))+
    mrow('Clicks', r=>nf(r.clicks))+
    mrow('CTR', r=>pct(r.ctr))+
    mrow('CPC', r=>usd(r.cpc,2))+
    mrow('Orders', r=>nf(r.orders))+
    mrow('Conv. Rate', r=>pct(r.cvr))+
    mrow('Units', r=>nf(r.units));
  return `<div class="kpi-row">${cards}</div>
    <div class="chart-row">
      <div class="chart-box"><h3>Spend vs. Attributed Sales</h3><canvas id="c_${ch}_1"></canvas></div>
      <div class="chart-box"><h3>ROAS by Week</h3><canvas id="c_${ch}_2"></canvas></div>
    </div>
    <div class="section-hd"><h2>${CH[ch].name} — Weekly Detail</h2><span class="badge">${rows.length} weeks</span></div>
    <div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function channelCharts(ch){
  const rows=rowsOf(ch); const labels=rows.map(r=>fwk(r.wk)); const c=CH[ch].color;
  charts.push(new Chart(document.getElementById('c_'+ch+'_1'),{type:'line',
    data:{labels,datasets:[
      {label:'Spend',data:rows.map(r=>r.spend),borderColor:'#fd5000',backgroundColor:'#fd500022',tension:.3,fill:true},
      {label:'Sales',data:rows.map(r=>r.sales),borderColor:c,backgroundColor:c+'22',tension:.3,fill:true}]},
    options:{plugins:{legend:{labels:{boxWidth:12,font:{size:11}}}},scales:{y:{ticks:{callback:v=>'$'+(v/1000)+'k'}}}}}));
  charts.push(new Chart(document.getElementById('c_'+ch+'_2'),{type:'bar',
    data:{labels,datasets:[{label:'ROAS',data:rows.map(r=>r.roas.toFixed(2)),backgroundColor:c}]},
    options:{plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>v+'x'}}}}}));
}

function overviewPanel(){
  const tot=(ch,i,key)=>rowsOf(ch)[i][key];
  const n=DATA.instacart.length;
  const sum=(i,key)=>ORDER.reduce((a,ch)=>a+tot(ch,i,key),0);
  const lastI=n-1, prevI=n-2;
  const spend=sum(lastI,'spend'), sales=sum(lastI,'sales'), impr=sum(lastI,'impr'), clicks=sum(lastI,'clicks'), orders=sum(lastI,'orders');
  const pSpend=sum(prevI,'spend'), pSales=sum(prevI,'sales');
  const roas= spend? sales/spend:0, pRoas= pSpend? pSales/pSpend:0;
  const ctr= impr? clicks/impr*100:0;
  const cards=
    kpi('Total Spend', usd(spend), delta(spend,pSpend,true))+
    kpi('Attributed Sales', usd(sales), delta(sales,pSales))+
    kpi('Blended ROAS', nf(roas,2)+'x', delta(roas,pRoas))+
    kpi('Impressions', nf(impr), null)+
    kpi('Clicks', nf(clicks), null)+
    kpi('Avg CTR', pct(ctr), null);
  // channel summary table (latest week)
  const head=`<th class="left">Channel</th><th>Spend</th><th>Sales</th><th>ROAS</th><th>Impr</th><th>Clicks</th><th>CTR</th><th>Orders</th>`;
  const body=ORDER.map(ch=>{const r=rowsOf(ch)[lastI];
    return `<tr><td class="left">${CH[ch].name}</td><td>${usd(r.spend)}</td><td>${usd(r.sales)}</td><td>${nf(r.roas,2)}x</td><td>${nf(r.impr)}</td><td>${nf(r.clicks)}</td><td>${pct(r.ctr)}</td><td>${nf(r.orders)}</td></tr>`;}).join('');
  return `<div class="kpi-row">${cards}</div>
    <div class="chart-row">
      <div class="chart-box"><h3>Total Spend vs. Sales (all channels)</h3><canvas id="ov1"></canvas></div>
      <div class="chart-box"><h3>ROAS by Channel (latest week)</h3><canvas id="ov2"></canvas></div>
    </div>
    <div class="section-hd"><h2>Latest Week by Channel</h2><span class="badge">wk ${fwk(DATA.instacart[lastI].wk)}</span></div>
    <div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
function overviewCharts(){
  const n=DATA.instacart.length; const labels=DATA.instacart.map(r=>fwk(r.wk));
  const sumKey=key=>Array.from({length:n},(_,i)=>ORDER.reduce((a,ch)=>a+rowsOf(ch)[i][key],0));
  charts.push(new Chart(document.getElementById('ov1'),{type:'line',
    data:{labels,datasets:[
      {label:'Spend',data:sumKey('spend'),borderColor:'#fd5000',backgroundColor:'#fd500022',tension:.3,fill:true},
      {label:'Sales',data:sumKey('sales'),borderColor:'#1b69b3',backgroundColor:'#1b69b322',tension:.3,fill:true}]},
    options:{plugins:{legend:{labels:{boxWidth:12,font:{size:11}}}},scales:{y:{ticks:{callback:v=>'$'+(v/1000)+'k'}}}}}));
  charts.push(new Chart(document.getElementById('ov2'),{type:'bar',
    data:{labels:ORDER.map(ch=>CH[ch].name),datasets:[{label:'ROAS',
      data:ORDER.map(ch=>{const r=rowsOf(ch)[n-1];return r.roas.toFixed(2);}),
      backgroundColor:ORDER.map(ch=>CH[ch].color)}]},
    options:{plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>v+'x'}}}}}));
}

function showTab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  render(name);
}
function render(name){
  clearCharts();
  if(name==='overview'){document.getElementById('panel-overview').innerHTML=overviewPanel(); overviewCharts();}
  else {document.getElementById('panel-'+name).innerHTML=channelPanel(name); channelCharts(name);}
}
render('overview');
</script>
</body>
</html>'''

HTML = HTML.replace("__DATA__", data_js)
open("index.html","w",encoding="utf-8").write(HTML)
print("wrote index.html", len(HTML)//1024, "KB")
