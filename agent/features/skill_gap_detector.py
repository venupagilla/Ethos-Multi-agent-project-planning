"""
skill_gap_detector.py
---------------------
Compares the required skills of each task (and the entire project) against
the collective skills of all employees.

Outputs:
  - project_level_gaps: skills needed by the project that NO employee has
  - task_level_gaps: per-task list of unmatched skills
  - recommendations: plain-English hiring/upskill suggestions
"""

from typing import Any


def detect_gaps(
    tasks: list[dict[str, Any]],
    employees: list[dict[str, Any]],
    project: dict[str, Any],
) -> dict[str, Any]:
    """
    Detect skill gaps across the employee pool for the given set of tasks.

    Args:
        tasks: decomposed task list
        employees: full employee pool
        project: original project dict

    Returns:
        {
            project_level_gaps: list[str],
            task_level_gaps: [{ task_id, task_title, missing_skills }],
            recommendations: list[str],
            has_gaps: bool
        }
    """
    all_emp_skills = set()
    for emp in employees:
        for skill in emp["skills"]:
            all_emp_skills.add(skill.lower())

    task_level_gaps = []
    all_missing: set[str] = set()

    for task in tasks:
        required = task.get("required_skills", [])
        missing = []
        for skill in required:
            skill_lower = skill.lower()
            # Check exact or partial match
            matched = any(
                skill_lower == es or skill_lower in es or es in skill_lower
                for es in all_emp_skills
            )
            if not matched:
                missing.append(skill)
                all_missing.add(skill)

        if missing:
            task_level_gaps.append({
                "task_id": task["task_id"],
                "task_title": task["title"],
                "missing_skills": missing,
            })

    # Project-level required skills
    project_required = project.get("required_skills", [])
    project_gaps = []
    for skill in project_required:
        skill_lower = skill.lower()
        matched = any(
            skill_lower == es or skill_lower in es or es in skill_lower
            for es in all_emp_skills
        )
        if not matched:
            project_gaps.append(skill)

    recommendations = _build_recommendations(all_missing)

    return {
        "project_level_gaps": project_gaps,
        "task_level_gaps": task_level_gaps,
        "recommendations": recommendations,
        "has_gaps": bool(all_missing or project_gaps),
    }


def _build_recommendations(missing_skills: set[str]) -> list[str]:
    if not missing_skills:
        return ["✅ All required skills are covered by the current employee pool."]

    recs = []
    for skill in sorted(missing_skills):
        recs.append(
            f"🔍 Skill '{skill}' is not available internally — consider hiring a contractor "
            f"or enrolling an existing employee in a '{skill}' training program."
        )
    return recs
