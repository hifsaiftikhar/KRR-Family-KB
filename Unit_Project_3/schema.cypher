// ============================================================
// NEO4J GRAPH DATABASE SCHEMA DESIGN
// ============================================================

// 1. NODE LABELS & PROPERTIES
// ------------------------------------------------------------
// Label: :Person
// Properties:
//   - name (String): Unique identifier, representing the lowercase name of the person.
//   - gender (String): "male" or "female".
//   - dob (Integer): Year of birth (e.g. 1975).
//
// Example node creation:
// CREATE (p:Person {name: "hassan", gender: "male", dob: 1975})


// 2. RELATIONSHIP TYPES
// ------------------------------------------------------------
// Relationship: -[:PARENT_OF]->
// Direction: Directed from Parent to Child.
// Example: (ali)-[:PARENT_OF]->(hassan)
//
// Relationship: -[:MARRIED_TO]->
// Direction: Undirected / Bi-directional.
// Example: (ali)-[:MARRIED_TO]->(fatima)


// 3. INFERRED RELATIONSHIP TYPES (DEDUCED BY HYBRID PROLOG ENGINE)
// ------------------------------------------------------------
// Deduced by bidirectional hybrid Prolog engine and stored back into Neo4j:
// - -[:INFERRED_GRANDFATHER]->
// - -[:INFERRED_GRANDMOTHER]->
// - -[:INFERRED_UNCLE]->
// - -[:INFERRED_AUNT]->
// - -[:INFERRED_COUSIN]->
//
// Example: (tariq)-[:INFERRED_GRANDFATHER]->(usman)


// 4. UNIQUENESS CONSTRAINTS & INDEXES
// ------------------------------------------------------------
// Ensure name is unique:
CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE;

// Index on gender for fast retrieval of males/females:
CREATE INDEX person_gender_idx IF NOT EXISTS
FOR (p:Person) ON (p.gender);

// Index on Date of Birth:
CREATE INDEX person_dob_idx IF NOT EXISTS
FOR (p:Person) ON (p.dob);
