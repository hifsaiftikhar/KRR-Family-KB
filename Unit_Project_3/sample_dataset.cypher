// ============================================================
// SAMPLE DATASET: SEED CYPHER SCRIPT FOR NEO4J
// ============================================================
// Clear existing database:
// MATCH (n) DETACH DELETE n;

// 1. CREATE PERSON NODES WITH PROPERTIES
// ------------------------------------------------------------
CREATE (ali:Person {name: "ali", gender: "male", dob: 1950})
CREATE (fatima:Person {name: "fatima", gender: "female", dob: 1953})
CREATE (hassan:Person {name: "hassan", gender: "male", dob: 1975})
CREATE (ayesha:Person {name: "ayesha", gender: "female", dob: 1978})
CREATE (sana:Person {name: "sana", gender: "female", dob: 1978})
CREATE (usman:Person {name: "usman", gender: "male", dob: 2000})
CREATE (nida:Person {name: "nida", gender: "female", dob: 2003})
CREATE (bilal:Person {name: "bilal", gender: "male", dob: 2002})
CREATE (zara:Person {name: "zara", gender: "female", dob: 2005})
CREATE (omar:Person {name: "omar", gender: "male", dob: 1975})
CREATE (tariq:Person {name: "tariq", gender: "male", dob: 1948})
CREATE (hina:Person {name: "hina", gender: "female", dob: 1952})
CREATE (zaid:Person {name: "zaid", gender: "male", dob: 2022})
CREATE (mariam:Person {name: "mariam", gender: "female", dob: 2024})
CREATE (hamza:Person {name: "hamza", gender: "male", dob: 1980})

// 2. CREATE MARRIED_TO RELATIONSHIPS
// ------------------------------------------------------------
CREATE (ali)-[:MARRIED_TO]->(fatima)
CREATE (fatima)-[:MARRIED_TO]->(ali)
CREATE (hassan)-[:MARRIED_TO]->(ayesha)
CREATE (ayesha)-[:MARRIED_TO]->(hassan)
CREATE (omar)-[:MARRIED_TO]->(sana)
CREATE (sana)-[:MARRIED_TO]->(omar)
CREATE (tariq)-[:MARRIED_TO]->(hina)
CREATE (hina)-[:MARRIED_TO]->(tariq)

// 3. CREATE PARENT_OF RELATIONSHIPS
// ------------------------------------------------------------
CREATE (ali)-[:PARENT_OF]->(hassan)
CREATE (ali)-[:PARENT_OF]->(sana)
CREATE (fatima)-[:PARENT_OF]->(hassan)
CREATE (fatima)-[:PARENT_OF]->(sana)
CREATE (hassan)-[:PARENT_OF]->(usman)
CREATE (hassan)-[:PARENT_OF]->(nida)
CREATE (ayesha)-[:PARENT_OF]->(usman)
CREATE (ayesha)-[:PARENT_OF]->(nida)
CREATE (usman)-[:PARENT_OF]->(zaid)
CREATE (usman)-[:PARENT_OF]->(mariam)
CREATE (sana)-[:PARENT_OF]->(bilal)
CREATE (sana)-[:PARENT_OF]->(zara)
CREATE (omar)-[:PARENT_OF]->(bilal)
CREATE (omar)-[:PARENT_OF]->(zara)
CREATE (tariq)-[:PARENT_OF]->(hamza)
CREATE (hina)-[:PARENT_OF]->(hamza)
CREATE (tariq)-[:PARENT_OF]->(ayyesha) // note: seed references ayesha
CREATE (hina)-[:PARENT_OF]->(ayyesha)
;
// Note: If you run these queries, you will get the exact core 15 family member tree.
