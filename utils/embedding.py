import os
import numpy as np

# --------------------------
# clean text (reusable)
# --------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).lower()


# --------------------------
# embedding backend (lazy load)
# --------------------------
_model = None

def _load_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            _model = False  # no transformer available
    return _model


def get_embedding(text: str):
    """
    Generate embedding for a given text.
    - HuggingFace (384 dims) if available
    - Fallback to hash-based embedding (fixed length: 384)
    """
    text = clean_text(text)
    if not text:
        return np.zeros(384).tolist()

    model = _load_model()
    if model:
        return model.encode(text).tolist()

    # fallback dummy embedding (fixed length 384)
    vec = np.zeros(384)
    for i, word in enumerate(text.split()[:384]):
        vec[i] = (hash(word) % 1000) / 1000.0
    return vec.tolist()


# --------------------------
# cosine similarity
# --------------------------
def cosine_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


# --------------------------
# compare texts
# --------------------------
def compare_texts(text1: str, text2: str):
    """
    Compare two texts → returns score (0–100) and verdict.
    Verdict is auto-classified: high / medium / low match.
    """
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    similarity = cosine_similarity(emb1, emb2)
    score = int(similarity * 100)

    if score >= 75:
        verdict = "high"
    elif score >= 50:
        verdict = "medium"
    else:
        verdict = "low"

    return score, verdict
