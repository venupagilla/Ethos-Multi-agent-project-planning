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

from fastapi import FastAPI, HTTPException, Request
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


# Mount static LAST so it doesn't shadow API routes
os.makedirs("output", exist_ok=True)
app.mount("/static", StaticFiles(directory="output"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)