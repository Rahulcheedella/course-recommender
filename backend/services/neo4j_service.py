import logging
from neo4j import GraphDatabase
from config import Config
from services.query_understanding import query_understanding_service

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.driver = None
        self.connect()

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD)
            )
            logger.info("Connected to Neo4j successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def execute_query(self, query, parameters=None):
        if not self.driver:
            self.connect()
        if not self.driver:
            return []

        try:
            with self.driver.session(database=Config.NEO4J_DATABASE) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []

    # ─────────────────────────────────────────────────────────────────────
    # GRAPHRAG STEP 3: GENERATE CYPHER FROM EXTRACTED ENTITIES
    # ─────────────────────────────────────────────────────────────────────

    def generate_cypher_from_entities(self, entities: dict) -> list[dict]:
        """
        Step 3 of the GraphRAG pipeline.

        Converts NLP-extracted entities into concrete Cypher query strings
        targeting the Neo4j knowledge graph.

        Returns a list of { label, cypher, params } objects so callers can
        execute each and merge the results.
        """
        cypher_queries = []

        technologies = entities.get("technologies", [])
        skills = entities.get("skills", [])
        departments = entities.get("departments", [])
        topics = entities.get("topics", [])
        categories = entities.get("categories", [])

        # ------------------------------------------------------------------
        # Query A: Direct Technology → Course match (highest priority)
        # ------------------------------------------------------------------
        for tech in technologies:
            cypher_queries.append({
                "label": f"Technology:{tech}",
                "cypher": """
                    MATCH (t:Technology)
                    WHERE toLower(t.name) = toLower($tech)
                       OR toLower(t.name) CONTAINS toLower($tech)
                       OR toLower($tech) CONTAINS toLower(t.name)
                    MATCH (c:Course)-[:COVERS]->(t)
                    RETURN c.id AS course_id, c.title AS title,
                           t.name AS matched_via, 'technology_match' AS match_type,
                           100 AS base_score
                    LIMIT 15
                """,
                "params": {"tech": tech}
            })

            # Query A2: 2-hop connected technologies (related graph nodes)
            cypher_queries.append({
                "label": f"RelatedTech:{tech}",
                "cypher": """
                    MATCH (t:Technology)
                    WHERE toLower(t.name) = toLower($tech)
                       OR toLower(t.name) CONTAINS toLower($tech)
                    MATCH (t)-[:RELATED_TO*1..2]-(related:Technology)
                    MATCH (c:Course)-[:COVERS]->(related)
                    RETURN c.id AS course_id, c.title AS title,
                           related.name AS matched_via, 'related_tech_2hop' AS match_type,
                           50 AS base_score
                    LIMIT 10
                """,
                "params": {"tech": tech}
            })

        # ------------------------------------------------------------------
        # Query B: Skill → Course match
        # ------------------------------------------------------------------
        for skill in skills:
            cypher_queries.append({
                "label": f"Skill:{skill}",
                "cypher": """
                    MATCH (s:Skill)
                    WHERE toLower(s.name) = toLower($skill)
                       OR toLower(s.name) CONTAINS toLower($skill)
                       OR toLower($skill) CONTAINS toLower(s.name)
                    MATCH (c:Course)-[:TEACHES]->(s)
                    RETURN c.id AS course_id, c.title AS title,
                           s.name AS matched_via, 'skill_match' AS match_type,
                           85 AS base_score
                    LIMIT 10
                """,
                "params": {"skill": skill}
            })

        # ------------------------------------------------------------------
        # Query C: Department → Course match
        # (lower weight; used for context, not primary search signal)
        # ------------------------------------------------------------------
        for dept in departments:
            cypher_queries.append({
                "label": f"Department:{dept}",
                "cypher": """
                    MATCH (d:Department {name: $dept})<-[:BELONGS_TO]-(c:Course)
                    RETURN c.id AS course_id, c.title AS title,
                           d.name AS matched_via, 'department_match' AS match_type,
                           25 AS base_score
                    LIMIT 12
                """,
                "params": {"dept": dept}
            })

        # ------------------------------------------------------------------
        # Query D: Category → Course match
        # ------------------------------------------------------------------
        for cat in categories:
            cypher_queries.append({
                "label": f"Category:{cat}",
                "cypher": """
                    MATCH (cat:Category {name: $cat})<-[:BELONGS_TO]-(c:Course)
                    RETURN c.id AS course_id, c.title AS title,
                           cat.name AS matched_via, 'category_match' AS match_type,
                           30 AS base_score
                    LIMIT 10
                """,
                "params": {"cat": cat}
            })

        return cypher_queries

    # ─────────────────────────────────────────────────────────────────────
    # GRAPHRAG STEP 4: EXECUTE CYPHER QUERIES & MERGE RESULTS
    # ─────────────────────────────────────────────────────────────────────

    def execute_graphrag_pipeline(self, query_text: str) -> dict:
        """
        Full 5-step GraphRAG pipeline execution:

        Step 1  — Raw user query text arrives.
        Step 2  — NLP entity extraction (departments, technologies, skills …).
        Step 3  — Entity → Cypher query generation.
        Step 4  — Execute each Cypher query against Neo4j.
        Step 5  — Merge + rank results (Llama grounding happens in llama_service).

        Returns structured context ready for LLM response generation.
        """

        # ── Step 2: NLP Entity Extraction ──────────────────────────────────
        understood = query_understanding_service.understand(query_text)

        departments = understood.get("departments", [])
        technologies = understood.get("technologies", [])
        skills = understood.get("skills", [])
        topics = understood.get("topics", [])
        categories = understood.get("categories", [])

        all_entities = list(dict.fromkeys(
            departments + technologies + skills + topics + categories
        ))

        logger.info(
            f"GraphRAG Step 2 — Extracted entities: dept={departments}, "
            f"tech={technologies}, skills={skills}"
        )

        # ── Step 3: Generate Cypher Queries ────────────────────────────────
        cypher_queries = self.generate_cypher_from_entities(understood)

        logger.info(
            f"GraphRAG Step 3 — Generated {len(cypher_queries)} Cypher queries"
        )

        # Store the generated Cypher for transparency display in frontend
        cypher_strings = [
            f"// {q['label']}\n{q['cypher'].strip()}"
            for q in cypher_queries[:3]   # show top 3 in UI
        ]

        # ── Step 4: Execute Cypher Against Neo4j ───────────────────────────
        course_scores: dict[str, float] = {}
        match_reasons: dict[str, str] = {}
        match_types: dict[str, str] = {}
        matched_techs: list[str] = []
        related_techs: list[str] = []

        neo4j_available = bool(self.driver)

        for q in cypher_queries:
            rows = self.execute_query(q["cypher"], q["params"])

            for row in rows:
                course_id = row.get("course_id")
                if not course_id:
                    continue

                base_score = float(row.get("base_score", 20))
                match_type = row.get("match_type", "")
                matched_via = row.get("matched_via", "")

                # Accumulate scores
                current = course_scores.get(course_id, 0.0)
                course_scores[course_id] = current + base_score

                # Track match reason (keep the highest-score one)
                if course_id not in match_reasons or base_score > course_scores.get(course_id, 0):
                    match_reasons[course_id] = matched_via
                    match_types[course_id] = match_type

                # Track discovered tech/entity names for transparency
                if match_type in ("technology_match", "skill_match") and matched_via:
                    if matched_via not in matched_techs:
                        matched_techs.append(matched_via)
                elif match_type == "related_tech_2hop" and matched_via:
                    if matched_via not in related_techs:
                        related_techs.append(matched_via)

        logger.info(
            f"GraphRAG Step 4 — Neo4j returned {len(course_scores)} distinct courses"
        )

        # Sort by accumulated score
        sorted_course_ids = sorted(
            course_scores.keys(),
            key=lambda cid: course_scores[cid],
            reverse=True
        )

        return {
            # Entity extraction results (Step 2)
            "entities": all_entities,
            "departments": departments,
            "technologies": technologies,
            "skills": skills,
            "topics": topics,
            "categories": categories,
            "understood_query": understood,

            # Cypher queries generated (Step 3 — for transparency)
            "cypher_queries": cypher_strings,

            # Neo4j execution results (Step 4)
            "neo4j_available": neo4j_available,
            "matched_course_ids": sorted_course_ids,
            "course_scores": course_scores,
            "match_reasons": match_reasons,
            "match_types": match_types,
            "matched_techs": matched_techs,
            "related_techs": related_techs,
        }

    # --- USER PROFILE & GRAPH NODE UPDATES ---
    def sync_user(self, user_data):
        """Syncs user node, department, skills, and initial interests in Neo4j."""
        query = """
        MERGE (u:User {id: $id})
        SET u.name = $name,
            u.email = $email,
            u.department = $department,
            u.experience = $experience

        WITH u
        MERGE (d:Department {name: $department})
        MERGE (u)-[:BELONGS_TO]->(d)
        """
        self.execute_query(query, user_data)

        # Sync Skills
        for skill in user_data.get("skills", []):
            skill_query = """
            MATCH (u:User {id: $id})
            MERGE (s:Skill {name: $skill})
            MERGE (u)-[:HAS_SKILL]->(s)
            """
            self.execute_query(skill_query, {"id": user_data["id"], "skill": skill})

        # Sync Preferred Domains / Interests
        for tech in user_data.get("interests", []):
            tech_query = """
            MATCH (u:User {id: $id})
            MERGE (t:Technology {name: $tech})
            MERGE (u)-[r:INTERESTED_IN]->(t)
            ON CREATE SET r.score = 5.0
            """
            self.execute_query(tech_query, {"id": user_data["id"], "tech": tech})

    def update_interest_score(self, user_id, tech_or_skill, weight=1.0):
        """Dynamically increments dynamic interest weight on graph relationship."""
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (t:Technology {name: $tech})
        MERGE (u)-[r:INTERESTED_IN]->(t)
        ON CREATE SET r.score = $weight
        ON MATCH SET r.score = coalesce(r.score, 0) + $weight
        RETURN r.score as new_score
        """
        return self.execute_query(query, {"user_id": user_id, "tech": tech_or_skill, "weight": weight})

    def record_course_interaction(self, user_id, course_id, interaction_type):
        """Record (User)-[:VIEWED|CLICKED|SAVED|ENROLLED_IN|COMPLETED]->(Course)."""
        rel_map = {
            "course_view": "VIEWED",
            "course_click": "CLICKED",
            "wishlist": "SAVED",
            "enrollment": "ENROLLED_IN",
            "completion": "COMPLETED"
        }
        rel_type = rel_map.get(interaction_type, "VIEWED")
        query = f"""
        MATCH (u:User {{id: $user_id}}), (c:Course {{id: $course_id}})
        MERGE (u)-[:{rel_type}]->(c)
        """
        self.execute_query(query, {"user_id": user_id, "course_id": course_id})

    # --- KNOWLEDGE GRAPH TRAVERSALS & EXPLANATION TRACES ---
    def get_user_graph_context(self, user_id):
        """Retrieves user's department, skills, interests, and interaction history."""
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:BELONGS_TO]->(d:Department)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (u)-[r:INTERESTED_IN]->(t:Technology)
        OPTIONAL MATCH (u)-[:VIEWED]->(vc:Course)
        OPTIONAL MATCH (u)-[:SAVED]->(sc:Course)
        OPTIONAL MATCH (u)-[:ENROLLED_IN]->(ec:Course)

        RETURN d.name as department,
               collect(DISTINCT s.name) as skills,
               collect(DISTINCT {tech: t.name, score: r.score}) as interests,
               collect(DISTINCT vc.id) as viewed_courses,
               collect(DISTINCT sc.id) as saved_courses,
               collect(DISTINCT ec.id) as enrolled_courses
        """
        result = self.execute_query(query, {"user_id": user_id})
        return result[0] if result else {}

    def extract_entities_and_search_graph(self, query_text):
        """
        Graph-RAG retrieval.

        Understands a natural-language query first and then retrieves
        relevant entities and courses from Neo4j.

        The user's requested technology/topic is treated as the primary
        search signal. Department is contextual unless the user explicitly
        searches for the department itself.
        """

        understood = query_understanding_service.understand(
            query_text
        )

        departments = understood.get("departments", [])
        technologies = understood.get("technologies", [])
        skills = understood.get("skills", [])
        topics = understood.get("topics", [])
        categories = understood.get("categories", [])

        entities = list(
            dict.fromkeys(
                departments
                + technologies
                + skills
                + topics
                + categories
            )
        )

        result = {
            "entities": entities,
            "departments": departments,
            "technologies": technologies,
            "skills": skills,
            "topics": topics,
            "categories": categories,
            "matched_techs": [],
            "related_techs": [],
            "matched_course_ids": [],
            "course_scores": {},
            "understood_query": understood
        }

        # ---------------------------------------------------------
        # 1. TECHNOLOGY MATCH
        # ---------------------------------------------------------

        for technology in technologies:

            query = """
            MATCH (t:Technology)
            WHERE toLower(t.name) = toLower($value)
            OR toLower(t.name) CONTAINS toLower($value)
            OR toLower($value) CONTAINS toLower(t.name)

            OPTIONAL MATCH (t)-[:RELATED_TO*1..2]-(related:Technology)

            OPTIONAL MATCH (course:Course)-[:COVERS]->(t)

            OPTIONAL MATCH (related_course:Course)-[:COVERS]->(related)

            RETURN
                collect(DISTINCT t.name) AS matched_techs,
                collect(DISTINCT related.name) AS related_techs,
                collect(DISTINCT course.id) AS direct_courses,
                collect(DISTINCT related_course.id) AS related_courses
            """

            rows = self.execute_query(
                query,
                {"value": technology}
            )

            for row in rows:

                result["matched_techs"].extend(
                    row.get("matched_techs", [])
                )

                result["related_techs"].extend(
                    row.get("related_techs", [])
                )

                for course_id in row.get(
                    "direct_courses",
                    []
                ):
                    if course_id:
                        result["matched_course_ids"].append(
                            course_id
                        )
                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 100
                        )

                for course_id in row.get(
                    "related_courses",
                    []
                ):
                    if course_id:
                        result["matched_course_ids"].append(
                            course_id
                        )
                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 45
                        )

        # ---------------------------------------------------------
        # 2. SKILL MATCH
        # ---------------------------------------------------------

        for skill in skills:

            query = """
            MATCH (s:Skill)
            WHERE toLower(s.name) = toLower($value)
            OR toLower(s.name) CONTAINS toLower($value)
            OR toLower($value) CONTAINS toLower(s.name)

            OPTIONAL MATCH (course:Course)-[:TEACHES]->(s)

            OPTIONAL MATCH (s)-[:RELATED_TO*1..2]-(related:Skill)

            OPTIONAL MATCH (related_course:Course)-[:TEACHES]->(related)

            RETURN
                collect(DISTINCT s.name) AS matched_skills,
                collect(DISTINCT related.name) AS related_skills,
                collect(DISTINCT course.id) AS direct_courses,
                collect(DISTINCT related_course.id) AS related_courses
            """

            rows = self.execute_query(
                query,
                {"value": skill}
            )

            for row in rows:

                result["matched_techs"].extend(
                    row.get("matched_skills", [])
                )

                result["related_techs"].extend(
                    row.get("related_skills", [])
                )

                for course_id in row.get(
                    "direct_courses",
                    []
                ):

                    if course_id:
                        result["matched_course_ids"].append(
                            course_id
                        )

                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 85
                        )

                for course_id in row.get(
                    "related_courses",
                    []
                ):

                    if course_id:
                        result["matched_course_ids"].append(
                            course_id
                        )

                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 35
                        )

        # ---------------------------------------------------------
        # 3. TOPIC MATCH
        # ---------------------------------------------------------

        for topic in topics:

            query = """
            MATCH (t:Topic)
            WHERE toLower(t.name) = toLower($value)
            OR toLower(t.name) CONTAINS toLower($value)
            OR toLower($value) CONTAINS toLower(t.name)

            OPTIONAL MATCH (course:Course)-[:TAGGED_WITH]->(t)

            OPTIONAL MATCH (t)-[:RELATED_TO*1..2]-(related:Topic)

            OPTIONAL MATCH (related_course:Course)-[:TAGGED_WITH]->(related)

            RETURN
                collect(DISTINCT t.name) AS matched_topics,
                collect(DISTINCT related.name) AS related_topics,
                collect(DISTINCT course.id) AS direct_courses,
                collect(DISTINCT related_course.id) AS related_courses
            """

            rows = self.execute_query(
                query,
                {"value": topic}
            )

            for row in rows:

                result["matched_techs"].extend(
                    row.get("matched_topics", [])
                )

                result["related_techs"].extend(
                    row.get("related_topics", [])
                )

                for course_id in row.get(
                    "direct_courses",
                    []
                ):

                    if course_id:

                        result["matched_course_ids"].append(
                            course_id
                        )

                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 90
                        )

                for course_id in row.get(
                    "related_courses",
                    []
                ):

                    if course_id:

                        result["matched_course_ids"].append(
                            course_id
                        )

                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 40
                        )

        # ---------------------------------------------------------
        # 4. DEPARTMENT MATCH
        # ---------------------------------------------------------

        for department in departments:

            query = """
            MATCH (d:Department {name: $department})
                <-[:BELONGS_TO]-(course:Course)

            RETURN collect(DISTINCT course.id) AS course_ids
            """

            rows = self.execute_query(
                query,
                {"department": department}
            )

            for row in rows:

                for course_id in row.get(
                    "course_ids",
                    []
                ):

                    if course_id:

                        result["matched_course_ids"].append(
                            course_id
                        )

                        # Department is deliberately lower weight
                        # than an explicit technology/topic search.
                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 20
                        )

        # ---------------------------------------------------------
        # 5. CATEGORY MATCH
        # ---------------------------------------------------------

        for category in categories:

            query = """
            MATCH (cat:Category {name: $category})
                <-[:BELONGS_TO]-(course:Course)

            RETURN collect(DISTINCT course.id) AS course_ids
            """

            rows = self.execute_query(
                query,
                {"category": category}
            )

            for row in rows:

                for course_id in row.get(
                    "course_ids",
                    []
                ):

                    if course_id:

                        result["matched_course_ids"].append(
                            course_id
                        )

                        result["course_scores"][course_id] = (
                            result["course_scores"].get(
                                course_id,
                                0
                            ) + 25
                        )

        result["matched_techs"] = list(
            dict.fromkeys(
                x for x in result["matched_techs"]
                if x
            )
        )

        result["related_techs"] = list(
            dict.fromkeys(
                x for x in result["related_techs"]
                if x
            )
        )

        result["matched_course_ids"] = list(
            dict.fromkeys(
                x for x in result["matched_course_ids"]
                if x
            )
        )

        return result

    def get_traversed_recommendations(self, user_id):
        """Traverse 2-hop & 3-hop relationships in Knowledge Graph, including cross-department skill paths."""
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:BELONGS_TO]->(d:Department)<-[:BELONGS_TO]-(c_dept:Course)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)<-[:TEACHES]-(c_skill:Course)
        OPTIONAL MATCH (u)-[r:INTERESTED_IN]->(t1:Technology)
        OPTIONAL MATCH (c_tech:Course)-[:COVERS]->(t1)
        OPTIONAL MATCH (t1)-[:RELATED_TO]->(t2:Technology)<-[:COVERS]-(c_reltech:Course)

        WITH u, d,
            collect(DISTINCT {course_id: c_dept.id, reason: 'Matches your department (' + d.name + ')'}) as dept_recs,
            collect(DISTINCT {course_id: c_skill.id, reason: 'Teaches skills matching your background (' + s.name + ')'}) as skill_recs,
            collect(DISTINCT {
                course_id: c_tech.id, 
                reason: CASE 
                    WHEN c_tech.department <> d.name THEN 'Cross-department recommendation: Connects your ' + d.name + ' background with your growing ' + t1.name + ' interest network'
                    ELSE 'Covers technology you are interested in (' + t1.name + ')'
                END
            }) as tech_recs,
            collect(DISTINCT {course_id: c_reltech.id, reason: 'Connected in Knowledge Graph: ' + t1.name + ' → ' + t2.name}) as rel_tech_recs

        RETURN dept_recs + skill_recs + tech_recs + rel_tech_recs as candidates
        """
        result = self.execute_query(query, {"user_id": user_id})
        if result and result[0].get("candidates"):
            return [c for c in result[0]["candidates"] if c.get("course_id")]
        return []

    def get_visual_graph(self, user_id):
        """Generates node-edge data for the interactive Knowledge Graph frontend page."""
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[r1:BELONGS_TO]->(d:Department)
        OPTIONAL MATCH (u)-[r2:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (u)-[r3:INTERESTED_IN]->(t:Technology)
        OPTIONAL MATCH (u)-[r4:SAVED|ENROLLED_IN|VIEWED]->(c:Course)
        OPTIONAL MATCH (c)-[r5:COVERS]->(ct:Technology)

        RETURN u, d, s, t, c, ct
        LIMIT 100
        """
        raw_records = self.execute_query(query, {"user_id": user_id})

        nodes = []
        edges = []
        node_ids = set()

        def add_node(node_id, label, type_group, val=10):
            if node_id not in node_ids:
                node_ids.add(node_id)
                nodes.append({
                    "id": str(node_id),
                    "label": str(label),
                    "group": type_group,
                    "value": val
                })

        for rec in raw_records:
            u = rec.get("u")
            if u:
                add_node(f"user_{user_id}", u.get("name", "User"), "User", 25)

            d = rec.get("d")
            if d:
                add_node(f"dept_{d['name']}", d["name"], "Department", 20)
                edges.append({"from": f"user_{user_id}", "to": f"dept_{d['name']}", "label": "BELONGS_TO"})

            s = rec.get("s")
            if s:
                add_node(f"skill_{s['name']}", s["name"], "Skill", 15)
                edges.append({"from": f"user_{user_id}", "to": f"skill_{s['name']}", "label": "HAS_SKILL"})

            t = rec.get("t")
            if t:
                add_node(f"tech_{t['name']}", t["name"], "Technology", 15)
                edges.append({"from": f"user_{user_id}", "to": f"tech_{t['name']}", "label": "INTERESTED_IN"})

            c = rec.get("c")
            if c:
                add_node(f"course_{c['id']}", c["title"], "Course", 18)
                edges.append({"from": f"user_{user_id}", "to": f"course_{c['id']}", "label": "INTERACTED"})

                ct = rec.get("ct")
                if ct:
                    add_node(f"tech_{ct['name']}", ct["name"], "Technology", 15)
                    edges.append({"from": f"course_{c['id']}", "to": f"tech_{ct['name']}", "label": "COVERS"})

        return {"nodes": nodes, "edges": edges}

    def search_by_title(self, query_text: str) -> dict:
        """
        Direct course-title search in the Knowledge Graph.

        Matches the raw user query against Course nodes by:
          - Course title       (score 150 — highest priority)
          - Course category    (score  60)
          - Course description (score  30)

        Returns the same structure as extract_entities_and_search_graph()
        so the search route can easily merge the two result sets.
        """
        if not query_text or not query_text.strip():
            return {"matched_course_ids": [], "course_scores": {}}

        term = query_text.strip().lower()

        # Split into individual words so "machine learning" matches
        # both "machine" and "learning" inside a title independently.
        words = [w for w in term.split() if len(w) >= 3]

        course_scores: dict = {}

        # --- Title match (150 pts per matching word) ---
        title_query = """
        MATCH (c:Course)
        WHERE toLower(c.title) CONTAINS $term
        RETURN c.id AS course_id, 150 AS score
        LIMIT 20
        """
        for row in self.execute_query(title_query, {"term": term}):
            cid = row.get("course_id")
            if cid:
                course_scores[cid] = course_scores.get(cid, 0) + 150

        # --- Per-word title match (80 pts each word hit) ---
        for word in words:
            word_query = """
            MATCH (c:Course)
            WHERE toLower(c.title) CONTAINS $word
            RETURN c.id AS course_id
            LIMIT 20
            """
            for row in self.execute_query(word_query, {"word": word}):
                cid = row.get("course_id")
                if cid:
                    course_scores[cid] = course_scores.get(cid, 0) + 80

        # --- Category match (60 pts) ---
        cat_query = """
        MATCH (c:Course)
        WHERE toLower(c.category) CONTAINS $term
        RETURN c.id AS course_id
        LIMIT 20
        """
        for row in self.execute_query(cat_query, {"term": term}):
            cid = row.get("course_id")
            if cid:
                course_scores[cid] = course_scores.get(cid, 0) + 60

        # --- Description keyword match (30 pts per word) ---
        for word in words:
            desc_query = """
            MATCH (c:Course)
            WHERE toLower(c.description) CONTAINS $word
            RETURN c.id AS course_id
            LIMIT 15
            """
            for row in self.execute_query(desc_query, {"word": word}):
                cid = row.get("course_id")
                if cid:
                    course_scores[cid] = course_scores.get(cid, 0) + 30

        sorted_ids = sorted(
            course_scores.keys(),
            key=lambda cid: course_scores[cid],
            reverse=True
        )

        return {
            "matched_course_ids": sorted_ids,
            "course_scores": course_scores
        }

    def close(self):
        if self.driver:
            self.driver.close()

neo4j_service = Neo4jService()
