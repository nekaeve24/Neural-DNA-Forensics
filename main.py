import re
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    print("🔵 INCOMING EVIDENCE:", data)

    transcript_text = str(data).lower()
    
    # --- PHASE 1: THE SMARTER PERJURY TRAP ---
    # We use "Regular Expressions" (regex) to ensure she isn't saying "NOT a real person"
    # This pattern looks for claims like "I am a real person" or just "real person" 
    # BUT it ignores them if the word "not" is nearby.
    
    perjury_triggers = ["real person", "real human", "live person"]
    lies_detected = []
    
    for trigger in perjury_triggers:
        if trigger in transcript_text:
            # Check if she said "NOT" before the trigger
            # This is a simple check: is "not [trigger]" present?
            if f"not a {trigger}" in transcript_text or f"not {trigger}" in transcript_text:
                continue # She is being honest (saying she is NOT one), so skip this trigger
            
            # If "not" wasn't found right before it, she is likely lying.
            lies_detected.append(trigger)
            
    # Also check for explicit robot denials
    if "not a robot" in transcript_text or "not an ai" in transcript_text:
         lies_detected.append("denied being a robot")

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
