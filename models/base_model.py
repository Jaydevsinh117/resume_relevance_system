import datetime

class BaseModel:
    """Base model with helper methods for JSON storage"""

    def to_dict(self):
        """Convert object to dict for saving in JSON"""
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict):
        """Create object from dict (JSON-loaded data)"""
        return cls(**data)

    @staticmethod
    def now():
        """Current UTC timestamp string"""
        return datetime.datetime.utcnow().isoformat()
