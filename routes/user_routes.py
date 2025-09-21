from flask import Blueprint, request, jsonify
from controllers import user_controller

# Blueprint for user routes
user_bp = Blueprint("user", __name__, url_prefix="/user")

# --------------------------
# 🔐 Authentication
# --------------------------
@user_bp.route("/register", methods=["POST"])
def register_user():
    """Register a new user"""
    data = request.get_json(silent=True) or request.form.to_dict()
    return user_controller.register_user(data)


@user_bp.route("/login", methods=["POST"])
def login_user():
    """Login a user"""
    data = request.get_json(silent=True) or request.form.to_dict()
    email = data.get("email")
    password = data.get("password")
    return user_controller.login_user(email, password)


@user_bp.route("/logout", methods=["POST"])
def logout_user():
    """Logout current user"""
    return user_controller.logout_user()


# --------------------------
# 📊 Dashboard
# --------------------------
@user_bp.route("/dashboard/<int:user_id>", methods=["GET"])
def get_dashboard(user_id):
    """Get dashboard data for a user"""
    return user_controller.get_user_dashboard(user_id)


# --------------------------
# 📄 Resume Management
# --------------------------
@user_bp.route("/resumes/<int:user_id>", methods=["GET"])
def get_resumes(user_id):
    """List all resumes for a user"""
    return user_controller.get_all_resumes(user_id)


@user_bp.route("/resume/<int:resume_id>/<int:user_id>", methods=["DELETE"])
def delete_resume(resume_id, user_id):
    """Delete a specific resume for a user"""
    return user_controller.delete_resume(resume_id, user_id)


@user_bp.route("/upload/<int:user_id>", methods=["POST"])
def upload_resume(user_id):
    """Upload a new resume for a user"""
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "no file provided"}), 400
    return user_controller.upload_resume(user_id, file)


# --------------------------
# ⚙️ Profile
# --------------------------
@user_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    """Update user profile"""
    data = request.get_json(silent=True) or request.form.to_dict()
    return user_controller.update_user_profile(user_id, data)


# --------------------------
# 📊 Evaluations
# --------------------------
@user_bp.route("/evaluations/<int:user_id>", methods=["GET"])
def get_evaluations(user_id):
    """Get all evaluations for a user's resumes"""
    return user_controller.get_evaluations(user_id)
