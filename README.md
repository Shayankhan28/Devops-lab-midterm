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

## Starting the Local Report Receiver

Open a new terminal and run:

```bash
python receiver/receiver.py
```

The receiver will automatically receive and save test reports as:

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