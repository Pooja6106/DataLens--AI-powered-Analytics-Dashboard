// ─────────────────────────────────────────
// STATE
// ─────────────────────────────────────────
const isDashboard = document.getElementById("kpi-revenue")  !== null;
const isUpload    = document.getElementById("dropzone")     !== null;

let currentPeriod   = "month";
let currentDateFrom = null;
let currentDateTo   = null;
let currentDept     = "auto";
let refreshTimer    = null;
let lastKpis        = null;
let lastPeriodData  = null;

// ─────────────────────────────────────────
// UPLOAD PAGE
// ─────────────────────────────────────────
if (isUpload) {
  const dropzone  = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");

  if (dropzone) {
    dropzone.addEventListener("dragover", e => {
      e.preventDefault();
      dropzone.classList.add("drag");
    });
    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("drag");
    });
    dropzone.addEventListener("drop", e => {
      e.preventDefault();
      dropzone.classList.remove("drag");
      if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    dropzone.addEventListener("click", () => fileInput.click());
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) handleFile(fileInput.files[0]);
    });
  }
}

function handleFile(file) {
  const uploadCard    = document.getElementById("upload-card");
  const progressCard  = document.getElementById("progress-card");
  const progFilename  = document.getElementById("prog-filename");

  if (uploadCard)   uploadCard.style.display   = "none";
  if (progressCard) progressCard.style.display = "block";
  if (progFilename) progFilename.textContent   = file.name;

  const steps = [
    { id: "step-1", pct: 15  },
    { id: "step-2", pct: 30  },
    { id: "step-3", pct: 50  },
    { id: "step-4", pct: 68  },
    { id: "step-5", pct: 82  },
    { id: "step-6", pct: 100 },
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
      const pct  = document.getElementById("prog-pct");
      const fill = document.getElementById("prog-bar-fill");
      if (pct)  pct.textContent      = steps[i].pct + "%";
      if (fill) fill.style.width     = steps[i].pct + "%";
      i++;
      if (i < steps.length) setTimeout(animateStep, 500);
    }
  }
  animateStep();

  const formData = new FormData();
  formData.append("file", file);

  fetch("/api/upload", { method: "POST", body: formData })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
        location.reload();
        return;
      }
      const last = document.querySelector(
        `#${steps[steps.length-1].id} .step-dot`);
      if (last) { last.className = "step-dot done"; last.textContent = "✓"; }
      const pct  = document.getElementById("prog-pct");
      const fill = document.getElementById("prog-bar-fill");
      if (pct)  pct.textContent  = "100%";
      if (fill) fill.style.width = "100%";
      showReport(data.report);
      setTimeout(() => window.location.href = data.redirect, 1500);
    })
    .catch(() => { alert("Upload failed."); location.reload(); });
}

