// ─────────────────────────────────────────
// AI ASSISTANT STATE
// ─────────────────────────────────────────
let assistantOpen    = false;
let activeTab        = "chat";
let chatHistory      = [];
let insightsLoaded   = false;
let chartsLoaded     = false;
let predictLoaded    = false;
let isTyping         = false;

// ─────────────────────────────────────────
// TOGGLE ASSISTANT
// ─────────────────────────────────────────
function toggleAssistant() {
  assistantOpen = !assistantOpen;
  const win = document.getElementById("ai-assistant-window");
  const badge = document.getElementById("ai-fab-badge");
  if (!win) return;
  win.classList.toggle("open", assistantOpen);
  if (assistantOpen && badge) badge.style.display = "none";
  if (assistantOpen && activeTab === "insights" && !insightsLoaded) {
    loadInsights();
  }
}

function closeAssistant() {
  assistantOpen = false;
  const win = document.getElementById("ai-assistant-window");
  if (win) win.classList.remove("open");
}

// ─────────────────────────────────────────
// TABS
// ─────────────────────────────────────────
function switchAiTab(tab) {
  activeTab = tab;
  document.querySelectorAll(".ai-tab")
    .forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".ai-panel")
    .forEach(p => p.classList.remove("active"));

  const tabEl   = document.getElementById("ai-tab-"   + tab);
  const panelEl = document.getElementById("ai-panel-" + tab);
  if (tabEl)   tabEl.classList.add("active");
  if (panelEl) panelEl.classList.add("active");

  if (tab === "insights" && !insightsLoaded) loadInsights();
  if (tab === "charts"   && !chartsLoaded)   loadChartSuggestions();
  if (tab === "predict"  && !predictLoaded)  loadPredictions();
}

// ─────────────────────────────────────────
// CHAT
// ─────────────────────────────────────────
function sendAiChat() {
  const input = document.getElementById("ai-chat-input");
  if (!input) return;
  const text = input.value.trim();
  if (!text || isTyping) return;
  input.value = "";

  addAiMsg(text, "user");
  chatHistory.push({ role: "user", content: text });
  showAiTyping();

  fetch("/api/chat", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      message: text,
      history: chatHistory
    })
  })
  .then(r => r.json())
  .then(data => {
    removeAiTyping();
    const reply = data.reply || data.error || "I apologise, something went wrong.";
    addAiMsg(reply, "bot");
    chatHistory.push({ role: "assistant", content: reply });
  })
  .catch(() => {
    removeAiTyping();
    addAiMsg("Connection error. Please try again.", "bot");
  });
}

function sendAiSugg(text) {
  const input = document.getElementById("ai-chat-input");
  if (input) input.value = text;
  sendAiChat();
}

function addAiMsg(text, type) {
  const msgs = document.getElementById("ai-messages");
  if (!msgs) return;

  const now  = new Date().toLocaleTimeString(
    [], { hour: "2-digit", minute: "2-digit" });
  const wrap = document.createElement("div");
  wrap.className = `ai-msg ${type}`;

  if (type === "bot") {
    wrap.innerHTML = `
      <div class="ai-msg-avatar bot">
        <svg viewBox="0 0 16 16">
          <path d="M8 1L10.5 6H15L11.5 9.5L13 14L8 11L3 14L4.5 9.5L1 6H5.5Z"/>
        </svg>
      </div>
      <div>
        <div class="ai-msg-bubble">${formatAiMsg(text)}</div>
        <div class="ai-msg-time">${now}</div>
      </div>`;
  } else {
    wrap.innerHTML = `
      <div>
        <div class="ai-msg-bubble">${text}</div>
        <div class="ai-msg-time" style="text-align:right">${now}</div>
      </div>
      <div class="ai-msg-avatar user-av">You</div>`;
  }

  msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight;
}

function formatAiMsg(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g,     "<em>$1</em>")
    .replace(/`(.*?)`/g,
      "<code style='background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:11px'>$1</code>")
    .replace(/Suggested next step:/g,
      "<span style='color:#1e40af;font-weight:600'>→ Suggested next step:</span>")
    .replace(/\n/g, "<br>");
}

