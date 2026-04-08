const chatHistory = [];

function sendSugg(btn) {
  const text = btn.textContent;
  document.getElementById("chat-suggestions").style.display = "none";
  addChatMsg(text, "user");
  chatHistory.push({ role: "user", content: text });
  showTyping();
  fetchReply(text);
}

function sendChat() {
  const input = document.getElementById("chat-input");
  const text  = input.value.trim();
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
    body:    JSON.stringify({ message, history: chatHistory })
  })
  .then(r => r.json())
  .then(data => {
    removeTyping();
    const reply = data.reply || data.error || "Sorry, something went wrong.";
    addChatMsg(reply, "ai");
    chatHistory.push({ role: "assistant", content: reply });
  })
  .catch(() => { removeTyping(); addChatMsg("Connection error. Please try again.", "ai"); });
}

function addChatMsg(text, type) {
  const el  = document.createElement("div");
  el.className = `chat-msg ${type}`;
  el.textContent = text;
  const msgs = document.getElementById("chat-messages");
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
  const el = document.createElement("div");
  el.className = "chat-typing"; el.id = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  const msgs = document.getElementById("chat-messages");
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}