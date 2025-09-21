import datetime
from flask import jsonify
from models.evaluator_model import Evaluation, db
from models.resume_model import Resume
from models.jd_model import JD
from sqlalchemy import func


# --------------------------
# score distribution (histogram)
# --------------------------
def score_distribution(admin_id=None, user_id=None):
    try:
        query = db.session.query(Evaluation)

        if admin_id:
            query = query.join(JD, JD.id == Evaluation.jd_id).filter(JD.admin_id == admin_id)
        if user_id:
            query = query.join(Resume, Resume.id == Evaluation.resume_id).filter(Resume.user_id == user_id)

        evaluations = query.all()
        if not evaluations:
            return jsonify({"status": "success", "message": "no evaluations found", "data": {}}), 200

        buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        for ev in evaluations:
            if ev.score <= 25:
                buckets["0-25"] += 1
            elif ev.score <= 50:
                buckets["26-50"] += 1
            elif ev.score <= 75:
                buckets["51-75"] += 1
            else:
                buckets["76-100"] += 1

        return jsonify({"status": "success", "message": "score distribution calculated", "data": buckets}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to calculate score distribution: {str(e).lower()}"}), 500


# --------------------------
# verdict breakdown (pie chart)
# --------------------------
def verdict_breakdown(admin_id=None, user_id=None):
    try:
        query = db.session.query(Evaluation)

        if admin_id:
            query = query.join(JD, JD.id == Evaluation.jd_id).filter(JD.admin_id == admin_id)
        if user_id:
            query = query.join(Resume, Resume.id == Evaluation.resume_id).filter(Resume.user_id == user_id)

        evaluations = query.all()
        if not evaluations:
            return jsonify({"status": "success", "message": "no evaluations found", "data": {}}), 200

        breakdown = {"high": 0, "medium": 0, "low": 0}
        for ev in evaluations:
            verdict = (ev.verdict or "").lower()
            if verdict in breakdown:
                breakdown[verdict] += 1
            else:
                breakdown["low"] += 1  # fallback bucket

        return jsonify({"status": "success", "message": "verdict breakdown calculated", "data": breakdown}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to calculate verdict breakdown: {str(e).lower()}"}), 500


# --------------------------
# timeline of evaluations (line chart)
# --------------------------
def evaluations_over_time(admin_id=None, user_id=None):
    try:
        query = db.session.query(Evaluation)

        if admin_id:
            query = query.join(JD, JD.id == Evaluation.jd_id).filter(JD.admin_id == admin_id)
        if user_id:
            query = query.join(Resume, Resume.id == Evaluation.resume_id).filter(Resume.user_id == user_id)

        evaluations = query.order_by(Evaluation.created_at.asc()).all()
        if not evaluations:
            return jsonify({"status": "success", "message": "no evaluations found", "data": []}), 200

        timeline = {}
        for ev in evaluations:
            date_key = ev.created_at.strftime("%Y-%m-%d")
            timeline[date_key] = timeline.get(date_key, 0) + 1

        data = [{"date": k, "count": v} for k, v in sorted(timeline.items())]

        return jsonify({"status": "success", "message": "timeline calculated", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to calculate timeline: {str(e).lower()}"}), 500


# --------------------------
# avg score per jd (bar chart for admin)
# --------------------------
def avg_score_per_jd(admin_id: int):
    try:
        results = (
            db.session.query(JD.id, JD.title, JD.filename, func.avg(Evaluation.score))
            .join(Evaluation, JD.id == Evaluation.jd_id)
            .filter(JD.admin_id == admin_id)
            .group_by(JD.id)
            .all()
        )

        if not results:
            return jsonify({"status": "success", "message": "no job descriptions found", "data": []}), 200

        jd_scores = [
            {"jd_id": r[0], "title": r[1] or r[2], "avg_score": round(r[3] or 0, 2)}
            for r in results
        ]

        return jsonify({"status": "success", "message": "avg score per JD calculated", "data": jd_scores}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to calculate avg scores: {str(e).lower()}"}), 500
