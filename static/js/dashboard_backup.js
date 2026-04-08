const isDashboard = document.getElementById("kpi-revenue") !== null;
const isUpload    = document.getElementById("dropzone")    !== null;

let currentPeriod   = "month";
let currentDateFrom = null;
let currentDateTo   = null;
let refreshTimer    = null;
let vizPanelOpen    = false;
let lastKpis        = null;
let lastPeriodData  = null;

if (isUpload) {
  const dropzone  = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  dropzone.addEventListener("dragover",  e => { e.preventDefault(); dropzone.classList.add("drag"); });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag"));
  dropzone.addEventListener("drop", e => {
    e.preventDefault(); dropzone.classList.remove("drag");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  });
  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });
}

function handleFile(file) {
  document.getElementById("upload-card").style.display   = "none";
  document.getElementById("progress-card").style.display = "block";
  document.getElementById("prog-filename").textContent   = file.name;
  const steps = [
    {id:"step-1",pct:15},{id:"step-2",pct:30},{id:"step-3",pct:50},
    {id:"step-4",pct:68},{id:"step-5",pct:82},{id:"step-6",pct:100},
  ];
  let i = 0;
  function animateStep() {
    if (i > 0) {
      const prev = document.querySelector(`#${steps[i-1].id} .step-dot`);
      if (prev) { prev.className = "step-dot done"; prev.textContent = "✓"; }
    }
    if (i < steps.length) {
      const cur = document.querySelector(`#${steps[i].id} .step-dot`);
      if (cur) { cur.className = "step-dot active"; cur.textContent = "..."; }
      document.getElementById("prog-pct").textContent      = steps[i].pct + "%";
      document.getElementById("prog-bar-fill").style.width = steps[i].pct + "%";
      i++;
      if (i < steps.length) setTimeout(animateStep, 500);
    }
  }
  animateStep();
  const formData = new FormData();
  formData.append("file", file);
  fetch("/api/upload", { method:"POST", body:formData })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert("Error: " + data.error); location.reload(); return; }
      const last = document.querySelector(`#${steps[steps.length-1].id} .step-dot`);
      if (last) { last.className = "step-dot done"; last.textContent = "✓"; }
      document.getElementById("prog-pct").textContent      = "100%";
      document.getElementById("prog-bar-fill").style.width = "100%";
      showReport(data.report);
      setTimeout(() => window.location.href = data.redirect, 1500);
    })
    .catch(() => { alert("Upload failed."); location.reload(); });
}

function showReport(report) {
  const card = document.getElementById("clean-report");
  if (!card) return;
  card.style.display = "block";
  document.getElementById("report-grid").innerHTML = `
    <div class="report-stat">
      <div class="report-stat-val">${report.final_rows.toLocaleString()}</div>
      <div class="report-stat-lbl">Rows cleaned</div>
    </div>
    <div class="report-stat">
      <div class="report-stat-val">${report.duplicates_removed}</div>
      <div class="report-stat-lbl">Duplicates removed</div>
    </div>
    <div class="report-stat">
      <div class="report-stat-val">${report.nulls_filled}</div>
      <div class="report-stat-lbl">Nulls filled</div>
    </div>`;
}

function formatMoney(n) {
  const num = parseFloat(n);
  if (num >= 1000000) return "$" + (num/1000000).toFixed(2) + "M";
  if (num >= 1000)    return "$" + (num/1000).toFixed(1)    + "K";
  return "$" + num.toFixed(2);
}

function setPeriod(period, btn) {
  currentPeriod = period;
  document.querySelectorAll(".period-tab").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  loadAll();
}

function applyDateFilter() {
  currentDateFrom = document.getElementById("date-from").value || null;
  currentDateTo   = document.getElementById("date-to").value   || null;
  document.querySelectorAll(".period-tab").forEach(b => b.classList.remove("active"));
  loadAll();
}

function manualRefresh() {
  loadAll();
  resetRefreshTimer();
}

function resetRefreshTimer() {
  if (refreshTimer) clearInterval(refreshTimer);
  let count = 30;
  const el  = document.getElementById("refresh-countdown");
  if (el) el.textContent = count + "s";
  refreshTimer = setInterval(() => {
    count--;
    if (el) el.textContent = count + "s";
    if (count <= 0) { count = 30; loadAll(); }
  }, 1000);
}

function buildParams() {
  const p = [`period=${currentPeriod}`];
  if (currentDateFrom) p.push("date_from=" + currentDateFrom);
  if (currentDateTo)   p.push("date_to="   + currentDateTo);
  return p.join("&");
}

async function loadAll() {
  await Promise.all([loadKPIs(), loadPeriodData()]);
}

