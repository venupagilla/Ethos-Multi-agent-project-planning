"""
task_decomposer.py
------------------
Breaks a project into a clear, numbered list of actionable sub-tasks using an LLM.
Each task includes: task_id, title, description, required_skills, estimated_days, dependencies.

LLM Provider: Groq  (model: openai/gpt-4o-mini by default, overridable via LLM_MODEL in .env)
"""

import json
import os
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from agent import config


def _get_llm():
    return ChatGroq(
        model=config.LLM_MODEL,
        temperature=0.3,
        groq_api_key=config.GROQ_API_KEY,
    )


from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ProjectTask(BaseModel):
    """Schema for a decomposed project task."""
    task_id: str = Field(description="Unique ID like T1, T2")
    title: str = Field(description="Short, descriptive title")
    description: str = Field(description="Actionable task details")
    required_skills: list[str] = Field(description="Skills needed for the task")
    estimated_days: int = Field(description="Realistic effort estimate")
    type: str = Field(description="Category: devops, development, testing, design")
    dependencies: list[str] = Field(description="IDs of prerequisite tasks")

class ProjectDecomposition(BaseModel):
    """List of tasks for the project."""
    tasks: list[ProjectTask]

def decompose(project: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Decompose a project into sub-tasks using the configured LLM.
    """
    import logging
    llm = _get_llm()

    system_prompt = """You are a senior software project manager and technical architect.
Your job is to decompose a software project into clear, atomic, actionable sub-tasks.
Generate between 5 and 10 tasks. Be practical and realistic."""

    user_prompt = """Project: {name}
Description: {description}
Required Skills: {skills}
Deadline: {deadline} days
Priority: {priority}

Decompose this project into 5-10 concrete sub-tasks."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    structured_llm = llm.with_structured_output(ProjectDecomposition)
    chain = prompt | structured_llm

    try:
        result = chain.invoke({
            "name": project['project_name'],
            "description": project['description'],
            "skills": ', '.join(project['required_skills']),
            "deadline": project['deadline_days'],
            "priority": project['priority']
        })
        logging.info(f"[decompose] Parsed tasks: {result.tasks}")
        return [t.model_dump() for t in result.tasks]
    except Exception as e:
        logging.error(f"[decompose] Error during task decomposition: {e}")
        return []
