"""
Unit Project 3: Neo4j Graph Database + Chatbot
Main console interface linking Neo4j (or local graph fallback) and AIML via Python.
Supports dynamic learning, graph statistics, discovery queries, and Hybrid Prolog-Neo4j reasoning.
"""

import os
import sys
import aiml
from neo4j_kb import Neo4jKB

def load_aiml_bot():
    """Load the AIML kernel and learn files."""
    bot = aiml.Kernel()
    bot.verbose(isVerbose=False)
    
    aiml_dir = os.path.join(os.path.dirname(__file__), "aiml_files")
    if not os.path.isdir(aiml_dir):
        print(f"Error: AIML folder not found: {aiml_dir}")
        sys.exit(1)
        
    for filename in os.listdir(aiml_dir):
        if filename.endswith(".aiml"):
            bot.learn(os.path.join(aiml_dir, filename))
            
    return bot

def format_query_response(db, rel_type, name, arg2=None):
    """Reason over retrieved graph data and format into natural language."""
    rel_type = rel_type.strip().lower()
    name = name.strip().lower()
    
    if rel_type in ("older_than", "younger_than"):
        if not arg2:
            return "Please provide two family members to compare."
        arg2 = arg2.strip().lower()
        res = db.verify_comparison(name, arg2, rel_type)
        if res:
            return f"Yes, {name.capitalize()} is {rel_type.replace('_', ' ')} {arg2.capitalize()}."
        return f"No, {name.capitalize()} is not {rel_type.replace('_', ' ')} {arg2.capitalize()}."
        
    elif rel_type in ("has_children", "is_married"):
        res = db.verify_boolean_status(name, rel_type)
        if res:
            if rel_type == "has_children":
                return f"Yes, {name.capitalize()} has children."
            else:
                return f"Yes, {name.capitalize()} is married."
        else:
            if rel_type == "has_children":
                return f"No, {name.capitalize()} does not have children."
            else:
                return f"No, {name.capitalize()} is not married."
                
    elif rel_type == "mutual":
        if not arg2:
            return "Please provide two names to find mutual connections."
        arg2 = arg2.strip().lower()
        mutuals = db.get_mutual_connections(name, arg2)
        if mutuals:
            return f"The mutual connections between {name.capitalize()} and {arg2.capitalize()} are: {', '.join(n.capitalize() for n in mutuals)}."
        return f"There are no mutual connections between {name.capitalize()} and {arg2.capitalize()} recorded in the database."

    # Normal relationship list queries
    results = db.get_relationship(name, rel_type)
    if not results:
        # Check if list queries
        if rel_type == "list_males":
            return "No males recorded in the database."
        elif rel_type == "list_females":
            return "No females recorded in the database."
        elif rel_type == "list_members":
            return "No family members recorded in the database."
        return f"I do not have any recorded information about the {rel_type.replace('_', ' ')} of {name.capitalize()}."
        
    names_str = ", ".join(n.capitalize() for n in results)
    
    if rel_type == "father":
        return f"The father of {name.capitalize()} is {names_str}."
    elif rel_type == "mother":
        return f"The mother of {name.capitalize()} is {names_str}."
    elif rel_type == "child":
        return f"The child(ren) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "son":
        return f"The son(s) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "daughter":
        return f"The daughter(s) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "sibling":
        return f"The sibling(s) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "brother":
        return f"The brother(s) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "sister":
        return f"The sister(s) of {name.capitalize()} is/are: {names_str}."
    elif rel_type == "spouse":
        return f"The spouse of {name.capitalize()} is {names_str}."
    elif rel_type == "husband":
        return f"The husband of {name.capitalize()} is {names_str}."
    elif rel_type == "wife":
        return f"The wife of {name.capitalize()} is {names_str}."
    elif rel_type in ("grandfather", "grandmother", "grandparent"):
        return f"The {rel_type} of {name.capitalize()} is/are {names_str}."
    elif rel_type in ("grandchild", "grandson", "granddaughter"):
        return f"The {rel_type}(ren) of {name.capitalize()} is/are {names_str}."
    elif rel_type in ("uncle", "aunt", "cousin", "nephew", "niece"):
        return f"The {rel_type}(s) of {name.capitalize()} is/are {names_str}."
    elif rel_type in ("father_in_law", "mother_in_law", "son_in_law", "daughter_in_law", "brother_in_law", "sister_in_law"):
        return f"The {rel_type.replace('_', ' ')} of {name.capitalize()} is/are {names_str}."
    elif rel_type == "dob":
        return f"{name.capitalize()} was born in {names_str}."
    elif rel_type == "gender":
        return f"The gender of {name.capitalize()} is {names_str}."
    elif rel_type == "list_males":
        return f"The males in the family are: {names_str}."
    elif rel_type == "list_females":
        return f"The females in the family are: {names_str}."
    elif rel_type == "list_members":
        return f"All family members in the database are: {names_str}."
    elif rel_type in ("oldest", "youngest"):
        return f"The {rel_type} family member is {names_str}."
    return f"Result: {names_str}"

