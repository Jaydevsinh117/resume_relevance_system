from models.base_model import BaseModel

class Evaluation(BaseModel):
    def __init__(self, id: int, resume_id: int, jd_id: int,
                 score: float = None, verdict: str = None,
                 missing_skills: str = "[]", created_at: str = None):
        self.id = id
        self.resume_id = resume_id      # link to Resume
        self.jd_id = jd_id              # link to JD
        self.score = score
        self.verdict = verdict          # "high", "medium", "low"
        self.missing_skills = missing_skills  # stored as JSON string
        self.created_at = created_at or self.now()

    def __repr__(self):
        return f"<Evaluation Resume={self.resume_id}, JD={self.jd_id}, Score={self.score}, Verdict={self.verdict}>"
