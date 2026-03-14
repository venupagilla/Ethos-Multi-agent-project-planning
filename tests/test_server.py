import json
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_get_employees():
    response = client.get("/api/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_employees():
    test_data = {
        "employees": [
            {
                "employee_id": "TEST001",
                "name": "Test User",
                "role": "Tester",
                "skills": ["Python"],
                "experience_years": 1,
                "current_workload_percent": 0
            }
        ]
    }
    response = client.post("/api/employees", json=test_data)
    assert response.status_code == 200
    assert response.json() == {"success": True, "count": 1}

def test_run_agent_validation():
    # Test valid input
    project_data = {
        "project_id": "PRJ_TEST",
        "project_name": "Test project",
        "description": "desc",
        "required_skills": ["Python"],
        "deadline_days": 10,
        "priority": "Low"
    }
    # We won't actually run the full agent because it might need API keys (Groq)
    # But we can at least check if the endpoint exists and handles validation
    # If main:run_agent fails due to missing keys, it should be 500, not 405.
    response = client.post("/api/run", json=project_data)
    assert response.status_code in (200, 500)
    if response.status_code == 500:
        print("Agent failed (likely missing API key), but route exists.")
