import os
from datetime import datetime, timedelta

import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Config — webhook URLs from environment variables (fallback to defaults)
# ---------------------------------------------------------------------------

ASSIGNMENT_WEBHOOK_URL = os.environ.get(
    "ASSIGNMENT_WEBHOOK_URL",
    "https://hook.eu1.make.com/bcmh8kqm46gbz1ub1lxeg4up4uqyqisv",
)
EMAIL_WEBHOOK_URL = os.environ.get(
    "EMAIL_WEBHOOK_URL",
    "https://hook.eu1.make.com/4du237s6afj5ta7yjodoyar08e4cofp7",
)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(page_title="NeuraX — Project Assignment Agent", layout="wide")
st.title("🧠 NeuraX — Project Assignment Agent v4.0")


# ---------------------------------------------------------------------------
# Sidebar — employee upload + project inputs
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Employee Data Upload")
    st.markdown(
        "Upload an Excel or CSV file with columns: "
        "employee_id, name, role, skills, experience_years, current_workload_percent, mail"
    )
    employee_file = st.file_uploader("Upload Employee Excel or CSV", type=["xlsx", "csv"])
    employee_df = None
    if employee_file is not None:
        try:
            if employee_file.name.endswith(".csv"):
                employee_df = pd.read_csv(employee_file)
            else:
                employee_df = pd.read_excel(employee_file, engine="openpyxl")
            st.success("Employee data loaded!")
            st.dataframe(employee_df)
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.header("Project Details")
    project_id = st.text_input("Project ID", "PRJ001")
    project_name = st.text_input("Project Name", "AI Sales Assistant")
    description = st.text_area("Description", "Describe what the project does...")
    required_skills = st.text_input("Required Skills (comma separated)", "LLMs, Python, FastAPI")
    deadline_days = st.number_input("Deadline (days)", min_value=1, value=30)
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    run_agent = st.button("🚀 Run Agent")


# ---------------------------------------------------------------------------
# Main — agent run
# ---------------------------------------------------------------------------

