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
reports to the receiver on your computer. No self-hosted runner or Cloudflare
account is required for a temporary Quick Tunnel.

1. In **Settings → Secrets and variables → Actions**, add:
   - Repository variable `RECEIVER_URL` with the HTTPS `trycloudflare.com` URL
     printed by `cloudflared`.
   - Repository secret `REPORT_TOKEN` with a private token generated locally.
2. From the repository root, start the receiver in one PowerShell terminal:

```powershell
$env:REPORT_TOKEN = "your-private-token"
python -m uvicorn receiver.receiver:app --host 0.0.0.0 --port 8000
```

3. Install `cloudflared` if needed, then start a Quick Tunnel in another
   terminal:

   ```powershell
   winget install --id Cloudflare.cloudflared
   cloudflared tunnel --url http://127.0.0.1:8000
   ```

4. Copy the HTTPS `trycloudflare.com` URL printed by the command into the
   GitHub `RECEIVER_URL` variable. The Actions runner uses that public URL to
   reach your computer.
5. Keep the receiver and tunnel terminals open, then push a commit. The
   GitHub-hosted workflow sends the actual results to the receiver, which saves
   or replaces `test-report.json` in the repository root.

Quick Tunnel URLs are temporary and can change when restarted. Update
`RECEIVER_URL` in GitHub whenever the URL changes.

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