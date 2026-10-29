import json
import os
import sys
import requests

def send_report():
    report_file = "test-report.json"
    if not os.path.exists(report_file):
        print("Report file not found!")
        sys.exit(1)

    with open(report_file, "r") as f:
        pytest_data = json.load(f)

    # Required report format as per PDF requirements
    summary = pytest_data.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = summary.get("total", 0)
    
    overall_status = "PASSED" if failed == 0 and total > 0 else "FAILED"

    tests_list = []
    for test in pytest_data.get("tests", []):
        name = test.get("nodeid", "")
        outcome = test.get("outcome", "")
        call = test.get("call", {})
        longrepr = call.get("longrepr", "") if outcome == "failed" else ""
        
        tests_list.append({
            "name": name,
            "result": outcome,
            "failure_message": str(longrepr)
        })

    final_report = {
        "repository_name": os.getenv("GITHUB_REPOSITORY", "Local-Repo"),
        "branch": os.getenv("GITHUB_REF_NAME", "main"),
        "commit_sha": os.getenv("GITHUB_SHA", "local-sha"),
        "pipeline_run_id": os.getenv("GITHUB_RUN_ID", "12345"),
        "execution_timestamp": pytest_data.get("created", ""),
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "overall_status": overall_status,
        "tests": tests_list
    }

    # Save formatted report locally as test-report.json
    with open("test-report.json", "w") as f:
        json.dump(final_report, f, indent=2)

    # Send to Local Receiver via Webhook
    receiver_url = os.getenv("RECEIVER_URL")
    if receiver_url:
        try:
            res = requests.post(f"{receiver_url}/report", json=final_report, timeout=10)
            print("Receiver Response:", res.json())
        except Exception as e:
            print(f"Failed to send to receiver: {e}")
    else:
        print("RECEIVER_URL environment variable not set.")

if __name__ == "__main__":
    send_report()