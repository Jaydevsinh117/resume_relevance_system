from flask import Blueprint, request, jsonify
from controllers.jd_controller import (
    upload_jd,
    get_jd,
    get_all_jds,
    delete_jd,
    update_jd,
    search_jds,
    link_jd_to_evaluation,
)

# blueprint for jd routes (scoped under /admin)
jd_bp = Blueprint("jd", __name__, url_prefix="/admin")

# --------------------------
# upload jd
# --------------------------
@jd_bp.route("/<int:admin_id>/jd/upload", methods=["POST"])
def route_upload_jd(admin_id):
    """upload a new job description"""
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "no file provided"}), 400
    return upload_jd(admin_id, file)


# --------------------------
# get single jd
# --------------------------
@jd_bp.route("/<int:admin_id>/jd/<int:jd_id>", methods=["GET"])
def route_get_jd(admin_id, jd_id):
    """get details of a specific job description"""
    return get_jd(jd_id, admin_id)


# --------------------------
# get all jds
# --------------------------
@jd_bp.route("/<int:admin_id>/jds", methods=["GET"])
def route_get_all_jds(admin_id):
    """get all job descriptions for an admin"""
    return get_all_jds(admin_id)


# --------------------------
# delete jd
# --------------------------
@jd_bp.route("/<int:admin_id>/jd/<int:jd_id>", methods=["DELETE"])
def route_delete_jd(admin_id, jd_id):
    """delete a job description if owned by this admin"""
    return delete_jd(jd_id, admin_id)


# --------------------------
# update jd (replace file)
# --------------------------
@jd_bp.route("/<int:admin_id>/jd/<int:jd_id>", methods=["PUT"])
def route_update_jd(admin_id, jd_id):
    """update an existing job description"""
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "no file provided"}), 400
    return update_jd(jd_id, admin_id, file)


# --------------------------
# search jds
# --------------------------
@jd_bp.route("/<int:admin_id>/jds/search", methods=["GET"])
def route_search_jds(admin_id):
    """search job descriptions by keyword"""
    keyword = request.args.get("keyword", "")
    return search_jds(admin_id, keyword)


# --------------------------
# link jd to evaluation
# --------------------------
@jd_bp.route("/jd/<int:jd_id>/link/<int:resume_id>", methods=["POST"])
def route_link_jd_to_eval(jd_id, resume_id):
    """link a job description to a resume (trigger evaluation)"""
    return link_jd_to_evaluation(jd_id, resume_id)
