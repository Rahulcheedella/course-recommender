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

    query_str = request.args.get(
        "q",
        ""
    ).strip()

    dept = request.args.get(
        "department"
    )

    category = request.args.get(
        "category"
    )

    difficulty = request.args.get(
        "difficulty"
    )

    min_rating = request.args.get(
        "min_rating"
    )

    user_id = request.args.get(
        "user_id"
    )

    filters = {}

    if dept:
        filters["department"] = dept

    if category:
        filters["category"] = category

    if difficulty:
        filters["difficulty"] = difficulty

    if min_rating:
        filters["min_rating"] = min_rating

    # -----------------------------------------------------
    # GRAPH-AWARE SEARCH
    # -----------------------------------------------------

    if query_str:

        graph_result = (
            neo4j_service.extract_entities_and_search_graph(
                query_str
            )
        )

        graph_ids = graph_result.get(
            "matched_course_ids",
            []
        )

        graph_scores = graph_result.get(
            "course_scores",
            {}
        )

        all_courses = (
            mongodb_service.get_all_courses()
        )

        results = []

        for course in all_courses:

            if graph_ids and course["id"] not in graph_ids:
                continue

            # Apply normal filters
            if filters.get("department"):
                if course.get("department") != filters["department"]:
                    continue

            if filters.get("category"):
                if course.get("category") != filters["category"]:
                    continue

            if filters.get("difficulty"):
                if course.get("difficulty") != filters["difficulty"]:
                    continue

            if filters.get("min_rating"):
                if course.get("rating", 0) < float(
                    filters["min_rating"]
                ):
                    continue

            course = dict(course)

            course["_search_score"] = (
                graph_scores.get(
                    course["id"],
                    0
                )
            )

            results.append(course)

        results.sort(
            key=lambda x: (
                x.get("_search_score", 0),
                x.get("rating", 0)
            ),
            reverse=True
        )

    else:

        results = (
            mongodb_service.search_courses(
                query_str,
                filters
            )
        )

    # -----------------------------------------------------
    # LOG SEARCH
    # -----------------------------------------------------

    if user_id and query_str:

        interest_engine.process_event(
            user_id,
            "search",
            metadata={
                "query": query_str
            }
        )

    return jsonify({
        "results": results,
        "count": len(results),
        "query": query_str
    }), 200
