from flask import Blueprint, request, jsonify
from services.interest_engine import interest_engine
from services.mongodb_service import mongodb_service
from services.neo4j_service import neo4j_service

interaction_bp = Blueprint("interactions", __name__)

@interaction_bp.route("", methods=["POST"])
def record_interaction():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    event_type = data.get("event_type")  # click, view, wishlist, enrollment, completion, search
    course_id = data.get("course_id")
    metadata = data.get("metadata", {})

    if not user_id or not event_type:
        return jsonify({"error": "user_id and event_type are required"}), 400

    # 1. Update Graph & Mongo logs via interest engine
    interest_engine.process_event(user_id, event_type, course_id=course_id, metadata=metadata)

    # 2. Record graph relationship
    if course_id:
        neo4j_service.record_course_interaction(user_id, course_id, event_type)

    return jsonify({"message": f"Interaction '{event_type}' recorded successfully"}), 200

@interaction_bp.route("/wishlist", methods=["POST"])
def toggle_wishlist():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    course_id = data.get("course_id")

    if not user_id or not course_id:
        return jsonify({"error": "user_id and course_id are required"}), 400

    is_added = mongodb_service.toggle_wishlist(user_id, course_id)
    if is_added:
        interest_engine.process_event(user_id, "wishlist", course_id=course_id)
        neo4j_service.record_course_interaction(user_id, course_id, "wishlist")

    return jsonify({"wishlisted": is_added, "message": "Wishlist updated"}), 200

@interaction_bp.route("/enrollment", methods=["POST"])
def enroll_course():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    course_id = data.get("course_id")

    if not user_id or not course_id:
        return jsonify({"error": "user_id and course_id are required"}), 400

    mongodb_service.enroll_course(user_id, course_id)
    interest_engine.process_event(user_id, "enrollment", course_id=course_id)
    neo4j_service.record_course_interaction(user_id, course_id, "enrollment")

    return jsonify({"enrolled": True, "message": "Successfully enrolled in course"}), 200

@interaction_bp.route("/completion", methods=["POST"])
def mark_completion():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    course_id = data.get("course_id")

    if not user_id or not course_id:
        return jsonify({"error": "user_id and course_id are required"}), 400

    mongodb_service.mark_completed(user_id, course_id)
    interest_engine.process_event(user_id, "completion", course_id=course_id)
    neo4j_service.record_course_interaction(user_id, course_id, "completion")

    return jsonify({"completed": True, "message": "Course marked as completed"}), 200
