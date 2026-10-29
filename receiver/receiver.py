from fastapi import FastAPI, Request
import json
from pathlib import Path

app = FastAPI(title="Local Test Report Receiver")
REPORT_PATH = Path(__file__).parent.parent / "test-report.json"

@app.post("/report")
async def receive_report(request: Request):
    data = await request.json()
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Successfully received and saved test-report.json")
    return {"status": "success", "message": "Report saved locally"}