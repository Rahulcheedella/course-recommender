from flask import Blueprint, jsonify, request

from services.recommendation_engine import recommendation_engine
from services.mongodb_service import mongodb_service


rec_bp = Blueprint(
    "recommendations",
    __name__
)


# ---------------------------------------------------------
# PERSONALIZED RECOMMENDATIONS
# ---------------------------------------------------------

@rec_bp.route("/<user_id>", methods=["GET"])
def get_user_recommendations(user_id):

    recs = recommendation_engine.get_user_recommendations(
        user_id
    )

    return jsonify(recs), 200


# ---------------------------------------------------------
# QUERY-AWARE HOMEPAGE RECOMMENDATIONS
# ---------------------------------------------------------

@rec_bp.route("/contextual", methods=["GET"])
def get_contextual_recommendations():

    query = request.args.get(
        "q",
        ""
    ).strip()

    user_id = request.args.get(
        "user_id"
    )

    if not query:

        return jsonify({
            "query": "",
            "message": "No active search query.",
            "matched_courses": []
        }), 200

    result = (
        recommendation_engine.get_query_recommendations(
            user_id,
            query,
            limit=8
        )
    )

    # Human-readable homepage message
    technologies = result.get(
        "technologies",
        []
    )

    departments = result.get(
        "departments",
        []
    )

    if technologies:

        primary = ", ".join(
            technologies[:2]
        )

        message = (
            f"You're looking for {primary} courses. "
            f"Here are the best matches we found for you."
        )

    else:

        message = (
            "Here are the courses that best match "
            "your search and learning profile."
        )

    if departments:

        message += (
            f" We have also considered your "
            f"{departments[0]} background."
        )

    result["message"] = message

    return jsonify(result), 200


# ---------------------------------------------------------
# TRENDING
# ---------------------------------------------------------

@rec_bp.route("/trending", methods=["GET"])
def get_trending():

    courses = mongodb_service.get_all_courses()

    trending = sorted(
        courses,
        key=lambda x: (
            x.get("rating", 0),
            x.get("students", 0)
        ),
        reverse=True
    )[:8]

    for course in trending:

        course["recommendation_reason"] = (
            "Trending across the platform"
        )

    return jsonify({
        "trending_courses": trending
    }), 200


# ---------------------------------------------------------
# DEPARTMENT
# ---------------------------------------------------------

@rec_bp.route(
    "/department/<department>",
    methods=["GET"]
)
def get_department_recommendations(
    department
):

    courses = mongodb_service.get_all_courses()

    dept_courses = [
        c
        for c in courses
        if c.get("department") == department
    ]

    dept_courses.sort(
        key=lambda x: (
            x.get("rating", 0),
            x.get("students", 0)
        ),
        reverse=True
    )

    for course in dept_courses:

        course["recommendation_reason"] = (
            f"Relevant to {department} engineering"
        )

    return jsonify({
        "courses": dept_courses
    }), 200
