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
so the upstream NeuraX orchestrator can import and invoke it directly.
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
    Run the full planning and assignment pipeline for a given project.

    Args:
        project: dict matching the project schema
                 (project_id, project_name, description,
                  required_skills, deadline_days, priority)
        output_dir: directory to write report files to
        verbose: if True, print progress to stdout

    Returns:
        {
            assignments: list,
            risk_report: dict,
            skill_gaps: dict,
            rebalance_log: list,
            json_path: str,
            markdown_path: str,
            markdown: str,
        }
    """
    from agent.task_decomposer import decompose
    from agent.employee_analyzer import load_employees
    from agent.features.skill_gap_detector import detect_gaps
    from agent.features.workload_balancer import rebalance
    from agent.features.risk_assessor import assess_risk
    from agent.features.report_generator import generate
    from agent.super_agent import SuperAgent

    _log(verbose, f"\n{'='*60}")
    _log(verbose, f"  NeuraX Project Assignment Agent")
    _log(verbose, f"  Project: {project['project_name']} ({project['project_id']})")
    _log(verbose, f"{'='*60}\n")


    # Step 1: Task Decomposition (SuperAgent will use this or similar logic)
    _log(verbose, "📋 Step 1: Decomposing project into tasks and workflow (SuperAgent)...")
    employees = load_employees()
    super_agent = SuperAgent(employees)
    tasks = decompose(project)
    project["tasks"] = tasks
    _log(verbose, f"   → Generated {len(tasks)} tasks with types.")

    # Step 2: Skill Gap Detection (unchanged)
    _log(verbose, "🔍 Step 2: Detecting skill gaps...")
    skill_gaps = detect_gaps(tasks, employees, project)
    if skill_gaps["has_gaps"]:
        _log(verbose, f"   ⚠️  Gaps found: {skill_gaps['project_level_gaps'] + [g['missing_skills'] for g in skill_gaps['task_level_gaps']]}")
    else:
        _log(verbose, "   ✅ No skill gaps found.")

    # Step 3: Multi-Agent Task Assignment
    _log(verbose, "🤖 Step 3: Assigning tasks using multi-agent system...")
    assignments = super_agent.run(project)
    assigned_count = sum(1 for a in assignments if a["assigned_employee_id"])
    _log(verbose, f"   → {assigned_count}/{len(assignments)} tasks successfully assigned.")

    # Step 4: Workload Rebalancing (unchanged)
    _log(verbose, "⚖️  Step 4: Checking workload balance...")
    final_assignments, rebalance_log = rebalance(assignments, employees)
    for entry in rebalance_log:
        _log(verbose, f"   {entry}")


    # Step 5: Risk Assessment (unchanged)
    _log(verbose, "🔴 Step 5: Assessing project risk...")
    risk_report = assess_risk(project, final_assignments)
    _log(verbose, f"   → Overall Risk: {risk_report['overall_risk_level']}")

    # Step 6: Report Generation (unchanged)
    _log(verbose, "📄 Step 6: Generating reports...")
    report = generate(project, final_assignments, risk_report, skill_gaps, rebalance_log, output_dir)
    _log(verbose, f"   → JSON:     {report['json_path']}")
    _log(verbose, f"   → Markdown: {report['markdown_path']}")
    _log(verbose, f"\n{'='*60}\n")

    return {
        "tasks": tasks,
        "assignments": final_assignments,
        "risk_report": risk_report,
        "skill_gaps": skill_gaps,
        "rebalance_log": rebalance_log,
        "json_path": report["json_path"],
        "markdown_path": report["markdown_path"],
        "markdown": report["markdown"],
    }


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)
