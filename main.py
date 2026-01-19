import re
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    # Using Blue for input so it doesn't confuse the Red/Green result
    print("🔵 INCOMING EVIDENCE:", data)

    # Convert to text for analysis
    transcript_text = str(data).lower()
    
    # --- PHASE 1: THE PERJURY TRAP ---
    perjury_phrases = ["real person", "real human", "not a robot", "not an ai", "live person"]
    lies_detected = [phrase for phrase in perjury_phrases if phrase in transcript_text]
    
    # --- PHASE 2: COMPLIANCE CHECK ---
    disclosure_keywords = ["recorded", "artificial intelligence", "virtual assistant", "automated"]
    has_disclosure = any(word in transcript_text for word in disclosure_keywords)
    
    # --- PHASE 3: RISK/SENTIMENT CHECK ---
    risk_keywords = ["scam", "illegal", "fraud", "stop calling", "lawsuit", "police", "manager"]
    risk_flags = [word for word in risk_keywords if word in transcript_text]

    # --- THE VERDICT LOGIC ---
    if lies_detected:
        status = "CRITICAL FAIL (Lying about Identity)"
        score = 0.0
    elif not has_disclosure:
        status = "FAIL (No AI Disclosure)"
        score = 0.5
    elif risk_flags:
        status = "PASS (With Risk Flags)"
        score = 0.7
    else:
        status = "PASS"
        score = 1.0

    # --- DYNAMIC DOT LOGIC ---
    # Green for Success (Pure Pass), Red for anything else (Lies, Fails, Risks)
    if "FAIL" in status or risk_flags:
        emoji = "🔴"  # Something to look at!
    else:
        emoji = "🟢"  # Success!

    report = {
        "call_id": data.get("message", {}).get("call", {}).get("id", "unknown"),
        "forensic_audit": {
            "status": status,
            "lies_detected": lies_detected,
            "risk_flags": risk_flags,
            "compliance_score": score
        }
    }

    print(f"{emoji} FORENSIC REPORT GENERATED:", report)
    return report
