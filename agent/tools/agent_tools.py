"""LangChain Tools for the NeuraX Planner Agent."""

import json
from langchain.tools import tool


@tool
def decompose_project_tool(project_json: str) -> str:
    """
    Decompose a project into actionable sub-tasks.
    Input: JSON string of the project dict.
    Output: JSON string list of task dicts.
    """
    from agent.task_decomposer import decompose
    project = json.loads(project_json)
    tasks = decompose(project)
    return json.dumps(tasks, indent=2)


@tool
def analyze_employees_tool(task_json: str) -> str:
    """
    Rank all employees by fitness for a given task.
    Input: JSON string of a single task dict.
    Output: JSON string list of ranked {employee, fitness_score} dicts.
    """
    from agent.employee_analyzer import load_employees, rank_employees_for_task
    task = json.loads(task_json)
    employees = load_employees()
    ranked = rank_employees_for_task(task, employees)
    # Slim down for readability in the agent context
    slim = [
        {
            "employee_id": r["employee"]["employee_id"],
            "name": r["employee"]["name"],
            "role": r["employee"]["role"],
            "fitness_score": r["fitness_score"],
            "current_workload_percent": r["employee"]["current_workload_percent"],
        }
        for r in ranked
    ]
    return json.dumps(slim, indent=2)


@tool
def assign_tasks_tool(tasks_and_employees_json: str) -> str:
    """
    Assign a list of tasks to employees.
    Input: JSON string with keys 'tasks' (list) and 'employees' (list).
    Output: JSON string list of assignment dicts.
    """
    from agent.assignment_engine import assign_tasks
    data = json.loads(tasks_and_employees_json)
    assignments = assign_tasks(data["tasks"], data["employees"])
    return json.dumps(assignments, indent=2)
