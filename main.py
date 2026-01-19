import re
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    # 1. Get the raw data from the voice agent
    data = await request.json()
    print("🔴 INCOMING EVIDENCE:", data)

    # 2. Extract the conversation text
    # We convert the whole data dump to text to search it easily for this demo
    transcript_text = str(data).lower()
    
    # 3. FORENSIC ANALYSIS (The "Neural DNA" Logic)
    
    # Check A: Did the agent disclose recording/AI status? (Compliance)
    # If these words are missing, the agent fails the audit.
    compliance_keywords = ["recorded", "artificial intelligence", "ai", "virtual assistant", "system"]
    is_compliant = any(word in transcript_text for word in compliance_keywords)
    
    # Check B: Did the user sound angry? (Risk Detection)
    risk_keywords = ["stupid", "hate", "scam", "illegal", "manager", "lawsuit"]
    risk_flags = [word for word in risk_keywords if word in transcript_text]

    # 4. Generate the Verdict
    audit_report = {
        "compliance_status": "PASS" if is_compliant else "FAIL",
        "risk_detected": len(risk_flags) > 0,
        "risk_flags": risk_flags,
        "basal_accountability_score": 0.95 if not risk_flags else 0.45
    }

    print("🟢 FORENSIC REPORT GENERATED:", audit_report)
    return audit_report
