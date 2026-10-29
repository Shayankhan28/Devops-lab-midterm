import os
import tempfile
from fastapi.testclient import TestClient

# Temporary file create karo taake asli submissions.json affect na ho
temp_file = tempfile.NamedTemporaryFile(delete=False)
os.environ["SUBMISSIONS_FILE"] = temp_file.name

from backend.main import app

client = TestClient(app)


def test_valid_submission():
    response = client.post(
        "/submissions",
        json={
            "name": "Muhammad Shayan",
            "registration_number": "FA22-BSE-001",
            "assignment_title": "DevOps Lab",
            "submission_url": "https://github.com/test/repo"
        }
    )

    assert response.status_code == 201

    submissions = client.get("/submissions")
    assert len(submissions.json()) > 0


def test_missing_registration_number():
    response = client.post(
        "/submissions",
        json={
            "name": "Muhammad Shayan",
            "assignment_title": "DevOps Lab",
            "submission_url": "https://github.com/test/repo"
        }
    )

    assert response.status_code == 422


def test_invalid_submission_url():
    response = client.post(
        "/submissions",
        json={
            "name": "Muhammad Shayan",
            "registration_number": "FA22-BSE-001",
            "assignment_title": "DevOps Lab",
            "submission_url": "invalid-url"
        }
    )

    assert response.status_code == 422