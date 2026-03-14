"""
assignment_engine.py
--------------------
Maps each decomposed task to the best-fit employee using a greedy scoring pass.
After each assignment it updates the employee's effective workload so subsequent
tasks see the updated capacity.

Workload hard cap: 90% — no employee is assigned beyond this threshold.
"""

import copy
from typing import Any

from agent.employee_analyzer import rank_employees_for_task


WORKLOAD_PER_TASK_BASE = 10  # Default workload increment per task assignment (%)


def assign_tasks(
    tasks: list[dict[str, Any]],
    employees: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Assign each task to the best available employee.

    Args:
        tasks: list of task dicts from task_decomposer
        employees: list of employee dicts (will NOT be mutated — deep copy used internally)

    Returns:
        List of assignment dicts:
        {
            task_id, task_title, required_skills, estimated_days,
            assigned_employee_id, assigned_employee_name, assigned_role,
            fitness_score, workload_after_assignment, unassigned_reason
        }
    """
    # Deep copy so the original list isn't mutated
    working_employees = copy.deepcopy(employees)
    assignments = []

    for task in tasks:
        ranked = rank_employees_for_task(task, working_employees, exclude_overloaded=True)

        assigned = False
        for candidate in ranked:
            emp = candidate["employee"]
            projected_workload = emp["current_workload_percent"] + WORKLOAD_PER_TASK_BASE

            if projected_workload <= 90:
                # Commit the assignment
                emp["current_workload_percent"] = projected_workload

                assignments.append({
                    "task_id": task["task_id"],
                    "task_title": task["title"],
                    "task_description": task.get("description", ""),
                    "required_skills": task.get("required_skills", []),
                    "estimated_days": task.get("estimated_days", 0),
                    "dependencies": task.get("dependencies", []),
                    "assigned_employee_id": emp["employee_id"],
                    "assigned_employee_name": emp["name"],
                    "assigned_role": emp["role"],
                    "fitness_score": candidate["fitness_score"],
                    "workload_after_assignment": projected_workload,
                    "unassigned_reason": None,
                })
                assigned = True
                break

        if not assigned:
            assignments.append({
                "task_id": task["task_id"],
                "task_title": task["title"],
                "task_description": task.get("description", ""),
                "required_skills": task.get("required_skills", []),
                "estimated_days": task.get("estimated_days", 0),
                "dependencies": task.get("dependencies", []),
                "assigned_employee_id": None,
                "assigned_employee_name": "UNASSIGNED",
                "assigned_role": None,
                "fitness_score": 0.0,
                "workload_after_assignment": None,
                "unassigned_reason": "All eligible employees at or above 90% workload cap",
            })

    return assignments
