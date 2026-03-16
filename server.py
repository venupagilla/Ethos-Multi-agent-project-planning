"""
server.py
---------
FastAPI server exposing the Ethos Project Assignment Agent via HTTP.

Endpoints:
  GET  /                        -> Serves the frontend HTML
  GET  /api/projects            -> Returns sample projects from data/projects.json
  GET  /api/employees           -> Returns employee pool
  POST /api/employees           -> Uploads/overwrites the employee pool
  POST /api/run                 -> Runs the full agent pipeline, returns JSON result
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.config import DATA_DIR, FRONTEND_DIR
from agent.planner_agent import run_pipeline as _run_pipeline # Corrected import name if it was _run_agent
from main import run_agent as _run_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
FRONTEND_PATH = FRONTEND_DIR / "index.html"


from agent.models import ProjectInput, EmployeesInput


# ---------------------------------------------------------------------------
# Lifespan — replaces the deprecated @app.on_event("startup")
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    logger.info("=== Registered routes ===")
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path    = getattr(route, "path", None)
        if methods and path:
            logger.info("  %s  %s", sorted(methods), path)
    logger.info("=========================")
    yield
    # --- shutdown (add cleanup here if needed) ---


# ---------------------------------------------------------------------------
# App + middleware
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Ethos Project Assignment Agent",
    version="4.0",
    lifespan=lifespan,          # modern replacement for on_event
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML page."""
    return FRONTEND_PATH.read_text(encoding="utf-8")


from agent import database

@app.get("/api/projects")
async def get_projects():
    """Return all projects from database, fallback to JSON."""
    projects = database.get_projects()
    if not projects:
        path = DATA_DIR / "projects.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                projects = json.load(f)
                for p in projects:
                    database.save_project(p)
    return projects


@app.api_route("/api/employees", methods=["GET", "POST"])
async def employees_endpoint(request: Request):
    """
    GET  -> return the current employee pool from DB.
    POST -> accept a JSON body {"employees": [...]} and save to DB.
    """
    if request.method == "GET":
        employees = database.get_employees()
        if not employees:
            # Fallback to JSON if DB is empty
            path = DATA_DIR / "employees.json"
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    employees = json.load(f)
                    database.save_employees(employees)
        return JSONResponse(content=employees)

    # ---- POST ----
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="Request body must be valid JSON.")

    if "employees" not in body or not isinstance(body["employees"], list):
        raise HTTPException(
            status_code=422,
            detail='Body must be {"employees": [...]}',
        )

    employees = body["employees"]
    logger.info("POST /api/employees -- saving %d employees to SQLite", len(employees))

    try:
        database.save_employees(employees)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save employees to DB: {e}")

    return JSONResponse(content={"success": True, "count": len(employees)})


@app.post("/api/employees/csv")
async def upload_employees_csv(file: UploadFile = File(...)):
    """
    Accept a CSV file upload and import employees into the DB.
    Expected columns (case-insensitive):
      employee_id, name, role, department, skills,
      experience_years, current_workload_percent, email
    'skills' can be a JSON array string or a comma-separated list within quotes.
    """
    import csv
    import io

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Only .csv files are accepted.")

    raw = await file.read()
    try:
        content = raw.decode("utf-8-sig")  # handle BOM from Excel-saved CSVs
    except UnicodeDecodeError:
        content = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(content))
    # Normalize header names: strip whitespace and lower-case
    reader.fieldnames = [h.strip().lower() for h in (reader.fieldnames or [])]

    employees = []
    for i, row in enumerate(reader, start=2):  # row 1 = header
        try:
            # Parse skills — could be a JSON array or semicolon/comma separated
            raw_skills = row.get("skills", "").strip()
            if raw_skills.startswith("["):
                import json as _json
                skills = _json.loads(raw_skills)
            else:
                # Support semicolon or pipe delimiters in addition to commas
                delimiter = ";" if ";" in raw_skills else ("|" if "|" in raw_skills else ",")
                skills = [s.strip().strip('"').strip("'") for s in raw_skills.split(delimiter) if s.strip()]

            employees.append({
                "employee_id":              row.get("employee_id", f"EMP{i:03d}").strip(),
                "name":                     row.get("name", "Unknown").strip(),
                "role":                     row.get("role", "").strip(),
                "department":               row.get("department", "").strip(),
                "skills":                   skills,
                "experience_years":         float(row.get("experience_years", 0) or 0),
                "current_workload_percent": float(row.get("current_workload_percent", 0) or 0),
                "email":                    row.get("email", "").strip() or "tagoresrisai@gmail.com",
            })
        except Exception as exc:
            logger.warning(f"Skipping CSV row {i}: {exc}")

    if not employees:
        raise HTTPException(status_code=422, detail="No valid employee rows found in CSV.")

    logger.info("POST /api/employees/csv -- importing %d employees from CSV", len(employees))
    try:
        database.save_employees(employees)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save employees: {e}")

    return JSONResponse(content={"success": True, "count": len(employees)})

