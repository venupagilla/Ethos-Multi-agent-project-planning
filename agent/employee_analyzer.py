"""
employee_analyzer.py
--------------------
Loads the employee pool and computes a fitness score for each employee
against a given task's required skills and estimated load.

Fitness Score Formula (0–100):
  - Skill match ratio:    60 points max
  - Experience bonus:     20 points max (capped at 10 years → 20pts)
  - Workload penalty:    -20 points max (100% workload = -20pts)
"""

import json
import os
from typing import Any
from agent.utils import normalize_skill
from agent import config

DATA_PATH = config.DATA_DIR / "employees.json"


from agent import database

def load_employees() -> list[dict[str, Any]]:
    """Load all employees from the database."""
    return database.get_employees()


def compute_fitness(employee: dict[str, Any], required_skills: list[str]) -> float:
    """
    Compute a fitness score (0–100) for an employee given a task's required skills.

    Args:
        employee: employee dict
        required_skills: list of skill strings required by the task

    Returns:
        float fitness score
    """
    emp_skills_lower = {normalize_skill(s) for s in employee["skills"]}
    req_skills_lower = [normalize_skill(s) for s in required_skills]

    if not req_skills_lower:
        skill_score = 70.0
    else:
        matched = sum(1 for s in req_skills_lower if s in emp_skills_lower)
        # Also check partial matches (e.g., "LLM" matches "LLMs")
        partial = sum(
            1
            for s in req_skills_lower
            if s not in emp_skills_lower
            and any(s in emp_s or emp_s in s for emp_s in emp_skills_lower)
        )
        skill_score = 70.0 * min((matched + 0.5 * partial) / len(req_skills_lower), 1.0)

    experience_score = min(employee["experience_years"] / 10.0, 1.0) * 30.0
    workload_penalty = (employee["current_workload_percent"] / 100.0) * 20.0

    return round(skill_score + experience_score - workload_penalty, 2)


def rank_employees_for_task(
    task: dict[str, Any],
    employees: list[dict[str, Any]],
    exclude_overloaded: bool = True,
) -> list[dict[str, Any]]:
    """
    Rank all employees for a given task by fitness score.

    Args:
        task: task dict with 'required_skills' key
        employees: list of employee dicts (use their current_workload_percent)
        exclude_overloaded: if True, employees at >= 90% workload are excluded

    Returns:
        Sorted list of dicts: {employee, fitness_score}
    """
    required_skills = task.get("required_skills", [])
    ranked = []
    for emp in employees:
        if exclude_overloaded and emp["current_workload_percent"] >= 90:
            continue
        score = compute_fitness(emp, required_skills)
        ranked.append({"employee": emp, "fitness_score": score})

    ranked.sort(key=lambda x: x["fitness_score"], reverse=True)
    return ranked
