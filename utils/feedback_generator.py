def generate_feedback(evaluation: dict) -> dict:
    """
    Input: evaluation dict from utils/evaluator.py
           {
             "score": 72,
             "verdict": "medium",
             "missing_skills": ["docker", "kubernetes"],
             ...
           }
    Output: feedback dict with actionable advice
    """
    score = evaluation.get("score", 0)
    verdict = evaluation.get("verdict", "low")
    missing_skills = evaluation.get("missing_skills", [])

    feedback = {
        "summary": f"Your score is {score}/100. " + verdict_feedback(verdict),
        "skills_advice": skills_feedback(missing_skills),
        "pro_tip": random_tip(),
    }
    return feedback
