const sampleRows = [
  {date:"2026-07-01",sku:"TEA-001",product_name:"Jasmine Tea Gift Box",category:"Tea",impressions:12000,clicks:300,orders:21,units:23,revenue:3450,ad_spend:820,cost:1550,stock:52},
  {date:"2026-07-02",sku:"TEA-001",product_name:"Jasmine Tea Gift Box",category:"Tea",impressions:12800,clicks:315,orders:23,units:25,revenue:3750,ad_spend:850,cost:1680,stock:52},
  {date:"2026-07-01",sku:"FRUIT-002",product_name:"Dried Mango Pack",category:"Snacks",impressions:18000,clicks:250,orders:5,units:6,revenue:354,ad_spend:310,cost:210,stock:430},
  {date:"2026-07-02",sku:"FRUIT-002",product_name:"Dried Mango Pack",category:"Snacks",impressions:17500,clicks:235,orders:4,units:4,revenue:236,ad_spend:295,cost:145,stock:430},
  {date:"2026-07-01",sku:"SAUCE-003",product_name:"Chili Sauce Trio",category:"Food",impressions:9500,clicks:380,orders:34,units:39,revenue:2301,ad_spend:420,cost:1170,stock:18},
  {date:"2026-07-02",sku:"SAUCE-003",product_name:"Chili Sauce Trio",category:"Food",impressions:10200,clicks:410,orders:38,units:43,revenue:2537,ad_spend:440,cost:1290,stock:18},
  {date:"2026-07-01",sku:"COFFEE-004",product_name:"Drip Coffee Set",category:"Beverage",impressions:5000,clicks:160,orders:12,units:13,revenue:1287,ad_spend:390,cost:620,stock:88},
  {date:"2026-07-02",sku:"COFFEE-004",product_name:"Drip Coffee Set",category:"Beverage",impressions:5300,clicks:170,orders:11,units:12,revenue:1188,ad_spend:400,cost:570,stock:88}
];

const severityOrder = {critical: 0, high: 1, medium: 2};
const money = new Intl.NumberFormat("en-US", {style: "currency", currency: "CNY", maximumFractionDigits: 0});
const percent = value => `${(value * 100).toFixed(1)}%`;
const ratio = (a, b) => b ? a / b : 0;

function aggregate(rows) {
  const grouped = new Map();
  rows.forEach(row => {
    const current = grouped.get(row.sku) || {...row, dates: new Set(), impressions:0, clicks:0, orders:0, units:0, revenue:0, ad_spend:0, cost:0};
    current.dates.add(row.date);
    ["impressions","clicks","orders","units","revenue","ad_spend","cost"].forEach(key => current[key] += Number(row[key]));
    current.stock = Number(row.stock);
    grouped.set(row.sku, current);
  });
  return [...grouped.values()].map(item => ({
    ...item,
    ctr: ratio(item.clicks, item.impressions),
    conversion: ratio(item.orders, item.clicks),
    roi: ratio(item.revenue, item.ad_spend),
    profit: item.revenue - item.ad_spend - item.cost,
    cover: item.units ? item.stock / (item.units / item.dates.size) : 999
  }));
}

function diagnose(items) {
  const findings = [];
  const push = (item, severity, code, evidence, action, owner) => findings.push({item, severity, code, evidence, action, owner});
  items.forEach(item => {
    if (item.ctr < .02) push(item,"medium","LOW_CTR",`CTR ${percent(item.ctr)} is below 2.0%.`,"Review creative, title and audience targeting.","Growth / Advertising");
    if (item.conversion < .03) push(item,"high","LOW_CONVERSION",`Conversion ${percent(item.conversion)} is below 3.0%.`,"Audit product page, price, reviews and checkout friction.","Product Operations");
    if (item.roi > 0 && item.roi < 1.5) push(item,"high","LOW_AD_ROI",`Ad ROI ${item.roi.toFixed(2)} is below 1.50.`,"Reduce spend after review and test a new creative or audience.","Growth / Advertising");
    if (item.profit < 0) push(item,"critical","NEGATIVE_CONTRIBUTION",`Contribution profit is ${money.format(item.profit)}.`,"Review price, discount, sourcing cost and paid traffic.","Business Owner");
    if (item.cover < 7) push(item,"high","STOCKOUT_RISK",`Estimated stock cover is ${item.cover.toFixed(1)} days.`,"Confirm forecast and supplier lead time before reorder.","Supply Chain");
    else if (item.cover > 60 && item.cover < 999) push(item,"medium","OVERSTOCK_RISK",`Estimated stock cover is ${item.cover.toFixed(1)} days.`,"Slow procurement and test a margin-safe promotion.","Supply Chain");
  });
  return findings.sort((a,b) => severityOrder[a.severity] - severityOrder[b.severity] || a.item.sku.localeCompare(b.item.sku));
}

