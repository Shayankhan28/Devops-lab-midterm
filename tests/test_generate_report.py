from scripts.generate_report import build_report


def test_build_report_includes_counts_results_metadata_and_failure_messages(
    tmp_path, monkeypatch
):
    results_file = tmp_path / "test-results.xml"
    results_file.write_text(
        """\
<testsuites tests="3" failures="1" errors="0" skipped="1">
  <testsuite name="pytest" tests="3" failures="1" errors="0" skipped="1">
    <testcase classname="tests.test_submission" name="test_valid_submission" />
    <testcase classname="tests.test_submission" name="test_invalid_submission">
      <failure message="assertion failed">Expected 201, got 422</failure>
    </testcase>
    <testcase classname="tests.test_submission" name="test_skipped">
      <skipped message="not applicable" />
    </testcase>
  </testsuite>
</testsuites>
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repository")
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_RUN_ID", "456")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")

    report = build_report(results_file)

    assert report["repository_name"] == "owner/repository"
    assert report["branch"] == "main"
    assert report["commit_sha"] == "abc123"
    assert report["pipeline_run_id"] == "456.2"
    assert report["execution_timestamp"]
    assert report["total_tests"] == 3
    assert report["passed_tests"] == 1
    assert report["failed_tests"] == 1
    assert report["overall_status"] == "FAILED"
    assert report["tests"] == [
        {
            "name": "tests.test_submission::test_valid_submission",
            "result": "passed",
            "failure_message": "",
        },
        {
            "name": "tests.test_submission::test_invalid_submission",
            "result": "failed",
            "failure_message": "assertion failed\nExpected 201, got 422",
        },
        {
            "name": "tests.test_submission::test_skipped",
            "result": "skipped",
            "failure_message": "not applicable",
        },
    ]


def test_build_report_marks_empty_test_run_as_failed(tmp_path):
    results_file = tmp_path / "test-results.xml"
    results_file.write_text(
        '<testsuites tests="0"><testsuite name="pytest" tests="0" /></testsuites>',
        encoding="utf-8",
    )

    report = build_report(results_file)

    assert report["total_tests"] == 0
    assert report["overall_status"] == "FAILED"
