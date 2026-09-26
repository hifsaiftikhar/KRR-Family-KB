"""
Unit Project 1: Static Prolog KB + Chatbot
Main console interface linking Prolog and AIML via Python
"""

import os
import sys
import aiml
import pytholog as pl

# 30+ Pytholog compatible rules
RULES = [
    "father(X, Y) :- male(X), parent(X, Y)",
    "mother(X, Y) :- female(X), parent(X, Y)",
    "son(X, Y) :- male(X), parent(Y, X)",
    "daughter(X, Y) :- female(X), parent(Y, X)",
    "child(X, Y) :- parent(Y, X)",
    "grandparent(X, Y) :- parent(X, Z), parent(Z, Y)",
    "grandfather(X, Y) :- male(X), grandparent(X, Y)",
    "grandmother(X, Y) :- female(X), grandparent(X, Y)",
    "grandchild(X, Y) :- grandparent(Y, X)",
    "grandson(X, Y) :- male(X), grandchild(X, Y)",
    "granddaughter(X, Y) :- female(X), grandchild(X, Y)",
    "sibling(X, Y) :- parent(Z, X), parent(Z, Y)",
    "brother(X, Y) :- male(X), sibling(X, Y)",
    "sister(X, Y) :- female(X), sibling(X, Y)",
    "husband(X, Y) :- married(X, Y)",
    "wife(X, Y) :- married(Y, X)",
    "spouse(X, Y) :- married(X, Y)",
    "spouse(X, Y) :- married(Y, X)",
    "uncle(X, Y) :- male(X), sibling(X, Z), parent(Z, Y)",
    "aunt(X, Y) :- female(X), sibling(X, Z), parent(Z, Y)",
    "cousin(X, Y) :- parent(Z, X), parent(W, Y), sibling(Z, W)",
    "ancestor(X, Y) :- parent(X, Y)",
    "ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y)",
    "descendant(X, Y) :- ancestor(Y, X)",
    "has_children(X) :- parent(X, Y)",
    "is_married(X) :- married(X, Y)",
    "is_married(X) :- married(Y, X)",
    "older_than(X, Y) :- dob(X, DX), dob(Y, DY), DX < DY",
    "younger_than(X, Y) :- older_than(Y, X)",
    "father_in_law(X, Y) :- male(X), spouse(Y, Z), parent(X, Z)",
    "mother_in_law(X, Y) :- female(X), spouse(Y, Z), parent(X, Z)",
    "son_in_law(X, Y) :- male(X), parent(Y, Z), spouse(Z, X)",
    "daughter_in_law(X, Y) :- female(X), parent(Y, Z), spouse(Z, X)",
    "nephew(X, Y) :- male(X), uncle(Y, X)",
    "niece(X, Y) :- female(X), aunt(Y, X)",
    "brother_in_law(X, Y) :- male(X), spouse(Y, Z), sibling(X, Z)",
    "brother_in_law(X, Y) :- male(X), sibling(Y, Z), spouse(Z, X)",
    "sister_in_law(X, Y) :- female(X), spouse(Y, Z), sibling(X, Z)",
    "sister_in_law(X, Y) :- female(X), sibling(Y, Z), spouse(Z, X)",
]

