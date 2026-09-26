"""
Flask Web Interface for Unit Project 3
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import main
from neo4j_kb import Neo4jKB

# Initialize DB client and AIML bot
db = Neo4jKB()
db.initialize_database()
bot = main.load_aiml_bot()

app = Flask(__name__)

# Premium, modern glassmorphic HTML/CSS/JS template for Neo4j/Cypher/Hybrid reasoning
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Neo4j Graph KB Agent — Unit 3</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #080b11;
      --glass-bg: rgba(255, 255, 255, 0.03);
      --glass-border: rgba(255, 255, 255, 0.07);
      --primary: hsl(199, 90%, 50%); /* Neo4j blue theme */
      --primary-hover: hsl(199, 90%, 60%);
      --accent: hsl(160, 85%, 45%);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(circle at 50% 0%, #11283d 0%, var(--bg-color) 75%);
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
      background: rgba(0, 163, 224, 0.15);
      border: 1px solid var(--primary);
      color: var(--primary-hover);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .container {
      max-width: 1100px;
      width: 100%;
      margin: 24px auto;
      padding: 0 16px;
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 360px;
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
      box-shadow: 0 4px 12px rgba(0, 163, 224, 0.3);
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
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
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
      box-shadow: 0 4px 12px rgba(0, 163, 224, 0.2);
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

    /* Cypher Section */
    #cypher-input {
      width: 100%;
      height: 100px;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--glass-border);
      border-radius: 10px;
      color: var(--primary-hover);
      font-family: monospace;
      font-size: 0.95rem;
      margin-bottom: 12px;
      outline: none;
      resize: vertical;
    }

    #cypher-input:focus {
      border-color: var(--primary);
    }

    #cypher-result {
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid var(--glass-border);
      color: #34d399;
      font-family: monospace;
      font-size: 0.9rem;
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

    /* Side Panel - Graph Stats & Actions */
    .side-panel {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .card {
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .card h3 {
      font-size: 1.05rem;
      font-weight: 600;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 8px;
      color: var(--primary-hover);
      margin-bottom: 12px;
    }

    .stat-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 0.9rem;
    }

    .stat-label { color: var(--text-muted); }
    .stat-val { font-weight: 600; color: #fff; }

    .action-btn {
      width: 100%;
      padding: 12px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid var(--accent);
      color: var(--accent);
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
      transition: 0.3s;
      margin-top: 8px;
    }

    .action-btn:hover {
      background: var(--accent);
      color: #080b11;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }

    #db-status-badge {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 6px;
    }
    .status-online { background-color: var(--accent); }
    .status-fallback { background-color: #f59e0b; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Family Knowledge Base Agent</h1>
      <p>Unit Project 3: Neo4j Graph DB Chatbot</p>
    </div>
    <span class="badge">Part 3</span>
  </header>

  <div class="container">
    <div class="left-column">
      <div class="tabs">
        <button class="tab active" onclick="showTab('chat')">AIML Chatbot</button>
        <button class="tab" onclick="showTab('cypher')">Cypher Query Runner</button>
      </div>

      <!-- CHAT PANEL -->
      <div class="panel" id="panel-chat">
        <div id="chat-box"></div>
        <div class="input-row">
          <input id="chat-input" placeholder="Ask questions or teach facts..."
                 onkeydown="if(event.key==='Enter') sendChat()">
          <button onclick="sendChat()">Send</button>
        </div>
        <div class="query-examples">
          <span class="ex" onclick="fillChat('Who is the grandfather of Bilal?')">Grandfather of Bilal?</span>
          <span class="ex" onclick="fillChat('Is Hassan older than Usman?')">Hassan older than Usman?</span>
          <span class="ex" onclick="fillChat('What are the mutual connections between Hassan and Usman?')">Mutual connections?</span>
          <span class="ex" onclick="fillChat('David is married to Sarah')">Teach Marriage</span>
          <span class="ex" onclick="fillChat('Sarah is a female')">Teach Gender</span>
        </div>
      </div>

      <!-- CYPHER PANEL -->
      <div class="panel hidden" id="panel-cypher">
        <p class="hint">Enter a Neo4j Cypher query to execute directly against the database.</p>
        <textarea id="cypher-input" placeholder="e.g. MATCH (n:Person) RETURN n.name AS name, n.gender AS gender LIMIT 10">MATCH (p:Person) RETURN p.name AS name, p.gender AS gender, p.dob AS dob LIMIT 10</textarea>
        <button onclick="sendCypher()"
                style="padding:12px 24px; background:var(--primary); color:white; border:none;
                       border-radius:10px; cursor:pointer; font-weight:600; width:fit-content; transition:0.3s;">
          Execute Cypher Query
        </button>
        <div id="cypher-result">Query results will be displayed here...</div>
        <div class="query-examples">
          <span class="ex" onclick="fillCypher('MATCH (p:Person {name: &quot;ali&quot;})-[:PARENT_OF]->(c) RETURN c.name AS children')">Ali's children</span>
          <span class="ex" onclick="fillCypher('MATCH (p:Person {gender: &quot;male&quot;}) RETURN p.name AS name')">All males</span>
          <span class="ex" onclick="fillCypher('MATCH (p1:Person)-[:MARRIED_TO]-(p2:Person) RETURN p1.name, p2.name')">All marriages</span>
        </div>
      </div>
    </div>

    <!-- SIDE PANEL -->
    <div class="side-panel">
      <!-- GRAPH STATS CARD -->
      <div class="card">
        <h3>Graph Database Status</h3>
        <div class="stat-row" style="align-items: center;">
          <span class="stat-label">Connection status:</span>
          <span class="stat-val" style="display: flex; align-items: center;">
            <span id="db-status-indicator" class="status-fallback"></span>
            <span id="db-status-text">Fallback (Offline)</span>
          </span>
        </div>
      </div>

      <div class="card">
        <h3>Graph Statistics</h3>
        <div class="stat-row">
          <span class="stat-label">Total Nodes:</span>
          <span class="stat-val" id="stat-nodes">0</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Male Nodes:</span>
          <span class="stat-val" id="stat-males">0</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Female Nodes:</span>
          <span class="stat-val" id="stat-females">0</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Parent Relationships:</span>
          <span class="stat-val" id="stat-parents">0</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Spouse Relationships:</span>
          <span class="stat-val" id="stat-married">0</span>
        </div>
        <button class="action-btn" onclick="refreshStats()" style="border-color: var(--primary); color: var(--primary); background: rgba(0, 163, 224, 0.05);">
          Refresh Statistics
        </button>
      </div>

      <!-- HYBRID REASONING CARD -->
      <div class="card">
        <h3>Hybrid Reasoning Engine</h3>
        <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 12px;">
          Exports graph nodes/relations to Prolog, runs Prolog inference rules, and commits deduced relationships (INFERRED_GRANDFATHER, INFERRED_COUSIN, etc.) back to Neo4j.
        </p>
        <button class="action-btn" onclick="runHybridReasoning()">
          Trigger Hybrid Reasoning
        </button>
        <div id="hybrid-msg" style="font-size: 0.8rem; color: var(--accent); margin-top: 8px; font-weight: 500;"></div>
      </div>
    </div>
  </div>

  <script>
    function showTab(name) {
      document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', (i === 0 && name === 'chat') || (i === 1 && name === 'cypher'));
      });
      document.getElementById('panel-chat').classList.toggle('hidden', name !== 'chat');
      document.getElementById('panel-cypher').classList.toggle('hidden', name !== 'cypher');
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

    function fillCypher(text) {
      document.getElementById('cypher-input').value = text;
      document.getElementById('cypher-input').focus();
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
      refreshStats();
    }

    async function sendCypher() {
      const query = document.getElementById('cypher-input').value.trim();
      if (!query) return;
      const res = await fetch('/cypher', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query})
      });
      const data = await res.json();
      document.getElementById('cypher-result').textContent = data.result;
    }

    async function refreshStats() {
      const res = await fetch('/get_stats');
      const data = await res.json();
      
      document.getElementById('stat-nodes').textContent = data.stats.node_count;
      document.getElementById('stat-males').textContent = data.stats.male_count;
      document.getElementById('stat-females').textContent = data.stats.female_count;
      document.getElementById('stat-parents').textContent = data.stats.parent_relationships;
      document.getElementById('stat-married').textContent = data.stats.married_relationships;

      const indicator = document.getElementById('db-status-indicator');
      const statusText = document.getElementById('db-status-text');
      
      if (data.is_online) {
        indicator.className = 'status-online';
        statusText.textContent = 'Live Neo4j (Online)';
      } else {
        indicator.className = 'status-fallback';
        statusText.textContent = 'Fallback Graph (Offline)';
      }
    }

    async function runHybridReasoning() {
      document.getElementById('hybrid-msg').textContent = 'Running hybrid engine...';
      const res = await fetch('/hybrid_reasoning', { method: 'POST' });
      const data = await res.json();
      document.getElementById('hybrid-msg').textContent = `Success! Deduced and stored ${data.inferred} relationships.`;
      refreshStats();
    }

    // Welcome message
    addMsg('bot', 'Hello! I am your Neo4j Graph chatbot. Ask me about the family or teach me new facts, and I will store and traverse the graph live!');
    
    // Initial stats
    refreshStats();
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
    reply = main.process_interaction(db, bot, user_msg)
    return jsonify({"response": reply})

@app.route("/cypher", methods=["POST"])
def run_cypher():
    data = request.get_json()
    query = data.get("query", "").strip()
    result = db.run_cypher(query)
    
    # Format Cypher result into clean string
    if isinstance(result, list):
        if not result:
            formatted = "No records matched the Cypher query."
        else:
            lines = []
            for record in result:
                lines.append(str(record))
            formatted = "\n".join(lines)
    else:
        formatted = str(result)
        
    return jsonify({"result": formatted})

@app.route("/get_stats")
def get_stats():
    stats = db.get_statistics()
    is_online = db.driver is not None
    return jsonify({"stats": stats, "is_online": is_online})

@app.route("/hybrid_reasoning", methods=["POST"])
def hybrid_reasoning():
    inferred_count = db.run_hybrid_prolog_reasoning()
    return jsonify({"inferred": inferred_count})

if __name__ == "__main__":
    print("\nFlask web interface running at http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
