// ─────────────────────────────────────────
// CHART INSTANCES
// ─────────────────────────────────────────
const chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

function safeLabel(val) {
  if (val === null || val === undefined) return "Unknown";
  const s = String(val).trim();
  if (s === "" || s === "null" || s === "undefined") return "Unknown";
  if (!isNaN(val) && String(val).length <= 4) return "Code " + val;
  if (s.length > 30) return s.substring(0, 28) + "..";
  return s;
}

function safeNum(val) {
  const n = parseFloat(val);
  return isNaN(n) ? 0 : Math.round(n * 100) / 100;
}

function fmtAxis(v) {
  if (v >= 1_000_000_000) return "$" + (v / 1_000_000_000).toFixed(1) + "B";
  if (v >= 1_000_000)     return "$" + (v / 1_000_000).toFixed(1)     + "M";
  if (v >= 1_000)         return "$" + (v / 1_000).toFixed(1)         + "K";
  return "$" + v;
}

function noData(containerId, msg) {
  const wrap = document.getElementById(containerId + "-wrap")
             || document.getElementById(containerId);
  if (!wrap) return;
  wrap.innerHTML =
    `<div style="display:flex;align-items:center;justify-content:center;
      height:160px;font-size:12px;color:#94a3b8;text-align:center;
      padding:16px;flex-direction:column;gap:8px">
      <div style="font-size:24px">📊</div>
      <div>${msg}</div>
    </div>`;
}

const CHART_COLORS = [
  "#6366f1","#10b981","#f59e0b","#ef4444",
  "#06b6d4","#8b5cf6","#ec4899","#14b8a6",
  "#f97316","#84cc16","#3b82f6","#a855f7"
];

