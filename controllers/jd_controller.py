import os, uuid, datetime
from flask import jsonify, current_app
from werkzeug.utils import secure_filename
from models import JD
from utils.jd_parser import extract_text_from_jd
from utils.storage import load_data, save_data


# --------------------------
# upload jd
# --------------------------
async def upload_jd(admin_id: int, file):
    try:
        if not file:
            return jsonify({"status": "error", "message": "no file provided"}), 400

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            return jsonify({"status": "error", "message": "invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            return jsonify({"status": "error", "message": f"file type not allowed: {ext}"}), 400

        # save file
        newname = f"{uuid.uuid4().hex[:8]}_{filename}"
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], f"admin_{admin_id}")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, newname)

        raw_bytes = file.read()
        with open(path, "wb") as f:
            f.write(raw_bytes)

        parsed_text = extract_text_from_jd(raw_bytes, filename)

        # save in JSON
        db = load_data()
        jd = JD(
            id=len(db["jds"]) + 1,
            admin_id=admin_id,
            filename=newname,
            file_path=path,
            file_type=ext,
            parsed_text=parsed_text,
            title=filename,
        )
        db["jds"].append(jd.to_dict())
        save_data(db)

        return jsonify({"status": "success", "data": jd.to_dict()}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get single jd
# --------------------------
async def get_jd(jd_id: int, admin_id: int):
    try:
        db = load_data()
        jd = next((j for j in db["jds"] if j["id"] == jd_id and j["admin_id"] == admin_id), None)
        if not jd:
            return jsonify({"status": "error", "message": "jd not found"}), 404

        jd["parsed_preview"] = jd.get("parsed_text", "")[:300] + "..."
        return jsonify({"status": "success", "data": jd}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# get all jds for admin
# --------------------------
async def get_all_jds(admin_id: int):
    try:
        db = load_data()
        jds = [j for j in db["jds"] if j["admin_id"] == admin_id]
        return jsonify({"status": "success", "data": jds}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# delete jd
# --------------------------
async def delete_jd(jd_id: int, admin_id: int):
    try:
        db = load_data()
        jd = next((j for j in db["jds"] if j["id"] == jd_id and j["admin_id"] == admin_id), None)
        if not jd:
            return jsonify({"status": "error", "message": "jd not found"}), 404

        # delete file too
        if os.path.exists(jd["file_path"]):
            os.remove(jd["file_path"])

        db["jds"] = [j for j in db["jds"] if not (j["id"] == jd_id and j["admin_id"] == admin_id)]
        save_data(db)

        return jsonify({"status": "success", "message": f"jd {jd_id} deleted"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# update jd (replace file)
# --------------------------
async def update_jd(jd_id: int, admin_id: int, file):
    try:
        db = load_data()
        jd = next((j for j in db["jds"] if j["id"] == jd_id and j["admin_id"] == admin_id), None)
        if not jd:
            return jsonify({"status": "error", "message": "jd not found"}), 404

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            return jsonify({"status": "error", "message": "invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            return jsonify({"status": "error", "message": f"file type not allowed: {ext}"}), 400

        raw_bytes = file.read()
        with open(jd["file_path"], "wb") as f:
            f.write(raw_bytes)

        jd["parsed_text"] = extract_text_from_jd(raw_bytes, filename)
        jd["title"] = filename
        jd["uploaded_at"] = datetime.datetime.utcnow().isoformat()

        for i, j in enumerate(db["jds"]):
            if j["id"] == jd_id:
                db["jds"][i] = jd
                break

        save_data(db)
        return jsonify({"status": "success", "data": jd}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# search jds by keyword
# --------------------------
async def search_jds(admin_id: int, keyword: str):
    try:
        db = load_data()
        jds = [
            j for j in db["jds"]
            if j["admin_id"] == admin_id and keyword.lower() in (j.get("parsed_text") or "").lower()
        ]
        return jsonify({"status": "success", "data": jds}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------
# link jd to evaluation (stub)
# --------------------------
async def link_jd_to_evaluation(jd_id: int, resume_id: int):
    try:
        return jsonify({
            "status": "success",
            "message": "jd linked to evaluation (stub)",
            "data": {"jd_id": jd_id, "resume_id": resume_id}
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
