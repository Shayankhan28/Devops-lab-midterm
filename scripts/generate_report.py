import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests


def build_report(results_file: Path) -> dict:
    root = ET.parse(results_file).getroot()
    test_results = []

    for case in root.iter("testcase"):
        failures = list(case.findall("failure")) + list(case.findall("error"))
        skipped = case.find("skipped")

        if failures:
            result = "failed"
            failure_message = "\n".join(
                "\n".join(
                    part
                    for part in (
                        failure.get("message", "").strip(),
                        (failure.text or "").strip(),
                    )
                    if part
                )
                for failure in failures
            )
        elif skipped is not None:
            result = "skipped"
            failure_message = skipped.get("message", "").strip() or (
                skipped.text or ""
            ).strip()
        else:
            result = "passed"
            failure_message = ""

        classname = case.get("classname", "").strip()
        name = case.get("name", "unknown").strip()
        test_results.append(
            {
                "name": f"{classname}::{name}" if classname else name,
                "result": result,
                "failure_message": failure_message,
            }
        )

    passed = sum(test["result"] == "passed" for test in test_results)
    failed = sum(test["result"] == "failed" for test in test_results)
    run_id = os.getenv("GITHUB_RUN_ID", "local-run")
    run_attempt = os.getenv("GITHUB_RUN_ATTEMPT")

    return {
        "repository_name": os.getenv("GITHUB_REPOSITORY", "Local-Repo"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "pipeline_run_id": f"{run_id}.{run_attempt}" if run_attempt else run_id,
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tests": len(test_results),
        "passed_tests": passed,
        "failed_tests": failed,
        "overall_status": "PASSED" if test_results and not failed else "FAILED",
        "tests": test_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send pytest's JUnit XML results to the local report receiver."
    )
    parser.add_argument("results_file", type=Path)
    args = parser.parse_args()

    receiver_url = os.getenv("RECEIVER_URL", "").strip().rstrip("/")
    report_token = os.getenv("REPORT_TOKEN", "").strip()
    if not receiver_url:
        parser.error("RECEIVER_URL must be set to the receiver's public URL.")
    if not report_token:
        parser.error("REPORT_TOKEN must be set in the environment.")

    report = build_report(args.results_file)
    response = requests.post(
        f"{receiver_url}/report",
        json=report,
        headers={"Authorization": f"Bearer {report_token}"},
        timeout=20,
    )
    response.raise_for_status()
    print(
        f"Report delivered: {report['overall_status']} "
        f"({report['passed_tests']} passed, {report['failed_tests']} failed)."
    )
    print(json.dumps(response.json()))


if __name__ == "__main__":
    main()
