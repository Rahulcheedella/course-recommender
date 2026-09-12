import uuid
import logging
from flask import Blueprint, request, jsonify
from services.mongodb_service import mongodb_service
from services.neo4j_service import neo4j_service

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


def _safe_user(user_doc):
    """Strip MongoDB _id and password before returning to client."""
    if not user_doc:
        return None
    safe = dict(user_doc)
    safe.pop("_id", None)
    safe.pop("password", None)
    return safe


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        department = data.get("department", "CSE")
        skills = data.get("skills", [])
        experience = data.get("experience", "Beginner")
        interests = data.get("interests", [])

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if len(password) < 4:
            return jsonify({"error": "Password must be at least 4 characters"}), 400

        existing = mongodb_service.get_user_by_email(email)
        if existing:
            return jsonify({"error": "An account with this email already exists. Please log in."}), 400

        user_id = f"u-{uuid.uuid4().hex[:8]}"
        user_doc = {
            "id": user_id,
            "name": name or email.split("@")[0].replace(".", " ").title(),
            "email": email,
            "password": password,
            "department": department,
            "skills": [s.strip() for s in skills if s.strip()],
            "experience": experience,
            "interests": [i.strip() for i in interests if i.strip()]
        }

        # Store in MongoDB
        mongodb_service.create_user(user_doc)

        # Sync User Node & Relationships in Neo4j (non-blocking — if fails, still return success)
        try:
            neo4j_service.sync_user(user_doc)
        except Exception as e:
            logger.warning(f"Neo4j sync failed for new user {user_id}: {e}")

        return jsonify({
            "message": "Registration successful",
            "user": _safe_user(user_doc)
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed. Please try again."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = mongodb_service.get_user_by_email(email)

        if not user:
            return jsonify({"error": "No account found with this email address"}), 401

        if user.get("password") != password:
            return jsonify({"error": "Incorrect password. Please try again."}), 401

        return jsonify({
            "message": "Login successful",
            "user": _safe_user(user)
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed. Please try again."}), 500
