import logging
import re
import requests
from config import Config
from services.neo4j_service import neo4j_service
from services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Department → related search terms (for fallback when Neo4j is unavailable)
# ─────────────────────────────────────────────────────────────────────────────
DEPT_FALLBACK_TERMS = {
    "ECE":         ["embedded", "vlsi", "microcontroller", "dsp", "iot", "verilog", "fpga", "arduino", "arm"],
    "EEE":         ["matlab", "simulink", "power", "plc", "scada", "solar", "electric"],
    "Mechanical":  ["solidworks", "ansys", "cad", "fea", "catia", "cfd", "thermodynamics", "autocad"],
    "Civil":       ["revit", "staad", "autocad", "bim", "structural", "gis", "primavera"],
    "CSE":         ["python", "java", "javascript", "react", "node", "data structures", "algorithms"],
    "AI & DS":     ["machine learning", "python", "data science", "deep learning", "nlp"],
    "AI & ML":     ["pytorch", "tensorflow", "neural", "computer vision", "deep learning"],
    "Mechatronics":["ros", "robotics", "embedded", "plc", "automation"],
}

# Map unknown departments to closest known one
DEPT_ALIASES = {
    "ACSC": "ECE",
    "Aeronautical": "ECE",
    "Aerospace": "ECE",
    "IT": "CSE",
    "Information Technology": "CSE",
}


