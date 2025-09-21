from flask import Blueprint, request
from controllers.evaluator_controller import (
    evaluate_resume_against_jd,
    get_evaluation,
    get_all_evaluations,
    get_evaluations_by_user,
    get_evaluations_by_admin,
    update_evaluation,
    delete_evaluation,
    compare_multiple_resumes_to_jd,
    compare_multiple_jds_to_resume,
)

evaluator_bp = Blueprint("evaluator", __name__, url_prefix="/evaluations")

# --------------------------
# evaluate resume against jd
# --------------------------
@evaluator_bp.route("/<int:resume_id>/<int:jd_id>", methods=["POST"])
def route_evaluate_resume_against_jd(resume_id, jd_id):
    return evaluate_resume_against_jd(resume_id, jd_id)


# --------------------------
# get evaluation by id
# --------------------------
@evaluator_bp.route("/<int:evaluation_id>", methods=["GET"])
def route_get_evaluation(evaluation_id):
    return get_evaluation(evaluation_id)


# --------------------------
# get all evaluations
# --------------------------
@evaluator_bp.route("/", methods=["GET"])
def route_get_all_evaluations():
    return get_all_evaluations()


# --------------------------
# get evaluations by user
# --------------------------
@evaluator_bp.route("/user/<int:user_id>", methods=["GET"])
def route_get_evaluations_by_user(user_id):
    return get_evaluations_by_user(user_id)


# --------------------------
# get evaluations by admin
# --------------------------
@evaluator_bp.route("/admin/<int:admin_id>", methods=["GET"])
def route_get_evaluations_by_admin(admin_id):
    return get_evaluations_by_admin(admin_id)


# --------------------------
# update evaluation
# --------------------------
@evaluator_bp.route("/<int:evaluation_id>", methods=["PUT"])
def route_update_evaluation(evaluation_id):
    data = request.get_json(silent=True)
    if not data:
        return {"status": "error", "message": "invalid or missing json body"}, 400
    return update_evaluation(evaluation_id, data)


# --------------------------
# delete evaluation
# --------------------------
@evaluator_bp.route("/<int:evaluation_id>", methods=["DELETE"])
def route_delete_evaluation(evaluation_id):
    return delete_evaluation(evaluation_id)


# --------------------------
# compare multiple resumes to jd
# --------------------------
@evaluator_bp.route("/compare/user/<int:user_id>/jd/<int:jd_id>", methods=["POST"])
def route_compare_multiple_resumes_to_jd(user_id, jd_id):
    return compare_multiple_resumes_to_jd(user_id, jd_id)


# --------------------------
# compare multiple jds to resume
# --------------------------
@evaluator_bp.route("/compare/resume/<int:resume_id>/admin/<int:admin_id>", methods=["POST"])
def route_compare_multiple_jds_to_resume(resume_id, admin_id):
    return compare_multiple_jds_to_resume(resume_id, admin_id)



@evaluator_bp.route("/admin_jds/<int:admin_id>", methods=["GET"])
def route_get_evaluations_by_admin_jds(admin_id):
    return get_evaluations_by_admin_jds(admin_id)


