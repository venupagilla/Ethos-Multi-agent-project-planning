"""
super_agent.py
--------------
SuperAgent orchestrates the overall workflow:
  1. Decomposes the project into high-level tasks and workflow.
  2. Delegates tasks to specialized agents: DevOpsAgent, DevelopmentAgent, TestingAgent, DesignAgent.
  3. Collects and merges results from all agents.
"""


from typing import List, Dict

# Skill mappings for each agent type
DEVOPS_SKILLS = {"docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "devops"}
DEVELOPMENT_SKILLS = {"python", "node.js", "fastapi", "llms", "ml", "backend", "api", "pytorch/tensorflow", "data engineering", "nlp", "langchain", "databases"}
TESTING_SKILLS = {"pytest", "postman", "ci/cd", "testing", "validation", "qa"}
DESIGN_SKILLS = {"ui/ux", "react", "design", "frontend", "api design", "system architecture"}

def compute_skill_match(employee_skills, required_skills):
    # Lowercase and compare overlap
    emp = set(s.lower() for s in employee_skills)
    req = set(s.lower() for s in required_skills)
    return len(emp & req) / max(1, len(req))

def best_employee(employees, required_skills, agent_type_skills):
    best = None
    best_score = -1
    for emp in employees:
        emp_skills = set(s.lower() for s in emp.get("skills", []))
        # Only consider employees with at least one relevant skill for this agent type
        if not emp_skills & agent_type_skills:
            continue
        score = compute_skill_match(emp_skills, required_skills)
        if score > best_score:
            best = emp
            best_score = score
    return best, best_score


class SuperAgent:
    def __init__(self, employees: List[Dict]):
        self.employees = employees

    def generate_workflow(self, project):
        # For now, assume project['tasks'] is a list of dicts with 'type' field
        return project['tasks']

    def run(self, project):
        workflow = self.generate_workflow(project)
        assignments = []
        # Use the specialized agents for each type, so explanation is included
        for task in workflow:
            agent_type = task.get('type')
            if agent_type == 'devops':
                from agent.devops_agent import DevOpsAgent
                agent = DevOpsAgent(self.employees)
            elif agent_type == 'development':
                from agent.development_agent import DevelopmentAgent
                agent = DevelopmentAgent(self.employees)
            elif agent_type == 'testing':
                from agent.testing_agent import TestingAgent
                agent = TestingAgent(self.employees)
            elif agent_type == 'design':
                from agent.design_agent import DesignAgent
                agent = DesignAgent(self.employees)
            else:
                agent = None
            if agent:
                assignments.extend(agent.handle_task(task))
            else:
                # Fallback if no agent type matches
                assignments.append({
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
                    "unassigned_reason": "No suitable agent type for this task.",
                    "explanation": "No suitable agent type for this task."
                })
        return assignments