// ─────────────────────────────────────────
// RENDER ALL CHARTS
// ─────────────────────────────────────────
function renderAllCharts(periodData, kpis) {
  const grid = document.getElementById("chart-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const trend    = periodData.trend    || [];
  const cats     = periodData.category_breakdown
                || (kpis && kpis.category_breakdown) || [];
  const regions  = periodData.region_breakdown
                || (kpis && kpis.region_breakdown)   || [];
  const products = periodData.top_products
                || (kpis && kpis.top_products)        || [];
  const scatter  = periodData.scatter  || [];
  const heatmap  = periodData.heatmap  || null;

  // ── Area chart — trend ──
  if (trend.length > 0) {
    addCard(grid, "area-trend", "full-width", "Revenue trend", "Total performance over time");
    setTimeout(() => renderAreaChart("area-trend-canvas", trend), 50);
  }

  // ── Bar chart — categories ──
  if (cats.length > 0) {
    addCard(grid, "bar-cat", "half-width", "Breakdown by category", "Revenue by category");
    setTimeout(() => renderBarChart("bar-cat-canvas", cats, "category", "revenue"), 50);
  }

  // ── Doughnut — regions ──
  if (regions.length > 0) {
    addCard(grid, "donut-region", "half-width", "Regional distribution", "Revenue share by region");
    setTimeout(() => renderDonutChart("donut-region-canvas", regions.slice(0, 8), "region", "revenue"), 50);
  }

  // ── Orders trend ──
  if (trend.length > 0) {
    addCard(grid, "orders-trend", "half-width", "Order volume trend", "Number of records per period");
    setTimeout(() => renderOrdersChart("orders-trend-canvas", trend), 50);
  }

  // ── Heatmap ──
  if (heatmap && heatmap.days && heatmap.days.length > 1 && heatmap.hours && heatmap.hours.length > 1) {
    addCard(grid, "heatmap", "half-width", "Activity heatmap", "Performance by day and time");
    setTimeout(() => renderHeatmap("heatmap-wrap", heatmap), 50);
  }

  // ── Scatter ──
  if (scatter.length > 5) {
    addCard(grid, "scatter", "half-width", "Correlation analysis", "Value vs Quantity relationship");
    setTimeout(() => renderScatter("scatter-canvas", scatter), 50);
  }

  // ── Top products bar ──
  if (products.length > 0) {
    addCard(grid, "top-bar", "half-width", "Top items", "Highest performing items");
    setTimeout(() => renderTopBar("top-bar-canvas", products), 50);
  }
}

// ─────────────────────────────────────────
// ADD CARD TO GRID
// ─────────────────────────────────────────
function addCard(grid, id, width, title, sub) {
  const card = document.createElement("div");
  card.className = `chart-card ${width}`;
  card.innerHTML = `
    <div class="chart-card-header">
      <div>
        <div class="chart-title">${title}</div>
        <div class="chart-sub">${sub}</div>
      </div>
    </div>
    <div class="chart-wrap" id="${id}-wrap" style="height:180px;position:relative">
      <canvas id="${id}-canvas"></canvas>
    </div>`;
  grid.appendChild(card);
}

// ─────────────────────────────────────────
// AREA CHART
// ─────────────────────────────────────────
function renderAreaChart(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  const labels = data.map(d => d.period || d.month || d.day || "");
  const values = data.map(d => safeNum(d.total_revenue || d.revenue || 0));

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label:           "Revenue",
        data:            values,
        borderColor:     "#6366f1",
        backgroundColor: "rgba(99,102,241,0.1)",
        borderWidth:     2,
        fill:            true,
        tension:         0.4,
        pointRadius:     4,
        pointBackgroundColor: "#6366f1",
        pointHoverRadius: 6,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => " " + fmtAxis(ctx.parsed.y)
          }
        }
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: { font: { size: 9 }, color: "#94a3b8", maxRotation: 45 }
        },
        y: {
          grid:  { color: "rgba(0,0,0,0.04)" },
          ticks: { font: { size: 9 }, color: "#94a3b8", callback: fmtAxis }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// ORDERS CHART
// ─────────────────────────────────────────
function renderOrdersChart(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels:   data.map(d => d.period || d.month || ""),
      datasets: [{
        label:           "Orders",
        data:            data.map(d => safeNum(d.order_count || d.orders || 0)),
        backgroundColor: "rgba(16,185,129,0.7)",
        borderRadius:    4,
        borderSkipped:   false,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 }, color: "#94a3b8", maxRotation: 45 } },
        y: { grid: { color: "rgba(0,0,0,0.04)" }, ticks: { font: { size: 9 }, color: "#94a3b8" } }
      }
    }
  });
}

