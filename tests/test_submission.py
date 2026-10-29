import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    submissions_file = tmp_path / "submissions.json"
    monkeypatch.setenv("SUBMISSIONS_FILE", str(submissions_file))
    return TestClient(app)


def test_valid_submission_is_saved_and_listed(client):
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
    assert any(
        submission["registration_number"] == "FA22-BSE-001"
        for submission in submissions.json()
    )


def test_missing_registration_number_is_rejected_with_message(client):
    response = client.post(
        "/submissions",
        json={
            "name": "Muhammad Shayan",
            "assignment_title": "DevOps Lab",
            "submission_url": "https://github.com/test/repo"
        }
    )

    assert response.status_code == 422
    assert "Registration number is required" in response.json()["errors"]


def test_invalid_submission_url_is_rejected_and_not_saved(client):
    submissions_before = client.get("/submissions").json()
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
    assert client.get("/submissions").json() == submissions_before