def process_learning(db, fact_data):
    """Parse fact details and commit them to the graph database (or fallback)."""
    parts = fact_data.split("|")
    fact_type = parts[0].strip().lower()
    
    if fact_type == "gender":
        name = parts[1].strip().lower()
        gender = parts[2].strip().lower()
        db.add_person(name, gender=gender)
        return f"I have recorded that {name.capitalize()} is a {gender}."
        
    elif fact_type == "parent":
        p_name = parts[1].strip().lower()
        c_name = parts[2].strip().lower()
        p_type = parts[3].strip().lower()
        
        # Set relationships
        db.add_parent(p_name, c_name)
        if p_type == "father":
            db.add_person(p_name, gender="male")
            return f"I have learned that {p_name.capitalize()} is the father of {c_name.capitalize()}."
        elif p_type == "mother":
            db.add_person(p_name, gender="female")
            return f"I have learned that {p_name.capitalize()} is the mother of {c_name.capitalize()}."
        return f"I have learned that {p_name.capitalize()} is a parent of {c_name.capitalize()}."
        
    elif fact_type == "married":
        s1 = parts[1].strip().lower()
        s2 = parts[2].strip().lower()
        db.add_marriage(s1, s2)
        return f"I have recorded that {s1.capitalize()} is married to {s2.capitalize()}."
        
    elif fact_type == "dob":
        name = parts[1].strip().lower()
        year = parts[2].strip()
        db.add_person(name, dob=int(year))
        return f"I have recorded that {name.capitalize()} was born in {year}."
        
    return "Failed to parse learning input."

def process_interaction(db, bot, user_input):
    """Coordinate AIML response matching with Neo4j database actions."""
    aiml_reply = bot.respond(user_input.strip())
    if not aiml_reply:
        return "I didn't understand that. Try teaching me facts or querying relationships."
        
    if aiml_reply.startswith("LEARN:"):
        fact_data = aiml_reply[len("LEARN:"):].strip()
        return process_learning(db, fact_data)
        
    if aiml_reply.startswith("QUERY:"):
        query_data = aiml_reply[len("QUERY:"):].strip()
        parts = query_data.split("|")
        rel_type = parts[0]
        
        # Lists and global stats queries might not have name arguments
        name = parts[1] if len(parts) > 1 else ""
        arg2 = parts[2] if len(parts) > 2 else None
        
        return format_query_response(db, rel_type, name, arg2)
        
    return aiml_reply

def main():
    print("Connecting to Neo4j database client...")
    db = Neo4jKB()
    
    # Check if empty/offline, seed initial core family dataset
    print("Initializing/Seeding Graph database...")
    db.initialize_database()
    print("Database ready.")
    
    print("Loading AIML Chatbot...")
    bot = load_aiml_bot()
    print("AIML Chatbot loaded successfully.")
    
    print("\n" + "="*60)
    print("  UNIT PROJECT 3: NEO4J GRAPH DATABASE CHATBOT")
    print("  Teach me facts (e.g. 'John is the father of Mike')")
    print("  Ask me queries (e.g. 'Who is the father of Hassan?')")
    print("  Options: type 'stats' for graph data, 'hybrid' for Prolog reasoning.")
    print("  Type 'exit' to quit.")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Goodbye!")
                break
            elif user_input.lower() == "stats":
                stats = db.get_statistics()
                print("\n[Neo4j Graph Database Statistics]")
                print(f"  Nodes (People): {stats['node_count']}")
                print(f"  Males:           {stats['male_count']}")
                print(f"  Females:         {stats['female_count']}")
                print(f"  Parent relationships: {stats['parent_relationships']}")
                print(f"  Married relationships: {stats['married_relationships']}\n")
                continue
            elif user_input.lower() == "hybrid":
                count = db.run_hybrid_prolog_reasoning()
                print(f"\n[Hybrid Reasoning] Inferred and committed {count} relationships back to Neo4j.\n")
                continue
                
            reply = process_interaction(db, bot, user_input)
            print(f"Bot: {reply}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
            
    db.close()

if __name__ == "__main__":
    main()
