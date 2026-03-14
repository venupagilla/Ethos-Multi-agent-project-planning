"""
testing_agent.py
---------------
Handles testing-related tasks and assignments.
"""


from agent.utils import normalize_skill, compute_skill_match_ratio, compute_workload_increment
from agent.employee_analyzer import compute_fitness

TESTING_SKILLS = {"pytest", "postman", "ci/cd", "testing", "validation", "qa"}


class TestingAgent:
    def __init__(self, employees):
        self.employees = employees

    def handle_task(self, task):
        best = None
        best_score = -1
        best_overlap = set()
        for emp in self.employees:
            emp_skills = set(normalize_skill(s) for s in emp.get("skills", []))
            if not emp_skills & set(normalize_skill(s) for s in TESTING_SKILLS):
                continue
            
            # Use standardized fitness calculation
            score = compute_fitness(emp, task.get('required_skills', []))
            _, overlap = compute_skill_match_ratio(emp.get("skills", []), task.get('required_skills', []))
            
            if score > best_score:
                best = emp
                best_score = score
                best_overlap = overlap
        if best:
            explanation = f"Best skill match for required skills: {', '.join(sorted(best_overlap)) if best_overlap else 'General testing expertise'}"
            return [{
                "task_id": task.get("task_id"),
                "task_title": task.get("title"),
                "task_description": task.get("description", ""),
                "required_skills": task.get("required_skills", []),
                "estimated_days": task.get("estimated_days", 0),
                "dependencies": task.get("dependencies", []),
                "assigned_employee_id": best["employee_id"],
                "assigned_employee_name": best["name"],
                "assigned_role": best.get("role"),
                "fitness_score": best_score,
                "workload_after_assignment": best.get("current_workload_percent", 0) + compute_workload_increment(task.get("estimated_days", 0)),
                "unassigned_reason": None,
                "explanation": explanation
            }]
        else:
            return [{
                "task_id": task.get("task_id"),
                "task_title": task.get("title"),
                "task_description": task.get("description", ""),
                "required_skills": task.get("required_skills", []),
                "estimated_days": task.get("estimated_days", 0),
                "dependencies": task.get("dependencies", []),
                "assigned_employee_id": None,
                "assigned_employee_name": "UNASSIGNED",
                "assigned_role": None,
                "fitness_score": 0.0,
                "workload_after_assignment": None,
                "unassigned_reason": "No suitable employee found for required skills.",
                "explanation": "No suitable employee found for required skills."
            }]