function showReport(report) {
  const card = document.getElementById("clean-report");
  const grid = document.getElementById("report-grid");
  if (!card || !grid) return;
  card.style.display = "block";
  grid.innerHTML = `
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

// ─────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────
function formatMoney(n) {
  const num = parseFloat(n) || 0;
  if (num >= 1_000_000) return "$" + (num / 1_000_000).toFixed(2) + "M";
  if (num >= 1_000)     return "$" + (num / 1_000).toFixed(1)     + "K";
  return "$" + num.toFixed(2);
}

function buildParams() {
  const p = [`period=${currentPeriod}`];
  if (currentDateFrom) p.push("date_from=" + currentDateFrom);
  if (currentDateTo)   p.push("date_to="   + currentDateTo);
  if (currentDept && currentDept !== "auto")
    p.push("dept=" + currentDept);
  return p.join("&");
}

// ─────────────────────────────────────────
// DEPARTMENT SWITCHER
// ─────────────────────────────────────────
function switchDept(dept, btn) {
  currentDept = dept;
  document.querySelectorAll(".dept-tab")
    .forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  loadAll();
}

// ─────────────────────────────────────────
// SIDEBAR SLICER FUNCTIONS
// ─────────────────────────────────────────
function setPeriodSlicer(period, el) {
  currentPeriod = period;
  document.querySelectorAll(".period-pill")
    .forEach(p => p.classList.remove("active"));
  if (el) el.classList.add("active");
  loadAll();
}

function clearDates() {
  currentDateFrom = null;
  currentDateTo   = null;
  const df = document.getElementById("date-from");
  const dt = document.getElementById("date-to");
  if (df) df.value = "";
  if (dt) dt.value = "";
  loadAll();
}

function setQuickDate(range, btn) {
  document.querySelectorAll(
    ".slicer-section .period-pill"
  ).forEach(b => {
    if (["Today","7 Days","30 Days","All Time"]
        .includes(b.textContent.trim())) {
      b.classList.remove("active");
    }
  });
  if (btn) btn.classList.add("active");

  const today = new Date();
  const fmt   = d => d.toISOString().split("T")[0];

  if (range === "all") {
    currentDateFrom = null; currentDateTo = null;
    const df = document.getElementById("date-from");
    const dt = document.getElementById("date-to");
    if (df) df.value = "";
    if (dt) dt.value = "";
  } else if (range === "today") {
    currentDateFrom = fmt(today);
    currentDateTo   = fmt(today);
  } else if (range === "7days") {
    const s = new Date(today);
    s.setDate(s.getDate() - 7);
    currentDateFrom = fmt(s);
    currentDateTo   = fmt(today);
  } else if (range === "30days") {
    const s = new Date(today);
    s.setDate(s.getDate() - 30);
    currentDateFrom = fmt(s);
    currentDateTo   = fmt(today);
  }

  if (range !== "all") {
    const df = document.getElementById("date-from");
    const dt = document.getElementById("date-to");
    if (df) df.value = currentDateFrom || "";
    if (dt) dt.value = currentDateTo   || "";
  }
  loadAll();
}

function populateCategorySlicer(categories) {
  const el = document.getElementById("category-slicer");
  if (!el || !categories || !categories.length) return;
  el.innerHTML = categories.slice(0, 10).map(c => `
    <div class="slicer-item active"
      onclick="toggleSlicerItem(this,'category')">
      <div class="slicer-check checked">✓</div>
      <span class="slicer-item-label"
        title="${c.category}">${c.category}</span>
    </div>`).join("");
}

function populateRegionSlicer(regions) {
  const el = document.getElementById("region-slicer");
  if (!el || !regions || !regions.length) return;
  el.innerHTML = regions.slice(0, 10).map(r => `
    <div class="slicer-item active"
      onclick="toggleSlicerItem(this,'region')">
      <div class="slicer-check checked">✓</div>
      <span class="slicer-item-label"
        title="${r.region}">${r.region}</span>
    </div>`).join("");
}

function toggleSlicerItem(el, type) {
  el.classList.toggle("active");
  const check = el.querySelector(".slicer-check");
  if (check) {
    check.classList.toggle("checked",
      el.classList.contains("active"));
    check.textContent =
      el.classList.contains("active") ? "✓" : "";
  }
}

function resetCategorySlicer() {
  document.querySelectorAll(
    "#category-slicer .slicer-item"
  ).forEach(el => {
    el.classList.add("active");
    const check = el.querySelector(".slicer-check");
    if (check) {
      check.classList.add("checked");
      check.textContent = "✓";
    }
  });
}

function resetRegionSlicer() {
  document.querySelectorAll(
    "#region-slicer .slicer-item"
  ).forEach(el => {
    el.classList.add("active");
    const check = el.querySelector(".slicer-check");
    if (check) {
      check.classList.add("checked");
      check.textContent = "✓";
    }
  });
}

// ─────────────────────────────────────────
// PERIOD TABS
// ─────────────────────────────────────────
function setPeriod(period, btn) {
  currentPeriod = period;
  document.querySelectorAll(".period-tab")
    .forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  loadAll();
}

// ─────────────────────────────────────────
// DATE FILTERS
// ─────────────────────────────────────────
function setQuickDate(range, btn) {
  document.querySelectorAll(".qbtn")
    .forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");

  const today = new Date();
  const fmt   = d => d.toISOString().split("T")[0];

  if (range === "all") {
    currentDateFrom = null;
    currentDateTo   = null;
    const df = document.getElementById("date-from");
    const dt = document.getElementById("date-to");
    if (df) df.value = "";
    if (dt) dt.value = "";
  } else if (range === "today") {
    currentDateFrom = fmt(today);
    currentDateTo   = fmt(today);
  } else if (range === "yesterday") {
    const y = new Date(today);
    y.setDate(y.getDate() - 1);
    currentDateFrom = fmt(y);
    currentDateTo   = fmt(y);
  } else if (range === "7days") {
    const s = new Date(today);
    s.setDate(s.getDate() - 7);
    currentDateFrom = fmt(s);
    currentDateTo   = fmt(today);
  } else if (range === "30days") {
    const s = new Date(today);
    s.setDate(s.getDate() - 30);
    currentDateFrom = fmt(s);
    currentDateTo   = fmt(today);
  }

  if (range !== "all") {
    const df = document.getElementById("date-from");
    const dt = document.getElementById("date-to");
    if (df) df.value = currentDateFrom;
    if (dt) dt.value = currentDateTo;
  }
  loadAll();
}

function applyDateFilter() {
  document.querySelectorAll(".period-tab")
    .forEach(b => b.classList.remove("active"));
  const df = document.getElementById("date-from");
  const dt = document.getElementById("date-to");
  currentDateFrom = (df && df.value) ? df.value : null;
  currentDateTo   = (dt && dt.value) ? dt.value : null;
  loadAll();
}

// ─────────────────────────────────────────
// REFRESH
// ─────────────────────────────────────────
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
    if (count <= 0) {
      count = 30;
      loadAll();
    }
  }, 1000);
}

// ─────────────────────────────────────────
// LOAD ALL
// ─────────────────────────────────────────
async function loadAll() {
  await Promise.all([loadKPIs(), loadPeriodData()]);
}

// ─────────────────────────────────────────
// LOAD KPIs
// ─────────────────────────────────────────
async function loadKPIs() {
  try {
    const res  = await fetch("/api/kpis?" + buildParams());
    const kpis = await res.json();

    if (kpis.error) {
      console.error("KPI error:", kpis.error);
      const pill = document.getElementById("clean-pill");
      if (pill) pill.textContent = "Error: " + kpis.error;
      return;
    }

    lastKpis = kpis;

    // ── Department detection badge ──
    const detectedEl = document.getElementById("dept-detected");
    if (detectedEl && kpis.detection) {
      detectedEl.textContent =
        `✓ ${kpis.dept_icon || ""} ${kpis.dept_name || ""} · ` +
        `${kpis.detection.confidence || 0}% confidence`;
    }

    // ── KPI Cards ──
    const cards  = kpis.kpi_cards || [];
    const ids    = ["kpi-revenue","kpi-orders","kpi-aov","kpi-customers"];
    const sparks = ["spark-revenue","spark-orders","spark-aov","spark-customers"];

    if (cards.length > 0) {
      cards.forEach((card, i) => {
        const el = document.getElementById(ids[i]);
        if (!el) return;
        el.className = `kpi-card ${card.color || "purple"}`;
        el.innerHTML = `
          <div class="kpi-label">${card.label}</div>
          <div class="kpi-value">${card.value}</div>
          <div class="kpi-trend">${card.trend}</div>
          <canvas class="kpi-spark-canvas"
            id="${sparks[i]}" height="32"></canvas>`;
        el.classList.remove("shimmer");
      });
    } else {
      // Fallback — use raw values
      const r0 = document.getElementById("kpi-revenue");
      const r1 = document.getElementById("kpi-orders");
      const r2 = document.getElementById("kpi-aov");
      const r3 = document.getElementById("kpi-customers");

      if (r0) {
        r0.innerHTML = `
          <div class="kpi-label">Total Revenue</div>
          <div class="kpi-value">${formatMoney(kpis.total_revenue)}</div>
          <div class="kpi-trend up">▲ All time</div>
          <canvas class="kpi-spark-canvas" id="spark-revenue" height="32"></canvas>`;
        r0.classList.remove("shimmer");
      }
      if (r1) {
        r1.innerHTML = `
          <div class="kpi-label">Total Orders</div>
          <div class="kpi-value">${parseInt(kpis.total_orders || 0).toLocaleString()}</div>
          <div class="kpi-trend">Records</div>
          <canvas class="kpi-spark-canvas" id="spark-orders" height="32"></canvas>`;
        r1.classList.remove("shimmer");
      }
      if (r2) {
        r2.innerHTML = `
          <div class="kpi-label">Avg Order Value</div>
          <div class="kpi-value">${formatMoney(kpis.avg_order_value)}</div>
          <div class="kpi-trend">Per transaction</div>
          <canvas class="kpi-spark-canvas" id="spark-aov" height="32"></canvas>`;
        r2.classList.remove("shimmer");
      }
      if (r3) {
        r3.innerHTML = `
          <div class="kpi-label">Total Customers</div>
          <div class="kpi-value">${parseInt(kpis.total_customers || kpis.total_rows || 0).toLocaleString()}</div>
          <div class="kpi-trend">Unique</div>
          <canvas class="kpi-spark-canvas" id="spark-customers" height="32"></canvas>`;
        r3.classList.remove("shimmer");
      }
    }

    // ── Status pill ──
    const pill = document.getElementById("clean-pill");
    if (pill) {
      pill.textContent =
        "✓ " + parseInt(kpis.total_rows || 0).toLocaleString() +
        " rows · " + (kpis.dept_name || "Sales") +
        " · " + currentPeriod;
    }

    // ── Week banner ──
    renderWeekBanner(kpis.week_vs_last_week || {});

    // ── Top products ──
    renderTopProducts(
      kpis.trending_today || kpis.top_products || []);

    // ── Sparklines ──
    if (kpis.monthly_trend && kpis.monthly_trend.length > 1) {
      const vals = kpis.monthly_trend.map(d => d.revenue || 0);
      setTimeout(() => {
        renderSparkline("spark-revenue",   vals, "#6366f1");
        renderSparkline("spark-orders",    vals, "#10b981");
        renderSparkline("spark-aov",       vals, "#f59e0b");
        renderSparkline("spark-customers", vals, "#3b82f6");
      }, 100);
    }

    // ── Chat suggestions ──
    if (kpis.suggestions) {
      const suggEl = document.getElementById("chat-suggestions");
      if (suggEl) {
        suggEl.innerHTML = kpis.suggestions.map(s =>
          `<button class="sugg-btn" onclick="sendSugg(this)">${s}</button>`
        ).join("");
      }
    }

  } catch (err) {
    console.error("loadKPIs failed:", err);
  }
}

// ─────────────────────────────────────────
// LOAD PERIOD DATA + CHARTS
// ─────────────────────────────────────────
async function loadPeriodData() {
  try {
    const res  = await fetch("/api/period-data?" + buildParams());
    const data = await res.json();
    if (data.error) {
      console.error("Period data error:", data.error);
      return;
    }
    lastPeriodData = data;
    renderAllCharts(data, lastKpis || {});
  } catch (err) {
    console.error("loadPeriodData failed:", err);
  }
}

// ─────────────────────────────────────────
// AI STORY
// ─────────────────────────────────────────
async function loadStory() {
  const body = document.getElementById("story-body");
  if (!body) return;
  body.innerHTML =
    '<div class="story-placeholder">Generating AI analysis...</div>';
  try {
    const res   = await fetch("/api/story?" + buildParams());
    const story = await res.json();

    if (story.error) {
      body.innerHTML =
        `<div class="story-placeholder"
          style="color:#ef4444">${story.error}</div>`;
      return;
    }

    const highlights = (story.highlights || []).map(h =>
      `<span class="story-chip chip-green">${h}</span>`
    ).join("");
    const risks = (story.risks || []).map(r =>
      `<span class="story-chip chip-red">${r}</span>`
    ).join("");

    body.innerHTML = `
      <div class="story-headline">${story.headline || ""}</div>
      <div class="story-summary">${story.summary || ""}</div>
      <div class="story-section-title" style="margin-top:8px">
        Highlights
      </div>
      <div style="margin-bottom:8px">${highlights}</div>
      <div class="story-section-title">Risks</div>
      <div style="margin-bottom:8px">${risks}</div>
      <div class="story-section-title">Recommendation</div>
      <div class="story-summary">${story.recommendation || ""}</div>`;

  } catch (err) {
    body.innerHTML =
      '<div class="story-placeholder" style="color:#ef4444">' +
      'Failed to load story. Check Groq API key.</div>';
  }
}

// ─────────────────────────────────────────
// VIZ PANEL
// ─────────────────────────────────────────
let vizPanelOpen = false;

function toggleVizPanel() {
  vizPanelOpen = !vizPanelOpen;
  const panel = document.getElementById("viz-panel");
  if (panel) panel.classList.toggle("open", vizPanelOpen);
  if (vizPanelOpen) loadVizConfig();
}

async function loadVizConfig() {
  try {
    const res    = await fetch("/api/viz-config?" + buildParams());
    const config = await res.json();
    renderVizPanel(config);
  } catch (err) {
    console.error("Viz config error:", err);
  }
}

function renderVizPanel(config) {
  const recEl = document.getElementById("viz-recommended");
  const avEl  = document.getElementById("viz-available");
  if (!recEl || !avEl) return;

  recEl.innerHTML = (config.recommended || []).map(v => `
    <div class="viz-item active"
      onclick="toggleVizChart('${v.id}', this)">
      <div class="viz-item-icon">📊</div>
      <div>
        <div class="viz-item-title">${v.title}</div>
        <div class="viz-item-desc">${v.description}</div>
      </div>
      <span class="viz-badge">ON</span>
    </div>`).join("");

  avEl.innerHTML = (config.available || []).map(v => `
    <div class="viz-item"
      onclick="addVizChart('${v.type}', this)">
      <div class="viz-item-icon">${v.icon}</div>
      <div>
        <div class="viz-item-title">${v.title}</div>
      </div>
    </div>`).join("");
}

function toggleVizChart(id, el) {
  el.classList.toggle("active");
  const badge = el.querySelector(".viz-badge");
  if (badge) badge.textContent =
    el.classList.contains("active") ? "ON" : "OFF";
  loadPeriodData();
}

function addVizChart(type, el) {
  el.classList.toggle("active");
  if (type === "table") { showDataTable(); return; }
  loadPeriodData();
}

// ─────────────────────────────────────────
// DATA TABLE
// ─────────────────────────────────────────
function showDataTable() {
  const wrap = document.getElementById("data-table-wrap");
  if (!wrap) return;
  wrap.style.display = "block";
  if (lastPeriodData && lastPeriodData.trend) {
    renderDataTable(lastPeriodData.trend, currentPeriod);
  }
  wrap.scrollIntoView({ behavior: "smooth" });
}

function hideDataTable() {
  const wrap = document.getElementById("data-table-wrap");
  if (wrap) wrap.style.display = "none";
}

function showDataTableSidebar() {
  showDataTable();
}

// ─────────────────────────────────────────
// WEEK BANNER
// ─────────────────────────────────────────
function renderWeekBanner(data) {
  if (!data || !data.this_week) return;
  const banner = document.getElementById("week-banner");
  if (banner) banner.style.display = "grid";

  const fmt = n => {
    const v = parseFloat(n) || 0;
    return "$" + (v >= 1000 ? (v/1000).toFixed(1)+"K" : v.toFixed(0));
  };

  const thisEl   = document.getElementById("week-this");
  const lastEl   = document.getElementById("week-last");
  const changeEl = document.getElementById("week-change");

  if (thisEl)   thisEl.textContent   = fmt(data.this_week);
  if (lastEl)   lastEl.textContent   = fmt(data.last_week);
  if (changeEl) {
    changeEl.textContent = (data.change >= 0 ? "▲ +" : "▼ ") +
      (data.change || 0) + "%";
    changeEl.style.color =
      data.direction === "up" ? "#10b981" : "#ef4444";
  }
}

// ─────────────────────────────────────────
// TOP PRODUCTS / ITEMS
// ─────────────────────────────────────────
function renderTopProducts(data) {
  const el = document.getElementById("top-products");
  if (!el) return;

  if (!data || !data.length) {
    el.innerHTML =
      '<p style="font-size:12px;color:#94a3b8;margin-top:10px">' +
      'No product/item data detected</p>';
    return;
  }

  const max = data[0].revenue || 1;
  el.innerHTML = data.map((p, i) => `
    <div class="product-item">
      <div class="product-rank">${i + 1}</div>
      <div class="product-bar-wrap">
        <div class="product-name">${p.product || p.name || "Item " + (i+1)}</div>
        <div class="product-bar">
          <div class="product-bar-fill"
            style="width:${Math.round((p.revenue / max) * 100)}%">
          </div>
        </div>
      </div>
      <div class="product-rev">
        ${formatMoney(p.revenue)}
      </div>
    </div>`).join("");
}
// Populate sidebar slicers
if (kpis.category_breakdown)
  populateCategorySlicer(kpis.category_breakdown);
if (kpis.region_breakdown)
  populateRegionSlicer(kpis.region_breakdown);

// ─────────────────────────────────────────
// INIT DASHBOARD
// ─────────────────────────────────────────
if (isDashboard) {
  document.addEventListener("DOMContentLoaded", () => {
    loadAll();
    resetRefreshTimer();
  });
}