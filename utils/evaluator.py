import re
import json
import datetime
from utils.embedding import compare_texts  # 🔥 semantic similarity (fallback if model missing)

# --------------------------
# helper: tokenize text
# --------------------------
def tokenize(text: str):
    return re.findall(r"[a-zA-Z]+", (text or "").lower())


# --------------------------
# core evaluator: compare resume vs jd
# --------------------------
def evaluate_texts(resume_text: str, jd_text: str):
    """
    Compare resume text and JD text.
    Hybrid: semantic embeddings (if available) + token overlap fallback.
    Returns (score, verdict, missing_skills).
    """
    r_tokens, j_tokens = tokenize(resume_text), tokenize(jd_text)

    # If JD text empty → auto low
    if not j_tokens:
        return 0, "low", []

    # ✅ semantic score (if embedding backend available)
    try:
        score, verdict = compare_texts(resume_text, jd_text)
    except Exception:
        # fallback → plain token overlap
        overlap = len(set(r_tokens) & set(j_tokens))
        soft_score = overlap / max(1, len(set(j_tokens)))
        score = int(soft_score * 100)
        verdict = "high" if score >= 75 else "medium" if score >= 50 else "low"

    # ✅ missing skills (tokens in JD not in resume)
    missing = [w for w in set(j_tokens) if w not in r_tokens]

    return score, verdict, missing


# --------------------------
# utility: package evaluation result
# --------------------------
def build_evaluation_result(resume_id: int, jd_id: int, score: int, verdict: str, missing_skills: list):
    """
    Wrap evaluation result in a consistent dict format.
    """
    return {
        "resume_id": resume_id,
        "jd_id": jd_id,
        "score": score,
        "verdict": verdict,
        "missing_skills": missing_skills,
        "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
