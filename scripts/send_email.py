import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from scripts.generate_report import build_report


def create_email(report: dict, sender: str, recipient: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = (
        f"Test report: {report['overall_status']} "
        f"- {report['repository_name']} ({report['branch']})"
    )
    message["From"] = sender
    message["To"] = recipient

    lines = [
        f"Repository: {report['repository_name']}",
        f"Branch: {report['branch']}",
        f"Commit: {report['commit_sha']}",
        f"Pipeline run: {report['pipeline_run_id']}",
        f"Execution timestamp: {report['execution_timestamp']}",
        f"Overall status: {report['overall_status']}",
        (
            f"Tests: {report['total_tests']} total, "
            f"{report['passed_tests']} passed, {report['failed_tests']} failed"
        ),
        "",
        "Individual test results:",
    ]

    for test in report["tests"]:
        lines.append(f"- {test['result'].upper()}: {test['name']}")
        if test["failure_message"]:
            lines.append(f"  Failure: {test['failure_message']}")

    message.set_content("\n".join(lines))
    return message


def send_report_email(results_file: Path) -> None:
    settings = {
        "SMTP_HOST": os.getenv("SMTP_HOST", "").strip(),
        "SMTP_PORT": os.getenv("SMTP_PORT", "").strip(),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", "").strip(),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "EMAIL_FROM": os.getenv("EMAIL_FROM", "").strip(),
        "EMAIL_TO": os.getenv("EMAIL_TO", "").strip(),
    }
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise RuntimeError(f"Missing email configuration: {', '.join(missing)}")

    try:
        smtp_port = int(settings["SMTP_PORT"])
    except ValueError as error:
        raise RuntimeError("SMTP_PORT must be an integer.") from error

    report = build_report(results_file)
    message = create_email(report, settings["EMAIL_FROM"], settings["EMAIL_TO"])

    with smtplib.SMTP(settings["SMTP_HOST"], smtp_port, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(settings["SMTP_USERNAME"], settings["SMTP_PASSWORD"])
        smtp.send_message(message)

    print(
        f"Email sent: {report['overall_status']} "
        f"({report['passed_tests']} passed, {report['failed_tests']} failed)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Email pytest results from a JUnit XML report."
    )
    parser.add_argument("results_file", type=Path)
    args = parser.parse_args()
    send_report_email(args.results_file)


if __name__ == "__main__":
    main()