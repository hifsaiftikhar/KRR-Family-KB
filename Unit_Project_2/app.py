"""
Flask Web Interface for Unit Project 2
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import main

# Initialize components
main.kb_global = main.load_prolog_kb()
bot = main.load_aiml_bot()

app = Flask(__name__)

# Premium, modern glassmorphic HTML/CSS/JS template with KB facts viewer
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dynamic Family KB Agent — Unit 2</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #0b0f19;
      --glass-bg: rgba(255, 255, 255, 0.04);
      --glass-border: rgba(255, 255, 255, 0.08);
      --primary: hsl(142, 70%, 45%); /* Emerald theme for learning */
      --primary-hover: hsl(142, 70%, 55%);
      --accent: hsl(190, 90%, 50%);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(circle at 50% 0%, #11221a 0%, var(--bg-color) 75%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: var(--glass-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--glass-border);
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    header h1 {
      font-size: 1.4rem;
      font-weight: 700;
      background: linear-gradient(135deg, #fff 30%, var(--primary-hover));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    header p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .badge {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid var(--primary);
      color: var(--primary-hover);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .container {
      max-width: 1080px;
      width: 100%;
      margin: 24px auto;
      padding: 0 16px;
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 16px;
    }

    @media (max-width: 768px) {
      .container {
        grid-template-columns: 1fr;
      }
    }

    .left-column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .tabs {
      display: flex;
      gap: 8px;
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      padding: 4px;
      border-radius: 12px;
      width: fit-content;
    }

    .tab {
      padding: 8px 18px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    .tab.active {
      background: var(--primary);
      color: white;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .panel {
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 24px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      display: flex;
      flex-direction: column;
      flex: 1;
      min-height: 460px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .panel.hidden { display: none; }

    /* Chat Section */
    #chat-box {
      flex: 1;
      height: 360px;
      overflow-y: auto;
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 16px;
      background: rgba(0, 0, 0, 0.2);
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .msg {
      max-width: 80%;
      line-height: 1.5;
      padding: 10px 16px;
      border-radius: 14px;
      font-size: 0.95rem;
      animation: fadeIn 0.3s ease forwards;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .msg.user {
      align-self: flex-end;
      background: var(--primary);
      color: white;
      border-bottom-right-radius: 4px;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }

    .msg.bot {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--glass-border);
      color: var(--text);
      border-bottom-left-radius: 4px;
    }

    .msg-label {
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .input-row {
      display: flex;
      gap: 8px;
    }

    .input-row input {
      flex: 1;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--glass-border);
      border-radius: 10px;
      color: var(--text);
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.3s;
    }

    .input-row input:focus {
      border-color: var(--primary);
    }

    .input-row button {
      padding: 12px 24px;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s;
    }

    .input-row button:hover {
      background: var(--primary-hover);
      transform: translateY(-1px);
    }

    /* Prolog Section */
    #prolog-input {
      width: 100%;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--glass-border);
      border-radius: 10px;
      color: var(--accent);
      font-family: monospace;
      font-size: 1rem;
      margin-bottom: 12px;
      outline: none;
    }

    #prolog-input:focus {
      border-color: var(--accent);
    }

    #prolog-result {
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid var(--glass-border);
      color: #34d399;
      font-family: monospace;
      font-size: 0.95rem;
      padding: 16px;
      border-radius: 10px;
      min-height: 120px;
      white-space: pre-wrap;
      margin-top: 16px;
    }

    .hint {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 12px;
    }

    .query-examples {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 14px;
    }

    .ex {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--glass-border);
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .ex:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text);
    }

    /* Side Panel - Facts list */
    .side-panel {
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: calc(100vh - 120px);
      overflow-y: auto;
    }

    .side-panel h3 {
      font-size: 1.1rem;
      font-weight: 600;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 8px;
      color: var(--accent);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .refresh-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.75rem;
      font-weight: 500;
    }

    .refresh-btn:hover { color: var(--accent); }

    .facts-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-family: monospace;
      font-size: 0.85rem;
    }

    .fact-item {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.04);
      padding: 6px 10px;
      border-radius: 6px;
      color: #34d399;
      animation: flashGreen 1s ease-out;
    }

    @keyframes flashGreen {
      0% { background: rgba(16, 185, 129, 0.3); }
      100% { background: rgba(255, 255, 255, 0.02); }
    }

    .empty-facts {
      color: var(--text-muted);
      font-style: italic;
      font-size: 0.85rem;
      text-align: center;
      padding: 20px 0;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Family Knowledge Base Agent</h1>
      <p>Unit Project 2: Dynamic Prolog KB (Live Learning)</p>
    </div>
    <span class="badge">Part 2</span>
  </header>

  <div class="container">
    <div class="left-column">
      <div class="tabs">
        <button class="tab active" onclick="showTab('chat')">AIML Chatbot</button>
        <button class="tab" onclick="showTab('prolog')">Prolog Query Terminal</button>
      </div>

      <!-- CHAT PANEL -->
      <div class="panel" id="panel-chat">
        <div id="chat-box"></div>
        <div class="input-row">
          <input id="chat-input" placeholder="Teach facts (e.g. John is the father of Mike) or ask queries..."
                 onkeydown="if(event.key==='Enter') sendChat()">
          <button onclick="sendChat()">Send</button>
        </div>
        <div class="query-examples">
          <span class="ex" onclick="fillChat('Ali is the father of Hassan')">Learn: Ali father of Hassan</span>
          <span class="ex" onclick="fillChat('Fatima is the mother of Hassan')">Learn: Fatima mother of Hassan</span>
          <span class="ex" onclick="fillChat('Ali was born in 1950')">Learn: Ali born in 1950</span>
          <span class="ex" onclick="fillChat('Who is the father of Hassan?')">Query: Father of Hassan?</span>
          <span class="ex" onclick="fillChat('Who are the siblings of Hassan?')">Query: Siblings of Hassan?</span>
        </div>
      </div>

      <!-- PROLOG PANEL -->
      <div class="panel hidden" id="panel-prolog">
        <p class="hint">Enter a query in Pytholog/Prolog format. Use uppercase letters for variables.</p>
        <input id="prolog-input" placeholder="e.g. father(X, hassan)" value="father(X, hassan)">
        <button onclick="sendProlog()"
                style="padding:12px 24px; background:var(--accent); color:#0b0f19; border:none;
                       border-radius:10px; cursor:pointer; font-weight:600; width:fit-content; transition:0.3s;">
          Execute Prolog Query
        </button>
        <div id="prolog-result">Query results will be displayed here...</div>
        <div class="query-examples">
          <span class="ex" onclick="fillProlog('father(X, Y)')">father(X, Y)</span>
          <span class="ex" onclick="fillProlog('male(X)')">male(X)</span>
          <span class="ex" onclick="fillProlog('sibling(X, Y)')">sibling(X, Y)</span>
        </div>
      </div>
    </div>

    <!-- SIDE PANEL: LIVE FACTS -->
    <div class="side-panel">
      <h3>
        <span>Dynamic Facts KB</span>
        <button class="refresh-btn" onclick="refreshFacts()">refresh</button>
      </h3>
      <div class="facts-list" id="facts-container">
        <div class="empty-facts">No facts stored in family_kb.pl yet. Teach me some!</div>
      </div>
    </div>
  </div>

  <script>
    let currentFacts = [];

    function showTab(name) {
      document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', (i === 0 && name === 'chat') || (i === 1 && name === 'prolog'));
      });
      document.getElementById('panel-chat').classList.toggle('hidden', name !== 'chat');
      document.getElementById('panel-prolog').classList.toggle('hidden', name !== 'prolog');
    }

    function addMsg(who, text) {
      const box = document.getElementById('chat-box');
      const div = document.createElement('div');
      div.className = 'msg ' + who;
      div.innerHTML = `<div class="msg-label">${who === 'user' ? 'You' : 'Bot'}</div>${text}`;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }

    function fillChat(text) {
      document.getElementById('chat-input').value = text;
      document.getElementById('chat-input').focus();
    }

    function fillProlog(text) {
      document.getElementById('prolog-input').value = text;
      document.getElementById('prolog-input').focus();
    }

    async function sendChat() {
      const inp = document.getElementById('chat-input');
      const text = inp.value.trim();
      if (!text) return;
      addMsg('user', text);
      inp.value = '';
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      });
      const data = await res.json();
      addMsg('bot', data.response);
      refreshFacts();
    }

    async function sendProlog() {
      const query = document.getElementById('prolog-input').value.trim();
      if (!query) return;
      const res = await fetch('/prolog', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query})
      });
      const data = await res.json();
      document.getElementById('prolog-result').textContent = data.result;
    }

    async function refreshFacts() {
      const res = await fetch('/get_facts');
      const data = await res.json();
      const container = document.getElementById('facts-container');
      
      if (!data.facts || data.facts.length === 0) {
        container.innerHTML = '<div class="empty-facts">No facts stored in family_kb.pl yet. Teach me some!</div>';
        currentFacts = [];
        return;
      }
      
      let html = '';
      data.facts.forEach(fact => {
        // If it's a new fact, it flashes
        const isNew = !currentFacts.includes(fact);
        html += `<div class="fact-item" style="${isNew ? 'animation: flashGreen 1s ease-out;' : ''}">${fact}</div>`;
      });
      container.innerHTML = html;
      currentFacts = data.facts;
    }

    // Welcome message
    addMsg('bot', 'Hello! I am your Dynamic Prolog Chatbot. Teach me family relationships and I will write them to family_kb.pl live!');
    
    // Initial fetch
    refreshFacts();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    reply = main.process_interaction(main.kb_global, bot, user_msg)
    return jsonify({"response": reply})

@app.route("/prolog", methods=["POST"])
def prolog_query():
    data = request.get_json()
    query = data.get("query", "").strip()
    result = main.query_prolog(main.kb_global, query)
    formatted = main.format_prolog_response(query, result)
    return jsonify({"result": formatted})

@app.route("/get_facts")
def get_facts():
    kb_path = os.path.join(os.path.dirname(__file__), "family_kb.pl")
    facts = []
    if os.path.exists(kb_path):
        with open(kb_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("%") and ":-" not in line:
                    facts.append(line)
    return jsonify({"facts": facts})

if __name__ == "__main__":
    print("\nFlask web interface running at http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
