"""
server.py
---------
FastAPI server exposing the NeuraX Project Assignment Agent via HTTP.

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
from pydantic import BaseModel
from dotenv import load_dotenv

from main import run_agent as _run_agent

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_PATH = BASE_DIR / "frontend" / "index.html"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProjectInput(BaseModel):
    project_id: str
    project_name: str
    description: str
    required_skills: list[str]
    deadline_days: int
    priority: str


class EmployeesInput(BaseModel):
    employees: list[dict]


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
    title="NeuraX Project Assignment Agent",
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


@app.get("/api/projects")
async def get_projects():
    """Return all sample projects."""
    path = DATA_DIR / "projects.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="projects.json not found.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# app.api_route with an explicit methods list is the most reliable way to
# register GET and POST on the same path. It avoids the decorator-ordering
# quirk that caused the POST to be silently dropped in previous versions.
@app.api_route("/api/employees", methods=["GET", "POST"])
async def employees_endpoint(request: Request):
    """
    GET  -> return the current employee pool.
    POST -> accept a JSON body {"employees": [...]} and overwrite the pool.
    """
    if request.method == "GET":
        path = DATA_DIR / "employees.json"
        if not path.exists():
            return JSONResponse(content=[])
        with open(path, encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))

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
    logger.info("POST /api/employees -- saving %d employees", len(employees))

    try:
        with open(DATA_DIR / "employees.json", "w", encoding="utf-8") as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
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
            "tasks": result["tasks"],
            "assignments": result["assignments"],
            "risk_report": result["risk_report"],
            "skill_gaps": result["skill_gaps"],
            "rebalance_log": result["rebalance_log"],
            "json_path": result["json_path"],
            "markdown_path": result["markdown_path"],
            "markdown": result["markdown"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)