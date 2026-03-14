"""
utils.py
--------
Shared utility functions for the Ethos agents.
"""

# Synonym mapping for skill normalization (shared with other agents)
SKILL_SYNONYMS = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "llms": "large language models",
    "ci/cd": "cicd",
    "pythontensorflow": "pytorch/tensorflow",
    "nlp": "natural language processing",
    "ui/ux": "uiux",
    "reactjs": "react",
    "data analysis": "data analytics",
    "apis": "api",
    "databases": "database",
}

def normalize_skill(skill: str) -> str:
    """Normalize a skill string for better matching."""
    # 1. Lowercase and remove leading/trailing whitespace
    s = skill.lower().strip()
    
    # 2. Key for synonym lookup (remove internal spaces and dashes)
    lookup_key = s.replace(" ", "").replace("-", "")
    normalized = SKILL_SYNONYMS.get(lookup_key, s)
    
    # 3. Final clean key for internal comparison (no spaces, no dashes)
    return normalized.replace(" ", "").replace("-", "").replace(".", "")

def compute_skill_match_ratio(employee_skills: list[str], required_skills: list[str]) -> tuple[float, set[str]]:
    """Compute the ratio of matched skills and return the overlapping skills."""
    emp = set(normalize_skill(s) for s in employee_skills)
    req = set(normalize_skill(s) for s in required_skills)
    if not req:
        return 1.0, set()
    overlap = emp & req
    return len(overlap) / len(req), overlap

def compute_workload_increment(estimated_days: float) -> float:
    """
    Calculate workload increment based on estimated days.
    Assuming a standard capacity where 1 day = 5% workload.
    """
    return round(float(estimated_days) * 5.0, 1)