def load_prolog_kb():
    """Load facts from family_kb.pl and append rules."""
    kb = pl.KnowledgeBase("FamilyKB")
    kb_path = os.path.join(os.path.dirname(__file__), "family_kb.pl")
    
    if not os.path.exists(kb_path):
        print(f"Error: {kb_path} not found.")
        sys.exit(1)
        
    facts = []
    with open(kb_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%") or ":-" in line:
                continue
            fact = line.rstrip(".")
            if "(" in fact and fact.endswith(")"):
                facts.append(fact)
                
    kb(facts)
    kb(RULES)
    return kb

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

def preprocess_query(query_str):
    """
    Lowercase constant names to prevent pytholog from treating them as variables.
    e.g., father(X, Hassan) -> father(X, hassan)
          older_than(Ali, Hassan) -> older_than(ali, hassan)
    """
    if "(" not in query_str:
        return query_str
    try:
        rel = query_str.split("(")[0].strip()
        args_str = query_str.split("(")[1].rstrip(")")
        args = [a.strip() for a in args_str.split(",")]
        new_args = []
        for arg in args:
            # Keep pytholog variables uppercase, lowercase names
            if arg in ("X", "Y", "Z", "W", "GP", "DX", "DY"):
                new_args.append(arg)
            else:
                new_args.append(arg.lower())
        return f"{rel}({', '.join(new_args)})"
    except Exception:
        return query_str

def query_prolog(kb, query_str):
    """Preprocess query_str to fix capitalization bug, then query pytholog."""
    cleaned_query = preprocess_query(query_str)
    try:
        result = kb.query(pl.Expr(cleaned_query))
        return result
    except Exception as e:
        print(f"Prolog execution error: {e}")
        return None

def format_prolog_response(query_str, result):
    """Translate Prolog query results into friendly English sentences."""
    # Preprocess the query to reflect the actual query sent to pytholog
    query_str = preprocess_query(query_str)
    try:
        rel = query_str.split("(")[0].strip()
        args = query_str.split("(")[1].rstrip(")").split(",")
        args = [a.strip() for a in args]
    except Exception:
        return f"Result: {result}"

    if not result:
        return "No, that does not seem to be true or is not recorded."

    # If result is boolean (e.g. Yes/No queries like older_than(ali, hassan))
    if isinstance(result, list) and len(result) > 0 and not isinstance(result[0], dict):
        if result[0] == "No":
            return "No."
        return "Yes, that is correct."

    variables = [arg for arg in args if arg[0].isupper()]
    
    # Extract unique values
    unique_bindings = []
    seen = set()
    for binding in result:
        if isinstance(binding, dict):
            val_tuple = tuple(binding[k] for k in sorted(binding.keys()))
            if val_tuple not in seen:
                seen.add(val_tuple)
                unique_bindings.append(binding)
                
    # Filter out self-relations (e.g. Usman is not his own sibling)
    target_person = None
    if len(args) > 1:
        if args[0][0].isupper() and not args[1][0].isupper():
            target_person = args[1]
        elif not args[0][0].isupper() and args[1][0].isupper():
            target_person = args[0]
            
    if target_person:
        filtered = []
        for b in unique_bindings:
            keep = True
            for k, v in b.items():
                if str(v).lower() == target_person.lower():
                    keep = False
                    break
            if keep:
                filtered.append(b)
        unique_bindings = filtered

    if not unique_bindings:
        return "No results found."

    # Format output based on relation type
    if rel == "father" and "X" in variables:
        fathers = [b["X"] for b in unique_bindings]
        return f"The father of {args[1].capitalize()} is {', '.join(f.capitalize() for f in fathers)}."
    elif rel == "mother" and "X" in variables:
        mothers = [b["X"] for b in unique_bindings]
        return f"The mother of {args[1].capitalize()} is {', '.join(m.capitalize() for m in mothers)}."
    elif rel in ("child", "son", "daughter") and "X" in variables:
        children = [b["X"] for b in unique_bindings]
        names_str = ", ".join(c.capitalize() for c in children)
        return f"The {rel}(ren) of {args[1].capitalize()} is/are: {names_str}."
    elif rel == "sibling" and "X" in variables:
        siblings = [b["X"] for b in unique_bindings]
        names_str = ", ".join(s.capitalize() for s in siblings)
        return f"The sibling(s) of {args[1].capitalize()} is/are: {names_str}."
    elif rel == "brother" and "X" in variables:
        brothers = [b["X"] for b in unique_bindings]
        names_str = ", ".join(b.capitalize() for b in brothers)
        return f"The brother(s) of {args[1].capitalize()} is/are: {names_str}."
    elif rel == "sister" and "X" in variables:
        sisters = [b["X"] for b in unique_bindings]
        names_str = ", ".join(s.capitalize() for s in sisters)
        return f"The sister(s) of {args[1].capitalize()} is/are: {names_str}."
    elif rel == "spouse" and "X" in variables:
        spouses = [b["X"] for b in unique_bindings]
        return f"The spouse of {args[0].capitalize()} is {', '.join(s.capitalize() for s in spouses)}."
    elif rel == "husband" and "X" in variables:
        husbands = [b["X"] for b in unique_bindings]
        return f"The husband of {args[1].capitalize()} is {', '.join(h.capitalize() for h in husbands)}."
    elif rel == "wife" and "X" in variables:
        wives = [b["X"] for b in unique_bindings]
        return f"The wife of {args[1].capitalize()} is {', '.join(w.capitalize() for w in wives)}."
    elif rel in ("grandfather", "grandmother", "grandparent") and "X" in variables:
        gps = [b["X"] for b in unique_bindings]
        return f"The {rel} of {args[1].capitalize()} is/are {', '.join(g.capitalize() for g in gps)}."
    elif rel in ("grandchild", "grandson", "granddaughter") and "X" in variables:
        gcs = [b["X"] for b in unique_bindings]
        return f"The {rel}(ren) of {args[1].capitalize()} is/are {', '.join(g.capitalize() for g in gcs)}."
    elif rel in ("uncle", "aunt", "cousin", "nephew", "niece") and "X" in variables:
        relatives = [b["X"] for b in unique_bindings]
        return f"The {rel}(s) of {args[1].capitalize()} is/are {', '.join(r.capitalize() for r in relatives)}."
    elif rel in ("father_in_law", "mother_in_law", "son_in_law", "daughter_in_law", "brother_in_law", "sister_in_law") and "X" in variables:
        relatives = [b["X"] for b in unique_bindings]
        return f"The {rel.replace('_', ' ')} of {args[1].capitalize()} is/are {', '.join(r.capitalize() for r in relatives)}."
    elif rel == "dob" and "X" in variables:
        dobs = [b["X"] for b in unique_bindings]
        return f"{args[0].capitalize()} was born in {', '.join(str(d) for d in dobs)}."
    elif rel == "male" and "X" in variables:
        males = [b["X"] for b in unique_bindings]
        return f"The males in the family are: {', '.join(m.capitalize() for m in males)}."
    elif rel == "female" and "X" in variables:
        females = [b["X"] for b in unique_bindings]
        return f"The females in the family are: {', '.join(f.capitalize() for f in females)}."
    elif rel in ("ancestor", "descendant") and "X" in variables:
        relatives = [b["X"] for b in unique_bindings]
        return f"The {rel}(s) of {args[1].capitalize()} is/are: {', '.join(r.capitalize() for r in relatives)}."
    elif rel in ("older_than", "younger_than", "has_children", "is_married"):
        if len(unique_bindings) > 0:
            return "Yes, that is correct."
        return "No, that is false."
        
    # Default formatting fallback
    lines = []
    for binding in unique_bindings:
        lines.append(", ".join(f"{k} = {v.capitalize() if isinstance(v, str) else v}" for k, v in binding.items()))
    return "\n".join(lines)

def process_interaction(kb, bot, user_input):
    """Pass input to AIML bot, intercept Prolog queries, run and format them."""
    aiml_reply = bot.respond(user_input.strip())
    if not aiml_reply:
        return "I didn't understand that. Type HELP to see supported questions."
        
    if aiml_reply.startswith("QUERY:"):
        prolog_query_str = aiml_reply[len("QUERY:"):].strip()
        raw_result = query_prolog(kb, prolog_query_str)
        return format_prolog_response(prolog_query_str, raw_result)
        
    return aiml_reply

def main():
    print("Loading Prolog Knowledge Base...")
    kb = load_prolog_kb()
    print("Prolog KB loaded successfully.")
    
    print("Loading AIML Chatbot...")
    bot = load_aiml_bot()
    print("AIML Chatbot loaded successfully.")
    
    print("\n" + "="*60)
    print("  UNIT PROJECT 1: STATIC PROLOG KB + CHATBOT")
    print("  Type your questions in natural language. Type 'exit' to quit.")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Goodbye!")
                break
            reply = process_interaction(kb, bot, user_input)
            print(f"Bot: {reply}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
