import datetime
import json
from dateutil.parser import parse as date_parse
from flask import jsonify
from models.evaluator_model import Evaluation, db
from models.jd_model import JD
from models.resume_model import Resume


def _parse_date(date_val):
    """Convert string to datetime if needed."""
    if isinstance(date_val, str):
        try:
            return date_parse(date_val)
        except Exception:
            return None
    return date_val


# --------------------------
# filter evaluations by admin
# --------------------------
def filter_evaluations_by_admin(admin_id: int, start_date=None, end_date=None, min_score=None, verdict=None):
    try:
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)

        query = (
            db.session.query(Evaluation)
            .join(JD, JD.id == Evaluation.jd_id)
            .filter(JD.admin_id == admin_id)
        )

        if start_date:
            query = query.filter(Evaluation.created_at >= start_date)
        if end_date:
            query = query.filter(Evaluation.created_at <= end_date)
        if min_score:
            query = query.filter(Evaluation.score >= min_score)
        if verdict:
            query = query.filter(Evaluation.verdict.ilike(f"%{verdict}%"))

        evaluations = query.all()
        data = [
            {
                "id": ev.id,
                "resume_id": ev.resume_id,
                "jd_id": ev.jd_id,
                "score": ev.score,
                "verdict": ev.verdict,
                "created_at": ev.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for ev in evaluations
        ]

        return jsonify({"status": "success", "message": "admin evaluations fetched", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to fetch evaluations: {str(e).lower()}"}), 500


# --------------------------
# filter evaluations by user
# --------------------------
def filter_evaluations_by_user(user_id: int, start_date=None, end_date=None, min_score=None, verdict=None):
    try:
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)

        query = (
            db.session.query(Evaluation)
            .join(Resume, Resume.id == Evaluation.resume_id)
            .filter(Resume.user_id == user_id)
        )

        if start_date:
            query = query.filter(Evaluation.created_at >= start_date)
        if end_date:
            query = query.filter(Evaluation.created_at <= end_date)
        if min_score:
            query = query.filter(Evaluation.score >= min_score)
        if verdict:
            query = query.filter(Evaluation.verdict.ilike(f"%{verdict}%"))

        evaluations = query.all()
        data = [
            {
                "id": ev.id,
                "resume_id": ev.resume_id,
                "jd_id": ev.jd_id,
                "score": ev.score,
                "verdict": ev.verdict,
                "created_at": ev.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for ev in evaluations
        ]

        return jsonify({"status": "success", "message": "user evaluations fetched", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to fetch evaluations: {str(e).lower()}"}), 500


# --------------------------
# filter resumes by date
# --------------------------
def filter_resumes_by_date(user_id=None, start_date=None, end_date=None):
    try:
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)

        query = db.session.query(Resume)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        if start_date:
            query = query.filter(Resume.uploaded_at >= start_date)
        if end_date:
            query = query.filter(Resume.uploaded_at <= end_date)

        resumes = query.all()
        data = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "filename": r.filename,
                "uploaded_at": r.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for r in resumes
        ]

        return jsonify({"status": "success", "message": "resumes fetched", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to fetch resumes: {str(e).lower()}"}), 500


# --------------------------
# filter jds by date
# --------------------------
def filter_jds_by_date(admin_id=None, start_date=None, end_date=None):
    try:
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)

        query = db.session.query(JD)
        if admin_id:
            query = query.filter(JD.admin_id == admin_id)
        if start_date:
            query = query.filter(JD.uploaded_at >= start_date)
        if end_date:
            query = query.filter(JD.uploaded_at <= end_date)

        jds = query.all()
        data = [
            {
                "id": jd.id,
                "admin_id": jd.admin_id,
                "title": jd.title,
                "filename": jd.filename,
                "uploaded_at": jd.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for jd in jds
        ]

        return jsonify({"status": "success", "message": "job descriptions fetched", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to fetch job descriptions: {str(e).lower()}"}), 500
