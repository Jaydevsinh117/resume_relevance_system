import os, uuid, datetime
from flask import jsonify, current_app
from werkzeug.utils import secure_filename
from models import Resume, Evaluation
from utils.storage import load_data, save_data
from utils.resume_parser import extract_text_from_resume


# --------------------------
# upload resume
# --------------------------
async def upload_resume(user_id: int, file):
    try:
        if not file or not file.filename.strip():
            return jsonify({"status": "error", "message": "no file provided"}), 400

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            return jsonify({"status": "error", "message": "invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            return jsonify({"status": "error", "message": f"file type not allowed: {ext}"}), 400

        # save file
        newname = f"{uuid.uuid4().hex[:8]}_{filename}"
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{user_id}")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, newname)

        raw_bytes = file.read()
        with open(path, "wb") as f:
            f.write(raw_bytes)

        parsed_text = extract_text_from_resume(raw_bytes, filename)

        db = load_data()
        resume = Resume(
            id=len(db["resumes"]) + 1,
            user_id=user_id,
            original_filename=filename,
            filename=newname,
            file_path=path,
            file_type=ext,
            parsed_text=parsed_text
        )

        db["resumes"].append(resume.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": resume.to_dict()}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get single resume
# --------------------------
async def get_resume(resume_id: int, user_id: int):
    try:
        db = load_data()
        resume = next((r for r in db["resumes"] if r["id"] == resume_id and r["user_id"] == user_id), None)
        if not resume:
            return jsonify({"status": "error", "message": "resume not found"}), 404
        return jsonify({"status": "success", "data": resume}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get all resumes
# --------------------------
async def get_all_resumes(user_id: int):
    try:
        db = load_data()
        resumes = [r for r in db["resumes"] if r["user_id"] == user_id]
        return jsonify({"status": "success", "data": resumes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# delete resume
# --------------------------
async def delete_resume(resume_id: int, user_id: int):
    try:
        db = load_data()
        resume = next((r for r in db["resumes"] if r["id"] == resume_id and r["user_id"] == user_id), None)
        if not resume:
            return jsonify({"status": "error", "message": "resume not found"}), 404

        if os.path.exists(resume["file_path"]):
            os.remove(resume["file_path"])

        db["resumes"] = [r for r in db["resumes"] if not (r["id"] == resume_id and r["user_id"] == user_id)]
        save_data(db)

        return jsonify({"status": "success", "message": f"resume {resume_id} deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# update resume
# --------------------------
async def update_resume(resume_id: int, user_id: int, file):
    try:
        db = load_data()
        resume = next((r for r in db["resumes"] if r["id"] == resume_id and r["user_id"] == user_id), None)
        if not resume:
            return jsonify({"status": "error", "message": "resume not found"}), 404

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            return jsonify({"status": "error", "message": "invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            return jsonify({"status": "error", "message": f"file type not allowed: {ext}"}), 400

        newname = f"{uuid.uuid4().hex[:8]}_{filename}"
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{user_id}")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, newname)

        raw_bytes = file.read()
        with open(path, "wb") as f:
            f.write(raw_bytes)

        parsed_text = extract_text_from_resume(raw_bytes, filename)

        if os.path.exists(resume["file_path"]):
            os.remove(resume["file_path"])

        resume["filename"] = newname
        resume["file_path"] = path
        resume["file_type"] = ext
        resume["parsed_text"] = parsed_text
        resume["uploaded_at"] = datetime.datetime.utcnow().isoformat()

        for i, r in enumerate(db["resumes"]):
            if r["id"] == resume_id:
                db["resumes"][i] = resume
                break

        save_data(db)
        return jsonify({"status": "success", "data": resume}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# search resumes
# --------------------------
async def search_resumes(user_id: int, keyword: str):
    try:
        db = load_data()
        resumes = [
            {"id": r["id"], "filename": r["filename"], "match_found": keyword.lower() in (r.get("parsed_text") or "").lower()}
            for r in db["resumes"] if r["user_id"] == user_id
        ]
        return jsonify({"status": "success", "data": resumes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# link resume to evaluation
# --------------------------
async def link_resume_to_evaluation(resume_id: int, jd_id: int):
    try:
        db = load_data()
        evaluation = next((e for e in db["evaluations"] if e["resume_id"] == resume_id and e["jd_id"] == jd_id), None)
        if evaluation:
            return jsonify({"status": "error", "message": "evaluation already exists"}), 409

        new_eval = Evaluation(
            id=len(db["evaluations"]) + 1,
            resume_id=resume_id,
            jd_id=jd_id,
            score=0,
            verdict="pending",
            missing_skills="[]",
        )
        db["evaluations"].append(new_eval.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": new_eval.to_dict()}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
