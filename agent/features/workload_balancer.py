"""
workload_balancer.py
--------------------
After initial assignment, detects any employee whose projected workload
exceeds the 90% hard cap and attempts to reassign those tasks to the
next-best available employee.
"""

import copy
from typing import Any

from agent.employee_analyzer import rank_employees_for_task

WORKLOAD_CAP = 90
WORKLOAD_PER_TASK_BASE = 10


def rebalance(
    assignments: list[dict[str, Any]],
    employees: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Attempt to rebalance assignments so no employee exceeds the workload cap.

    Args:
        assignments: list of assignment dicts from assignment_engine
        employees: original employee list (deep-copied internally)

    Returns:
        (rebalanced_assignments, change_log)
        change_log is a list of strings describing what was changed
    """
    working_employees = copy.deepcopy(employees)
    # Rebuild simulated workloads from the assignments
    emp_map = {e["employee_id"]: e for e in working_employees}
    for a in assignments:
        if a["assigned_employee_id"]:
            emp_map[a["assigned_employee_id"]]["current_workload_percent"] += WORKLOAD_PER_TASK_BASE

    rebalanced = copy.deepcopy(assignments)
    change_log = []

    for i, assignment in enumerate(rebalanced):
        emp_id = assignment.get("assigned_employee_id")
        if emp_id is None:
            continue

        emp = emp_map[emp_id]
        if emp["current_workload_percent"] > WORKLOAD_CAP:
            # Try to find a better candidate
            task = {
                "task_id": assignment["task_id"],
                "title": assignment["task_title"],
                "required_skills": assignment["required_skills"],
            }
            all_emps = list(emp_map.values())
            ranked = rank_employees_for_task(task, all_emps, exclude_overloaded=False)

            for candidate in ranked:
                c_emp = candidate["employee"]
                if c_emp["employee_id"] == emp_id:
                    continue
                projected = c_emp["current_workload_percent"] + WORKLOAD_PER_TASK_BASE
                if projected <= WORKLOAD_CAP:
                    # Reassign
                    old_name = assignment["assigned_employee_name"]
                    # Roll back old employee's workload
                    emp["current_workload_percent"] -= WORKLOAD_PER_TASK_BASE
                    # Commit new assignment
                    c_emp["current_workload_percent"] = projected
                    rebalanced[i]["assigned_employee_id"] = c_emp["employee_id"]
                    rebalanced[i]["assigned_employee_name"] = c_emp["name"]
                    rebalanced[i]["assigned_role"] = c_emp["role"]
                    rebalanced[i]["fitness_score"] = candidate["fitness_score"]
                    rebalanced[i]["workload_after_assignment"] = projected
                    change_log.append(
                        f"Task {assignment['task_id']} reassigned from {old_name} → "
                        f"{c_emp['name']} (workload: {projected}%)"
                    )
                    break

    if not change_log:
        change_log.append("✅ No rebalancing needed — all assignments are within workload caps.")

    return rebalanced, change_log
