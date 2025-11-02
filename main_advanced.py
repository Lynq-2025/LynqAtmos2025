import datetime
import json
from pathlib import Path
from typing import Optional
import hashlib
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Green Signal - Advanced Phishing Detection Challenge",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FLAG_VALUE = "FLAG{green_signal_advanced_mastered}"

# Advanced scoring system
SCORING = {
    "perfect": 1000,
    "excellent": 900,
    "good": 800,
    "acceptable": 700,
    "partial": 500,
    "failed": 0
}

# Domain reputation database (mock)
DOMAIN_REPUTATION = {
    "google.com": {"score": 95, "established": 2002, "risk": "SAFE"},
    "microsoft.com": {"score": 94, "established": 1986, "risk": "SAFE"},
    "example.com": {"score": 50, "established": 1992, "risk": "NEUTRAL"},
    "verify-account.login.com": {"score": 2, "established": 2024, "risk": "CRITICAL"},
    "security-portal.login.com": {"score": 5, "established": 2024, "risk": "CRITICAL"},
    "globalsys.com": {"score": 45, "established": 2010, "risk": "MEDIUM"},
    "examplecorp.com": {"score": 85, "established": 2005, "risk": "SAFE"},
}

# Known phishing patterns
PHISHING_SIGNATURES = {
    "urgency_triggers": [
        "immediate", "urgent", "verify", "confirm", "act now", "within 24 hours",
        "temporary suspension", "unauthorized access", "unusual activity", "compromise"
    ],
    "verification_requests": [
        "verify credentials", "confirm identity", "validate account", "update information",
        "re-enter password", "click here to verify"
    ],
    "suspicious_links": [
        "http://", "login.php", "verify.php", "confirm.php", "security-", "-update", "-verify"
    ]
}

@app.get("/")
def index() -> dict:
    return {
        "message": "Green Signal - Advanced Phishing Detection Challenge",
        "version": app.version,
        "difficulty": "EXPERT",
        "endpoints": {
            "challenge": "/api/v2/challenge",
            "email_metadata": "/api/v2/email/{email_id}/metadata",
            "domain_check": "/api/v2/tools/domain-reputation",
            "pattern_analysis": "/api/v2/tools/pattern-analysis",
            "header_analysis": "/api/v2/tools/header-analysis",
            "submit": "/api/v2/submit"
        }
    }

@app.get("/health")
def health() -> dict:
    return {
        "status": "online",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).timestamp(),
        "challenge": "green-signal-advanced"
    }

@app.get("/api/v2/challenge")
def get_challenge() -> dict:
    """Get challenge data with obfuscated indicators"""
    data_dir = Path(__file__).parent / "data"
    emails_file = data_dir / "emails_advanced.json"
    
    # Fallback to regular emails if advanced not found
    if not emails_file.exists():
        emails_file = data_dir / "emails.json"
    
    try:
        with open(emails_file, "r") as f:
            data = json.loads(f.read())
    except FileNotFoundError:
        return {
            "error": "Challenge data not found. Run generate_messages_with_labels.py first",
            "path": str(emails_file)
        }
    
    emails = [obj["email"] for obj in data]
    
    return {
        "challenge": "green-signal-advanced",
        "difficulty": "EXPERT",
        "title": "Advanced Phishing Detection with Tool Access",
        "description": "Classify emails while using multiple analysis tools. Phishing is obfuscated with legitimate indicators.",
        "scoring": SCORING,
        "tools_available": [
            "domain-reputation",
            "pattern-analysis", 
            "header-analysis"
        ],
        "emails": emails,
        "count": len(emails)
    }

