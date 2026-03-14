"""
report_generator.py
-------------------
Generates two output formats from the final assignment data:
  1. Structured JSON  → machine-readable for downstream Ethos agents
  2. Markdown Report  → human-readable, can be emailed to the manager
"""

import json
import os
from datetime import datetime
from typing import Any


def generate(
    project: dict[str, Any],
    assignments: list[dict[str, Any]],
    risk_report: dict[str, Any],
    skill_gaps: dict[str, Any],
    rebalance_log: list[str],
    output_dir: str = "output",
) -> dict[str, str]:
    """
    Generate JSON + Markdown reports and save to output_dir.

    Returns:
        { "json_path": str, "markdown_path": str, "markdown": str }
    """
    os.makedirs(output_dir, exist_ok=True)
    pid = project["project_id"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Build structured JSON ---
    structured = {
        "project": project,
        "generated_at": timestamp,
        "assignments": assignments,
        "risk_report": risk_report,
        "skill_gaps": skill_gaps,
        "rebalance_log": rebalance_log,
    }
    json_path = os.path.join(output_dir, f"{pid}_assignments.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)

    # --- Build Markdown ---
    md = _build_markdown(project, assignments, risk_report, skill_gaps, rebalance_log, timestamp)
    md_path = os.path.join(output_dir, f"{pid}_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    return {"json_path": json_path, "markdown_path": md_path, "markdown": md}


def _build_markdown(
    project, assignments, risk_report, skill_gaps, rebalance_log, timestamp
) -> str:
    lines = []

    # Header
    lines += [
        f"# 📋 Project Assignment Report",
        f"",
        f"**Project:** {project['project_name']} (`{project['project_id']}`)",
        f"**Generated:** {timestamp}",
        f"**Priority:** {project.get('priority', 'N/A')}  |  "
        f"**Deadline:** {project.get('deadline_days', '?')} days  |  "
        f"**Overall Risk:** `{risk_report['overall_risk_level']}`",
        f"",
        f"> {risk_report['risk_summary']}",
        f"",
        "---",
        f"",
    ]

    # Task assignments table
    lines += [
        "## 🗂️ Task Assignments",
        "",
        "| # | Task | Assigned To | Role | Fit Score | Est. Days | Risk |",
        "|---|------|-------------|------|-----------|-----------|------|",
    ]
    risk_by_task = {r["task_id"]: r for r in risk_report["task_risks"]}
    for a in assignments:
        risk_info = risk_by_task.get(a["task_id"], {})
        risk_badge = risk_info.get("risk_level", "?")
        assignee = a["assigned_employee_name"]
        if a["assigned_employee_id"] is None:
            assignee = "⛔ UNASSIGNED"
        lines.append(
            f"| {a['task_id']} | {a['task_title']} | {assignee} | "
            f"{a.get('assigned_role') or '-'} | {a['fitness_score']:.1f} | "
            f"{a['estimated_days']}d | {risk_badge} |"
        )

    lines += ["", "---", ""]

    # Detailed task cards
    lines += ["## 📌 Task Details", ""]
    for a in assignments:
        risk_info = risk_by_task.get(a["task_id"], {})
        lines += [
            f"### {a['task_id']}: {a['task_title']}",
            f"",
            f"**Description:** {a.get('task_description', 'N/A')}",
            f"**Required Skills:** {', '.join(a.get('required_skills', []))}",
            f"**Estimated Duration:** {a['estimated_days']} days",
            f"**Dependencies:** {', '.join(a.get('dependencies', [])) or 'None'}",
            f"**Assigned To:** {a['assigned_employee_name']}"
            + (f" ({a['assigned_role']})" if a.get("assigned_role") else ""),
            f"**Assignee Workload After:** {a.get('workload_after_assignment', 'N/A')}%",
            f"**Skill Fitness Score:** {a['fitness_score']:.1f} / 100",
            f"",
            f"**Risk Flags:**",
        ]
        for flag in risk_info.get("flags", ["✅ No significant risks"]):
            lines.append(f"- {flag}")
        lines.append("")

    lines += ["---", ""]

    # Skill gaps
    lines += ["## 🔍 Skill Gap Analysis", ""]
    if skill_gaps["has_gaps"]:
        if skill_gaps["project_level_gaps"]:
            lines.append(
                f"**Project-level gaps:** {', '.join(skill_gaps['project_level_gaps'])}"
            )
        for tg in skill_gaps["task_level_gaps"]:
            lines.append(
                f"- **{tg['task_id']} ({tg['task_title']}):** missing `{', '.join(tg['missing_skills'])}`"
            )
        lines.append("")
        lines.append("**Recommendations:**")
        for rec in skill_gaps["recommendations"]:
            lines.append(f"- {rec}")
    else:
        lines.append("✅ All required skills are fully covered by the current team.")
    lines += ["", "---", ""]

    # Workload rebalancing log
    lines += ["## ⚖️ Workload Rebalancing Log", ""]
    for entry in rebalance_log:
        lines.append(f"- {entry}")
    lines += ["", "---", ""]

    # Footer
    lines += [
        "## 🏢 Employee Workload Summary",
        "",
        "| Employee | Role | Tasks Assigned | Est. Final Workload |",
        "|----------|------|----------------|---------------------|",
    ]
    emp_tasks: dict[str, list] = {}
    for a in assignments:
        eid = a.get("assigned_employee_id")
        if eid:
            emp_tasks.setdefault(eid, []).append(a)
    for emp_id, tasks in emp_tasks.items():
        name = tasks[0]["assigned_employee_name"]
        role = tasks[0]["assigned_role"]
        final_wl = tasks[-1].get("workload_after_assignment", "?")
        lines.append(f"| {name} | {role} | {len(tasks)} | {final_wl}% |")

    lines += ["", f"*Report generated by Ethos Project Assignment Agent*"]

    return "\n".join(lines)
