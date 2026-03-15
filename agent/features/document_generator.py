"""
document_generator.py
---------------------
Generates Software System Requirement Document (SRS) and Design Requirement Document (DRD) 
using Groq based on project details and decomposed tasks.
"""

import logging
from typing import Any, Dict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from agent import config

logger = logging.getLogger(__name__)

def _get_llm():
    return ChatGroq(
        model=config.LLM_MODEL,
        temperature=0.4,
        groq_api_key=config.GROQ_API_KEY,
    )

def generate_documents(project: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Generates SRS and DRD documents.
    """
    llm = _get_llm()
    
    tasks_summary = "\n".join([f"- {t['task_id']}: {t['title']} ({t['description']})" for t in tasks])
    
    # 1. Generate SRS
    srs_system_prompt = "You are an expert Business Analyst. Generate a professional Software Requirements Specification (SRS) document."
    srs_user_prompt = f"""
    Project: {project['project_name']}
    Description: {project['description']}
    Tasks: 
    {tasks_summary}
    
    Provide a concise but comprehensive SRS including Introduction, Functional Requirements, Non-functional Requirements, and Scope.
    Format in Markdown.
    """
    
    # 2. Generate DRD
    drd_system_prompt = "You are a Senior Software Architect. Generate a professional Design Requirement Document (DRD)."
    drd_user_prompt = f"""
    Project: {project['project_name']}
    Description: {project['description']}
    Tasks: 
    {tasks_summary}
    
    Provide a professional DRD including System Architecture, Database Design, API Design, and Technical Stack.
    Format in Markdown.
    """
    
    try:
        srs_response = llm.invoke([
            ("system", srs_system_prompt),
            ("human", srs_user_prompt)
        ])
        srs_content = srs_response.content
        
        drd_response = llm.invoke([
            ("system", drd_system_prompt),
            ("human", drd_user_prompt)
        ])
        drd_content = drd_response.content
        
        return {
            "srs": srs_content,
            "drd": drd_content
        }
    except Exception as e:
        logger.error(f"Error generating documents: {e}")
        return {
            "srs": "Error generating SRS.",
            "drd": "Error generating DRD."
        }
