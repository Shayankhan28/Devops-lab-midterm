# CSC418 DevOps Lab Midterm

## Assignment Submission Portal with Automated Testing

This project was developed as part of the CSC418 DevOps Lab Midterm Examination. The system allows students to submit assignment details through a web interface, validates input data, stores valid submissions, and displays saved submissions. The project also includes automated testing, CI pipeline integration, and a local test report receiver.

---

## Features

- Submit assignment details
- Validate required fields
- Validate submission URLs
- Store valid submissions
- Display saved submissions
- Automated testing using Pytest
- Continuous Integration using GitHub Actions
- Local JSON test report receiver

---

## Prerequisites

- Python 3.10 or later
- Git

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd Lab-mid-term
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the FastAPI server:

```bash
cd backend
uvicorn main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

---

## Running Automated Tests

Execute all test cases using:

```bash
pytest
```

The test results will be displayed in the terminal.

---

## Sending Reports to Your Computer

This project uses Cloudflare Quick Tunnel to let GitHub-hosted Actions send
reports to the receiver on your computer. No Cloudflare account or auth token
is required. Keep both the receiver and tunnel running while the workflow executes.

1. In **Settings → Secrets and variables → Actions → Secrets**, add:
   - `RECEIVER_URL` with the HTTPS `trycloudflare.com` URL printed by `cloudflared`.
   - `REPORT_TOKEN` with the same private token configured for the local receiver.
2. From the repository root, start the receiver in one terminal if it is not
   already running:

```powershell
$env:REPORT_TOKEN = "your-private-token"
python -m uvicorn receiver.receiver:app --host 0.0.0.0 --port 8000
```

3. In another terminal, start the Cloudflare Quick Tunnel:

   ```powershell
   cloudflared tunnel --url http://127.0.0.1:8000
   ```

4. Copy the HTTPS `trycloudflare.com` URL printed in the terminal into the
   GitHub `RECEIVER_URL` secret. The Actions runner uses that public URL to
   reach your computer.
5. Keep the receiver and tunnel terminals open, then push a commit. The
   GitHub-hosted workflow sends actual test results to the receiver, which saves
   or replaces `test-report.json` in the repository root.

The Quick Tunnel URL may change when restarted. Update the `RECEIVER_URL`
GitHub secret whenever it changes.

The report includes run metadata, test counts, each test result, and failure
messages when available.

The report step runs after both passing and failing test runs. A test failure
still makes the GitHub Actions job fail after the report is sent. The token
protects the receiver endpoint; do not share or commit it.

To generate a token in PowerShell without printing it, run:

```powershell
$env:REPORT_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
Set-Clipboard $env:REPORT_TOKEN
```

Paste the clipboard value into the GitHub `REPORT_TOKEN` secret and use the
environment variable when starting the receiver.

The receiver saves reports as:

```text
test-report.json
```

## Email Test Reports (Bonus)

The workflow can email the report after both passing and failing test runs.
Configure an SMTP account, then add these repository secrets under
**Settings → Secrets and variables → Actions → Secrets**:

- `SMTP_HOST` (Gmail: `smtp.gmail.com`)
- `SMTP_PORT` (Gmail: `587`)
- `SMTP_USERNAME` (your SMTP account username)
- `SMTP_PASSWORD` (use a provider app password; never use or commit your normal account password)
- `EMAIL_FROM` (the sender address authorized by the SMTP account)
- `EMAIL_TO` (the destination address)

For Gmail, enable 2-Step Verification and create an App Password in your Google
Account security settings. Store that app password as `SMTP_PASSWORD`.

Then add the repository variable `EMAIL_REPORT_ENABLED` with the exact value
`true` under **Settings → Secrets and variables → Actions → Variables**.
Until this variable is enabled, the email step is skipped and does not affect CI.
Once enabled, an email delivery error fails the job so the notification failure
is visible. The email contains repository, branch, commit and run identifiers,
the overall status and counts, and each test result with failure details.

---

## Project Structure

```text
Lab-mid-term/
│
├── backend/
│   ├── main.py
│   └── submissions.json
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│   └── test_submission.py
│
├── receiver/
│   └── receiver.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Required Test Cases

### Test Case 1: Valid Submission

Input:

- Valid student name
- Valid registration number
- Valid assignment title
- Valid submission URL

Expected Result:

- Submission is accepted and saved successfully.

### Test Case 2: Missing Registration Number

Input:

- Student name provided
- Registration number missing
- Assignment title provided
- Valid submission URL

Expected Result:

- Validation error is returned.
- Submission is not saved.

### Test Case 3: Invalid Submission URL

Input:

- Valid student name
- Valid registration number
- Valid assignment title
- Invalid URL

Expected Result:

- Submission is rejected.
- Submission is not saved.

---

## Repository Contents

This repository contains:

- Application source code
- Automated test cases
- GitHub Actions CI configuration
- Local report receiver
- Project documentation

---

## Author

Muhammad Shayan Khan  
Bachelor of Software Engineering (BSE)  
COMSATS University Islamabad, Attock Campus