from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    # detailed_log: Accept ANY data sent by Vapi
    data = await request.json()
    
    # This prints the raw message to your Railway logs so we can see it
    print("🔴 RECEIVED DATA FROM VAPI:", data)
    
    # Send back a fake report to keep Vapi happy
    return {
        "call_id": "unknown",
        "forensic_audit": {
            "compliance_status": "PASS",
            "risk_flags": [],
            "lead_sentiment": 0.85
        }
    }
