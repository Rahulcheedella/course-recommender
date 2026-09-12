from flask import Blueprint, request, jsonify
from services.mongodb_service import mongodb_service
from services.interest_engine import interest_engine
from services.neo4j_service import neo4j_service

user_bp = Blueprint("user", __name__)

@user_bp.route("/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    user = mongodb_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_data = dict(user)
    user_data.pop("password", None)
    user_data.pop("_id", None)
    return jsonify({"user": user_data}), 200

@user_bp.route("/<user_id>/interests", methods=["GET"])
def get_user_interests(user_id):
    scores = interest_engine.get_user_interest_percentages(user_id)
    return jsonify({"interests": scores}), 200

@user_bp.route("/<user_id>/history", methods=["GET"])
def get_user_history(user_id):
    history = mongodb_service.get_user_interactions(user_id)
    return jsonify({"history": history}), 200

@user_bp.route("/<user_id>/wishlist", methods=["GET"])
def get_wishlist(user_id):
    courses = mongodb_service.get_wishlist(user_id)
    return jsonify({"wishlist": courses}), 200

@user_bp.route("/<user_id>/enrollments", methods=["GET"])
def get_enrollments(user_id):
    enrollments = mongodb_service.get_user_enrollments(user_id)
    return jsonify({"enrollments": enrollments}), 200

@user_bp.route("/learning-path/<user_id>", methods=["GET"])
def get_learning_path(user_id):
    target_role = request.args.get("role", "AI Engineer")
    user = mongodb_service.get_user_by_id(user_id)
    dept = user.get("department", "CSE") if user else "CSE"

    courses = mongodb_service.get_all_courses()

    # Pre-defined domain learning path roadmaps using actual courses
    paths = {
        "AI Engineer": [
            {"step": 1, "title": "Programming & Fundamentals", "course_id": "c-dsa-001", "name": "Python Programming Masterclass"},
            {"step": 2, "title": "Machine Learning Foundations", "course_id": "c-ai-002", "name": "Machine Learning with Python"},
            {"step": 3, "title": "Deep Learning & Neural Networks", "course_id": "c-ai-003", "name": "Deep Learning Specialization"},
            {"step": 4, "title": "Generative AI & LLMs", "course_id": "c-genai-001", "name": "Generative AI Complete Guide"},
            {"step": 5, "title": "Advanced RAG & Vector DBs", "course_id": "c-genai-002", "name": "Retrieval Augmented Generation"}
        ],
        "Full Stack Developer": [
            {"step": 1, "title": "Web Basics (HTML/CSS/JS)", "course_id": "c-fs-002", "name": "HTML CSS JavaScript Complete Course"},
            {"step": 2, "title": "Modern Frontend Framework", "course_id": "c-fs-003", "name": "React.js Complete Guide"},
            {"step": 3, "title": "Backend API Server", "course_id": "c-fs-005", "name": "Node.js Backend Development"},
            {"step": 4, "title": "Database Architecture", "course_id": "c-fs-006", "name": "MongoDB for Developers"},
            {"step": 5, "title": "Full Stack MERN Integration", "course_id": "c-fs-008", "name": "Complete MERN Stack Development"}
        ],
        "ECE Embedded Engineer": [
            {"step": 1, "title": "Digital Electronics & Logic", "course_id": "c-ece-002", "name": "Verilog HDL Practical Approach"},
            {"step": 2, "title": "Embedded C & Microcontrollers", "course_id": "c-ece-003", "name": "Mastering Microcontrollers with Embedded C"},
            {"step": 3, "title": "Digital Signal Processing", "course_id": "c-ece-004", "name": "Digital Signal Processing in Python"},
            {"step": 4, "title": "VLSI Design & ASIC", "course_id": "c-ece-001", "name": "Complete Digital VLSI Design Course"},
            {"step": 5, "title": "Connected IoT Devices", "course_id": "c-ece-005", "name": "Internet of Things with ESP32"}
        ],
        "Mechanical Design Specialist": [
            {"step": 1, "title": "Engineering Python Computations", "course_id": "c-mech-001", "name": "Python for Mechanical Engineers"},
            {"step": 2, "title": "3D Assembly & Product CAD", "course_id": "c-mech-002", "name": "SOLIDWORKS Mechanical Design"},
            {"step": 3, "title": "Finite Element Stress Simulation", "course_id": "c-mech-003", "name": "Ansys Workbench FEA"},
            {"step": 4, "title": "Computational Fluid Dynamics", "course_id": "c-mech-007", "name": "Computational Fluid Dynamics (CFD)"}
        ],
        "Civil BIM & Structural Specialist": [
            {"step": 1, "title": "2D Blueprinting & Site Drafting", "course_id": "c-civ-005", "name": "AutoCAD for Civil Engineers"},
            {"step": 2, "title": "3D Building Information Modeling", "course_id": "c-civ-001", "name": "Autodesk Revit Architecture Masterclass"},
            {"step": 3, "title": "Structural Load Analysis", "course_id": "c-civ-002", "name": "STAAD Pro V8i Structural Analysis"},
            {"step": 4, "title": "Construction Project Scheduling", "course_id": "c-civ-004", "name": "Project Management with Primavera P6"}
        ]
    }

    path_items = paths.get(target_role, paths["AI Engineer"])
    # Hydrate course objects
    for item in path_items:
        course_obj = mongodb_service.get_course_by_id(item["course_id"])
        item["course_details"] = course_obj

    return jsonify({
        "role": target_role,
        "department": dept,
        "steps": path_items
    }), 200
