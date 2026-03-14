"""
planner_agent.py
----------------
Main LangChain Agent that orchestrates the full project planning pipeline.

Flow:
  1. Decompose project → task list (via LLM tool)
  2. Detect skill gaps vs. employee pool
  3. Assign tasks to employees (greedy fitness scoring)
  4. Rebalance workloads if needed
  5. Assess project risk
  6. Generate JSON + Markdown report

The agent is designed to be called as a Python function (module mode)
so the upstream Ethos orchestrator can import and invoke it directly.
"""

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def run_pipeline(
    project: dict[str, Any],
    output_dir: str = "output",
    verbose: bool = True,
) -> dict[str, Any]:
    """
    Run the full planning and assignment pipeline using LangGraph.
    """
    from agent.graph import create_graph, save_graph_visualization
    from agent.employee_analyzer import load_employees

    _log(verbose, f"\n{'='*60}")
    _log(verbose, f"  Ethos Project Assignment Agent (LangGraph Mode)")
    _log(verbose, f"  Project: {project['project_name']} ({project['project_id']})")
    _log(verbose, f"{'='*60}\n")

    # Initialize Graph
    graph = create_graph()
    
    # Save visualization
    os.makedirs(output_dir, exist_ok=True)
    save_graph_visualization(graph, os.path.join(output_dir, "agent_workflow.mermaid"))

    # Initial State
    initial_state = {
        "project": project,
        "employees": load_employees(),
        "tasks": [],
        "assignments": [],
        "skill_gaps": {},
        "rebalance_log": [],
        "risk_report": {},
        "output_dir": output_dir,
        "report": {},
        "status": "Starting"
    }

    # Execute Graph
    _log(verbose, "🚀 Executing LangGraph workflow...")
    final_execution_state = graph.invoke(initial_state)
    _log(verbose, "✅ LangGraph workflow complete.")

    res = final_execution_state
    report = res["report"]

    return {
        "tasks": res["tasks"],
        "assignments": res["assignments"],
        "risk_report": res["risk_report"],
        "skill_gaps": res["skill_gaps"],
        "rebalance_log": res["rebalance_log"],
        "json_path": report.get("json_path"),
        "markdown_path": report.get("markdown_path"),
        "markdown": report.get("markdown", ""),
    }


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)