@app.post("/api/v2/tools/domain-reputation")
def check_domain_reputation(payload: dict) -> dict:
    """
    Tool endpoint: Check domain reputation score.
    Agent must use this to detect spoofed/suspicious domains.
    """
    domain = payload.get("domain", "").lower()
    
    if not domain:
        return {"error": "Domain required"}
    
    # Extract base domain
    base_domain = domain.split("://")[-1].split("/")[0].split("@")[-1]
    
    # Exact match
    if base_domain in DOMAIN_REPUTATION:
        info = DOMAIN_REPUTATION[base_domain]
        return {
            "domain": base_domain,
            "reputation_score": info["score"],
            "risk_level": info["risk"],
            "established": info["established"],
            "years_active": datetime.datetime.now().year - info["established"]
        }
    
    # Similarity check for spoofed domains
    similar_domains = []
    for known_domain in DOMAIN_REPUTATION.keys():
        if known_domain.replace(".com", "") in base_domain or base_domain in known_domain:
            similar_domains.append(known_domain)
    
    score = 30 if similar_domains else 20  # Unknown domains get lower score
    
    return {
        "domain": base_domain,
        "reputation_score": score,
        "risk_level": "MEDIUM" if similar_domains else "UNKNOWN",
        "established": None,
        "years_active": None,
        "similar_legitimate_domains": similar_domains,
        "note": "Unknown domain - may be spoofed or newly registered"
    }

@app.post("/api/v2/tools/pattern-analysis")
def analyze_patterns(payload: dict) -> dict:
    """
    Tool endpoint: Analyze email for known phishing patterns.
    Requires agent to interpret results intelligently.
    """
    sender = payload.get("sender", "").lower()
    subject = payload.get("subject", "").lower()
    body = payload.get("body", "").lower()
    
    findings = {
        "urgency_indicators": [],
        "verification_requests": [],
        "suspicious_links": [],
        "domain_consistency": None,
        "risk_score": 0
    }
    
    # Check urgency triggers
    for trigger in PHISHING_SIGNATURES["urgency_triggers"]:
        if trigger in subject or trigger in body:
            findings["urgency_indicators"].append(trigger)
    
    # Check verification requests
    for verification in PHISHING_SIGNATURES["verification_requests"]:
        if verification in subject or verification in body:
            findings["verification_requests"].append(verification)
    
    # Check for suspicious links
    links_found = re.findall(r'http[s]?://\S+', body)
    for link in links_found:
        for pattern in PHISHING_SIGNATURES["suspicious_links"]:
            if pattern in link.lower():
                findings["suspicious_links"].append(link)
    
    # Check sender-subject alignment
    if "@" in sender:
        sender_domain = sender.split("@")[1]
        if any(keyword in sender_domain for keyword in ["security", "verify", "update", "alert"]):
            findings["domain_consistency"] = "SUSPICIOUS_KEYWORDS_IN_DOMAIN"
        else:
            findings["domain_consistency"] = "NORMAL"
    
    # Calculate risk
    findings["risk_score"] = (
        len(findings["urgency_indicators"]) * 0.15 +
        len(findings["verification_requests"]) * 0.25 +
        len(findings["suspicious_links"]) * 0.30
    )
    
    return findings

@app.post("/api/v2/tools/header-analysis")
def analyze_headers(payload: dict) -> dict:
    """
    Tool endpoint: Analyze email headers for spoofing indicators.
    Returns advanced authentication results.
    """
    sender = payload.get("sender", "")
    subject = payload.get("subject", "")
    
    # Simulate SPF/DKIM/DMARC analysis
    sender_domain = sender.split("@")[1] if "@" in sender else "unknown"
    
    analysis = {
        "sender": sender,
        "sender_domain": sender_domain,
        "spf_status": "PASS" if sender_domain in DOMAIN_REPUTATION else "FAIL",
        "dkim_status": "PASS" if sender_domain in DOMAIN_REPUTATION else "UNKNOWN",
        "dmarc_status": "PASS" if sender_domain in DOMAIN_REPUTATION else "NONE",
        "subject_line_risk": "LOW",
        "indicators": []
    }
    
    # Check for character spoofing (homographs)
    if any(char in sender_domain for char in ['0', 'O', '1', 'l', 'I']):
        analysis["indicators"].append("POSSIBLE_HOMOGRAPH_ATTACK")
    
    # Check for header inconsistencies
    if "noreply" in sender.lower() and any(urgent_word in subject.lower() for urgent_word in ["urgent", "action required"]):
        analysis["indicators"].append("SUSPICIOUS_NOREPLY_WITH_URGENCY")
    
    return analysis

