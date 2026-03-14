"""
models.py
---------
Shared Pydantic models for the NeuraX system.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional

class ProjectInput(BaseModel):
    project_id: str
    project_name: str
    description: str
    required_skills: List[str]
    deadline_days: int
    priority: str

class EmployeesInput(BaseModel):
    employees: List[Dict]

class TaskAssignment(BaseModel):
    task_id: str
    task_title: str
    task_description: str
    required_skills: List[str]
    estimated_days: int
    dependencies: List[str]
    assigned_employee_id: Optional[str]
    assigned_employee_name: str
    assigned_role: Optional[str]
    fitness_score: float
    workload_after_assignment: Optional[float]
    unassigned_reason: Optional[str]
