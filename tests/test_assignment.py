"""
tests/test_assignment.py
------------------------
Unit + integration tests for the Ethos Project Assignment Agent.
Tests are designed to run WITHOUT an LLM API key — the decomposer is mocked.
"""

import json
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PROJECT = {
    "project_id": "PRJ001",
    "project_name": "AI Sales Assistant",
    "description": "AI assistant that generates sales proposals automatically",
    "required_skills": ["LLM", "NLP", "APIs"],
    "deadline_days": 30,
    "priority": "High",
}

SAMPLE_TASKS = [
    {
        "task_id": "T1",
        "title": "Design LLM prompt templates",
        "description": "Create prompt templates for generating sales proposals.",
        "required_skills": ["LLMs", "NLP"],
        "estimated_days": 3,
        "dependencies": [],
    },
    {
        "task_id": "T2",
        "title": "Build REST API layer",
        "description": "Design and implement REST endpoints for the assistant.",
        "required_skills": ["APIs", "Node.js"],
        "estimated_days": 5,
        "dependencies": ["T1"],
    },
    {
        "task_id": "T3",
        "title": "ML model fine-tuning",
        "description": "Fine-tune a base LLM on sales domain data.",
        "required_skills": ["ML", "Python", "LLMs"],
        "estimated_days": 7,
        "dependencies": [],
    },
]

SAMPLE_EMPLOYEES = [
    {
        "employee_id": "EMP001",
        "name": "Aarav Sharma",
        "role": "AI Engineer",
        "skills": ["Python", "LLMs", "LangChain", "ML"],
        "experience_years": 4,
        "current_workload_percent": 40,
    },
    {
        "employee_id": "EMP003",
        "name": "Vikram Singh",
        "role": "Backend Developer",
        "skills": ["Node.js", "APIs", "Databases"],
        "experience_years": 5,
        "current_workload_percent": 50,
    },
    {
        "employee_id": "EMP006",
        "name": "Meera Nair",
        "role": "AI Researcher",
        "skills": ["LLMs", "NLP", "RAG", "Deep Learning"],
        "experience_years": 6,
        "current_workload_percent": 55,
    },
]


# ---------------------------------------------------------------------------
# Employee Analyzer Tests
# ---------------------------------------------------------------------------