@app.post("/api/run")
async def run_agent(project: ProjectInput):
    """Run the full planning and assignment pipeline."""
    try:
        result = _run_agent(
            project.model_dump(),
            output_dir=str(BASE_DIR / "output"),
            verbose=False,
        )
        return {
            "success": True,
            "tasks": result.get("tasks", []),
            "assignments": result.get("assignments", []),
            "risk_report": result.get("risk_report", {}),
            "skill_gaps": result.get("skill_gaps", {}),
            "rebalance_log": result.get("rebalance_log", []),
            "json_path": result.get("json_path"),
            "markdown_path": result.get("markdown_path"),
            "markdown": result.get("markdown", ""),
        }
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Pipeline execution failed",
                "message": str(e)
            }
        )


@app.get("/api/analytics")
async def get_analytics():
    """Return workforce skill analytics."""
    try:
        dist = database.get_skill_distribution()
        logger.info(f"Analytics: {dist}")
        return dist
    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag-chat")
async def rag_chat(request: Request):
    """Chat with project documentation using RAG."""
    body = await request.json()
    project_id = body.get("project_id")
    query = body.get("query")
    
    if not project_id or not query:
        raise HTTPException(status_code=400, detail="Missing project_id or query")
    
    try:
        from agent.tools.vector_service import query_project_data
        # Run sync function in thread to avoid blocking
        response = await asyncio.to_thread(query_project_data, project_id, query)
        return {"response": response}
    except Exception as e:
        logger.error(f"RAG Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


import asyncio

def _send_emails_sync(emails):
    from agent.tools.mcp_client import MCPClient
    
    # Initialize the MCP Client
    gmail = MCPClient(
        "gmail",
        "npx.cmd",
        ["-y", "@gongrzhe/server-gmail-autoauth-mcp"]
    )
    
    init_res = gmail.initialize()
    logger.info(f"Gmail MCP init: {init_res}")
    
    success_count = 0
    for email_task in emails:
        to_addr = email_task.get("email")
        body_text = email_task.get("body", "")
        subject = email_task.get("subject", "You have a new project assignment")
        
        if not to_addr:
            continue

        result = gmail.call_tool(
            "send_email",
            {
                "to": [to_addr],
                "subject": subject,
                "body": body_text
            }
        )
        success_count += 1
        logger.info(f"Email sent to {to_addr}. Result: {result}")
    return success_count


@app.post("/api/send-emails")
async def send_emails_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="Request body must be valid JSON.")
    
    logger.info(f"Received request for /api/send-emails: {body}")
    emails = body.get("emails", [])
    if not emails:
        logger.info("No emails to send.")
        return JSONResponse(content={"success": True, "count": 0, "message": "No emails to send"})

    logger.info(f"Sending {len(emails)} emails via Gmail MCP...")
    try:
        success_count = await asyncio.to_thread(_send_emails_sync, emails)
        return JSONResponse(content={"success": True, "count": success_count})
    except Exception as e:
        logger.error(f"Error sending MCP emails: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Mount static LAST so it doesn't shadow API routes
os.makedirs("output", exist_ok=True)
app.mount("/static", StaticFiles(directory="output"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)