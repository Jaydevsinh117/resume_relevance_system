from flask import Blueprint, request, jsonify
import controllers.admin_controller as admin_controller

# blueprint for admin routes
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# --------------------------
# 🔐 auth routes (open access)
# --------------------------
@admin_bp.route("/register", methods=["POST"])
def register_admin():
    """Register a new admin"""
    data = request.get_json(silent=True) or request.form.to_dict()
    return admin_controller.register_admin(data)


@admin_bp.route("/login", methods=["POST"])
def login_admin():
    """Login an admin"""
    data = request.get_json(silent=True) or request.form.to_dict()
    email = data.get("email")
    password = data.get("password")
    return admin_controller.login_admin(email, password)


@admin_bp.route("/logout", methods=["POST"])
def logout_admin():
    """Logout the current admin"""
    return admin_controller.logout_admin()


# --------------------------
# 📊 dashboard
# --------------------------
@admin_bp.route("/dashboard/<int:admin_id>", methods=["GET"])
def get_dashboard(admin_id):
    """Get dashboard data for an admin"""
    return admin_controller.get_admin_dashboard(admin_id)


# --------------------------
# 📄 JD management
# --------------------------
@admin_bp.route("/jds/<int:admin_id>", methods=["GET"])
def get_all_jds(admin_id):
    """Get all job descriptions uploaded by an admin"""
    return admin_controller.get_all_jds(admin_id)


@admin_bp.route("/jd/<int:jd_id>/<int:admin_id>", methods=["DELETE"])
def delete_jd(jd_id, admin_id):
    """Delete a job description if owned by this admin"""
    return admin_controller.delete_jd(jd_id, admin_id)


@admin_bp.route("/upload/<int:admin_id>", methods=["POST"])
def upload_jd(admin_id):
    """Upload a new job description"""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "no file part in request"}), 400
    file = request.files["file"]
    return admin_controller.upload_jd(admin_id, file)


# --------------------------
# ⚙️ profile
# --------------------------
@admin_bp.route("/profile/<int:admin_id>", methods=["PUT"])
def update_profile(admin_id):
    """Update admin profile (name, email, password)"""
    data = request.get_json(silent=True) or request.form.to_dict()
    return admin_controller.update_admin_profile(admin_id, data)


# --------------------------
# 👑 super-admin utilities
# --------------------------
@admin_bp.route("/users", methods=["GET"])
def get_all_users():
    """Get list of all users (super-admin utility)"""
    return admin_controller.get_all_users()
