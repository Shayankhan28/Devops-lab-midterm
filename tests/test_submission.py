import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Root directory ko path mein add karne ke liye

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# 1. Valid Submission Test
def test_valid_submission(tmp_path, monkeypatch):
    test_file = tmp_path / "test_submissions.json"
    monkeypatch.setenv("SUBMISSIONS_FILE", str(test_file))

    payload = {
        "name": "Ali Hassan",
        "registration_number": "FA20-BSE-001",
        "assignment_title": "DevOps Lab Midterm",
        "submission_url": "https://github.com/example/repo"
    }
    response = client.post("/submissions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Submission saved successfully"
    assert data["submission"]["name"] == "Ali Hassan"

# 2. Missing Registration Number Test
def test_missing_registration_number(tmp_path, monkeypatch):
    test_file = tmp_path / "test_submissions.json"
    monkeypatch.setenv("SUBMISSIONS_FILE", str(test_file))

    payload = {
        "name": "Ali Hassan",
        "registration_number": "   ",  # Blank/Empty
        "assignment_title": "DevOps Lab Midterm",
        "submission_url": "https://github.com/example/repo"
    }
    response = client.post("/submissions", json=payload)
    assert response.status_code == 422
    assert "Registration number is required" in response.json()["errors"]

# 3. Invalid Submission URL Test
def test_invalid_submission_url(tmp_path, monkeypatch):
    test_file = tmp_path / "test_submissions.json"
    monkeypatch.setenv("SUBMISSIONS_FILE", str(test_file))

    payload = {
        "name": "Ali Hassan",
        "registration_number": "FA20-BSE-001",
        "assignment_title": "DevOps Lab Midterm",
        "submission_url": "invalid-url-format"
    }
    response = client.post("/submissions", json=payload)
    assert response.status_code == 422
    assert "Submission URL must be a valid http or https URL" in response.json()["errors"]