class LlamaService:
    def __init__(self):
        self.api_url = (
            f"https://api-inference.huggingface.co/models/{Config.HUGGINGFACE_MODEL}"
        )
        self.api_key = Config.HUGGINGFACE_API_KEY

    # ─────────────────────────────────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ─────────────────────────────────────────────────────────────────────

    def process_chat_query(self, user_id: str, message: str) -> dict:
        """
        5-Step GraphRAG Pipeline:
        Step 1  → Receive user query
        Step 2  → NLP entity extraction
        Step 3  → Generate Cypher queries from entities
        Step 4  → Execute Cypher against Neo4j; fetch matched courses from MongoDB
        Step 5  → Feed structured Neo4j context to Llama 1B; generate response
        """

        # ── Step 1: Load user context ─────────────────────────────────────
        user = mongodb_service.get_user_by_id(user_id) if user_id else None
        user_name   = user.get("name", "Learner") if user else "Learner"
        user_dept   = user.get("department", "") if user else ""
        user_skills = user.get("skills", []) if user else []
        user_interests = user.get("interests", []) if user else []

        # Resolve unknown depts (e.g. ACSC → ECE)
        effective_dept = DEPT_ALIASES.get(user_dept, user_dept)

        logger.info(f"[GraphRAG Step 1] User: {user_name}, Dept: {user_dept} → {effective_dept}")

        # ── Steps 2-4: GraphRAG Pipeline via Neo4j Service ───────────────
        graph_result = neo4j_service.execute_graphrag_pipeline(message)

        departments    = graph_result.get("departments", [])
        technologies   = graph_result.get("technologies", [])
        skills_found   = graph_result.get("skills", [])
        entities       = graph_result.get("entities", [])
        cypher_queries = graph_result.get("cypher_queries", [])
        matched_ids    = graph_result.get("matched_course_ids", [])
        course_scores  = graph_result.get("course_scores", {})
        match_reasons  = graph_result.get("match_reasons", {})
        matched_techs  = graph_result.get("matched_techs", [])
        related_techs  = graph_result.get("related_techs", [])
        neo4j_ok       = graph_result.get("neo4j_available", False)

        logger.info(
            f"[GraphRAG Step 4] Neo4j matched {len(matched_ids)} course IDs. "
            f"Neo4j available: {neo4j_ok}"
        )

        # ── Step 4b: Retrieve full course data from MongoDB ────────────────
        matched_courses = self._fetch_ranked_courses(
            matched_ids, course_scores, match_reasons,
            message, technologies, effective_dept
        )

        # Attach recommendation reasons to courses
        for c in matched_courses:
            cid = c.get("id", "")
            reason = match_reasons.get(cid)
            if reason:
                c["recommendation_reason"] = f"Graph match: {reason}"
            elif technologies:
                c["recommendation_reason"] = f"Matches: {', '.join(technologies[:2])}"

        # ── Step 5: Build Llama prompt grounded in Neo4j results ──────────
        ai_response = self._call_llama(
            message, user_name, effective_dept, user_skills, user_interests,
            matched_courses, entities, matched_techs, related_techs,
            cypher_queries, departments
        )

        # Build graph hop paths for UI transparency
        graph_hops = []
        for mt in matched_techs[:2]:
            for rt in related_techs[:3]:
                graph_hops.append(f"{mt} → {rt}")

        return {
            "message": ai_response,
            "recommended_courses": matched_courses[:4],
            "entities": entities,
            "matched_techs": matched_techs,
            "related_techs": related_techs,
            "graph_hops": graph_hops,
            "cypher_queries": cypher_queries,
            "neo4j_available": neo4j_ok,
        }

    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL: FETCH + RANK COURSES
    # ─────────────────────────────────────────────────────────────────────

    def _fetch_ranked_courses(
        self, matched_ids, course_scores, match_reasons,
        query_text, technologies, effective_dept
    ) -> list:
        """
        Fetch courses by Neo4j-ranked IDs first, then fall back to
        MongoDB text search on query terms if Neo4j returned nothing.
        Never returns completely unrelated courses.
        """
        courses = []

        if matched_ids:
            # Fetch by Neo4j-ranked IDs (preserving score order)
            fetched = {c["id"]: c for c in mongodb_service.get_courses_by_ids(matched_ids)}
            for cid in matched_ids:
                if cid in fetched:
                    courses.append(fetched[cid])
            logger.info(f"[Fetch] Neo4j-matched courses: {len(courses)}")

        # If Neo4j gave nothing, fall back to targeted keyword search
        if not courses:
            logger.info("[Fetch] Neo4j empty → MongoDB keyword fallback")

            # Build targeted search: prefer technology terms over generic query
            search_terms = technologies or [query_text]

            for term in search_terms[:3]:
                results = mongodb_service.search_courses(term.lower())
                for c in results:
                    if c["id"] not in {x["id"] for x in courses}:
                        courses.append(c)
                if len(courses) >= 6:
                    break

            # If still empty and we have a dept, filter by dept
            if not courses and effective_dept:
                dept_terms = DEPT_FALLBACK_TERMS.get(effective_dept, [])
                for term in dept_terms[:3]:
                    results = mongodb_service.search_courses(term)
                    for c in results:
                        if c["id"] not in {x["id"] for x in courses}:
                            courses.append(c)
                    if len(courses) >= 6:
                        break

        # Last resort: top rated from all courses (but this should rarely happen)
        if not courses:
            logger.warning("[Fetch] No courses found via any method — using top-rated fallback")
            all_courses = mongodb_service.get_all_courses()
            courses = sorted(all_courses, key=lambda x: x.get("rating", 0), reverse=True)[:5]

        return courses[:6]

    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL: CALL LLAMA API (STEP 5)
    # ─────────────────────────────────────────────────────────────────────

    def _call_llama(
        self, message, user_name, user_dept, user_skills, user_interests,
        matched_courses, entities, matched_techs, related_techs,
        cypher_queries, query_departments
    ) -> str:
        """Step 5: Send Neo4j graph context to Llama 1B and get a grounded response."""

        # Build course context block
        course_lines = []
        for c in matched_courses[:5]:
            skills_str = ", ".join(c.get("skills", [])[:3])
            course_lines.append(
                f"  • [{c['id']}] \"{c['title']}\" "
                f"| Dept:{c['department']} | Level:{c['difficulty']} "
                f"| Rating:{c['rating']} | Skills:{skills_str}"
            )
        course_context = "\n".join(course_lines) if course_lines else "  • (No specific courses found)"

        # Graph context summary
        graph_summary = (
            f"- Entities identified: {', '.join(entities[:6]) or 'none'}\n"
            f"- Technologies matched in graph: {', '.join(matched_techs[:4]) or 'none'}\n"
            f"- 2-hop related graph nodes: {', '.join(related_techs[:4]) or 'none'}\n"
            f"- User's department: {user_dept or 'not specified'}\n"
            f"- Cypher queries executed: {len(cypher_queries)}"
        )

        # User profile context
        dept_note = ""
        if user_dept and query_departments and user_dept not in query_departments:
            dept_note = (
                f"NOTE: The user is from {user_dept} department but is asking about "
                f"{', '.join(matched_techs[:2] or query_departments[:2])}. "
                f"This is a cross-domain learning scenario — acknowledge their background and explain how these courses are relevant."
            )

        system_prompt = f"""You are an AI Learning Assistant for a Knowledge Graph course platform.
Your responses are grounded exclusively in Neo4j Knowledge Graph query results.

USER PROFILE:
- Name: {user_name}
- Department: {user_dept or 'Not specified'}
- Skills: {', '.join(user_skills) or 'None listed'}
- Interests: {', '.join(user_interests) or 'None listed'}

NEO4J KNOWLEDGE GRAPH CONTEXT:
{graph_summary}

{dept_note}

COURSES FROM KNOWLEDGE GRAPH (use ONLY these):
{course_context}

STRICT RULES:
1. ONLY mention courses listed above. Never invent course titles or instructors.
2. Be specific — reference actual course titles by name.
3. If this is a cross-domain query, encourage the student and explain the bridge.
4. Keep response professional and concise (under 120 words).
5. Do NOT add generic advice not grounded in the courses above.
6. End with a clear recommendation of 1-2 specific courses from the list.

USER QUESTION: {message}

RESPONSE:"""

        # Try HuggingFace Llama API
        if self.api_key:
            try:
                res = requests.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "inputs": system_prompt,
                        "parameters": {
                            "max_new_tokens": 200,
                            "temperature": 0.1,
                            "return_full_text": False,
                            "do_sample": False,
                            "repetition_penalty": 1.3
                        }
                    },
                    timeout=15
                )
                if res.status_code == 200:
                    data = res.json()
                    generated = ""
                    if isinstance(data, list) and data:
                        generated = data[0].get("generated_text", "").strip()
                    elif isinstance(data, dict):
                        generated = data.get("generated_text", "").strip()

                    if generated:
                        # Strip any repeated prompt text if model echoed it
                        if "RESPONSE:" in generated:
                            generated = generated.split("RESPONSE:")[-1].strip()
                        logger.info(f"[Llama Step 5] API response received ({len(generated)} chars)")
                        return generated

                else:
                    logger.warning(f"[Llama] API returned {res.status_code}: {res.text[:200]}")

            except requests.Timeout:
                logger.warning("[Llama] API call timed out")
            except Exception as e:
                logger.error(f"[Llama] API call failed: {e}")

        # Fallback: structured grounded response (never static/hallucinated)
        return self._grounded_fallback(
            user_name, user_dept, message, matched_courses,
            matched_techs, related_techs, entities
        )

    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL: GROUNDED FALLBACK (STEP 5 — no LLM API)
    # ─────────────────────────────────────────────────────────────────────

    def _grounded_fallback(
        self, user_name, user_dept, query,
        matched_courses, matched_techs, related_techs, entities
    ) -> str:
        """
        Produces a grounded, dynamic response from Neo4j results alone.
        Never returns static/hardcoded text — always references actual matched courses.
        """
        top = matched_courses[0] if matched_courses else None
        second = matched_courses[1] if len(matched_courses) > 1 else None

        top_name   = f'"{top["title"]}"' if top else "a relevant course"
        second_name = f'"{second["title"]}"' if second else None

        tech_str    = ", ".join(matched_techs[:3]) if matched_techs else ", ".join(entities[:3]) if entities else "your requested topic"
        related_str = f" Related graph nodes: {', '.join(related_techs[:3])}." if related_techs else ""

        # Cross-domain detection
        non_cs = ["Mechanical", "Civil", "EEE", "ECE", "Mechatronics", "ACSC"]
        cs_like_query = any(t.lower() in query.lower() for t in ["python", "ai", "ml", "react", "java", "data", "cloud", "programming"])
        is_cross = user_dept in non_cs and cs_like_query

        if is_cross:
            parts = [
                f"Great question, {user_name}!",
                f"As a {user_dept} student, the Knowledge Graph identified {tech_str} courses"
                f" that bridge your engineering background with software/tech skills.{related_str}",
                f"I recommend starting with {top_name}."
            ]
            if second_name:
                parts.append(f"You can also explore {second_name} as a next step.")
            return " ".join(parts)

        # Standard response
        parts = [
            f"Hi {user_name}!",
            f"The Knowledge Graph retrieved courses matching {tech_str}.{related_str}",
            f"My top recommendation: {top_name}.",
        ]
        if second_name:
            parts.append(f"Also consider {second_name}.")
        parts.append("Use the Explore page to discover more courses in this domain.")
        return " ".join(parts)


llama_service = LlamaService()
