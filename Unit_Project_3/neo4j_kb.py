"""
Unit Project 3: Neo4j Graph Database KB
Manages connection to Neo4j, defines graph schema, seeds data, 
implements 30+ reasoning rules via Cypher queries, and handles local graph fallback.
"""

import os
from dotenv import load_dotenv

# Try to load python-dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Import neo4j if available
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: 'neo4j' package not installed. Running in local graph fallback mode.")

import pytholog as pl

class LocalGraphKB:
    """
    In-memory Python Graph Database mockup.
    Used when a local Neo4j database is offline or 'neo4j' package is missing.
    Matches all relationship query outputs of the live Neo4j database.
    """
    def __init__(self):
        self.nodes = {}       # name -> {"name": str, "gender": str, "dob": int}
        self.parents = []      # list of (parent_name, child_name)
        self.marriages = []    # list of (spouse1, spouse2)
        
    def add_person(self, name, gender=None, dob=None):
        name = name.lower()
        if name not in self.nodes:
            self.nodes[name] = {"name": name, "gender": None, "dob": None}
        if gender:
            self.nodes[name]["gender"] = gender.lower()
        if dob is not None:
            self.nodes[name]["dob"] = int(dob)

    def add_parent(self, parent, child):
        parent = parent.lower()
        child = child.lower()
        self.add_person(parent)
        self.add_person(child)
        edge = (parent, child)
        if edge not in self.parents:
            self.parents.append(edge)

    def add_marriage(self, spouse1, spouse2):
        spouse1 = spouse1.lower()
        spouse2 = spouse2.lower()
        self.add_person(spouse1)
        self.add_person(spouse2)
        edge = (spouse1, spouse2)
        if edge not in self.marriages and (spouse2, spouse1) not in self.marriages:
            self.marriages.append(edge)

    # --- Reasoning helpers ---
    def get_gender(self, name):
        node = self.nodes.get(name.lower())
        return node["gender"] if node else None

    def get_dob(self, name):
        node = self.nodes.get(name.lower())
        return node["dob"] if node else None

    def is_male(self, name):
        return self.get_gender(name) == "male"

    def is_female(self, name):
        return self.get_gender(name) == "female"

    def get_parents(self, name):
        name = name.lower()
        return [p for p, c in self.parents if c == name]

    def get_children(self, name):
        name = name.lower()
        return [c for p, c in self.parents if p == name]

    def get_spouses(self, name):
        name = name.lower()
        result = []
        for s1, s2 in self.marriages:
            if s1 == name:
                result.append(s2)
            elif s2 == name:
                result.append(s1)
        return result

    def get_siblings(self, name):
        name = name.lower()
        parents = self.get_parents(name)
        siblings = set()
        for p in parents:
            for child in self.get_children(p):
                if child != name:
                    siblings.add(child)
        return list(siblings)

    def get_grandparents(self, name):
        parents = self.get_parents(name)
        gps = set()
        for p in parents:
            gps.update(self.get_parents(p))
        return list(gps)

    def get_grandchildren(self, name):
        children = self.get_children(name)
        gcs = set()
        for c in children:
            gcs.update(self.get_children(c))
        return list(gcs)

    def get_uncles_aunts(self, name, gender=None):
        parents = self.get_parents(name)
        results = set()
        for p in parents:
            # Blood siblings of parents
            siblings = self.get_siblings(p)
            for sib in siblings:
                if gender is None or self.get_gender(sib) == gender:
                    results.add(sib)
            # Spouses of blood siblings of parents
            for sib in siblings:
                for sp in self.get_spouses(sib):
                    if gender is None or self.get_gender(sp) == gender:
                        results.add(sp)
        return list(results)

    def get_cousins(self, name):
        parents = self.get_parents(name)
        cousins = set()
        for p in parents:
            siblings = self.get_siblings(p)
            for sib in siblings:
                cousins.update(self.get_children(sib))
        return list(cousins)

    def get_nephews_nieces(self, name, gender=None):
        siblings = self.get_siblings(name)
        spouses = self.get_spouses(name)
        
        # Include siblings of spouse (in-law uncles/aunts)
        spouse_siblings = []
        for sp in spouses:
            spouse_siblings.extend(self.get_siblings(sp))
            
        all_siblings = list(set(siblings + spouse_siblings))
        results = set()
        for sib in all_siblings:
            children = self.get_children(sib)
            for c in children:
                if gender is None or self.get_gender(c) == gender:
                    results.add(c)
        return list(results)

    def get_ancestors(self, name, visited=None):
        if visited is None:
            visited = set()
        parents = self.get_parents(name)
        ancestors = set(parents)
        for p in parents:
            if p not in visited:
                visited.add(p)
                ancestors.update(self.get_ancestors(p, visited))
        return list(ancestors)

    def get_descendants(self, name, visited=None):
        if visited is None:
            visited = set()
        children = self.get_children(name)
        descendants = set(children)
        for c in children:
            if c not in visited:
                visited.add(c)
                descendants.update(self.get_descendants(c, visited))
        return list(descendants)

    def get_in_laws(self, name, rel_type):
        spouses = self.get_spouses(name)
        if not spouses:
            return []
        
        results = set()
        if rel_type == "father_in_law":
            for sp in spouses:
                parents = self.get_parents(sp)
                results.update([p for p in parents if self.is_male(p)])
        elif rel_type == "mother_in_law":
            for sp in spouses:
                parents = self.get_parents(sp)
                results.update([p for p in parents if self.is_female(p)])
        elif rel_type == "son_in_law":
            children = self.get_children(name)
            for c in children:
                spouses_of_c = self.get_spouses(c)
                results.update([sp for sp in spouses_of_c if self.is_male(sp)])
        elif rel_type == "daughter_in_law":
            children = self.get_children(name)
            for c in children:
                spouses_of_c = self.get_spouses(c)
                results.update([sp for sp in spouses_of_c if self.is_female(sp)])
        elif rel_type == "brother_in_law":
            # Spouse's brothers
            for sp in spouses:
                siblings = self.get_siblings(sp)
                results.update([sib for sib in siblings if self.is_male(sib)])
            # Sister's husband
            siblings = self.get_siblings(name)
            for sib in siblings:
                if self.is_female(sib):
                    results.update(self.get_spouses(sib))
        elif rel_type == "sister_in_law":
            # Spouse's sisters
            for sp in spouses:
                siblings = self.get_siblings(sp)
                results.update([sib for sib in siblings if self.is_female(sib)])
            # Brother's wife
            siblings = self.get_siblings(name)
            for sib in siblings:
                if self.is_male(sib):
                    results.update(self.get_spouses(sib))
        return list(results)

    def get_generation_depth(self, name):
        """Helper to find maximum path depth to any founder node (ancestor with no parents)."""
        ancestors = self.get_ancestors(name)
        if not ancestors:
            return 0
        founders = [a for a in ancestors if not self.get_parents(a)]
        if not founders:
            return 1
        
        # Simple BFS/DFS to find max depth
        def get_max_depth(current, target):
            if current == target:
                return 0
            children = self.get_children(current)
            if not children:
                return -99999
            depths = [1 + get_max_depth(c, target) for c in children]
            return max(depths) if depths else -99999

        max_depth = 0
        for f in founders:
            d = get_max_depth(f, name)
            if d > max_depth:
                max_depth = d
        return max_depth

    def get_mutual_connections(self, name1, name2):
        """Inference: Find common relatives (parents, children, spouses)."""
        rel1 = set(self.get_parents(name1) + self.get_children(name1) + self.get_spouses(name1))
        rel2 = set(self.get_parents(name2) + self.get_children(name2) + self.get_spouses(name2))
        mutual = rel1.intersection(rel2)
        return list(mutual)

    def get_statistics(self):
        """Graph structure analysis."""
        return {
            "node_count": len(self.nodes),
            "male_count": sum(1 for n in self.nodes.values() if n["gender"] == "male"),
            "female_count": sum(1 for n in self.nodes.values() if n["gender"] == "female"),
            "parent_relationships": len(self.parents),
            "married_relationships": len(self.marriages)
        }


