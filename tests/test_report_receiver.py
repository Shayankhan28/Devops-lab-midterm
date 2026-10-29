import json

from fastapi.testclient import TestClient

import receiver.receiver as report_receiver


def test_report_receiver_requires_token(monkeypatch, tmp_path):
    monkeypatch.delenv("REPORT_TOKEN", raising=False)
    monkeypatch.setattr(report_receiver, "REPORT_FILE", tmp_path / "test-report.json")

    response = TestClient(report_receiver.app).post("/report", json={})

    assert response.status_code == 503


def test_report_receiver_rejects_invalid_token(monkeypatch, tmp_path):
    monkeypatch.setenv("REPORT_TOKEN", "expected-token")
    monkeypatch.setattr(report_receiver, "REPORT_FILE", tmp_path / "test-report.json")

    response = TestClient(report_receiver.app).post(
        "/report",
        json={},
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert not report_receiver.REPORT_FILE.exists()


def test_report_receiver_saves_report(monkeypatch, tmp_path):
    monkeypatch.setenv("REPORT_TOKEN", "expected-token")
    report_file = tmp_path / "test-report.json"
    monkeypatch.setattr(report_receiver, "REPORT_FILE", report_file)
    report = {
        "overall_status": "PASSED",
        "total_tests": 1,
        "passed_tests": 1,
        "failed_tests": 0,
        "tests": [{"name": "test_example", "result": "passed", "failure_message": ""}],
    }

    response = TestClient(report_receiver.app).post(
        "/report",
        json=report,
        headers={"Authorization": "Bearer expected-token"},
    )

    assert response.status_code == 200
    assert json.loads(report_file.read_text(encoding="utf-8")) == report
