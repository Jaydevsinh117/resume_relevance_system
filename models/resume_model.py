from models.base_model import BaseModel

class Resume(BaseModel):
    def __init__(self, id: int, user_id: int, original_filename: str, filename: str,
                 file_path: str, file_type: str, parsed_text: str = None, uploaded_at: str = None):
        self.id = id
        self.user_id = user_id
        self.original_filename = original_filename
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.parsed_text = parsed_text
        self.uploaded_at = uploaded_at or self.now()

    def __repr__(self):
        return f"<Resume id={self.id}, filename={self.filename}, user_id={self.user_id}, uploaded_at={self.uploaded_at}>"
