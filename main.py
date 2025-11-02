import datetime
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Green Signal - Phishing Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FLAG_VALUE = "FLAG{green_signal_secured}"


@app.get("/", tags=["meta"])
def index() -> dict[str, object]:
    return {
        "message": "Green Signal - Phishing Intelligence API",
        "version": app.version,
        "endpoints": {
            "health": "/health",
            "challenge": "/api/challenges/green-signal",
            "examples": "/api/messages/examples",
            "classify": "/api/llm/classify",
            "forward": "/forward_message",
        },
    }


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    return {
        "status": "online",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).timestamp(),
        "challenge": "green-signal",
    }


@app.get("/api/challenges/green-signal", tags=["challenge"])
def get_challenge() -> dict[str, object]:
    data_dir = Path(__file__).parent / "data"

    emails_json_file = data_dir / "emails.json"

    with open(emails_json_file, "r") as f:
        data = json.loads(f.read())
        emails = [obj["email"] for obj in data]

    return {
        "challenge": "green-signal",
        "title": "Green Signal - Phishing Intelligence",
        "description": (
            "Classify incoming messages and forward phishing attempts to the secure inbox to capture the flag."
        ),
        "emails": emails,
    }


@app.post("/api/challenges/green-signal/submit", tags=["challenge"])
def validate_submission(payload: dict[str, object]) -> dict[str, object]:
    """
    payload:
    [{
        "email": {
            "sender": "user@example.com",
            "subject": "Subject line",
            "body": "Email body text"
        },
        "classification": "PHISHING" | "LEGITIMATE",
        "reasoning_summary": "Reasoning text"
    }]
    """
    data_dir = Path(__file__).parent / "data"
    original_file = data_dir / "emails.json"

    with open(original_file, "r") as f:
        data = json.loads(f.read())

    if len(payload) != len(data):
        return {
            "success": False,
            "message": "❌ Submission length does not match original data length.",
        }

    phishing_emails = [obj["email"] for obj in data if obj["label"] == "PHISHING"]
    payload_phishing_emails = [
        obj["email"]  # type: ignore
        for obj in payload
        if obj["classification"] == "PHISHING"  # type: ignore
    ]
    if set(phishing_emails) != set(payload_phishing_emails):
        return {
            "success": False,
            "message": f"❌ Phishing classifications do not match original data. {len(phishing_emails)} phishing emails expected, but {len(payload_phishing_emails)} found.",
        }

    return {
        "success": True,
        "message": "✅ Submission validated successfully.",
        "flag": FLAG_VALUE,
    }


@app.exception_handler(Exception)
async def fallback_exception_handler(request, exc):  # type: ignore[override]
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
        },
    )
