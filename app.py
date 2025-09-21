"""
Main entry point for Resume Relevance System
- JSON-based storage instead of SQLAlchemy
- Loads config from config.py (DevelopmentConfig / ProductionConfig)
- Registers all route blueprints
- Handles global errors gracefully
"""

import os
from flask import Flask, jsonify

# --------------------------
# INIT APP
# --------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# --------------------------
# LOAD CONFIG
# --------------------------
env = os.environ.get("FLASK_ENV", "development").lower()
if env == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# --------------------------
# REGISTER ROUTES (BLUEPRINTS)
# --------------------------
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from routes.resume_routes import resume_bp
from routes.jd_routes import jd_bp
from routes.evaluator_routes import evaluator_bp

# Core routes
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")

# Optional routes (uncomment when implemented)
app.register_blueprint(resume_bp, url_prefix="/resume")
app.register_blueprint(jd_bp, url_prefix="/jd")
app.register_blueprint(evaluator_bp, url_prefix="/evaluation")

# Optional analytics routes
try:
    from routes.analytics_routes import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
except ImportError:
    pass  # skip if analytics not implemented yet

# --------------------------
# ROOT ROUTE
# --------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "success",
        "message": "🚀 Resume Relevance System (JSON storage) is running",
        "available_routes": [
            "/admin/*",
            "/user/*",
            "/resume/*",
            "/jd/*",
            "/evaluation/*",
            "/analytics/* (optional)"
        ]
    }), 200

# --------------------------
# GLOBAL ERROR HANDLERS
# --------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "internal server error"}), 500

# --------------------------
# RUN SERVER
# --------------------------
if __name__ == "__main__":
    # Always run with debug only in development
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", True)
    )
