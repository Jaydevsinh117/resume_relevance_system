from models.base_model import BaseModel

class JD(BaseModel):
    def __init__(self, id: int, admin_id: int, filename: str, file_path: str, file_type: str,
                 title: str = None, parsed_text: str = None, uploaded_at: str = None):
        self.id = id
        self.admin_id = admin_id
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.title = title
        self.parsed_text = parsed_text
        self.uploaded_at = uploaded_at or self.now()

    def __repr__(self):
        return f"<JD {self.title or self.filename} (Admin {self.admin_id})>"
