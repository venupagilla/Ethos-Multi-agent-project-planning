from agent.base_agent import BaseAgent
from agent.utils import compute_workload_increment

class DevelopmentAgent(BaseAgent):
    def __init__(self, employees):
        super().__init__(employees)
        self.persona = "a Senior Development Expert"

    def handle_task(self, task):
        # Use LLM for intelligent selection
        selection = self._select_employee_with_llm(self.persona, task)
        
        emp_id = selection.get("employee_id")
        fitness = selection.get("fitness_score", 0.0)
        explanation = selection.get("reasoning", "No detailed reasoning provided by LLM.")

        best_emp = next((e for e in self.employees if e["employee_id"] == emp_id), None)

        if best_emp:
            return [{
                "task_id": task.get("task_id"),
                "task_title": task.get("title"),
                "task_description": task.get("description", ""),
                "required_skills": task.get("required_skills", []),
                "estimated_days": task.get("estimated_days", 0),
                "dependencies": task.get("dependencies", []),
                "assigned_employee_id": best_emp["employee_id"],
                "assigned_employee_name": best_emp["name"],
                "assigned_role": best_emp.get("role"),
                "fitness_score": float(fitness),
                "workload_after_assignment": best_emp.get("current_workload_percent", 0) + compute_workload_increment(task.get("estimated_days", 0)),
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
                "unassigned_reason": explanation if emp_id is None else "Selected employee not found in database.",
                "explanation": explanation
            }]
