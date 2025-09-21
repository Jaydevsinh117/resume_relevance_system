import datetime, json
from flask import jsonify
from models import Evaluation, Resume, JD
from utils.evaluator import evaluate_texts
from utils.storage import load_data, save_data


# --------------------------
# 1. evaluate resume against jd
# --------------------------
async def evaluate_resume_against_jd(resume_id: int, jd_id: int):
    try:
        db = load_data()
        resume = next((r for r in db["resumes"] if r["id"] == resume_id), None)
        jd = next((j for j in db["jds"] if j["id"] == jd_id), None)

        if not resume:
            return jsonify({"status": "error", "message": "resume not found"}), 404
        if not jd:
            return jsonify({"status": "error", "message": "job description not found"}), 404

        # prevent duplicate
        existing = next((e for e in db["evaluations"] if e["resume_id"] == resume_id and e["jd_id"] == jd_id), None)
        if existing:
            return jsonify({"status": "error", "message": "evaluation already exists"}), 409

        score, verdict, missing = evaluate_texts(resume.get("parsed_text", ""), jd.get("parsed_text", ""))

        evaluation = Evaluation(
            id=len(db["evaluations"]) + 1,
            resume_id=resume_id,
            jd_id=jd_id,
            score=score,
            verdict=verdict,
            missing_skills=json.dumps(missing),
            created_at=datetime.datetime.utcnow().isoformat(),
        )

        db["evaluations"].append(evaluation.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": evaluation.to_dict()}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 2. get evaluation by id
# --------------------------
async def get_evaluation(evaluation_id: int):
    try:
        db = load_data()
        ev = next((e for e in db["evaluations"] if e["id"] == evaluation_id), None)
        if not ev:
            return jsonify({"status": "error", "message": "evaluation not found"}), 404
        ev["missing_skills"] = json.loads(ev.get("missing_skills", "[]"))
        return jsonify({"status": "success", "data": ev}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 3. get all evaluations
# --------------------------
async def get_all_evaluations():
    try:
        db = load_data()
        data = db["evaluations"]
        for ev in data:
            ev["missing_skills"] = json.loads(ev.get("missing_skills", "[]"))
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 4. get evaluations by user
# --------------------------
async def get_evaluations_by_user(user_id: int):
    try:
        db = load_data()
        resumes = [r["id"] for r in db["resumes"] if r["user_id"] == user_id]
        evals = [e for e in db["evaluations"] if e["resume_id"] in resumes]
        if not evals:
            return jsonify({"status": "error", "message": "no evaluations for this user"}), 404
        for ev in evals:
            ev["missing_skills"] = json.loads(ev.get("missing_skills", "[]"))
        return jsonify({"status": "success", "data": evals}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 5. get evaluations by admin
# --------------------------
async def get_evaluations_by_admin(admin_id: int):
    try:
        db = load_data()
        jds = [j["id"] for j in db["jds"] if j["admin_id"] == admin_id]
        evals = [e for e in db["evaluations"] if e["jd_id"] in jds]
        if not evals:
            return jsonify({"status": "error", "message": "no evaluations for this admin"}), 404
        for ev in evals:
            ev["missing_skills"] = json.loads(ev.get("missing_skills", "[]"))
        return jsonify({"status": "success", "data": evals}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 6. update evaluation
# --------------------------
async def update_evaluation(evaluation_id: int, data: dict):
    try:
        db = load_data()
        ev = next((e for e in db["evaluations"] if e["id"] == evaluation_id), None)
        if not ev:
            return jsonify({"status": "error", "message": "evaluation not found"}), 404

        if "score" in data: ev["score"] = int(data["score"])
        if "verdict" in data: ev["verdict"] = data["verdict"]
        if "missing_skills" in data: ev["missing_skills"] = json.dumps(data["missing_skills"])

        for i, e in enumerate(db["evaluations"]):
            if e["id"] == evaluation_id:
                db["evaluations"][i] = ev
                break

        save_data(db)
        ev["missing_skills"] = json.loads(ev.get("missing_skills", "[]"))
        return jsonify({"status": "success", "data": ev}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 7. delete evaluation
# --------------------------
async def delete_evaluation(evaluation_id: int):
    try:
        db = load_data()
        before = len(db["evaluations"])
        db["evaluations"] = [e for e in db["evaluations"] if e["id"] != evaluation_id]
        save_data(db)
        if len(db["evaluations"]) == before:
            return jsonify({"status": "error", "message": "evaluation not found"}), 404
        return jsonify({"status": "success", "message": f"evaluation {evaluation_id} deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 8. compare multiple resumes to jd
# --------------------------
async def compare_multiple_resumes_to_jd(user_id: int, jd_id: int):
    try:
        db = load_data()
        resumes = [r for r in db["resumes"] if r["user_id"] == user_id]
        jd = next((j for j in db["jds"] if j["id"] == jd_id), None)
        if not resumes:
            return jsonify({"status": "error", "message": "no resumes found"}), 404
        if not jd:
            return jsonify({"status": "error", "message": "job description not found"}), 404

        results = []
        for r in resumes:
            score, verdict, missing = evaluate_texts(r.get("parsed_text", ""), jd.get("parsed_text", ""))
            exists = next((e for e in db["evaluations"] if e["resume_id"] == r["id"] and e["jd_id"] == jd_id), None)
            if exists:
                continue
            evaluation = Evaluation(
                id=len(db["evaluations"]) + 1,
                resume_id=r["id"],
                jd_id=jd_id,
                score=score,
                verdict=verdict,
                missing_skills=json.dumps(missing),
                created_at=datetime.datetime.utcnow().isoformat(),
            )
            db["evaluations"].append(evaluation.to_dict())
            results.append(evaluation.to_dict())

        save_data(db)
        return jsonify({"status": "success", "data": results}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# 9. compare multiple jds to resume
# --------------------------
async def compare_multiple_jds_to_resume(resume_id: int, admin_id: int):
    try:
        db = load_data()
        resume = next((r for r in db["resumes"] if r["id"] == resume_id), None)
        jds = [j for j in db["jds"] if j["admin_id"] == admin_id]

        if not resume:
            return jsonify({"status": "error", "message": "resume not found"}), 404
        if not jds:
            return jsonify({"status": "error", "message": "no job descriptions found"}), 404

        results = []
        for jd in jds:
            score, verdict, missing = evaluate_texts(resume.get("parsed_text", ""), jd.get("parsed_text", ""))
            exists = next((e for e in db["evaluations"] if e["resume_id"] == resume_id and e["jd_id"] == jd["id"]), None)
            if exists:
                continue
            evaluation = Evaluation(
                id=len(db["evaluations"]) + 1,
                resume_id=resume_id,
                jd_id=jd["id"],
                score=score,
                verdict=verdict,
                missing_skills=json.dumps(missing),
                created_at=datetime.datetime.utcnow().isoformat(),
            )
            db["evaluations"].append(evaluation.to_dict())
            results.append(evaluation.to_dict())

        save_data(db)
        return jsonify({"status": "success", "data": results}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
