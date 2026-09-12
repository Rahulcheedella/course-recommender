from flask import Blueprint, jsonify
from services.neo4j_service import neo4j_service

graph_bp = Blueprint("graph", __name__)

@graph_bp.route("/<user_id>", methods=["GET"])
def get_user_knowledge_graph(user_id):
    graph_data = neo4j_service.get_visual_graph(user_id)
    return jsonify(graph_data), 200