// ─────────────────────────────────────────
// BAR CHART (horizontal)
// ─────────────────────────────────────────
function renderBarChart(canvasId, data, labelKey, valueKey) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  const labels = data.map(d => safeLabel(d[labelKey]));
  const values = data.map(d => safeNum(d[valueKey]));

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data:            values,
        backgroundColor: CHART_COLORS.slice(0, data.length),
        borderRadius:    4,
        borderSkipped:   false,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      indexAxis:           "y",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => " " + fmtAxis(ctx.parsed.x) } }
      },
      scales: {
        x: {
          grid:  { color: "rgba(0,0,0,0.04)" },
          ticks: { font: { size: 9 }, color: "#94a3b8", callback: fmtAxis }
        },
        y: {
          grid:  { display: false },
          ticks: { font: { size: 9 }, color: "#64748b" }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// TOP ITEMS BAR
// ─────────────────────────────────────────
function renderTopBar(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  const labels = data.map(d => safeLabel(d.product || d.name || d.item || ""));
  const values = data.map(d => safeNum(d.revenue || d.value || 0));

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data:            values,
        backgroundColor: CHART_COLORS.slice(0, data.length),
        borderRadius:    4,
        borderSkipped:   false,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      indexAxis:           "y",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => " " + fmtAxis(ctx.parsed.x) } }
      },
      scales: {
        x: {
          grid:  { color: "rgba(0,0,0,0.04)" },
          ticks: { font: { size: 9 }, color: "#94a3b8", callback: fmtAxis }
        },
        y: {
          grid:  { display: false },
          ticks: { font: { size: 9 }, color: "#64748b" }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// DOUGHNUT CHART
// ─────────────────────────────────────────
function renderDonutChart(canvasId, data, labelKey, valueKey) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  const labels = data.map(d => safeLabel(d[labelKey]));
  const values = data.map(d => safeNum(d[valueKey]));

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data:            values,
        backgroundColor: CHART_COLORS.slice(0, data.length),
        borderWidth:     2,
        borderColor:     "#fff",
        hoverOffset:     4,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            font:      { size: 10 },
            padding:   8,
            color:     "#64748b",
            boxWidth:  10,
            generateLabels: chart => {
              const data = chart.data;
              return data.labels.map((label, i) => ({
                text:            label.length > 15 ? label.slice(0,13)+".." : label,
                fillStyle:       data.datasets[0].backgroundColor[i],
                strokeStyle:     "#fff",
                lineWidth:       1,
                index:           i
              }));
            }
          }
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${fmtAxis(ctx.parsed)}`
          }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// SCATTER CHART
// ─────────────────────────────────────────
function renderScatter(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.length) return;
  destroyChart(canvasId);

  chartInstances[canvasId] = new Chart(canvas.getContext("2d"), {
    type: "scatter",
    data: {
      datasets: [{
        label:           "Data points",
        data:            data.map(d => ({ x: safeNum(d.x), y: safeNum(d.y) })),
        backgroundColor: "rgba(99,102,241,0.4)",
        pointRadius:     4,
        pointHoverRadius: 6,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid:  { color: "rgba(0,0,0,0.04)" },
          ticks: { font: { size: 9 }, color: "#94a3b8", callback: fmtAxis }
        },
        y: {
          grid:  { color: "rgba(0,0,0,0.04)" },
          ticks: { font: { size: 9 }, color: "#94a3b8" }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// HEATMAP
// ─────────────────────────────────────────
function renderHeatmap(containerId, data) {
  const wrap = document.getElementById(containerId);
  if (!wrap || !data) return;
  if (!data.days || data.days.length < 2 ||
      !data.hours || data.hours.length < 2) {
    wrap.innerHTML =
      `<div style="display:flex;align-items:center;justify-content:center;
        height:160px;font-size:12px;color:#94a3b8">
        Not enough time data for heatmap
      </div>`;
    return;
  }

  const maxVal = Math.max(...data.data.flat().map(Number));

  const getColor = v => {
    if (!v || v === 0) return "rgba(99,102,241,0.05)";
    const intensity = Math.min(v / maxVal, 1);
    return `rgba(99,102,241,${(0.15 + intensity * 0.85).toFixed(2)})`;
  };

  const getTextColor = v => {
    if (!v || v === 0) return "transparent";
    const intensity = v / maxVal;
    return intensity > 0.5 ? "#fff" : "#6366f1";
  };

  let html = `
    <div style="overflow-x:auto;padding:4px">
    <table style="border-collapse:collapse;width:100%;font-size:9px">
      <thead>
        <tr>
          <th style="width:70px;text-align:right;padding:3px 6px 3px 0;color:#94a3b8"></th>
          ${data.hours.map(h =>
            `<th style="text-align:center;padding:2px;color:#94a3b8;font-weight:400">${h}h</th>`
          ).join("")}
        </tr>
      </thead>
      <tbody>`;

  data.days.forEach((day, i) => {
    html += `<tr>
      <td style="text-align:right;padding:3px 6px 3px 0;
        color:#64748b;font-weight:500;white-space:nowrap">
        ${day.slice(0, 3)}
      </td>`;
    data.hours.forEach((h, j) => {
      const v   = Number(data.data[i]?.[j] || 0);
      const col = getColor(v);
      const txt = getTextColor(v);
      const lbl = v > 0
        ? (v >= 1_000_000 ? (v/1_000_000).toFixed(1)+"M"
          : v >= 1_000 ? (v/1_000).toFixed(0)+"K"
          : Math.round(v))
        : "";
      html += `<td style="background:${col};color:${txt};
        text-align:center;padding:3px 2px;border-radius:3px;
        min-width:24px;height:22px">${lbl}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table></div>`;
  wrap.innerHTML = html;
}

