"""
base_agent.py
-------------
Base class for all specialized agents, providing shared LLM connectivity via Groq.
"""

from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from agent import config

class BaseAgent:
    def __init__(self, employees: List[Dict[str, Any]]):
        self.employees = employees
        self.llm = ChatGroq(
            model=config.LLM_MODEL,
            temperature=0.2,
            groq_api_key=config.GROQ_API_KEY,
        )

    def _get_system_prompt(self, persona: str) -> str:
        return f"""You are {persona} in the Ethos autonomous project management system.
Your goal is to find the MOST SUITABLE employee for a specific task based on their skills, experience, and current workload.

Rules:
- If a perfect match is not found, select the closest one.
- Consider workload: if an employee is already at 90%, they are likely not a good choice.
- You must provide a clear and professional reasoning for your choice.
- You must provide a fitness_score between 0 and 100 (where 100 is a perfect match)."""

    def _select_employee_with_llm(self, persona: str, task: Dict[str, Any]) -> Dict[str, Any]:
        from langchain_core.prompts import ChatPromptTemplate
        from agent.models import AgentSelection
        from agent.employee_analyzer import rank_employees_for_task
        import json
        import logging

        # Pre-filter: rank employees locally by skill fit + workload, then pass
        # only the top 10 candidates to the LLM. This keeps prompt size O(1)
        # regardless of employee pool size, supporting 500+ row datasets.
        task_for_ranking = {"required_skills": task.get("required_skills", [])}
        ranked = rank_employees_for_task(task_for_ranking, self.employees, exclude_overloaded=True)
        if not ranked:
            # Fallback: all employees are overloaded — include them anyway so we can still pick
            ranked = rank_employees_for_task(task_for_ranking, self.employees, exclude_overloaded=False)

        top_candidates = [r["employee"] for r in ranked[:10]]

        employee_data = []
        for emp in top_candidates:
            employee_data.append({
                "id": emp["employee_id"],
                "name": emp["name"],
                "role": emp["role"],
                "skills": emp["skills"],
                "workload": f"{emp.get('current_workload_percent', 0)}%"
            })

        user_prompt_template = """Task: {title}
Description: {description}
Required Skills: {skills}
Duration: {days} days

Candidates:
{candidates}

Select the best candidate for this task."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt(persona)),
            ("human", user_prompt_template)
        ])

        # Modern LangChain: LCEL + Structured Output
        structured_llm = self.llm.with_structured_output(AgentSelection)
        chain = prompt | structured_llm

        try:
            result = chain.invoke({
                "title": task.get('title'),
                "description": task.get('description'),
                "skills": ", ".join(task.get('required_skills', [])),
                "days": task.get('estimated_days'),
                "candidates": json.dumps(employee_data, indent=2)
            })
            
            # Normalize score: if LLM returns 0.0-1.0 scale, convert to 0-100
            score = result.fitness_score
            if 0 < score <= 1.0:
                score = score * 100.0
                
            return {
                "employee_id": result.employee_id,
                "fitness_score": score,
                "reasoning": result.reasoning
            }
        except Exception as e:
            logging.error(f"[BaseAgent] LangChain selection error: {e}")
            return {
                "employee_id": None,
                "fitness_score": 0.0,
                "reasoning": f"LangChain error: {str(e)}"
            }

    def handle_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """To be implemented by subclasses."""
        raise NotImplementedError