function analyze(rows, source) {
  if (!rows.length) throw new Error("The dataset is empty.");
  const fields = ["date","sku","product_name","category","impressions","clicks","orders","units","revenue","ad_spend","cost","stock"];
  fields.forEach(field => { if (!(field in rows[0])) throw new Error(`Missing required field: ${field}`); });
  const numeric = ["impressions","clicks","orders","units","revenue","ad_spend","cost","stock"];
  rows.forEach(row => numeric.forEach(key => row[key] = Number(row[key])));
  const items = aggregate(rows);
  const findings = diagnose(items);
  const total = key => rows.reduce((sum,row) => sum + Number(row[key]), 0);
  const revenue = total("revenue"), adSpend = total("ad_spend"), cost = total("cost");
  renderSummary({gmv:revenue, orders:total("orders"), conversion:ratio(total("orders"),total("clicks")), roi:ratio(revenue,adSpend), profit:revenue-adSpend-cost});
  renderFindings(findings);
  renderActions(findings);
  renderTrace();
  document.getElementById("run-status").textContent = "Analysis complete";
  document.getElementById("message").textContent = `${source}: ${rows.length} rows and ${items.length} SKUs analyzed locally. No external request was made.`;
}

function renderSummary(summary) {
  document.getElementById("gmv").textContent = money.format(summary.gmv);
  document.getElementById("orders").textContent = summary.orders.toLocaleString();
  document.getElementById("conversion").textContent = percent(summary.conversion);
  document.getElementById("roi").textContent = summary.roi.toFixed(2);
  document.getElementById("profit").textContent = money.format(summary.profit);
}

function renderFindings(findings) {
  const body = document.getElementById("finding-rows");
  document.getElementById("finding-count").textContent = `${findings.length} findings`;
  body.innerHTML = findings.length ? findings.map(f => `<tr><td><span class="badge ${f.severity}">${f.severity}</span></td><td><strong>${escapeHtml(f.item.sku)}</strong><br>${escapeHtml(f.item.product_name)}</td><td>${escapeHtml(f.code)}</td><td>${escapeHtml(f.evidence)}</td></tr>`).join("") : '<tr><td colspan="4" class="empty">No threshold breaches found.</td></tr>';
}

function renderActions(findings) {
  const list = document.getElementById("action-list");
  list.innerHTML = findings.length ? findings.map((f,index) => `<article class="action-card"><span class="rank">${index+1}</span><div><h3>${escapeHtml(f.action)}</h3><p>${escapeHtml(f.evidence)}</p><small>${escapeHtml(f.owner)} · Human approval required</small></div></article>`).join("") : '<div class="empty-card">No immediate action is required under the current guardrails.</div>';
}

function renderTrace() {
  const steps = [
    ["validate_input","Validate schema and business invariants"],
    ["compute_portfolio_metrics","Calculate portfolio KPIs"],
    ["aggregate_by_sku","Aggregate operational signals by SKU"],
    ["diagnose_skus","Apply explicit, reviewable guardrails"],
    ["build_recommendations","Prioritize actions and owners"]
  ];
  document.getElementById("trace-list").innerHTML = steps.map(([tool,purpose]) => `<li><strong>${tool}</strong> — ${purpose}</li>`).join("");
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const headers = lines.shift().split(",").map(value => value.trim());
  return lines.map(line => Object.fromEntries(line.split(",").map((value,index) => [headers[index], value.trim()])));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
}

document.getElementById("sample-button").addEventListener("click", () => analyze(sampleRows.map(row => ({...row})), "Synthetic sample"));
document.getElementById("csv-input").addEventListener("change", event => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try { analyze(parseCsv(reader.result), file.name); }
    catch (error) { document.getElementById("message").textContent = `Analysis failed: ${error.message}`; document.getElementById("run-status").textContent = "Needs attention"; }
  };
  reader.readAsText(file);
});

analyze(sampleRows.map(row => ({...row})), "Synthetic sample");
