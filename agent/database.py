import sqlite3
import json
import os
from pathlib import Path
from agent import config

DB_PATH = config.DATA_DIR / "ethos_data.db"

def init_db():
    """Initialize the SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT,
            skills TEXT, -- JSON array string
            experience_years REAL,
            current_workload_percent REAL,
            mail TEXT
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            project_name TEXT NOT NULL,
            description TEXT,
            required_skills TEXT, -- JSON array string
            deadline_days INTEGER,
            priority TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_employees(employees: list[dict]):
    """Save/Overwrite all employees in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM employees")
    for emp in employees:
        cursor.execute('''
            INSERT INTO employees (employee_id, name, role, skills, experience_years, current_workload_percent, mail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            emp.get("employee_id"),
            emp.get("name"),
            emp.get("role"),
            json.dumps(emp.get("skills", [])),
            emp.get("experience_years", 0),
            emp.get("current_workload_percent", 0),
            emp.get("mail")
        ))
    
    conn.commit()
    conn.close()

def get_employees():
    """Retrieve all employees from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    
    employees = []
    for row in rows:
        emp = dict(row)
        emp["skills"] = json.loads(emp["skills"])
        employees.append(emp)
        
    conn.close()
    return employees

def save_project(project: dict):
    """Save or update a project."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO projects (project_id, project_name, description, required_skills, deadline_days, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        project.get("project_id"),
        project.get("project_name"),
        project.get("description"),
        json.dumps(project.get("required_skills", [])),
        project.get("deadline_days"),
        project.get("priority")
    ))
    
    conn.commit()
    conn.close()

def get_projects():
    """Retrieve all projects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    
    projects = []
    for row in rows:
        p = dict(row)
        p["required_skills"] = json.loads(p["required_skills"])
        projects.append(p)
        
    conn.close()
    return projects

def get_skill_distribution():
    """Count occurrences of each skill across the workforce."""
    employees = get_employees()
    dist = {}
    for emp in employees:
        skills = emp.get("skills", [])
        for skill in skills:
            s = skill.strip()
            if s:
                dist[s] = dist.get(s, 0) + 1
    
    # Sort by frequency
    sorted_dist = dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))
    import logging
    logging.getLogger(__name__).info(f"Generated skill distribution: {sorted_dist}")
    return sorted_dist

if __name__ == "__main__":
    # Ensure tables are created
    init_db()
    
    # Optional migration from JSON
    try:
        json_path = config.DATA_DIR / "employees.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                save_employees(data)
                print(f"Migrated {len(data)} employees from JSON to SQLite.")
    except Exception as e:
        print(f"Migration skip or failure: {e}")

    print(f"Database initialized at {DB_PATH}")