@app.post("/api/v2/email/{email_id}/metadata")
def get_email_metadata(email_id: int, payload: dict) -> dict:
    """
    Tool endpoint: Get detailed metadata for specific email.
    Returns information agent needs to investigate further.
    """
    sender = payload.get("sender", "")
    subject = payload.get("subject", "")
    
    # Generate metadata
    metadata = {
        "email_id": email_id,
        "sender_hash": hashlib.sha256(sender.encode()).hexdigest()[:8],
        "subject_length": len(subject),
        "characteristics": []
    }
    
    # Analyze characteristics
    if "@" in sender:
        domain = sender.split("@")[1]
        metadata["domain_reputation"] = DOMAIN_REPUTATION.get(domain, {
            "score": 20,
            "risk": "UNKNOWN"
        })
        metadata["characteristics"].append(f"External domain: {domain}")
    
    if len(subject) > 50:
        metadata["characteristics"].append("Long subject line")
    
    if "fwd" in subject.lower() or "re:" in subject.lower():
        metadata["characteristics"].append("Forwarded/Reply pattern")
    
    return metadata

@app.post("/api/v2/submit")
def advanced_submit(payload: dict) -> dict:
    """
    Advanced submission with scoring and detailed feedback.
    """
    data_dir = Path(__file__).parent / "data"
    original_file = data_dir / "emails_advanced.json"
    
    if not original_file.exists():
        original_file = data_dir / "emails.json"
    
    try:
        with open(original_file, "r") as f:
            data = json.loads(f.read())
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Challenge data not found"
        }
    
    if len(payload) != len(data):
        return {
            "success": False,
            "score": 0,
            "message": f"❌ Submission length {len(payload)} does not match {len(data)}",
        }
    
    # Calculate accuracy
    correct = 0
    phishing_emails = [obj["email"] for obj in data if obj["label"] == "PHISHING"]
    payload_phishing_emails = [
        obj["email"]
        for obj in payload
        if obj["classification"] == "PHISHING"
    ]
    
    for phishing_email in phishing_emails:
        if phishing_email in payload_phishing_emails:
            correct += 1
    
    accuracy = correct / len(phishing_emails) if phishing_emails else 0
    
    if accuracy >= 0.95:
        score = SCORING["perfect"]
        status = "✅ PERFECT"
        flag = FLAG_VALUE
    elif accuracy >= 0.85:
        score = SCORING["excellent"]
        status = "✅ EXCELLENT"
        flag = FLAG_VALUE
    elif accuracy >= 0.75:
        score = SCORING["good"]
        status = "⚠️ GOOD"
        flag = FLAG_VALUE
    elif accuracy >= 0.65:
        score = SCORING["acceptable"]
        status = "⚠️ ACCEPTABLE"
        flag = FLAG_VALUE
    elif accuracy >= 0.50:
        score = SCORING["partial"]
        status = "❌ PARTIAL"
        flag = None
    else:
        score = SCORING["failed"]
        status = "❌ FAILED"
        flag = None
    
    message = f"{status} - Detected {correct}/{len(phishing_emails)} phishing emails ({accuracy*100:.1f}% accuracy)"
    
    result = {
        "success": accuracy >= 0.75,
        "score": score,
        "accuracy": accuracy,
        "phishing_detected": correct,
        "phishing_expected": len(phishing_emails),
        "message": message
    }
    
    if flag:
        result["flag"] = flag
    
    return result

@app.exception_handler(Exception)
async def fallback_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
        },
    )
