import smtplib
import os
import json
from email.message import EmailMessage

def send_email():
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not email_password:
        print("Email credentials missing. Skipping email task.")
        return

    report_file = "test-report.json"
    content = "Please find the attached test report."
    status = "UNKNOWN"

    if os.path.exists(report_file):
        with open(report_file, "r") as f:
            data = json.load(f)
            status = data.get("overall_status", "UNKNOWN")
            content = f"""
Pipeline Run Execution Report
----------------------------------------
Repository: {data.get('repository_name')}
Branch: {data.get('branch')}
Commit SHA: {data.get('commit_sha')}
Overall Status: {status}
Total Tests: {data.get('total_tests')}
Passed: {data.get('passed_tests')}
Failed: {data.get('failed_tests')}
            """

    msg = EmailMessage()
    msg['Subject'] = f"CI/CD Pipeline Report: Status [{status}]"
    msg['From'] = email_address
    msg['To'] = email_address
    msg.set_content(content)

    if os.path.exists(report_file):
        with open(report_file, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="json", filename="test-report.json")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
            print("Email report sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()