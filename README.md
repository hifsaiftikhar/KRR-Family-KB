# Knowledge Representation & Reasoning — Unit Projects

A three-unit progressive project demonstrating knowledge representation using **Prolog**, **AIML**, **Python**, and **Neo4j Graph Database**.

---

## Project Overview

| Unit | Title | Knowledge Store | Key Feature |
|------|-------|----------------|-------------|
| Unit 1 | Static Prolog KB + Chatbot | Prolog `.pl` file | Pre-loaded facts, AIML queries |
| Unit 2 | Dynamic Prolog Learning Chatbot | Prolog `.pl` file | Learns facts from conversation |
| Unit 3 | Neo4j Graph Database Chatbot | Neo4j graph DB | Graph nodes, relationships, Cypher queries |

---

## Unit Project 1 — Static Prolog KB + Chatbot

### What it does
- A family knowledge base with **5 fact types**: `male`, `female`, `parent`, `dob`, `married`
- **35 Prolog rules** for derived relationships: father, mother, grandparent, uncle, cousin, ancestor, etc.
- AIML chatbot accepts natural language queries and returns answers via Prolog inference

### How to run
```bash
cd Unit_Project_1
pip install -r requirements.txt
python main.py
```

### Example queries
```
Who is the father of Hassan?
Who are the grandchildren of Ali?
Who are the cousins of Bilal?
Who are the ancestors of Usman?
When was Ali born?
Is Hassan older than Usman?
List all males
```

---

## Unit Project 2 — Dynamic Prolog Learning Chatbot

### What it does
- Same 35 Prolog rules as Unit 1 — but **no pre-loaded facts**
- User teaches facts through natural language conversation
- Facts are written to `family_kb.pl` using **file handling**
- KB reloads after each new fact so derived queries work immediately

### How to run
```bash
cd Unit_Project_2
pip install -r requirements.txt
python main.py
```

### Teach facts first, then query
```
Ali is a male
Fatima is a female
Ali is the father of Hassan
Fatima is the mother of Hassan
Hassan is a male
Hassan is the father of Usman
Ali is married to Fatima
Ali was born in 1950
```
Then query:
```
Who is the father of Hassan?
Who is the grandfather of Usman?
When was Ali born?
```
Type `reset kb` to clear all learned facts and start fresh.

---

## Unit Project 3 — Neo4j Graph Database Chatbot

### What it does
- Replaces the Prolog `.pl` file with a **Neo4j graph database**
- Family members stored as **nodes** with properties (`name`, `gender`, `dob`)
- Relationships stored as **edges** (`PARENT_OF`, `MARRIED_TO`)
- Derived relationships computed via **Cypher multi-hop queries**
- Supports dynamic learning, graph stats, and hybrid Prolog reasoning

### Prerequisites
1. Install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a local instance named `family_kb` with password `password`
3. Start the instance

### How to run
```bash
cd Unit_Project_3
pip install -r requirements.txt
python main.py
```

### Special commands
| Command | Description |
|---------|-------------|
| `stats` | Show node and relationship counts |
| `hybrid` | Run Prolog reasoning over Neo4j data and write inferred relationships back |

### View the graph visually
Open Neo4j Browser at `http://localhost:7474` and run:
```cypher
MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50
```

### Example session
```
Ali is a male
Ali is the father of Hassan
Ali is married to Fatima
Who is the father of Hassan?
Who are the ancestors of Usman?
stats
hybrid
```

---

## Tech Stack

- **Python 3.10**
- **python-aiml** — AIML pattern matching chatbot
- **pytholog** — Prolog inference engine in Python
- **neo4j** — Python driver for Neo4j graph database
- **python-dotenv** — Environment variable management

---

## Project Structure

```
krr/
├── Unit_Project_1/
│   ├── main.py
│   ├── app.py
│   ├── family_kb.pl
│   ├── requirements.txt
│   └── aiml_files/
│       └── family.aiml
├── Unit_Project_2/
│   ├── main.py
│   ├── family_kb.pl
│   ├── requirements.txt
│   └── aiml_files/
│       ├── family_learning.aiml
│       └── family_queries.aiml
└── Unit_Project_3/
    ├── main.py
    ├── neo4j_kb.py
    ├── schema.cypher
    ├── sample_dataset.cypher
    ├── requirements.txt
    └── aiml_files/
        └── family_queries.aiml
```