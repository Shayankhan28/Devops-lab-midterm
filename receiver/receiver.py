import hmac
import json
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI()
REPORT_FILE = Path(__file__).resolve().parents[1] / "test-report.json"

@app.post("/report")
async def receive_report(
    request: Request, authorization: str | None = Header(default=None)
):
    report_token = os.getenv("REPORT_TOKEN", "")
    if not report_token:
        raise HTTPException(
            status_code=503, detail="Report receiver is not configured."
        )
    if not authorization or not hmac.compare_digest(
        authorization, f"Bearer {report_token}"
    ):
        raise HTTPException(status_code=401, detail="Invalid report token.")

    try:
        data = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400, detail="Request body must be valid JSON."
        ) from error
    if not isinstance(data, dict):
        raise HTTPException(status_code=422, detail="Report must be a JSON object.")

    REPORT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"message": "Report saved successfully"}
