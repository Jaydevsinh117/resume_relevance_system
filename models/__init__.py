"""
models package initializer

- Exposes plain Python models (Admin, User, JD, Resume, Evaluation)
- These models work with JSON storage (see utils/storage.py)
- No SQLAlchemy is used anymore
"""

from .admin_model import Admin
from .jd_model import JD
from .resume_model import Resume
from .user_model import User
from .evaluator_model import Evaluation

__all__ = ["Admin", "JD", "Resume", "User", "Evaluation"]
