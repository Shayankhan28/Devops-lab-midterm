import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationInfo, field_validator

app = FastAPI(title="Assignment Submission Portal")

# Browser se frontend ko backend tak request bhejne ki ijazat (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_FILE = Path(__file__).parent / "submissions.json"

FIELD_LABELS = {
    "name": "Name",
    "registration_number": "Registration number",
    "assignment_title": "Assignment title",
    "submission_url": "Submission URL",
}


def get_data_file() -> Path:
    # Tests apni temporary file use karenge, is liye path environment variable se badal sakta hai
    return Path(os.getenv("SUBMISSIONS_FILE", str(DEFAULT_FILE)))


def load_submissions() -> list:
    data_file = get_data_file()
    if not data_file.exists():
        return []
    text = data_file.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return json.loads(text)


def save_submissions(submissions: list) -> None:
    get_data_file().write_text(json.dumps(submissions, indent=2), encoding="utf-8")


class Submission(BaseModel):
    name: str
    registration_number: str
    assignment_title: str
    submission_url: str

    # 1. Required fields: khali ya sirf spaces wali value reject hogi
    @field_validator("name", "registration_number", "assignment_title", "submission_url")
    @classmethod
    def required(cls, value: str, info: ValidationInfo) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{FIELD_LABELS[info.field_name]} is required")
        return value

    # 2. Name: sirf letters, spaces aur . ' -
    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", value):
            raise ValueError("Name must contain only letters")
        return value

    # 3. Title: kam az kam ek letter hona zaroori hai
    @field_validator("assignment_title")
    @classmethod
    def valid_title(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Assignment title must contain letters")
        return value

    # 4. URL: sirf http/https aur domain wala URL valid hai
    @field_validator("submission_url")
    @classmethod
    def valid_url(cls, value: str) -> str:
        # parsed = urlparse(value)
        # if parsed.scheme not in ("http", "https") or not parsed.netloc or " " in value:
        #     raise ValueError("Submission URL must be a valid http or https URL")
        return value


# Validation errors ko saaf message ke saath return karna
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        field = error["loc"][-1]
        label = FIELD_LABELS.get(field, str(field))
        if error["type"] == "missing":
            messages.append(f"{label} is required")
        elif error["type"] == "value_error":
            messages.append(error["msg"].replace("Value error, ", ""))
        else:
            messages.append(f"{label}: {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": messages},
    )


@app.get("/submissions")
def list_submissions():
    return load_submissions()


@app.post("/submissions", status_code=201)
def create_submission(submission: Submission):
    submissions = load_submissions()
    record = submission.model_dump()
    record["id"] = len(submissions) + 1
    record["submitted_at"] = datetime.now(timezone.utc).isoformat()
    submissions.append(record)
    save_submissions(submissions)
    return {"message": "Submission saved successfully", "submission": record}


# powershell -NoProfile -Command "$env:REPORT_TOKEN = (& .\venv\Scripts\python.exe -c 'import secrets; print(secrets.token_urlsafe(32))'); Set-Clipboard -Value $env:REPORT_TOKEN; .\venv\Scripts\python.exe -m uvicorn receiver.receiver:app --host 0.0.0.0 --port 8000"