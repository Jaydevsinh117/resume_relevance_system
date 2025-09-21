import os
import uuid
from flask import jsonify, current_app
from werkzeug.utils import secure_filename

from models import User, Resume
from utils.storage import load_data, save_data
from utils.resume_parser import extract_text_from_resume


# --------------------------
# register (create) user
# --------------------------
def register_user(data):
    try:
        name = data.get("name", "Unnamed User")
        email = data.get("email", f"user{uuid.uuid4().hex[:5]}@example.com")
        password = data.get("password", "1234")

        db = load_data()

        # check duplicate email
        if any(u["email"] == email for u in db["users"]):
            return jsonify({"status": "error", "message": "email already exists"}), 409

        new_user = User(
            id=len(db["users"]) + 1,
            name=name,
            email=email,
            password=password,
        )

        db["users"].append(new_user.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": new_user.to_dict()}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# login user
# --------------------------
def login_user(email, password):
    try:
        db = load_data()
        user = next(
            (u for u in db["users"] if u["email"] == email and u["password"] == password),
            None,
        )
        if not user:
            return jsonify({"status": "error", "message": "invalid credentials"}), 401

        return jsonify({"status": "success", "data": user}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def logout_user():
    return jsonify({"status": "success", "message": "user logged out"}), 200


# --------------------------
# dashboard
# --------------------------
def get_user_dashboard(user_id: int):
    try:
        db = load_data()
        resumes = [r for r in db["resumes"] if r["user_id"] == user_id]
        evaluations = [ev for ev in db["evaluations"] if ev.get("user_id") == user_id]

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "resume_count": len(resumes),
                        "evaluation_count": len(evaluations),
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# upload resume
# --------------------------
def upload_resume(user_id: int, file):
    try:
        if not file:
            return jsonify({"status": "error", "message": "no file provided"}), 400

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            return jsonify({"status": "error", "message": "invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            return (
                jsonify({"status": "error", "message": f"file type not allowed: {ext}"}),
                400,
            )

        # store file
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
            parsed_text=parsed_text,
        )

        db["resumes"].append(resume.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": resume.to_dict()}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get resumes
# --------------------------
def get_all_resumes(user_id: int):
    try:
        db = load_data()
        resumes = [r for r in db["resumes"] if r["user_id"] == user_id]
        return jsonify({"status": "success", "data": resumes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def delete_resume(resume_id: int, user_id: int):
    try:
        db = load_data()
        before = len(db["resumes"])
        db["resumes"] = [
            r
            for r in db["resumes"]
            if not (r["id"] == resume_id and r["user_id"] == user_id)
        ]
        after = len(db["resumes"])
        save_data(db)

        if before == after:
            return jsonify({"status": "error", "message": "resume not found"}), 404

        return jsonify({"status": "success", "message": f"resume {resume_id} deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# update user profile
# --------------------------
def update_user_profile(user_id: int, data: dict):
    try:
        db = load_data()
        user = next((u for u in db["users"] if u["id"] == user_id), None)
        if not user:
            return jsonify({"status": "error", "message": "user not found"}), 404

        user["name"] = data.get("name", user["name"])
        user["email"] = data.get("email", user["email"])
        user["password"] = data.get("password", user["password"])

        for i, u in enumerate(db["users"]):
            if u["id"] == user_id:
                db["users"][i] = user
                break

        save_data(db)
        return jsonify({"status": "success", "data": user}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# evaluations
# --------------------------
def get_evaluations(user_id: int):
    try:
        db = load_data()
        evaluations = [ev for ev in db["evaluations"] if ev.get("user_id") == user_id]
        return jsonify({"status": "success", "data": evaluations}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
