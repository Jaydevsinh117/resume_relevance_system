import os

# Base project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Instance folder (for local-only files like uploads)
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# --------------------------
# CONFIG CLASSES
# --------------------------
class Config:
    # Secret key for sessions
    SECRET_KEY = os.environ.get("FLASK_SECRET") or os.urandom(24).hex()

    # File upload settings
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Templates & static
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    # Logging
    LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
