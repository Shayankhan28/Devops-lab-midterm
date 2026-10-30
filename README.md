# CSC418 DevOps Lab Midterm

An assignment submission portal with automated tests, GitHub Actions CI, a
local JSON report receiver, and optional email notifications.

| Component | Implementation |
| --- | --- |
| Frontend | Static HTML, CSS, and JavaScript |
| API | FastAPI |
| Data storage | Local JSON file |
| Tests | pytest and FastAPI `TestClient` |
| CI | GitHub Actions on every push |
| CI report delivery | Cloudflare Quick Tunnel to a local receiver |
| Optional notification | SMTP email |

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run the application locally](#run-the-application-locally)
- [Run tests locally](#run-tests-locally)
- [Run CI on GitHub](#run-ci-on-github)
- [Deploy the static demo to GitHub Pages](#deploy-the-static-demo-to-github-pages)
- [Receive CI reports on your computer](#receive-ci-reports-on-your-computer)
- [Optional: email reports](#optional-email-reports)
- [Demonstrate a failing and fixed run](#demonstrate-a-failing-and-fixed-run)
- [Project structure](#project-structure)

## Features

- Accepts a student's name, registration number, assignment title, and
  submission URL.
- Validates required fields and accepts only valid HTTP or HTTPS submission URLs.
- Saves valid submissions to `backend/submissions.json` and lists saved records.
- Tests valid submission, missing registration number, and invalid submission URL.
- Runs the test suite on each push and produces a machine-readable JUnit result.
- Sends run metadata and individual test results to a local JSON report receiver.
- Publishes the static frontend to GitHub Pages from `main` only after tests pass.
- Optionally emails the same test results after passing or failing runs.

## Requirements

- Python 3.10 or later (CI uses Python 3.12)
- Git
- For report delivery: `cloudflared` and an internet connection
- For email notifications: an SMTP account and its app password or SMTP credential

## Installation

Clone the repository and enter its folder:

```cmd
git clone https://github.com/Shayankhan28/Devops-lab-midterm.git
cd Devops-lab-midterm
```

Create and activate a virtual environment on Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the application locally

The API and static frontend run in separate terminals. Start the API from the
repository root:

```cmd
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, serve the frontend:

```cmd
cd frontend
python -m http.server 5500
```

Open the frontend at <http://127.0.0.1:5500>. The API is available at
<http://127.0.0.1:8000>; the submission collection endpoint is
<http://127.0.0.1:8000/submissions>.

Stop either local server with `Ctrl+C`.

## Run tests locally

From the repository root with the virtual environment active:

```cmd
python -m pytest -v
```

To run only the submission API tests:

```cmd
python -m pytest -v tests\test_submission.py
```

The tests use temporary storage, so test submissions do not modify the real
`backend/submissions.json` file. A non-zero pytest exit code indicates failure.

## Run CI on GitHub

The workflow in `.github/workflows/ci.yml` runs on every push to the repository.
It checks out the pushed revision, installs dependencies, runs pytest, creates
`test-results.xml`, sends the test report, and optionally emails it. A failed
test or configured report/email delivery failure makes the workflow fail.

Commit and push changes from Windows CMD:

```cmd
git status
git add README.md
git commit -m "Update project documentation"
git push origin main
```

Replace `README.md` and the commit message with the files and message for your
own change. Stage only intended files; review `git status` before committing.
To see the CI result, open the repository's **Actions** tab, select the latest
**Run Automated Tests** run, and inspect its steps.

## Deploy the static demo to GitHub Pages

The workflow publishes the contents of `frontend/` after the test step succeeds
on `main`. Deployments are skipped for other branches and for revisions whose
tests fail. The backend is not hosted on GitHub Pages; on a `github.io` URL the
frontend automatically uses demo mode and saves submissions in the visitor's
browser `localStorage`. Demo submissions are not sent to the API or stored in
the repository JSON file.

To enable Pages for this repository:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push a commit to `main` after tests pass.
4. In the Actions run, confirm the `deploy-pages` job succeeds.

The project site URL is <https://shayankhan28.github.io/Devops-lab-midterm/>.
The first publication may take a few minutes. Later successful pushes to `main`
update the site. Failed tests do not publish a new version, so the existing
deployment remains available.

## Receive CI reports on your computer

GitHub-hosted runners cannot write directly to your computer's `localhost`. A
Cloudflare Quick Tunnel provides a temporary HTTPS route to the local receiver.
It does not require a Cloudflare account. Keep both the receiver and tunnel
running while the GitHub Actions job executes.

### 1. Configure the GitHub repository secrets

Open **Settings → Secrets and variables → Actions → Secrets** and add:

| Secret name | Value |
| --- | --- |
| `REPORT_TOKEN` | A private random token shared only between the receiver and GitHub Actions |
| `RECEIVER_URL` | The HTTPS `trycloudflare.com` URL printed by `cloudflared` |

The workflow reads both values from repository secrets. Do not put credentials
in source code, commit them, or share them in screenshots.

To generate a new report token from PowerShell without printing it, run:

```powershell
$env:REPORT_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
Set-Clipboard $env:REPORT_TOKEN
```

Add the clipboard value as the GitHub `REPORT_TOKEN` secret. Start the receiver
in that same PowerShell window so it inherits the token:

```powershell
python -m uvicorn receiver.receiver:app --host 127.0.0.1 --port 8000
```

Keep the receiver window open.

### 2. Start the Cloudflare tunnel

In a second terminal, run:

```cmd
cloudflared tunnel --url http://127.0.0.1:8000
```

Copy the `https://....trycloudflare.com` URL printed by the command. Add or
update the `RECEIVER_URL` repository secret with that complete URL (no extra
path). Keep the tunnel window open too. Quick Tunnel URLs can change after a
restart; update the secret whenever the URL changes.

### 3. Push and verify report delivery

Push a commit to trigger the workflow:

```cmd
git add README.md
git commit -m "Update project documentation"
git push origin main
```

Replace `README.md` and the commit message with the files and message for your
own change.

The workflow sends the results after both passing and failing test runs. The
receiver creates or replaces `test-report.json` in the repository root. The
report includes the repository, branch, commit SHA, pipeline run identifier,
timestamp, test counts, overall status, and each test result with a failure
message when applicable.

Check the latest Actions run for a successful **Send test report** step, then
open `test-report.json` locally. Keep the receiver and tunnel running until
the report step has completed.

### Local receiver without GitHub Actions

To start only the receiver locally, set `REPORT_TOKEN` in PowerShell and run
Uvicorn as shown above. The receiver accepts authenticated reports at
`POST /report`; it does not run pytest by itself. GitHub Actions generates the
actual results and sends them to this endpoint.

### Troubleshooting

- **`RECEIVER_URL must be set`**: verify `RECEIVER_URL` is a repository secret
  under **Settings → Secrets and variables → Actions → Secrets**, not a
  repository variable.
- **Receiver returns `401`**: the receiver's `REPORT_TOKEN` and GitHub's
  `REPORT_TOKEN` secret must match. Restart the receiver after changing its
  local token.
- **Tunnel returns an error or times out**: check that the receiver is running
  on port `8000`, restart the Quick Tunnel, and update the `RECEIVER_URL`
  secret if its URL changed.
- **Email authentication fails**: check the SMTP host/port, sender account,
  and provider app password. Do not use a normal Gmail password.

## Optional: email reports

The email step is disabled unless the repository variable
`EMAIL_REPORT_ENABLED` is exactly `true`. To enable it, open
**Settings → Secrets and variables → Actions**.

Add these **repository secrets**:

| Secret name | Example or description |
| --- | --- |
| `SMTP_HOST` | Gmail: `smtp.gmail.com` |
| `SMTP_PORT` | Gmail with STARTTLS: `587` |
| `SMTP_USERNAME` | Full SMTP account username, often an email address |
| `SMTP_PASSWORD` | SMTP credential or provider app password; not the normal account password |
| `EMAIL_FROM` | Sender address authorized by the SMTP account |
| `EMAIL_TO` | Destination email address |

For Gmail, enable 2-Step Verification and create an App Password in your Google
Account security settings. Save the App Password as `SMTP_PASSWORD`; never
commit or share it.

Then open the **Variables** tab and add:

| Variable name | Value |
| --- | --- |
| `EMAIL_REPORT_ENABLED` | `true` |

When enabled, the workflow emails the repository, branch, commit, run ID,
timestamp, overall result, test counts, and individual test outcomes after both
passing and failing runs. Email configuration/delivery failure is visible in
the Actions run and causes the job to fail.

## Demonstrate a failing and fixed run

For the assignment demonstration, capture evidence of a passing run, a failing
run after introducing a temporary defect, and a passing run after fixing it.
Keep the receiver and tunnel active for each run if report delivery is enabled.

For example, temporarily bypass the URL validator in `backend/main.py`. The
existing invalid-URL test should then fail because the API accepts a URL that
the test expects to reject. Commit and push that temporary change, then verify
that Actions fails and the received JSON report says `FAILED`.

Restore the URL validation immediately, run the tests locally, and push the
fix. Verify the final Actions run succeeds and the received JSON report says
`PASSED`. Do not leave the demonstration defect in the final revision.

Suggested evidence:

1. Local pytest output showing passing tests.
2. GitHub Actions run showing successful CI.
3. Repository Actions secrets page (secret values must remain hidden).
4. `test-report.json` showing run metadata and test results.
5. Failing Actions run and its `FAILED` JSON report.
6. Corrected passing Actions run and its `PASSED` report.
7. Email received for the CI run, if the email bonus is enabled.

## Project structure

```text
Devops-lab-midterm/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── main.py
│   └── submissions.json
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── receiver/
│   └── receiver.py
├── scripts/
│   ├── generate_report.py
│   └── send_email.py
├── tests/
│   ├── test_generate_report.py
│   ├── test_report_receiver.py
│   ├── test_send_email.py
│   └── test_submission.py
├── requirements.txt
└── README.md
```

## Author

Muhammad Shayan Khan  
Bachelor of Software Engineering (BSE)  
COMSATS University Islamabad, Attock Campus
