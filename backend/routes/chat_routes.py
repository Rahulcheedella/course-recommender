from flask import Blueprint, request, jsonify
from services.llama_service import llama_service
from services.interest_engine import interest_engine

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message content is required"}), 400

    # 1. Log chat event to update graph interest weights
    if user_id:
        interest_engine.process_event(user_id, "chatbot_query", metadata={"query": message})

    # 2. Process query via Grounded Llama AI Assistant (GraphRAG pipeline)
    response_payload = llama_service.process_chat_query(user_id, message)

    return jsonify({
        "reply": response_payload["message"],
        "recommended_courses": response_payload["recommended_courses"],
        # GraphRAG transparency fields — shown in chatbot UI as entity tags
        "entities": response_payload.get("entities", []),
        "matched_techs": response_payload.get("matched_techs", []),
        "graph_hops": response_payload.get("graph_hops", [])
    }), 200