async function loadKPIs() {
  try {
    const res  = await fetch("/api/kpis?" + buildParams());
    const kpis = await res.json();
    if (kpis.error) return;
    lastKpis = kpis;

    document.getElementById("kpi-revenue").innerHTML = `
      <div class="kpi-label">Total Revenue</div>
      <div class="kpi-value">${formatMoney(kpis.total_revenue)}</div>
      <div class="kpi-trend up">▲ ${currentPeriod} view</div>
      <canvas class="kpi-spark-canvas" id="spark-revenue" height="32"></canvas>`;
    document.getElementById("kpi-revenue").classList.remove("shimmer");

    document.getElementById("kpi-orders").innerHTML = `
      <div class="kpi-label">Total Orders</div>
      <div class="kpi-value">${parseInt(kpis.total_orders).toLocaleString()}</div>
      <div class="kpi-trend">From dataset</div>
      <canvas class="kpi-spark-canvas" id="spark-orders" height="32"></canvas>`;
    document.getElementById("kpi-orders").classList.remove("shimmer");

    document.getElementById("kpi-aov").innerHTML = `
      <div class="kpi-label">Avg Order Value</div>
      <div class="kpi-value">${formatMoney(kpis.avg_order_value)}</div>
      <div class="kpi-trend">Per transaction</div>
      <canvas class="kpi-spark-canvas" id="spark-aov" height="32"></canvas>`;
    document.getElementById("kpi-aov").classList.remove("shimmer");

    document.getElementById("kpi-customers").innerHTML = `
      <div class="kpi-label">Total Customers</div>
      <div class="kpi-value">${parseInt(kpis.total_customers || kpis.total_rows).toLocaleString()}</div>
      <div class="kpi-trend">Unique in dataset</div>
      <canvas class="kpi-spark-canvas" id="spark-customers" height="32"></canvas>`;
    document.getElementById("kpi-customers").classList.remove("shimmer");

    document.getElementById("clean-pill").textContent =
      "✓ " + parseInt(kpis.total_rows).toLocaleString() + " rows · " + currentPeriod + " view";

    renderWeekBanner(kpis.week_vs_last_week || {});
    renderTopProducts(kpis.top_products || []);

    if (kpis.monthly_trend && kpis.monthly_trend.length) {
      const vals = kpis.monthly_trend.map(d => d.revenue);
      renderSparkline("spark-revenue",   vals, "#6366f1");
      renderSparkline("spark-aov",       vals.map(v => v / Math.max(1, kpis.total_orders / kpis.monthly_trend.length)), "#f59e0b");
      renderSparkline("spark-orders",    kpis.daily_orders ? kpis.daily_orders.map(d => d.orders) : vals, "#10b981");
      renderSparkline("spark-customers", vals, "#3b82f6");
    }

  } catch(err) {
    console.error("KPI load error:", err);
  }
}

async function loadPeriodData() {
  try {
    const res  = await fetch("/api/period-data?" + buildParams());
    const data = await res.json();
    if (data.error) return;
    lastPeriodData = data;
    renderAllCharts(data, lastKpis || {});
  } catch(err) {
    console.error("Period data error:", err);
  }
}

async function loadVizConfig() {
  try {
    const res    = await fetch("/api/viz-config");
    const config = await res.json();
    renderVizPanel(config);
  } catch(err) {
    console.error("Viz config error:", err);
  }
}

function renderVizPanel(config) {
  const recEl = document.getElementById("viz-recommended");
  const avEl  = document.getElementById("viz-available");
  if (!recEl || !avEl) return;

  recEl.innerHTML = config.recommended.map(v => `
    <div class="viz-item active" onclick="toggleVizChart('${v.id}', this)">
      <div class="viz-item-icon">📊</div>
      <div>
        <div class="viz-item-title">${v.title}</div>
        <div class="viz-item-desc">${v.description}</div>
      </div>
      <span class="viz-badge">ON</span>
    </div>`).join("");

  avEl.innerHTML = config.available.map(v => `
    <div class="viz-item" onclick="addVizChart('${v.type}', this)">
      <div class="viz-item-icon">${v.icon}</div>
      <div>
        <div class="viz-item-title">${v.title}</div>
      </div>
    </div>`).join("");
}

function toggleVizChart(id, el) {
  el.classList.toggle("active");
  const badge = el.querySelector(".viz-badge");
  if (badge) badge.textContent = el.classList.contains("active") ? "ON" : "OFF";
  loadPeriodData();
}

function addVizChart(type, el) {
  el.classList.toggle("active");
  if (type === "table") { showDataTable(); return; }
  loadPeriodData();
}

function toggleVizPanel() {
  vizPanelOpen = !vizPanelOpen;
  const panel = document.getElementById("viz-panel");
  if (panel) panel.classList.toggle("open", vizPanelOpen);
  if (vizPanelOpen) loadVizConfig();
}

function showDataTable() {
  const wrap = document.getElementById("data-table-wrap");
  if (wrap) wrap.style.display = "block";
  if (lastPeriodData && lastPeriodData.trend) {
    renderDataTable(lastPeriodData.trend, currentPeriod);
  }
  wrap.scrollIntoView({ behavior: "smooth" });
}

function hideDataTable() {
  const wrap = document.getElementById("data-table-wrap");
  if (wrap) wrap.style.display = "none";
}

async function loadStory() {
  const body = document.getElementById("story-body");
  body.innerHTML = '<div class="story-placeholder">Generating AI analysis...</div>';
  try {
    const res   = await fetch("/api/story");
    const story = await res.json();
    if (story.error) {
      body.innerHTML = `<div class="story-placeholder" style="color:#ef4444">${story.error}</div>`;
      return;
    }
    body.innerHTML = `
      <div class="story-headline">${story.headline}</div>
      <div class="story-summary">${story.summary}</div>
      <div class="story-section-title" style="margin-top:8px">Highlights</div>
      <div style="margin-bottom:8px">
        ${story.highlights.map(h=>`<span class="story-chip chip-green">${h}</span>`).join("")}
      </div>
      <div class="story-section-title">Risks</div>
      <div style="margin-bottom:8px">
        ${story.risks.map(r=>`<span class="story-chip chip-red">${r}</span>`).join("")}
      </div>
      <div class="story-section-title">Recommendation</div>
      <div class="story-summary">${story.recommendation}</div>`;
  } catch(err) {
    body.innerHTML = '<div class="story-placeholder" style="color:#ef4444">Failed to load story.</div>';
  }
}

if (isDashboard) {
  document.addEventListener("DOMContentLoaded", () => {
    loadAll();
    resetRefreshTimer();
  });
}