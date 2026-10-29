from scripts.send_email import create_email


def test_email_contains_run_summary_and_individual_failures():
    report = {
        "repository_name": "owner/repository",
        "branch": "main",
        "commit_sha": "abc123",
        "pipeline_run_id": "456.1",
        "execution_timestamp": "2026-10-30T00:00:00+00:00",
        "overall_status": "FAILED",
        "total_tests": 2,
        "passed_tests": 1,
        "failed_tests": 1,
        "tests": [
            {
                "name": "tests.test_submission::test_valid",
                "result": "passed",
                "failure_message": "",
            },
            {
                "name": "tests.test_submission::test_invalid_url",
                "result": "failed",
                "failure_message": "Expected 422, got 201",
            },
        ],
    }

    message = create_email(report, "sender@example.com", "recipient@example.com")
    body = message.get_content()

    assert message["To"] == "recipient@example.com"
    assert "owner/repository" in body
    assert "Commit: abc123" in body
    assert "Pipeline run: 456.1" in body
    assert "2 total, 1 passed, 1 failed" in body
    assert "FAILED: tests.test_submission::test_invalid_url" in body
    assert "Failure: Expected 422, got 201" in body
