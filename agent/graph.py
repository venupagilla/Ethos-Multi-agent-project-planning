"""
graph.py
--------
Defines the LangGraph orchestration for the Ethos Project Assignment Agent.
"""

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
    return {"report": report, "status": "Report Generated"}

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

    # Add edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "gap_detector")
    workflow.add_edge("gap_detector", "assigner")
    workflow.add_edge("assigner", "balancer")
    workflow.add_edge("balancer", "risk_assessor")
    workflow.add_edge("risk_assessor", "publisher")
    workflow.add_edge("publisher", END)

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
