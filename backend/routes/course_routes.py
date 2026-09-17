from flask import Blueprint, request, jsonify
from services.mongodb_service import mongodb_service
from services.interest_engine import interest_engine
from services.neo4j_service import neo4j_service

course_bp = Blueprint("courses", __name__)

@course_bp.route("", methods=["GET"])
def get_courses():
    courses = mongodb_service.get_all_courses()
    return jsonify({"courses": courses, "count": len(courses)}), 200

@course_bp.route("/<course_id>", methods=["GET"])
def get_course_details(course_id):
    course = mongodb_service.get_course_by_id(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    user_id = request.args.get("user_id")
    if user_id:
        # Log view interaction & increment graph interest weight
        interest_engine.process_event(user_id, "course_view", course_id=course_id)

    # Fetch related courses
    related_ids = course.get("related_ids", [])
    related_courses = mongodb_service.get_courses_by_ids(related_ids)

    return jsonify({"course": course, "related_courses": related_courses}), 200

@course_bp.route("/search", methods=["GET"])
def search_courses():

    query_str = request.args.get("q", "").strip()
    dept      = request.args.get("department")
    category  = request.args.get("category")
    difficulty = request.args.get("difficulty")
    min_rating = request.args.get("min_rating")
    user_id    = request.args.get("user_id")

    # Explicit sidebar filters (applied in addition to the text query)
    filters = {}
    if dept:
        filters["department"] = dept
    if category:
        filters["category"] = category
    if difficulty:
        filters["difficulty"] = difficulty
    if min_rating:
        filters["min_rating"] = min_rating

    no_results_message = None

    # ---------------------------------------------------------
    # SEARCH: MongoDB keyword match + Neo4j graph score boost
    #
    # MongoDB direct search is ALWAYS the primary source of results.
    # Neo4j graph scores are added on top to boost ranking of
    # graph-connected courses — they never restrict/exclude results.
    # ---------------------------------------------------------

    if query_str:

        # ── Step A: MongoDB keyword search (primary, always runs) ──────────
        # Returns all courses whose title/technologies/skills/tags/
        # category/description contain the query keywords.
        # This is the base result set — never gated by Neo4j.
        mongo_results = mongodb_service.search_courses(query_str, filters)

        # Build a fast lookup: course_id → mongo_score
        mongo_scores: dict = {
            c["id"]: c.get("_search_score", 0)
            for c in mongo_results
        }

        # ── Step B: Neo4j graph scores (optional boost) ────────────────────
        # If Neo4j is available, fetch graph scores for additional ranking.
        # These scores are ADDED to MongoDB scores, never used as a filter.
        neo4j_scores: dict = {}

        try:
            title_result  = neo4j_service.search_by_title(query_str)
            graph_result  = neo4j_service.extract_entities_and_search_graph(query_str)

            for cid, sc in title_result.get("course_scores", {}).items():
                neo4j_scores[cid] = neo4j_scores.get(cid, 0) + sc
            for cid, sc in graph_result.get("course_scores", {}).items():
                neo4j_scores[cid] = neo4j_scores.get(cid, 0) + sc
        except Exception:
            pass   # Neo4j offline — continue with MongoDB results only

        # ── Step C: Combine scores and build final result list ─────────────
        # Start from MongoDB results (guaranteed keyword-relevant).
        # Add Neo4j bonus scores on top for better ranking.
        results = []
        for course in mongo_results:
            cid = course["id"]
            combined_score = mongo_scores.get(cid, 0) + neo4j_scores.get(cid, 0)
            course = dict(course)
            course["_search_score"] = combined_score
            results.append(course)

        # Also include Neo4j-only matches (graph-related courses not yet
        # in the MongoDB keyword results) — fetch from MongoDB by ID.
        mongo_ids = set(mongo_scores.keys())
        extra_ids = [cid for cid in neo4j_scores if cid not in mongo_ids]
        if extra_ids:
            extra_courses = mongodb_service.get_courses_by_ids(extra_ids)
            for course in extra_courses:
                # Apply sidebar filters
                if filters.get("department") and course.get("department") != filters["department"]:
                    continue
                if filters.get("category") and course.get("category") != filters["category"]:
                    continue
                if filters.get("difficulty") and course.get("difficulty") != filters["difficulty"]:
                    continue
                if filters.get("min_rating") and course.get("rating", 0) < float(filters["min_rating"]):
                    continue
                course = dict(course)
                course["_search_score"] = neo4j_scores.get(course["id"], 0)
                results.append(course)

        # Sort: combined score desc, then rating as tiebreaker
        results.sort(
            key=lambda x: (x.get("_search_score", 0), x.get("rating", 0)),
            reverse=True
        )

        if not results:
            no_results_message = (
                "No courses directly match your search. "
                "Try different keywords or browse all courses."
            )

    else:
        results = mongodb_service.search_courses(query_str, filters)

    # -----------------------------------------------------
    # LOG SEARCH
    # -----------------------------------------------------

    if user_id and query_str:
        interest_engine.process_event(
            user_id,
            "search",
            metadata={"query": query_str}
        )

    response = {
        "results": results,
        "count": len(results),
        "query": query_str
    }
    if no_results_message:
        response["no_results_message"] = no_results_message

    return jsonify(response), 200
