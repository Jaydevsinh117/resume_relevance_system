import os, uuid, datetime
from flask import jsonify, current_app
from werkzeug.utils import secure_filename

from models import Admin, JD, User
from utils.storage import load_data, save_data
from utils.jd_parser import extract_text_from_jd


# --------------------------
# register admin
# --------------------------
def register_admin(data):
    try:
        name = data.get("name", "Unnamed Admin")
        email = data.get("email")
        password = data.get("password", "1234")

        if not email:
            return jsonify({"status": "error", "message": "email is required"}), 400

        db = load_data()
        if any(a["email"] == email for a in db["admins"]):
            return jsonify({"status": "error", "message": "admin already exists"}), 409

        new_admin = Admin(
            id=len(db["admins"]) + 1,
            name=name,
            email=email,
            password=password,
            created_at=datetime.datetime.utcnow().isoformat()
        )

        db["admins"].append(new_admin.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": new_admin.to_dict()}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# login / logout
# --------------------------
def login_admin(email, password):
    try:
        db = load_data()
        admin = next((a for a in db["admins"] if a["email"] == email and a["password"] == password), None)
        if not admin:
            return jsonify({"status": "error", "message": "invalid credentials"}), 401
        return jsonify({"status": "success", "message": "login successful", "data": admin}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def logout_admin():
    # No sessions since we are using JSON
    return jsonify({"status": "success", "message": "logout successful"}), 200


# --------------------------
# list all admins
# --------------------------
def get_all_admins():
    try:
        db = load_data()
        return jsonify({"status": "success", "data": db["admins"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get admin by id
# --------------------------
def get_admin(admin_id: int):
    try:
        db = load_data()
        admin = next((a for a in db["admins"] if a["id"] == admin_id), None)
        if not admin:
            return jsonify({"status": "error", "message": "admin not found"}), 404
        return jsonify({"status": "success", "data": admin}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# update admin
# --------------------------
def update_admin_profile(admin_id: int, data: dict):
    try:
        db = load_data()
        admin = next((a for a in db["admins"] if a["id"] == admin_id), None)
        if not admin:
            return jsonify({"status": "error", "message": "admin not found"}), 404

        admin["name"] = data.get("name", admin["name"])
        admin["email"] = data.get("email", admin["email"])
        admin["password"] = data.get("password", admin["password"])

        for i, a in enumerate(db["admins"]):
            if a["id"] == admin_id:
                db["admins"][i] = admin
                break

        save_data(db)
        return jsonify({"status": "success", "data": admin}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# delete admin
# --------------------------
def delete_admin(admin_id: int):
    try:
        db = load_data()
        before = len(db["admins"])
        db["admins"] = [a for a in db["admins"] if a["id"] != admin_id]
        after = len(db["admins"])

        save_data(db)
        if before == after:
            return jsonify({"status": "error", "message": "admin not found"}), 404

        return jsonify({"status": "success", "message": f"admin {admin_id} deleted"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# dashboard (counts JDs & Users)
# --------------------------
def get_admin_dashboard(admin_id: int):
    try:
        db = load_data()
        jd_count = sum(1 for jd in db["jds"] if jd["admin_id"] == admin_id)
        user_count = len(db["users"])

        return jsonify({
            "status": "success",
            "data": {
                "admin_id": admin_id,
                "total_jds": jd_count,
                "total_users": user_count
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# super-admin: list all users
# --------------------------
def get_all_users():
    try:
        db = load_data()
        return jsonify({"status": "success", "data": db["users"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# upload JD
# --------------------------
def upload_jd(admin_id: int, file):
    try:
        if not file:
            return jsonify({"status": "error", "message": "no file provided"}), 400

        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()

        newname = f"{uuid.uuid4().hex[:8]}_{filename}"
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], f"admin_{admin_id}")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, newname)

        raw_bytes = file.read()
        with open(path, "wb") as f:
            f.write(raw_bytes)

        parsed_text = extract_text_from_jd(raw_bytes, filename)

        db = load_data()
        jd = JD(
            id=len(db["jds"]) + 1,
            admin_id=admin_id,
            filename=newname,
            file_path=path,
            file_type=ext,
            parsed_text=parsed_text,
            title=filename,
            uploaded_at=datetime.datetime.utcnow().isoformat()
        )

        db["jds"].append(jd.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": jd.to_dict()}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