function showAiTyping() {
  isTyping = true;
  const msgs = document.getElementById("ai-messages");
  if (!msgs) return;
  const el = document.createElement("div");
  el.className = "ai-msg bot";
  el.id = "ai-typing-indicator";
  el.innerHTML = `
    <div class="ai-msg-avatar bot">
      <svg viewBox="0 0 16 16">
        <path d="M8 1L10.5 6H15L11.5 9.5L13 14L8 11L3 14L4.5 9.5L1 6H5.5Z"/>
      </svg>
    </div>
    <div class="ai-typing-dots">
      <span></span><span></span><span></span>
    </div>`;
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeAiTyping() {
  isTyping = false;
  const el = document.getElementById("ai-typing-indicator");
  if (el) el.remove();
}

// ─────────────────────────────────────────
// AUTO INSIGHTS
// ─────────────────────────────────────────
async function loadInsights() {
  const panel = document.getElementById("ai-insights-content");
  if (!panel) return;

  panel.innerHTML = `
    <div class="insights-loading">
      <div class="insights-spinner"></div>
      <span>Generating insights with AI...</span>
    </div>`;

  try {
    const res  = await fetch("/api/auto-insights");
    const data = await res.json();

    if (data.error) {
      panel.innerHTML = `
        <div class="insights-loading">
          <div style="font-size:24px">⚠️</div>
          <span style="color:#ef4444">${data.error}</span>
        </div>`;
      return;
    }

    insightsLoaded = true;
    const insights = data.insights || [];

    panel.innerHTML = insights.map(ins => `
      <div class="insight-card ${ins.type}">
        <div class="insight-card-header">
          <span class="insight-icon">${ins.icon}</span>
          <span class="insight-title">${ins.title}</span>
          <span class="insight-badge ${ins.type}">
            ${ins.type}
          </span>
        </div>
        <div class="insight-message">${ins.message}</div>
        <div class="insight-action">${ins.action}</div>
      </div>`).join("");

  } catch (err) {
    panel.innerHTML = `
      <div class="insights-loading">
        <div style="font-size:24px">❌</div>
        <span>Failed to load insights</span>
      </div>`;
  }
}

// ─────────────────────────────────────────
// CHART SUGGESTIONS
// ─────────────────────────────────────────
async function loadChartSuggestions() {
  const panel = document.getElementById("ai-charts-content");
  if (!panel) return;

  panel.innerHTML = `
    <div class="insights-loading">
      <div class="insights-spinner"></div>
      <span>Analysing data for chart recommendations...</span>
    </div>`;

  const chartIcons = {
    area:     "📈",
    bar:      "📊",
    doughnut: "🍩",
    donut:    "🍩",
    scatter:  "✦",
    heatmap:  "🔥",
    line:     "📉",
    pie:      "🥧",
    table:    "📋"
  };

  try {
    const res  = await fetch("/api/chart-suggestions");
    const data = await res.json();

    if (data.error) {
      panel.innerHTML = `
        <div class="insights-loading">
          <span style="color:#ef4444">${data.error}</span>
        </div>`;
      return;
    }

    chartsLoaded = true;
    const suggestions = data.suggestions || [];

    panel.innerHTML = suggestions.map((s, i) => `
      <div class="chart-sugg-card"
        onclick="applyChartSuggestion('${s.chart_type}')">
        <div class="chart-sugg-icon">
          ${chartIcons[s.chart_type] || "📊"}
        </div>
        <div class="chart-sugg-info">
          <div class="chart-sugg-title">${s.title}</div>
          <div class="chart-sugg-reason">${s.reason}</div>
        </div>
        <span class="chart-sugg-badge">
          #${s.priority || i+1}
        </span>
      </div>`).join("");

  } catch (err) {
    panel.innerHTML = `
      <div class="insights-loading">
        <span>Failed to load chart suggestions</span>
      </div>`;
  }
}

function applyChartSuggestion(chartType) {
  closeAssistant();
  if (typeof loadPeriodData === "function") {
    loadPeriodData();
  }
  addAiMsg(
    `I have highlighted the **${chartType} chart** recommendation. ` +
    `Check your dashboard for the visualisation. ` +
    `Suggested next step: Review the chart and compare with other metrics.`,
    "bot"
  );
  switchAiTab("chat");
  setTimeout(() => {
    const win = document.getElementById("ai-assistant-window");
    if (win) win.classList.add("open");
    assistantOpen = true;
  }, 300);
}

// ─────────────────────────────────────────
// PREDICTIONS
// ─────────────────────────────────────────
async function loadPredictions() {
  const panel = document.getElementById("ai-predict-content");
  if (!panel) return;

  panel.innerHTML = `
    <div class="insights-loading">
      <div class="insights-spinner"></div>
      <span>Generating trend predictions...</span>
    </div>`;

  const dirIcons = { up: "📈", down: "📉" };

  try {
    const res  = await fetch("/api/predictions");
    const data = await res.json();

    if (data.error) {
      panel.innerHTML = `
        <div class="insights-loading">
          <span style="color:#ef4444">${data.error}</span>
        </div>`;
      return;
    }

    predictLoaded = true;
    const preds   = data.predictions || [];
    const summary = data.summary     || "";

    let html = "";

    if (summary) {
      html += `
        <div class="pred-summary">
          <div class="pred-summary-label">Overall Forecast</div>
          ${summary}
        </div>`;
    }

    html += preds.map(p => `
      <div class="pred-card">
        <div class="pred-card-header">
          <span class="pred-metric">${p.metric}</span>
          <span class="pred-confidence ${p.confidence}">
            ${p.confidence} confidence
          </span>
        </div>
        <div class="pred-values">
          <div class="pred-val-item">
            <div class="pred-val-label">Current</div>
            <div class="pred-val-num">${p.current}</div>
          </div>
          <div class="pred-direction">
            ${dirIcons[p.direction] || "➡️"}
          </div>
          <div class="pred-val-item">
            <div class="pred-val-label">Predicted</div>
            <div class="pred-val-num"
              style="color:${p.direction === 'up'
                ? '#10b981' : '#ef4444'}">
              ${p.predicted}
            </div>
          </div>
        </div>
        <div class="pred-reasoning">${p.reasoning}</div>
      </div>`).join("");

    panel.innerHTML = html;

  } catch (err) {
    panel.innerHTML = `
      <div class="insights-loading">
        <span>Failed to load predictions</span>
      </div>`;
  }
}

function refreshInsights() {
  insightsLoaded = false;
  chartsLoaded   = false;
  predictLoaded  = false;
  if (activeTab === "insights") loadInsights();
  if (activeTab === "charts")   loadChartSuggestions();
  if (activeTab === "predict")  loadPredictions();
}

// ─────────────────────────────────────────
// EXISTING CHAT PANEL FUNCTIONS
// (keep these for the right-side chat panel)
// ─────────────────────────────────────────
function sendSugg(btn) {
  if (!btn) return;
  const text = btn.textContent.trim();
  const sugg = document.getElementById("chat-suggestions");
  if (sugg) sugg.style.display = "none";
  addChatMsg(text, "user");
  chatHistory.push({ role: "user", content: text });
  showTyping();
  fetchReply(text);
}

function sendChat() {
  const input = document.getElementById("chat-input");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addChatMsg(text, "user");
  chatHistory.push({ role: "user", content: text });
  showTyping();
  fetchReply(text);
}

function fetchReply(message) {
  fetch("/api/chat", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      message,
      history: chatHistory
    })
  })
  .then(r => r.json())
  .then(data => {
    removeTyping();
    const reply = data.reply || data.error || "Sorry, something went wrong.";
    addChatMsg(reply, "ai");
    chatHistory.push({ role: "assistant", content: reply });
  })
  .catch(() => {
    removeTyping();
    addChatMsg("Connection error. Please try again.", "ai");
  });
}

function addChatMsg(text, type) {
  const msgs = document.getElementById("chat-messages");
  if (!msgs) return;
  const el   = document.createElement("div");
  el.className = `chat-msg ${type}`;
  el.textContent = text;
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
  const msgs = document.getElementById("chat-messages");
  if (!msgs) return;
  const el = document.createElement("div");
  el.className = "chat-typing";
  el.id = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}