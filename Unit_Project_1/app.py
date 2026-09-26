"""
Flask Web Interface for Unit Project 1
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys

# Add path for main
sys.path.insert(0, os.path.dirname(__file__))
from main import load_prolog_kb, load_aiml_bot, query_prolog, format_prolog_response, process_interaction

kb = load_prolog_kb()
bot = load_aiml_bot()

app = Flask(__name__)

# Premium, modern glassmorphic HTML/CSS/JS template
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Family KB Agent — Unit 1</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #0b0f19;
      --glass-bg: rgba(255, 255, 255, 0.04);
      --glass-border: rgba(255, 255, 255, 0.08);
      --primary: hsl(250, 85%, 65%);
      --primary-hover: hsl(250, 85%, 75%);
      --accent: hsl(180, 80%, 50%);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(circle at 50% 0%, #1e1e38 0%, var(--bg-color) 70%);
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
      background: linear-gradient(135deg, #fff 30%, var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    header p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .badge {
      background: rgba(180, 80%, 50%, 0.15);
      border: 1px solid var(--accent);
      color: var(--accent);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .container {
      max-width: 960px;
      width: 100%;
      margin: 24px auto;
      padding: 0 16px;
      flex: 1;
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
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
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
      min-height: 480px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .panel.hidden { display: none; }

    /* Chat Section */
    #chat-box {
      flex: 1;
      height: 380px;
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
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
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
      gap: 8px;
      margin-top: 14px;
    }

    .ex {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--glass-border);
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .ex:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text);
      border-color: var(--text-muted);
    }

    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Family Knowledge Base Agent</h1>
      <p>Unit Project 1: Static Prolog KB + Chatbot</p>
    </div>
    <span class="badge">Part 1</span>
  </header>

  <div class="container">
    <div class="tabs">
      <button class="tab active" onclick="showTab('chat')">AIML Chatbot</button>
      <button class="tab" onclick="showTab('prolog')">Prolog Query Terminal</button>
    </div>

    <!-- CHAT PANEL -->
    <div class="panel" id="panel-chat">
      <div id="chat-box"></div>
      <div class="input-row">
        <input id="chat-input" placeholder="Ask in natural language e.g. Who is the grandfather of Bilal?"
               onkeydown="if(event.key==='Enter') sendChat()">
        <button onclick="sendChat()">Send</button>
      </div>
      <div class="query-examples">
        <span class="ex" onclick="fillChat('Who is the father of Hassan?')">Father of Hassan?</span>
        <span class="ex" onclick="fillChat('Who are the siblings of Usman?')">Siblings of Usman?</span>
        <span class="ex" onclick="fillChat('When was Sana born?')">DOB of Sana?</span>
        <span class="ex" onclick="fillChat('Is Hassan married?')">Is Hassan married?</span>
        <span class="ex" onclick="fillChat('Who is the uncle of Bilal?')">Uncle of Bilal?</span>
        <span class="ex" onclick="fillChat('List all females')">List females</span>
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
        <span class="ex" onclick="fillProlog('father(X, hassan)')">father(X, hassan)</span>
        <span class="ex" onclick="fillProlog('grandfather(X, bilal)')">grandfather(X, bilal)</span>
        <span class="ex" onclick="fillProlog('sibling(X, sana)')">sibling(X, sana)</span>
        <span class="ex" onclick="fillProlog('spouse(ali, X)')">spouse(ali, X)</span>
        <span class="ex" onclick="fillProlog('older_than(ali, hassan)')">older_than(ali, hassan)</span>
        <span class="ex" onclick="fillProlog('uncle(X, usman)')">uncle(X, usman)</span>
      </div>
    </div>
  </div>

  <script>
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

    // Welcome message
    addMsg('bot', 'Hello! I am your Prolog Family Agent. How can I help you today?');
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
    reply = process_interaction(kb, bot, user_msg)
    return jsonify({"response": reply})

@app.route("/prolog", methods=["POST"])
def prolog_query():
    data = request.get_json()
    query = data.get("query", "").strip()
    result = query_prolog(kb, query)
    formatted = format_prolog_response(query, result)
    return jsonify({"result": formatted})

if __name__ == "__main__":
    print("\nFlask web interface running at http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
