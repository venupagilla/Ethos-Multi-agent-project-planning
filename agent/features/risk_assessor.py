"""
risk_assessor.py
----------------
Scores the project and each individual task assignment for risk.

Risk factors:
  - Tight deadline (< 20 days → High, < 10 days → Critical)
  - High priority project → raises base risk
  - Assigned employee already > 70% workload → task-level risk flag
  - Unassigned tasks → Critical risk
  - Multiple tasks assigned to same person → cascade risk
"""

from typing import Any

PRIORITY_WEIGHT = {"High": 2, "Medium": 1, "Low": 0}
DEADLINE_THRESHOLDS = {
    "Critical": 10,
    "High": 20,
    "Medium": 35,
}


def assess_risk(
    project: dict[str, Any],
    assignments: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Assess overall project risk and per-task risk flags.

    Args:
        project: original project dict
        assignments: list of assignment dicts from assignment_engine

    Returns:
        {
            overall_risk_level: str,
            overall_risk_score: int,
            risk_summary: str,
            task_risks: [{ task_id, risk_level, flags: [str] }]
        }
    """
    risk_score = 0
    task_risks = []
    employee_task_counts: dict[str, int] = {}

    # --- Per-task risk ---
    for a in assignments:
        flags = []
        task_score = 0

        # Unassigned task
        if a["assigned_employee_id"] is None:
            flags.append("❌ Task is UNASSIGNED — no available employee meets requirements")
            task_score += 30

        else:
            # High post-assignment workload
            if a.get("workload_after_assignment", 0) >= 80:
                flags.append(
                    f"⚠️ Assignee workload will reach {a['workload_after_assignment']}% after this task"
                )
                task_score += 10

            # Cascade: same employee on many tasks
            emp_id = a["assigned_employee_id"]
            employee_task_counts[emp_id] = employee_task_counts.get(emp_id, 0) + 1
            if employee_task_counts[emp_id] >= 3:
                flags.append(
                    f"⚠️ {a['assigned_employee_name']} is assigned {employee_task_counts[emp_id]} tasks — cascade risk"
                )
                task_score += 5

            # Low fitness score
            if a["fitness_score"] < 30:
                flags.append(
                    f"⚠️ Low skill-fit score ({a['fitness_score']:.1f}/100) — consider upskilling or external hire"
                )
                task_score += 8

        # Tight deadline per task (estimated_days vs remaining project deadline)
        if a.get("estimated_days", 0) > project["deadline_days"]:
            flags.append("🔴 Task estimated duration exceeds project deadline")
            task_score += 15

        level = _score_to_level(task_score)
        task_risks.append({
            "task_id": a["task_id"],
            "task_title": a["task_title"],
            "risk_level": level,
            "risk_score": task_score,
            "flags": flags if flags else ["✅ No significant risks detected"],
        })
        risk_score += task_score

    # --- Project-level modifiers ---
    priority_bonus = PRIORITY_WEIGHT.get(project.get("priority", "Medium"), 1) * 5
    risk_score += priority_bonus

    deadline = project.get("deadline_days", 30)
    if deadline <= DEADLINE_THRESHOLDS["Critical"]:
        risk_score += 30
    elif deadline <= DEADLINE_THRESHOLDS["High"]:
        risk_score += 15
    elif deadline <= DEADLINE_THRESHOLDS["Medium"]:
        risk_score += 5

    unassigned_count = sum(1 for a in assignments if a["assigned_employee_id"] is None)
    if unassigned_count:
        risk_score += unassigned_count * 20

    overall_level = _score_to_level(risk_score)

    risk_summary = _build_summary(overall_level, project, unassigned_count)

    return {
        "overall_risk_level": overall_level,
        "overall_risk_score": risk_score,
        "risk_summary": risk_summary,
        "task_risks": task_risks,
    }


def _score_to_level(score: int) -> str:
    if score >= 60:
        return "Critical"
    if score >= 35:
        return "High"
    if score >= 15:
        return "Medium"
    return "Low"


def _build_summary(level: str, project: dict, unassigned: int) -> str:
    parts = [
        f"Project '{project['project_name']}' has an overall risk level of **{level}**.",
        f"Priority: {project.get('priority', 'N/A')} | Deadline: {project.get('deadline_days', '?')} days.",
    ]
    if unassigned:
        parts.append(f"⚠️ {unassigned} task(s) could not be assigned to any employee.")
    return " ".join(parts)
