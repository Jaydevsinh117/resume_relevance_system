from models.base_model import BaseModel

class User(BaseModel):
    def __init__(self, id: int, name: str, email: str, password: str, created_at: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.created_at = created_at or self.now()

    def __repr__(self):
        return f"<User {self.email}>"