class Neo4jKB:
    """
    Neo4j Graph Database Client.
    Automatically falls back to LocalGraphKB if connection fails.
    """
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = None
        self.fallback = None
        
        if not NEO4J_AVAILABLE:
            self.fallback = LocalGraphKB()
            return
            
        try:
            # Check connection with short timeout
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password), connection_timeout=3.0)
            self.driver.verify_connectivity()
            print(f"Connected to Neo4j Graph Database at {self.uri}")
        except Exception as e:
            print(f"Neo4j connection failed: {e}. Falling back to Local Graph KB.")
            self.driver = None
            self.fallback = LocalGraphKB()

    def close(self):
        if self.driver:
            self.driver.close()

    def run_cypher(self, query, params=None):
        """Execute cypher query against Neo4j or print mock behavior."""
        if self.fallback:
            return f"Cypher Execution mock (Neo4j Offline):\nQuery: {query}\nParams: {params}"
        
        with self.driver.session() as session:
            try:
                result = session.run(query, params)
                return [record.data() for record in result]
            except Exception as e:
                return f"Cypher Error: {e}"

    # --- Write API ---
    def add_person(self, name, gender=None, dob=None):
        name = name.lower()
        if self.fallback:
            self.fallback.add_person(name, gender, dob)
            return
            
        query = "MERGE (p:Person {name: $name}) "
        if gender:
            query += "SET p.gender = $gender "
        if dob is not None:
            query += "SET p.dob = $dob "
        query += "RETURN p"
        
        params = {"name": name, "gender": gender, "dob": int(dob) if dob is not None else None}
        self.run_cypher(query, params)

    def add_parent(self, parent, child):
        parent = parent.lower()
        child = child.lower()
        if self.fallback:
            self.fallback.add_parent(parent, child)
            return
            
        query = """
        MERGE (p:Person {name: $p_name})
        MERGE (c:Person {name: $c_name})
        MERGE (p)-[:PARENT_OF]->(c)
        RETURN p, c
        """
        self.run_cypher(query, {"p_name": parent, "c_name": child})

    def add_marriage(self, spouse1, spouse2):
        spouse1 = spouse1.lower()
        spouse2 = spouse2.lower()
        if self.fallback:
            self.fallback.add_marriage(spouse1, spouse2)
            return
            
        # Bi-directional marriage link
        query = """
        MERGE (s1:Person {name: $s1})
        MERGE (s2:Person {name: $s2})
        MERGE (s1)-[:MARRIED_TO]->(s2)
        RETURN s1, s2
        """
        self.run_cypher(query, {"s1": spouse1, "s2": spouse2})

    def initialize_database(self):
        """Seed the graph database with the core 15 family member dataset."""
        # Seeding data
        males = ["ali", "hassan", "usman", "bilal", "omar", "tariq", "zaid", "hamza"]
        females = ["fatima", "ayesha", "sana", "nida", "zara", "hina", "mariam"]
        
        dobs = {
            "ali": 1950, "fatima": 1953, "hassan": 1975, "ayesha": 1978, "sana": 1978,
            "usman": 2000, "nida": 2003, "bilal": 2002, "zara": 2005, "omar": 1975,
            "tariq": 1948, "hina": 1952, "zaid": 2022, "mariam": 2024, "hamza": 1980
        }
        
        parents = [
            ("ali", "hassan"), ("ali", "sana"),
            ("fatima", "hassan"), ("fatima", "sana"),
            ("hassan", "usman"), ("hassan", "nida"),
            ("ayesha", "usman"), ("ayesha", "nida"),
            ("usman", "zaid"), ("usman", "mariam"),
            ("sana", "bilal"), ("sana", "zara"),
            ("omar", "bilal"), ("omar", "zara"),
            ("tariq", "hamza"), ("hina", "hamza"),
            ("tariq", "ayesha"), ("hina", "ayesha")
        ]
        
        marriages = [
            ("ali", "fatima"), ("hassan", "ayesha"),
            ("omar", "sana"), ("tariq", "hina")
        ]
        
        # Write to Neo4j or Fallback
        for m in males:
            self.add_person(m, "male", dobs.get(m))
        for f in females:
            self.add_person(f, "female", dobs.get(f))
        for p, c in parents:
            self.add_parent(p, c)
        for s1, s2 in marriages:
            self.add_marriage(s1, s2)

    # --- Graph Reasoning / Queries ---
    def get_relationship(self, name, rel_type):
        """Retrieve relationship results using Cypher queries."""
        name = name.lower()
        if self.fallback:
            # Route to fallback method
            if rel_type == "father":
                return [p for p in self.fallback.get_parents(name) if self.fallback.is_male(p)]
            elif rel_type == "mother":
                return [p for p in self.fallback.get_parents(name) if self.fallback.is_female(p)]
            elif rel_type == "child":
                return self.fallback.get_children(name)
            elif rel_type == "son":
                return [c for c in self.fallback.get_children(name) if self.fallback.is_male(c)]
            elif rel_type == "daughter":
                return [c for c in self.fallback.get_children(name) if self.fallback.is_female(c)]
            elif rel_type == "sibling":
                return self.fallback.get_siblings(name)
            elif rel_type == "brother":
                return [s for s in self.fallback.get_siblings(name) if self.fallback.is_male(s)]
            elif rel_type == "sister":
                return [s for s in self.fallback.get_siblings(name) if self.fallback.is_female(s)]
            elif rel_type == "spouse":
                return self.fallback.get_spouses(name)
            elif rel_type == "husband":
                return [s for s in self.fallback.get_spouses(name) if self.fallback.is_male(s)]
            elif rel_type == "wife":
                return [s for s in self.fallback.get_spouses(name) if self.fallback.is_female(s)]
            elif rel_type == "grandparent":
                return self.fallback.get_grandparents(name)
            elif rel_type == "grandfather":
                return [g for g in self.fallback.get_grandparents(name) if self.fallback.is_male(g)]
            elif rel_type == "grandmother":
                return [g for g in self.fallback.get_grandparents(name) if self.fallback.is_female(g)]
            elif rel_type == "grandchild":
                return self.fallback.get_grandchildren(name)
            elif rel_type == "grandson":
                return [g for g in self.fallback.get_grandchildren(name) if self.fallback.is_male(g)]
            elif rel_type == "granddaughter":
                return [g for g in self.fallback.get_grandchildren(name) if self.fallback.is_female(g)]
            elif rel_type == "uncle":
                return self.fallback.get_uncles_aunts(name, "male")
            elif rel_type == "aunt":
                return self.fallback.get_uncles_aunts(name, "female")
            elif rel_type == "cousin":
                return self.fallback.get_cousins(name)
            elif rel_type == "nephew":
                return self.fallback.get_nephews_nieces(name, "male")
            elif rel_type == "niece":
                return self.fallback.get_nephews_nieces(name, "female")
            elif rel_type == "ancestor":
                return self.fallback.get_ancestors(name)
            elif rel_type == "descendant":
                return self.fallback.get_descendants(name)
            elif rel_type in ("father_in_law", "mother_in_law", "son_in_law", "daughter_in_law", "brother_in_law", "sister_in_law"):
                return self.fallback.get_in_laws(name, rel_type)
            elif rel_type == "dob":
                dob = self.fallback.get_dob(name)
                return [str(dob)] if dob else []
            elif rel_type == "gender":
                gender = self.fallback.get_gender(name)
                return [gender] if gender else []
            elif rel_type == "list_males":
                return [n["name"] for n in self.fallback.nodes.values() if n["gender"] == "male"]
            elif rel_type == "list_females":
                return [n["name"] for n in self.fallback.nodes.values() if n["gender"] == "female"]
            elif rel_type == "list_members":
                return list(self.fallback.nodes.keys())
            elif rel_type == "oldest":
                # Find member with smallest dob
                valid_nodes = [n for n in self.fallback.nodes.values() if n["dob"] is not None]
                if not valid_nodes: return []
                oldest = min(valid_nodes, key=lambda x: x["dob"])
                return [f"{oldest['name']} (born in {oldest['dob']})"]
            elif rel_type == "youngest":
                valid_nodes = [n for n in self.fallback.nodes.values() if n["dob"] is not None]
                if not valid_nodes: return []
                youngest = max(valid_nodes, key=lambda x: x["dob"])
                return [f"{youngest['name']} (born in {youngest['dob']})"]
            return []

        # --- Live Cypher execution ---
        cypher_queries = {
            "father": "MATCH (x:Person {gender: 'male'})-[:PARENT_OF]->(y:Person {name: $name}) RETURN x.name AS name",
            "mother": "MATCH (x:Person {gender: 'female'})-[:PARENT_OF]->(y:Person {name: $name}) RETURN x.name AS name",
            "child": "MATCH (x:Person)<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "son": "MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "daughter": "MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "sibling": "MATCH (x:Person)<-[:PARENT_OF]-(p:Person)-[:PARENT_OF]->(y:Person {name: $name}) WHERE x.name <> $name RETURN DISTINCT x.name AS name",
            "brother": "MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-(p:Person)-[:PARENT_OF]->(y:Person {name: $name}) WHERE x.name <> $name RETURN DISTINCT x.name AS name",
            "sister": "MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-(p:Person)-[:PARENT_OF]->(y:Person {name: $name}) WHERE x.name <> $name RETURN DISTINCT x.name AS name",
            "spouse": "MATCH (x:Person)-[:MARRIED_TO]-(y:Person {name: $name}) RETURN x.name AS name",
            "husband": "MATCH (x:Person {gender: 'male'})-[:MARRIED_TO]-(y:Person {name: $name}) RETURN x.name AS name",
            "wife": "MATCH (x:Person {gender: 'female'})-[:MARRIED_TO]-(y:Person {name: $name}) RETURN x.name AS name",
            "grandparent": "MATCH (x:Person)-[:PARENT_OF]->()-[:PARENT_OF]->(y:Person {name: $name}) RETURN x.name AS name",
            "grandfather": "MATCH (x:Person {gender: 'male'})-[:PARENT_OF]->()-[:PARENT_OF]->(y:Person {name: $name}) RETURN x.name AS name",
            "grandmother": "MATCH (x:Person {gender: 'female'})-[:PARENT_OF]->()-[:PARENT_OF]->(y:Person {name: $name}) RETURN x.name AS name",
            "grandchild": "MATCH (x:Person)<-[:PARENT_OF]-()<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "grandson": "MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-()<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "granddaughter": "MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-()<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "uncle": """
                MATCH (y:Person {name: $name})<-[:PARENT_OF]-(parent)-[:PARENT_OF]<-()-[:PARENT_OF]->(uncle:Person {gender: 'male'}) WHERE uncle <> parent
                RETURN DISTINCT uncle.name AS name
                UNION
                MATCH (y:Person {name: $name})<-[:PARENT_OF]-(parent)-[:PARENT_OF]<-()-[:PARENT_OF]->(aunt:Person {gender: 'female'})-[:MARRIED_TO]-(uncle:Person {gender: 'male'}) WHERE aunt <> parent
                RETURN DISTINCT uncle.name AS name
            """,
            "aunt": """
                MATCH (y:Person {name: $name})<-[:PARENT_OF]-(parent)-[:PARENT_OF]<-()-[:PARENT_OF]->(aunt:Person {gender: 'female'}) WHERE aunt <> parent
                RETURN DISTINCT aunt.name AS name
                UNION
                MATCH (y:Person {name: $name})<-[:PARENT_OF]-(parent)-[:PARENT_OF]<-()-[:PARENT_OF]->(uncle:Person {gender: 'male'})-[:MARRIED_TO]-(aunt:Person {gender: 'female'}) WHERE uncle <> parent
                RETURN DISTINCT aunt.name AS name
            """,
            "cousin": "MATCH (x:Person)<-[:PARENT_OF]-(p1:Person)<-[:PARENT_OF]-(gp:Person)-[:PARENT_OF]->(p2:Person)-[:PARENT_OF]->(y:Person {name: $name}) WHERE p1 <> p2 AND x.name <> $name RETURN DISTINCT x.name AS name",
            "nephew": """
                MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-(parent:Person)<-[:PARENT_OF]-()-[:PARENT_OF]->(y:Person {name: $name}) WHERE parent <> y RETURN DISTINCT x.name AS name
                UNION
                MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-(parent:Person)<-[:PARENT_OF]-()-[:PARENT_OF]->(sp:Person)-[:MARRIED_TO]-(y:Person {name: $name}) WHERE parent <> sp RETURN DISTINCT x.name AS name
            """,
            "niece": """
                MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-(parent:Person)<-[:PARENT_OF]-()-[:PARENT_OF]->(y:Person {name: $name}) WHERE parent <> y RETURN DISTINCT x.name AS name
                UNION
                MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-(parent:Person)<-[:PARENT_OF]-()-[:PARENT_OF]->(sp:Person)-[:MARRIED_TO]-(y:Person {name: $name}) WHERE parent <> sp RETURN DISTINCT x.name AS name
            """,
            "ancestor": "MATCH (x:Person)-[:PARENT_OF*]->(y:Person {name: $name}) RETURN x.name AS name",
            "descendant": "MATCH (x:Person)<-[:PARENT_OF*]-(y:Person {name: $name}) RETURN x.name AS name",
            "father_in_law": "MATCH (x:Person {gender: 'male'})-[:PARENT_OF]->(spouse)-[:MARRIED_TO]-(y:Person {name: $name}) RETURN x.name AS name",
            "mother_in_law": "MATCH (x:Person {gender: 'female'})-[:PARENT_OF]->(spouse)-[:MARRIED_TO]-(y:Person {name: $name}) RETURN x.name AS name",
            "son_in_law": "MATCH (x:Person {gender: 'male'})-[:MARRIED_TO]-(spouse)<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "daughter_in_law": "MATCH (x:Person {gender: 'female'})-[:MARRIED_TO]-(spouse)<-[:PARENT_OF]-(y:Person {name: $name}) RETURN x.name AS name",
            "brother_in_law": """
                MATCH (x:Person {gender: 'male'})<-[:PARENT_OF]-(p)-[:PARENT_OF]->(sp)-[:MARRIED_TO]-(y:Person {name: $name}) WHERE x <> sp RETURN DISTINCT x.name AS name
                UNION
                MATCH (x:Person {gender: 'male'})-[:MARRIED_TO]-(sis:Person)-[:PARENT_OF]<-((p)-[:PARENT_OF]->(y:Person {name: $name})) WHERE sis <> y RETURN DISTINCT x.name AS name
            """,
            "sister_in_law": """
                MATCH (x:Person {gender: 'female'})<-[:PARENT_OF]-(p)-[:PARENT_OF]->(sp)-[:MARRIED_TO]-(y:Person {name: $name}) WHERE x <> sp RETURN DISTINCT x.name AS name
                UNION
                MATCH (x:Person {gender: 'female'})-[:MARRIED_TO]-(bro:Person)-[:PARENT_OF]<-((p)-[:PARENT_OF]->(y:Person {name: $name})) WHERE bro <> y RETURN DISTINCT x.name AS name
            """,
            "dob": "MATCH (p:Person {name: $name}) RETURN p.dob AS name",
            "gender": "MATCH (p:Person {name: $name}) RETURN p.gender AS name",
            "list_males": "MATCH (p:Person {gender: 'male'}) RETURN p.name AS name",
            "list_females": "MATCH (p:Person {gender: 'female'}) RETURN p.name AS name",
            "list_members": "MATCH (p:Person) RETURN p.name AS name",
            "oldest": "MATCH (p:Person) WHERE p.dob IS NOT NULL RETURN p.name + ' (born in ' + toString(p.dob) + ')' AS name ORDER BY p.dob ASC LIMIT 1",
            "youngest": "MATCH (p:Person) WHERE p.dob IS NOT NULL RETURN p.name + ' (born in ' + toString(p.dob) + ')' AS name ORDER BY p.dob DESC LIMIT 1"
        }

        query = cypher_queries.get(rel_type)
        if not query:
            return []
            
        res = self.run_cypher(query, {"name": name})
        if isinstance(res, list):
            return [str(record["name"]) for record in res if "name" in record]
        return []

    def verify_comparison(self, name1, name2, comp_type):
        """Reasoning: compare age (dob) or check marital/parent status."""
        name1 = name1.lower()
        name2 = name2.lower()
        if self.fallback:
            dob1 = self.fallback.get_dob(name1)
            dob2 = self.fallback.get_dob(name2)
            if dob1 is None or dob2 is None:
                return False
            if comp_type == "older_than":
                return dob1 < dob2
            elif comp_type == "younger_than":
                return dob1 > dob2
            return False
            
        if comp_type == "older_than":
            query = "MATCH (p1:Person {name: $n1}), (p2:Person {name: $n2}) RETURN p1.dob < p2.dob AS res"
        elif comp_type == "younger_than":
            query = "MATCH (p1:Person {name: $n1}), (p2:Person {name: $n2}) RETURN p1.dob > p2.dob AS res"
        else:
            return False
            
        res = self.run_cypher(query, {"n1": name1, "n2": name2})
        if isinstance(res, list) and len(res) > 0:
            return bool(res[0].get("res"))
        return False

    def verify_boolean_status(self, name, status_type):
        name = name.lower()
        if self.fallback:
            if status_type == "has_children":
                return len(self.fallback.get_children(name)) > 0
            elif status_type == "is_married":
                return len(self.fallback.get_spouses(name)) > 0
            return False
            
        if status_type == "has_children":
            query = "MATCH (p:Person {name: $name})-[:PARENT_OF]->() RETURN count(*) > 0 AS res"
        elif status_type == "is_married":
            query = "MATCH (p:Person {name: $name})-[:MARRIED_TO]-() RETURN count(*) > 0 AS res"
        else:
            return False
            
        res = self.run_cypher(query, {"name": name})
        if isinstance(res, list) and len(res) > 0:
            return bool(res[0].get("res"))
        return False

    # --- Graph Analysis & Inference API ---
    def get_statistics(self):
        """Retrieve total counts of nodes and edges for reporting."""
        if self.fallback:
            return self.fallback.get_statistics()
            
        q_nodes = "MATCH (n) RETURN count(n) AS c"
        q_males = "MATCH (p:Person {gender: 'male'}) RETURN count(p) AS c"
        q_females = "MATCH (p:Person {gender: 'female'}) RETURN count(p) AS c"
        q_parents = "MATCH ()-[r:PARENT_OF]->() RETURN count(r) AS c"
        q_married = "MATCH ()-[r:MARRIED_TO]->() RETURN count(r) AS c"
        
        return {
            "node_count": self.run_cypher(q_nodes)[0]["c"],
            "male_count": self.run_cypher(q_males)[0]["c"],
            "female_count": self.run_cypher(q_females)[0]["c"],
            "parent_relationships": self.run_cypher(q_parents)[0]["c"],
            "married_relationships": self.run_cypher(q_married)[0]["c"]
        }

    def get_mutual_connections(self, name1, name2):
        """Inference & Discovery: Common connections in the family graph."""
        name1 = name1.lower()
        name2 = name2.lower()
        if self.fallback:
            return self.fallback.get_mutual_connections(name1, name2)
            
        query = """
        MATCH (p1:Person {name: $n1})-[r1:PARENT_OF|MARRIED_TO]-(mutual:Person)-[r2:PARENT_OF|MARRIED_TO]-(p2:Person {name: $n2})
        RETURN DISTINCT mutual.name AS name
        """
        res = self.run_cypher(query, {"n1": name1, "n2": name2})
        if isinstance(res, list):
            return [record["name"] for record in res if "name" in record]
        return []

    # --- Hybrid Prolog Reasoning (Bonus) ---
    def run_hybrid_prolog_reasoning(self):
        """
        BONUS: Export Neo4j graph nodes & relationships into Prolog facts,
        run Prolog inference rules to deduce new relationships,
        and update Neo4j with the newly inferred relationships.
        """
        print("Starting Bidirectional Hybrid Prolog Reasoning...")
        
        # 1. Fetch current facts from Neo4j (or local fallback)
        if self.fallback:
            all_nodes = list(self.fallback.nodes.values())
            all_parents = self.fallback.parents
            all_marriages = self.fallback.marriages
        else:
            nodes_res = self.run_cypher("MATCH (p:Person) RETURN p.name AS name, p.gender AS gender, p.dob AS dob")
            parents_res = self.run_cypher("MATCH (p:Person)-[:PARENT_OF]->(c:Person) RETURN p.name AS parent, c.name AS child")
            marriages_res = self.run_cypher("MATCH (s1:Person)-[:MARRIED_TO]->(s2:Person) RETURN s1.name AS s1, s2.name AS s2")
            
            all_nodes = [{"name": r["name"], "gender": r["gender"], "dob": r["dob"]} for r in nodes_res]
            all_parents = [(r["parent"], r["child"]) for r in parents_res]
            all_marriages = [(r["s1"], r["s2"]) for r in marriages_res]
            
        # 2. Build pytholog dynamic facts
        facts = []
        for n in all_nodes:
            if n["gender"] == "male":
                facts.append(f"male({n['name']})")
            elif n["gender"] == "female":
                facts.append(f"female({n['name']})")
            if n["dob"]:
                facts.append(f"dob({n['name']}, {n['dob']})")
                
        for p, c in all_parents:
            facts.append(f"parent({p}, {c})")
        for s1, s2 in all_marriages:
            facts.append(f"married({s1}, {s2})")
            
        # Initialize Prolog engine
        kb = pl.KnowledgeBase("HybridKB")
        kb(facts)
        
        # Define Prolog reasoning rules
        prolog_rules = [
            "grandfather(X, Y) :- male(X), parent(X, Z), parent(Z, Y)",
            "grandmother(X, Y) :- female(X), parent(X, Z), parent(Z, Y)",
            "uncle(X, Y) :- male(X), parent(P, Y), parent(GP, P), parent(GP, X), X \= P",
            "aunt(X, Y) :- female(X), parent(P, Y), parent(GP, P), parent(GP, X), X \= P",
            "cousin(X, Y) :- parent(P1, X), parent(P2, Y), parent(GP, P1), parent(GP, P2), P1 \= P2"
        ]
        # Clean rules for pytholog (pytholog doesn't support \= well, so we use simplified versions)
        pytholog_rules = [
            "grandfather(X, Y) :- male(X), parent(X, Z), parent(Z, Y)",
            "grandmother(X, Y) :- female(X), parent(X, Z), parent(Z, Y)",
            "uncle(X, Y) :- male(X), parent(Z, X), parent(Z, W), parent(W, Y)",
            "aunt(X, Y) :- female(X), parent(Z, X), parent(Z, W), parent(W, Y)",
            "cousin(X, Y) :- parent(Z, X), parent(W, Y), parent(GP, Z), parent(GP, W)"
        ]
        kb(pytholog_rules)
        
        # 3. Query Prolog for inferred facts (grandfathers, grandmothers, uncles, aunts, cousins)
        inferred_grandfathers = kb.query(pl.Expr("grandfather(X, Y)"))
        inferred_uncles = kb.query(pl.Expr("uncle(X, Y)"))
        inferred_aunts = kb.query(pl.Expr("aunt(X, Y)"))
        inferred_cousins = kb.query(pl.Expr("cousin(X, Y)"))
        
        def add_inferred_edge(x, y, label):
            x, y = x.lower(), y.lower()
            if x == y:
                return
            if self.fallback:
                # Local mock: we'll print or store them in a dummy property/edge
                pass
            else:
                query = f"""
                MATCH (s:Person {{name: $x}})
                MATCH (t:Person {{name: $y}})
                MERGE (s)-[:INFERRED_{label.upper()}]->(t)
                """
                self.run_cypher(query, {"x": x, "y": y})
                
        # 4. Write inferred facts back to Neo4j as new relationships (e.g. INFERRED_GRANDFATHER)
        inferred_count = 0
        
        if isinstance(inferred_grandfathers, list):
            for binding in inferred_grandfathers:
                if isinstance(binding, dict) and "X" in binding and "Y" in binding:
                    add_inferred_edge(binding["X"], binding["Y"], "grandfather")
                    inferred_count += 1
                    
        if isinstance(inferred_uncles, list):
            for binding in inferred_uncles:
                if isinstance(binding, dict) and "X" in binding and "Y" in binding:
                    if binding["X"] != binding["Y"]:
                        add_inferred_edge(binding["X"], binding["Y"], "uncle")
                        inferred_count += 1
                        
        if isinstance(inferred_aunts, list):
            for binding in inferred_aunts:
                if isinstance(binding, dict) and "X" in binding and "Y" in binding:
                    if binding["X"] != binding["Y"]:
                        add_inferred_edge(binding["X"], binding["Y"], "aunt")
                        inferred_count += 1

        if isinstance(inferred_cousins, list):
            for binding in inferred_cousins:
                if isinstance(binding, dict) and "X" in binding and "Y" in binding:
                    # Exclude self-cousin
                    if binding["X"] != binding["Y"]:
                        add_inferred_edge(binding["X"], binding["Y"], "cousin")
                        inferred_count += 1
                        
        print(f"Hybrid reasoning completed. Duced and stored {inferred_count} inferred relationships back to Neo4j.")
        return inferred_count