// ─────────────────────────────────────────
// SPARKLINE (for KPI cards)
// ─────────────────────────────────────────
function renderSparkline(canvasId, data, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data || data.length < 2) return;
  if (chartInstances["spark_" + canvasId]) {
    chartInstances["spark_" + canvasId].destroy();
  }
  chartInstances["spark_" + canvasId] = new Chart(
    canvas.getContext("2d"), {
    type: "line",
    data: {
      labels:   data.map((_, i) => i),
      datasets: [{
        data:        data.map(v => safeNum(v)),
        borderColor: color,
        borderWidth: 1.5,
        fill:        false,
        tension:     0.4,
        pointRadius: 0,
      }]
    },
    options: {
      responsive:          false,
      animation:           false,
      plugins: {
        legend:  { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  });
}

// ─────────────────────────────────────────
// DATA TABLE
// ─────────────────────────────────────────
function renderDataTable(data, period) {
  const container = document.getElementById("data-table-container");
  if (!container) return;
  if (!data || !data.length) {
    container.innerHTML =
      "<p style='font-size:12px;color:#94a3b8;padding:12px'>No data available</p>";
    return;
  }

  const keys = Object.keys(data[0]);
  let html = `
    <table class="dash-table">
      <thead>
        <tr>${keys.map(k =>
          `<th>${k.replace(/_/g," ")}</th>`
        ).join("")}</tr>
      </thead>
      <tbody>`;

  data.slice(0, 50).forEach(row => {
    html += `<tr>${keys.map(k => {
      const v = row[k];
      if (typeof v === "number") {
        return `<td>${v >= 1000 ? v.toLocaleString() : v}</td>`;
      }
      return `<td>${v !== null && v !== undefined ? v : "—"}</td>`;
    }).join("")}</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;

  const sub = document.getElementById("table-sub");
  if (sub) sub.textContent =
    `Showing ${Math.min(data.length, 50)} of ${data.length} records · ${period} view`;
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
    if (v >= 1_000_000_000) return "$" + (v/1_000_000_000).toFixed(1) + "B";
    if (v >= 1_000_000)     return "$" + (v/1_000_000).toFixed(1)     + "M";
    if (v >= 1_000)         return "$" + (v/1_000).toFixed(1)         + "K";
    return "$" + v.toFixed(0);
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
// TOP PRODUCTS LIST (sidebar panel)
// ─────────────────────────────────────────
function renderTopProducts(data) {
  const el = document.getElementById("top-products");
  if (!el) return;

  if (!data || !data.length) {
    el.innerHTML =
      `<p style="font-size:12px;color:#94a3b8;margin-top:10px;padding:8px">
        No item data detected
      </p>`;
    return;
  }

  const max = safeNum(data[0].revenue || data[0].value || 1);
  el.innerHTML = data.map((p, i) => {
    const name  = safeLabel(
      p.product || p.name || p.item || p.title || ("Item " + (i+1)));
    const rev   = safeNum(p.revenue || p.value || 0);
    const width = max > 0 ? Math.round((rev / max) * 100) : 0;
    return `
      <div class="product-item">
        <div class="product-rank">${i + 1}</div>
        <div class="product-bar-wrap">
          <div class="product-name">${name}</div>
          <div class="product-bar">
            <div class="product-bar-fill"
              style="width:${width}%"></div>
          </div>
        </div>
        <div class="product-rev">${fmtAxis(rev)}</div>
      </div>`;
  }).join("");
}