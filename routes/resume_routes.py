from flask import Blueprint, request, jsonify
from controllers import resume_controller

# blueprint for resume routes
resume_bp = Blueprint("resume", __name__, url_prefix="/resume")


# --------------------------
# upload resume
# --------------------------
@resume_bp.route("/upload/<int:user_id>", methods=["POST"])
def route_upload_resume(user_id):
    """upload a resume for a user"""
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "no file provided"}), 400
    return resume_controller.upload_resume(user_id, file)


# --------------------------
# get single resume
# --------------------------
@resume_bp.route("/<int:resume_id>/<int:user_id>", methods=["GET"])
def route_get_resume(resume_id, user_id):
    """get a specific resume for a user"""
    return resume_controller.get_resume(resume_id, user_id)


# --------------------------
# get all resumes for user
# --------------------------
@resume_bp.route("/all/<int:user_id>", methods=["GET"])
def route_get_all_resumes(user_id):
    """get all resumes uploaded by a user"""
    return resume_controller.get_all_resumes(user_id)


# --------------------------
# delete resume
# --------------------------
@resume_bp.route("/delete/<int:resume_id>/<int:user_id>", methods=["DELETE"])
def route_delete_resume(resume_id, user_id):
    """delete a resume owned by a user"""
    return resume_controller.delete_resume(resume_id, user_id)


# --------------------------
# update resume
# --------------------------
@resume_bp.route("/update/<int:resume_id>/<int:user_id>", methods=["PUT"])
def route_update_resume(resume_id, user_id):
    """update (replace) an existing resume"""
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "no file provided"}), 400
    return resume_controller.update_resume(resume_id, user_id, file)


# --------------------------
# search resumes
# --------------------------
@resume_bp.route("/search/<int:user_id>", methods=["GET"])
def route_search_resumes(user_id):
    """search resumes for a user by keyword"""
    keyword = request.args.get("keyword")
    return resume_controller.search_resumes(user_id, keyword)


# --------------------------
# link resume to evaluation
# --------------------------
@resume_bp.route("/link/<int:resume_id>/<int:jd_id>", methods=["POST"])
def route_link_resume_to_evaluation(resume_id, jd_id):
    """link a resume to a job description (trigger evaluation)"""
    return resume_controller.link_resume_to_evaluation(resume_id, jd_id)