if run_agent:
    # Guard: employee file must be uploaded before running
    if employee_df is None:
        st.warning(
            "No employee data uploaded. "
            "Please upload an Excel or CSV file in the sidebar before running the agent."
        )
        st.stop()

    skills = [s.strip() for s in required_skills.split(",") if s.strip()]
    project = {
        "project_id": project_id,
        "project_name": project_name,
        "description": description,
        "required_skills": skills,
        "deadline_days": deadline_days,
        "priority": priority,
    }

    with st.spinner("Running agent..."):
        try:
            # ----------------------------------------------------------------
            # 1. Parse and upload employee data
            # ----------------------------------------------------------------
            if "skills" in employee_df.columns:
                def split_skills(val):
                    if pd.isna(val):
                        return []
                    if ";" in str(val):
                        return [s.strip() for s in str(val).split(";") if s.strip()]
                    return [s.strip() for s in str(val).split(",") if s.strip()]

                employee_df["skills"] = employee_df["skills"].apply(split_skills)

            employees = employee_df.to_dict(orient="records")

            # Build employee_id -> {email, name} lookup for later use
            employee_email_map = {}
            for emp in employees:
                emp_id = str(emp.get("employee_id", "")).strip()
                email  = str(emp.get("mail", "")).strip()
                name   = str(emp.get("name", "")).strip()
                if emp_id and email:
                    employee_email_map[emp_id] = {"email": email, "name": name}

            try:
                emp_res = requests.post(
                    f"{BACKEND_URL}/api/employees",
                    json={"employees": employees},
                    timeout=10,
                )
            except Exception as req_exc:
                st.error(f"Network error while uploading employee data: {req_exc}")
                st.stop()

            if emp_res.status_code != 200:
                st.error(f"Failed to upload employee data: HTTP {emp_res.status_code}")
                st.write("**Request payload sent:**")
                st.json({"employees": employees})
                st.write("**Backend response:**")
                st.text(emp_res.text)
                st.write("**Backend response headers:**")
                st.json(dict(emp_res.headers))
                st.stop()

            st.info(f"Employee data uploaded ({len(employees)} employees).")

            # ----------------------------------------------------------------
            # 2. Run agent pipeline
            # ----------------------------------------------------------------
            try:
                res = requests.post(
                    f"{BACKEND_URL}/api/run",
                    json=project,
                    timeout=60,
                )
            except Exception as req_exc:
                st.error(f"Network error while calling /api/run: {req_exc}")
                st.stop()

            if res.status_code != 200:
                detail = res.json().get("detail", res.text)
                st.error(f"Agent pipeline failed (HTTP {res.status_code}): {detail}")
                st.stop()

            data = res.json()
            st.success("Assignment complete!")

            # ----------------------------------------------------------------
            # 3. Build webhook payloads
            # ----------------------------------------------------------------
            today = datetime.now().date()
            employees_payload = []
            email_payload = []

            for a in data["assignments"]:
                if not a["assigned_employee_id"]:
                    continue

                try:
                    est_days = int(a["estimated_days"])
                except (ValueError, TypeError) as parse_err:
                    st.warning(
                        f"Could not parse estimated_days for task "
                        f"{a.get('task_id')}: {parse_err}. Defaulting to 0."
                    )
                    est_days = 0

                deadline = today + timedelta(days=est_days)
                employees_payload.append({
                    "employee_id": a["assigned_employee_id"],
                    "task":        a["task_title"],
                    "deadline":    str(deadline),
                })

                emp_id   = str(a["assigned_employee_id"])
                emp_info = employee_email_map.get(emp_id)
                if emp_info and emp_info["email"]:
                    user_name = emp_info["name"] or emp_id
                    email_payload.append({
                        "email": emp_info["email"],
                        "body":  f"Hello {user_name}, here is your project update",
                    })

            # ----------------------------------------------------------------
            # 4. Send assignment webhook
            # ----------------------------------------------------------------
            try:
                wh_res = requests.post(
                    ASSIGNMENT_WEBHOOK_URL,
                    json={"employees": employees_payload},
                    timeout=10,
                )
                if wh_res.status_code == 200:
                    st.info("Assignment webhook sent successfully.")
                else:
                    st.warning(f"Assignment webhook failed: HTTP {wh_res.status_code}")
            except Exception as wh_err:
                st.warning(f"Assignment webhook error: {wh_err}")

            # ----------------------------------------------------------------
            # 5. Send email webhook
            # ----------------------------------------------------------------
            if email_payload:
                try:
                    email_res = requests.post(
                        EMAIL_WEBHOOK_URL,
                        json={"emails": email_payload},
                        timeout=10,
                    )
                    if email_res.status_code == 200:
                        st.info("Email webhook sent successfully.")
                    else:
                        st.warning(f"Email webhook failed: HTTP {email_res.status_code}")
                except Exception as email_err:
                    st.warning(f"Email webhook error: {email_err}")

            # ----------------------------------------------------------------
            # 6. UI — project summary metrics
            # ----------------------------------------------------------------
            st.subheader(f"📋 {project_name}")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Tasks",      len(data["assignments"]))
            col2.metric("Assigned",   sum(1 for a in data["assignments"] if a["assigned_employee_id"]))
            col3.metric("Deadline",   f"{deadline_days}d")
            col4.metric("Priority",   priority)
            col5.metric("Risk Score", data["risk_report"]["overall_risk_score"])
            st.info(data["risk_report"]["risk_summary"])

            # ----------------------------------------------------------------
            # 7. Assignment table
            # ----------------------------------------------------------------
            st.markdown("### 📊 Assignments")
            st.dataframe([
                {
                    "Task ID":    a["task_id"],
                    "Task":       a["task_title"],
                    "Assigned To": a["assigned_employee_name"],
                    "Fit Score":  a["fitness_score"],
                    "Est. Days":  a["estimated_days"],
                    "WL After":   a.get("workload_after_assignment", "—"),
                }
                for a in data["assignments"]
            ])

            # ----------------------------------------------------------------
            # 8. Risk flags
            # ----------------------------------------------------------------
            st.markdown("### 🔴 Risk Flags")
            for tr in data["risk_report"]["task_risks"]:
                st.write(f"**{tr['task_id']}** {tr['task_title']} — {tr['risk_level']}")
                for flag in tr["flags"]:
                    st.write(f"- {flag}")

            # ----------------------------------------------------------------
            # 9. Skill gaps
            # ----------------------------------------------------------------
            st.markdown("### 🔍 Skill Gaps")
            if not data["skill_gaps"]["has_gaps"]:
                st.success("All required skills are fully covered. No gaps detected.")
            else:
                for rec in data["skill_gaps"]["recommendations"]:
                    st.warning(rec)
                for tg in data["skill_gaps"]["task_level_gaps"]:
                    st.write(
                        f"**{tg['task_id']}** {tg['task_title']} — "
                        f"missing: {', '.join(tg['missing_skills'])}"
                    )

            # ----------------------------------------------------------------
            # 10. Rebalancing log
            # ----------------------------------------------------------------
            st.markdown("### ⚖️ Rebalancing Log")
            for log_line in data["rebalance_log"]:
                st.code(log_line)

            # ----------------------------------------------------------------
            # 11. Markdown report
            # ----------------------------------------------------------------
            st.markdown("### 📄 Report")
            st.code(data["markdown"], language="markdown")

            # ----------------------------------------------------------------
            # 12. Employee workloads after assignment
            # ----------------------------------------------------------------
            st.markdown("### 🏢 Employee Workloads After Assignment")
            emp_map = {}
            for a in data["assignments"]:
                if not a["assigned_employee_id"]:
                    continue
                emp = emp_map.setdefault(
                    a["assigned_employee_id"],
                    {
                        "name":    a["assigned_employee_name"],
                        "role":    a["assigned_role"],
                        "tasks":   [],
                        "finalWL": a.get("workload_after_assignment", 0),
                    },
                )
                emp["tasks"].append(a["task_title"])
                emp["finalWL"] = a.get("workload_after_assignment", 0)

            for emp in emp_map.values():
                st.write(f"**{emp['name']}** ({emp['role']}) — {emp['finalWL']}% workload")
                st.write(", ".join(emp["tasks"]))

        except Exception as e:
            st.error(f"Unexpected error: {e}")

else:
    st.info("Fill in project details in the sidebar and click 'Run Agent' to start.")