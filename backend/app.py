import logging
import os
import sys

# Make project root importable.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend connection
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Import Routes
from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.recommendation_routes import rec_bp
from routes.interaction_routes import interaction_bp
from routes.chat_routes import chat_bp
from routes.user_routes import user_bp
from routes.graph_routes import graph_bp

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(course_bp, url_prefix="/api/courses")
app.register_blueprint(rec_bp, url_prefix="/api/recommendations")
app.register_blueprint(interaction_bp, url_prefix="/api/interactions")
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(graph_bp, url_prefix="/api/knowledge-graph")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "system": "AI Knowledge Graph Course Recommendation API",
        "version": "1.0.0"
    }), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info(f"Starting Flask API Server on port {Config.PORT}...")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)