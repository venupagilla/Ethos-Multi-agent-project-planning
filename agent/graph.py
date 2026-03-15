"""
graph.py
--------
Defines the LangGraph orchestration for the Ethos Project Assignment Agent.
"""

import os
import logging
from typing import Annotated, Any, Dict, List, TypedDict

from langgraph.graph import StateGraph, END
from agent.task_decomposer import decompose
from agent.employee_analyzer import load_employees
from agent.super_agent import SuperAgent
from agent.features.skill_gap_detector import detect_gaps
from agent.features.workload_balancer import rebalance
from agent.features.risk_assessor import assess_risk
from agent.features.report_generator import generate
from agent.features.document_generator import generate_documents
from agent.tools.vector_service import index_project_data

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """The state of the project assignment process."""
    project: Dict[str, Any]
    employees: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    assignments: List[Dict[str, Any]]
    skill_gaps: Dict[str, Any]
    rebalance_log: List[str]
    risk_report: Dict[str, Any]
    output_dir: str
    report: Dict[str, str]
    generated_docs: Dict[str, str]
    status: str

# Nodes

def planner_node(state: AgentState) -> Dict[str, Any]:
    """Decompose project into tasks."""
    logger.info("[NODES] Running planner_node - Decomposing project...")
    tasks = decompose(state["project"])
    return {"tasks": tasks, "status": "Decomposition Complete"}

def detect_gaps_node(state: AgentState) -> Dict[str, Any]:
    """Detect skill gaps."""
    logger.info("[NODES] Running detect_gaps_node - Analyzing workforce...")
    gaps = detect_gaps(state["tasks"], state["employees"], state["project"])
    return {"skill_gaps": gaps, "status": "Gaps Detected"}

def assigner_node(state: AgentState) -> Dict[str, Any]:
    """Assign tasks using specialized agents via SuperAgent."""
    logger.info("[NODES] Running assigner_node - Multi-agent assignment...")
    super_agent = SuperAgent(state["employees"])
    # SuperAgent expects project with tasks
    project_with_tasks = state["project"].copy()
    project_with_tasks["tasks"] = state["tasks"]
    assignments = super_agent.run(project_with_tasks)
    return {"assignments": assignments, "status": "Assignment Complete"}

def balancer_node(state: AgentState) -> Dict[str, Any]:
    """Rebalance workloads."""
    logger.info("[NODES] Running balancer_node - Optimizing workloads...")
    final_assignments, log = rebalance(state["assignments"], state["employees"])
    return {"assignments": final_assignments, "rebalance_log": log, "status": "Rebalancing Complete"}

def risk_assessor_node(state: AgentState) -> Dict[str, Any]:
    """Assess project risk."""
    logger.info("[NODES] Running risk_assessor_node - Evaluating timeline risk...")
    risk = assess_risk(state["project"], state["assignments"])
    return {"risk_report": risk, "status": "Risk Assessed"}
def publisher_node(state: AgentState) -> Dict[str, Any]:
    """Generate final reports."""
    logger.info("[NODES] Running publisher_node - Generating reports...")
    report = generate(
        state["project"],
        state["assignments"],
        state["risk_report"],
        state["skill_gaps"],
        state["rebalance_log"],
        state["output_dir"]
    )
    
    # Save SRS and DRD if they exist (generated in future node but we can generate them earlier or just handle here)
    # Wait, the flow is publisher -> doc_generator. 
    # Let's move doc_generator BEFORE publisher so publisher can include links? 
    # Or just let doc_generator save its own files.
    
    return {"report": report, "status": "Report Generated"}

def doc_generator_node(state: AgentState) -> Dict[str, Any]:
    """Generate SRS and DRD documents."""
    logger.info("[NODES] Running doc_generator_node - Creating SRS and DRD...")
    docs = generate_documents(state["project"], state["tasks"])
    
    # Save to files
    project_id = state["project"]["project_id"]
    for doc_type in ["srs", "drd"]:
        path = os.path.join(state["output_dir"], f"{project_id}_{doc_type}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(docs.get(doc_type, ""))
        logger.info(f"Saved {doc_type.upper()} to {path}")
            
    return {"generated_docs": docs, "status": "Documents Generated"}

def indexer_node(state: AgentState) -> Dict[str, Any]:
    """Index all documents for RAG."""
    logger.info("[NODES] Running indexer_node - Indexing for RAG...")
    doc_map = state["generated_docs"].copy()
    doc_map["report"] = state["report"].get("markdown", "")
    index_project_data(state["project"]["project_id"], doc_map)
    return {"status": "Indexing Complete"}

# Graph Construction

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("gap_detector", detect_gaps_node)
    workflow.add_node("assigner", assigner_node)
    workflow.add_node("balancer", balancer_node)
    workflow.add_node("risk_assessor", risk_assessor_node)
    workflow.add_node("publisher", publisher_node)
    workflow.add_node("doc_generator", doc_generator_node)
    workflow.add_node("indexer", indexer_node)

    # Add edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "gap_detector")
    workflow.add_edge("gap_detector", "assigner")
    workflow.add_edge("assigner", "balancer")
    workflow.add_edge("balancer", "risk_assessor")
    workflow.add_edge("risk_assessor", "publisher")
    workflow.add_edge("publisher", "doc_generator")
    workflow.add_edge("doc_generator", "indexer")
    workflow.add_edge("indexer", END)

    return workflow.compile()

# Visualization Helper

def save_graph_visualization(graph, output_path: str):
    """Saves the graph as any visual format supported (Mermaid)."""
    try:
        mermaid_code = graph.get_graph().draw_mermaid()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        logger.info(f"Graph visualization saved to {output_path}")
    except Exception as e:
        logger.warning(f"Failed to generate graph visualization: {e}")
