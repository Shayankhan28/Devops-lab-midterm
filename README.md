# Assignment Submission Portal

A simple Assignment Submission Portal built with FastAPI for the CSC418 DevOps Lab Midterm.

## Features

- Submit assignment details
- Validate required fields
- Validate submission URL
- Save valid submissions
- Display saved submissions
- Automated testing using Pytest
- CI pipeline using GitHub Actions
- Local test report receiver

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
cd backend
uvicorn main:app --reload
```

Open your browser and visit:

```text
http://127.0.0.1:8000
```

## Run Automated Tests

```bash
pytest
```

## Start Local Receiver

Open a new terminal and run:

```bash
python receiver/receiver.py
```

The receiver will save the incoming report as:

```text
test-report.json
```

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

## Test Cases

### Test Case 1

Input:

- Valid name
- Valid registration number
- Valid assignment title
- Valid URL

Expected Result:

- Submission is saved successfully.

### Test Case 2

Input:

- Missing registration number

Expected Result:

- Validation error is returned.

### Test Case 3

Input:

- Invalid URL

Expected Result:

- Submission is rejected and not saved.

## Repository

This repository contains:

- Application source code
- Automated tests
- CI pipeline configuration
- Local report receiver

## Author

Muhammad Shayan Khan
COMSATS University Islamabad
Attock Campus