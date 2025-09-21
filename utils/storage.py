import json
import os
import threading

# --------------------------
# Global DB file path
# --------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DB_FILE = os.path.join(INSTANCE_DIR, "db.json")

# Thread lock (prevents race conditions if multiple requests write at once)
_lock = threading.Lock()


# --------------------------
# Ensure db.json exists
# --------------------------
def _init_db():
    """Create db.json with empty schema if it doesn't exist"""
    if not os.path.exists(DB_FILE):
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump(_empty_schema(), f, indent=2)


def _empty_schema():
    """Return the default empty schema for db.json"""
    return {
        "admins": [],
        "users": [],
        "resumes": [],
        "jds": [],
        "evaluations": [],
    }


# --------------------------
# Load full database
# --------------------------
def load_data():
    """Load the entire JSON database safely"""
    _init_db()
    with _lock:
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # fallback if file corrupted
                base = _empty_schema()
                save_data(base)
                return base


# --------------------------
# Save full database
# --------------------------
def save_data(data: dict):
    """Save the entire JSON database safely"""
    _init_db()
    with _lock:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)


# --------------------------
# Entity Helpers
# --------------------------
def get_admins():
    return load_data().get("admins", [])


def get_users():
    return load_data().get("users", [])


def get_resumes():
    return load_data().get("resumes", [])


def get_jds():
    return load_data().get("jds", [])


def get_evaluations():
    return load_data().get("evaluations", [])


# --------------------------
# Append Helper
# --------------------------
def append_to(entity: str, record: dict):
    """
    Append a new record to an entity list (admins, users, resumes, jds, evaluations).
    Automatically saves to db.json.
    """
    data = load_data()
    if entity not in data:
        raise ValueError(f"Unknown entity: {entity}")
    data[entity].append(record)
    save_data(data)
    return record


# --------------------------
# Reset database (utility)
# --------------------------
def reset_db():
    """Reset the database to an empty state (useful for testing)"""
    base = _empty_schema()
    save_data(base)
    return base
