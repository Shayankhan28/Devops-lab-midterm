import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

VALID_SUBMISSION = {
    "name": "Muhammad Shayan Khan",
    "registration_number": "FA22-BSE-154",
    "assignment_title": "DevOps Lab Midterm",
    "submission_url": "https://github.com/test/repo",
}


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    # Har test ke liye nayi khali file, asli submissions.json safe rehti hai
    data_file = tmp_path / "submissions.json"
    data_file.write_text("[]", encoding="utf-8")
    monkeypatch.setenv("SUBMISSIONS_FILE", str(data_file))


def test_valid_submission_is_saved_and_listed():
    response = client.post("/submissions", json=VALID_SUBMISSION)
    assert response.status_code == 201
    assert response.json()["message"] == "Submission saved successfully"

    submissions = client.get("/submissions").json()
    assert len(submissions) == 1
    assert submissions[0]["registration_number"] == "FA22-BSE-154"
    assert submissions[0]["submission_url"] == "https://github.com/test/repo"


def test_missing_registration_number_is_rejected():
    data = dict(VALID_SUBMISSION)
    del data["registration_number"]

    response = client.post("/submissions", json=data)
    assert response.status_code == 422
    assert "Registration number is required" in response.json()["errors"]

    assert client.get("/submissions").json() == []


def test_invalid_url_is_rejected_and_not_saved():
    data = dict(VALID_SUBMISSION)
    data["submission_url"] = "not-a-valid-url"

    response = client.post("/submissions", json=data)
    assert response.status_code == 422
    assert "Submission URL must be a valid http or https URL" in response.json()["errors"]

    assert client.get("/submissions").json() == []