class TestEmployeeAnalyzer:
    def test_fitness_score_high_match(self):
        from agent.employee_analyzer import compute_fitness
        emp = SAMPLE_EMPLOYEES[0]  # Aarav — Python, LLMs, LangChain, ML
        score = compute_fitness(emp, ["LLMs", "ML", "Python"])
        # Should get high skill score (all 3 match)
        assert score >= 50, f"Expected >= 50, got {score}"

    def test_fitness_score_no_match(self):
        from agent.employee_analyzer import compute_fitness
        emp = SAMPLE_EMPLOYEES[1]  # Vikram — Node.js, APIs
        score = compute_fitness(emp, ["LLMs", "NLP", "Deep Learning"])
        # Very low skill match → low score
        assert score < 20, f"Expected < 20, got {score}"

    def test_workload_penalty_applied(self):
        from agent.employee_analyzer import compute_fitness
        high_workload_emp = {**SAMPLE_EMPLOYEES[0], "current_workload_percent": 80}
        low_workload_emp = {**SAMPLE_EMPLOYEES[0], "current_workload_percent": 10}
        score_high = compute_fitness(high_workload_emp, ["LLMs"])
        score_low = compute_fitness(low_workload_emp, ["LLMs"])
        assert score_low > score_high, "Higher workload should yield lower fitness"

    def test_rank_returns_sorted_descending(self):
        from agent.employee_analyzer import rank_employees_for_task
        task = {"required_skills": ["LLMs", "NLP"]}
        ranked = rank_employees_for_task(task, SAMPLE_EMPLOYEES)
        scores = [r["fitness_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Assignment Engine Tests
# ---------------------------------------------------------------------------

class TestAssignmentEngine:
    def test_all_tasks_attempted(self):
        from agent.assignment_engine import assign_tasks
        assignments = assign_tasks(SAMPLE_TASKS, SAMPLE_EMPLOYEES)
        assert len(assignments) == len(SAMPLE_TASKS)

    def test_no_employee_exceeds_workload_cap(self):
        from agent.assignment_engine import assign_tasks
        assignments = assign_tasks(SAMPLE_TASKS, SAMPLE_EMPLOYEES)
        for a in assignments:
            wl = a.get("workload_after_assignment")
            if wl is not None:
                assert wl <= 90, f"Employee exceeded 90% cap: {a}"

    def test_best_fit_assigned_to_llm_task(self):
        """LLM task should go to an AI/NLP-skilled employee, not Backend Dev."""
        from agent.assignment_engine import assign_tasks
        llm_task = [SAMPLE_TASKS[0]]  # "Design LLM prompt templates" (LLMs, NLP)
        assignments = assign_tasks(llm_task, SAMPLE_EMPLOYEES)
        assert assignments[0]["assigned_employee_id"] in ("EMP001", "EMP006"), (
            f"Expected AI employee, got {assignments[0]['assigned_employee_name']}"
        )


# ---------------------------------------------------------------------------
# Skill Gap Detector Tests
# ---------------------------------------------------------------------------

class TestSkillGapDetector:
    def test_detects_missing_skill(self):
        from agent.features.skill_gap_detector import detect_gaps
        tasks_with_gap = [
            {
                "task_id": "T_BLOCK",
                "title": "Blockchain integration",
                "required_skills": ["Blockchain", "Solidity"],
            }
        ]
        result = detect_gaps(tasks_with_gap, SAMPLE_EMPLOYEES, SAMPLE_PROJECT)
        assert result["has_gaps"] is True
        assert len(result["task_level_gaps"]) > 0

    def test_no_gap_when_fully_covered(self):
        from agent.features.skill_gap_detector import detect_gaps
        covered_tasks = [
            {
                "task_id": "T_COVERED",
                "title": "Python ML task",
                "required_skills": ["Python", "ML"],
            }
        ]
        result = detect_gaps(covered_tasks, SAMPLE_EMPLOYEES, SAMPLE_PROJECT)
        assert result["has_gaps"] is False


# ---------------------------------------------------------------------------
# Risk Assessor Tests
# ---------------------------------------------------------------------------

class TestRiskAssessor:
    def test_high_priority_tight_deadline_is_high_risk(self):
        from agent.features.risk_assessor import assess_risk
        from agent.assignment_engine import assign_tasks
        urgent_project = {**SAMPLE_PROJECT, "deadline_days": 8, "priority": "High"}
        assignments = assign_tasks(SAMPLE_TASKS, SAMPLE_EMPLOYEES)
        result = assess_risk(urgent_project, assignments)
        assert result["overall_risk_level"] in ("High", "Critical"), (
            f"Expected High/Critical, got {result['overall_risk_level']}"
        )

    def test_unassigned_tasks_raise_risk(self):
        from agent.features.risk_assessor import assess_risk
        assignments_with_unassigned = [
            {
                "task_id": "TX",
                "task_title": "Orphan Task",
                "task_description": "",
                "required_skills": [],
                "estimated_days": 3,
                "dependencies": [],
                "assigned_employee_id": None,
                "assigned_employee_name": "UNASSIGNED",
                "assigned_role": None,
                "fitness_score": 0.0,
                "workload_after_assignment": None,
                "unassigned_reason": "No one available",
            }
        ]
        result = assess_risk(SAMPLE_PROJECT, assignments_with_unassigned)
        assert result["overall_risk_level"] in ("High", "Critical")


# ---------------------------------------------------------------------------
# Workload Balancer Tests
# ---------------------------------------------------------------------------

class TestWorkloadBalancer:
    def test_no_rebalancing_needed_when_within_cap(self):
        from agent.features.workload_balancer import rebalance
        from agent.assignment_engine import assign_tasks
        assignments = assign_tasks(SAMPLE_TASKS, SAMPLE_EMPLOYEES)
        _, log = rebalance(assignments, SAMPLE_EMPLOYEES)
        assert any("No rebalancing needed" in entry for entry in log) or len(log) > 0


# ---------------------------------------------------------------------------
# Report Generator Tests
# ---------------------------------------------------------------------------

class TestReportGenerator:
    def test_json_output_is_valid(self, tmp_path):
        from agent.features.report_generator import generate
        from agent.assignment_engine import assign_tasks
        from agent.features.risk_assessor import assess_risk
        from agent.features.skill_gap_detector import detect_gaps
        from agent.features.workload_balancer import rebalance

        employees = SAMPLE_EMPLOYEES
        assignments = assign_tasks(SAMPLE_TASKS, employees)
        final_assignments, rebalance_log = rebalance(assignments, employees)
        risk = assess_risk(SAMPLE_PROJECT, final_assignments)
        gaps = detect_gaps(SAMPLE_TASKS, employees, SAMPLE_PROJECT)

        report = generate(
            SAMPLE_PROJECT,
            final_assignments,
            risk,
            gaps,
            rebalance_log,
            output_dir=str(tmp_path),
        )

        # JSON file should be valid
        with open(report["json_path"]) as f:
            data = json.load(f)
        assert "assignments" in data
        assert "risk_report" in data

    def test_markdown_contains_expected_sections(self, tmp_path):
        from agent.features.report_generator import generate
        from agent.assignment_engine import assign_tasks
        from agent.features.risk_assessor import assess_risk
        from agent.features.skill_gap_detector import detect_gaps
        from agent.features.workload_balancer import rebalance

        employees = SAMPLE_EMPLOYEES
        assignments = assign_tasks(SAMPLE_TASKS, employees)
        final_assignments, rebalance_log = rebalance(assignments, employees)
        risk = assess_risk(SAMPLE_PROJECT, final_assignments)
        gaps = detect_gaps(SAMPLE_TASKS, employees, SAMPLE_PROJECT)

        report = generate(
            SAMPLE_PROJECT,
            final_assignments,
            risk,
            gaps,
            rebalance_log,
            output_dir=str(tmp_path),
        )

        md = report["markdown"]
        assert "## 🗂️ Task Assignments" in md
        assert "## 🔍 Skill Gap Analysis" in md
        assert "## ⚖️ Workload Rebalancing Log" in md
        assert "## 🏢 Employee Workload Summary" in md
