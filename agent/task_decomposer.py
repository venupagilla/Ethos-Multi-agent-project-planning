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
from dotenv import load_dotenv

load_dotenv(override=True)


def _get_llm():
    model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    return ChatGroq(
        model=model,
        temperature=0.3,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )


SYSTEM_PROMPT = """You are a senior software project manager and technical architect.
Your job is to decompose a software project into clear, atomic, actionable sub-tasks.
Return ONLY a valid JSON array of task objects. Do not include any markdown, explanation, or commentary.

Each task object must have exactly these fields:
- task_id: string (e.g. "T1", "T2", ...)
- title: string (short task title)
- description: string (1-2 sentences, concrete and actionable)
- required_skills: list of strings
- estimated_days: integer (realistic estimate)
- dependencies: list of task_ids that must complete first (empty list if none)

Generate between 5 and 10 tasks. Be practical and realistic."""


def decompose(project: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Decompose a project into sub-tasks using the configured LLM.

    Args:
        project: dict with keys project_id, project_name, description,
                 required_skills, deadline_days, priority

    Returns:
        List of task dicts
    """
    llm = _get_llm()

    user_prompt = f"""Project: {project['project_name']}
Description: {project['description']}
Required Skills: {', '.join(project['required_skills'])}
Deadline: {project['deadline_days']} days
Priority: {project['priority']}

Decompose this project into 5-10 concrete sub-tasks."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    tasks = json.loads(raw)
    return tasks
