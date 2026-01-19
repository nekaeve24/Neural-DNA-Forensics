import re
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    print("🔵 INCOMING EVIDENCE:", data)

    transcript_text = str(data).lower()
    
    # --- PHASE 1: THE CONTEXT WINDOW CHECK ---
    perjury_triggers = ["real person", "real human", "live person"]
    lies_detected = []
    
    for trigger in perjury_triggers:
        if trigger in transcript_text:
            # Find exactly where the "lie" appears in the text
            start_index = transcript_text.find(trigger)
            
            # Grab the 30 characters immediately BEFORE the trigger
            # This captures things like "not a...", "not actually a...", "never a..."
            context_window = transcript_text[max(0, start_index - 30):start_index]
            
            # If "not" or "never" is in that safety window, she is innocent.
            if "not" in context_window or "never" in context_window:
                continue 
            
            # If no denial words are found nearby, she is GUILTY.
            lies_detected.append(trigger)

    # --- PHASE 2: COMPLIANCE CHECK ---
    disclosure_keywords = ["recorded", "artificial intelligence", "virtual assistant", "automated", "ai"]
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
    if "FAIL" in status or risk_flags:
        emoji = "🔴"
    else:
        emoji = "🟢"

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
