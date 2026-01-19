from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import logging
import os

# --- NEURAL DNA CORE ---
# This acts as the "Forensic Substrate" for any voice agent.
# It is agnostic to the specific client (Tax, Medical, Legal).

app = FastAPI(title="Neural DNA Forensics Engine")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Model: Generic structure for any Vapi/Retell call
class TranscriptPayload(BaseModel):
    call_id: str
    transcript_text: str
    metadata: dict = {}

@app.get("/")
def read_root():
    return {"status": "online", "system": "Neural DNA Substrate v1.0"}

@app.post("/audit-call")
async def audit_call(payload: TranscriptPayload):
    logger.info(f"Received audit request for Call ID: {payload.call_id}")
    
    try:
        # --- 1. COMPLIANCE LAYER (White Label) ---
        # Checks for mandatory legal disclaimers (e.g., "Recorded Line", "Not Legal Advice")
        # In a real deployment, these keywords are pulled from a database based on the client ID.
        
        text_lower = payload.transcript_text.lower()
        
        # Example Generic Rule: Verify the agent announced the call is recorded
        has_disclaimer = "recorded" in text_lower or "quality assurance" in text_lower
        
        # --- 2. BEHAVIORAL LAYER ---
        # Analyzes sentiment and objection handling without exposing client data
        sentiment_score = 0.85 # Placeholder for your proprietary sentiment model
        
        # --- 3. RETURN VERDICT ---
        return {
            "call_id": payload.call_id,
            "forensic_audit": {
                "compliance_status": "PASS" if has_disclaimer else "FLAGGED",
                "risk_flags": [] if has_disclaimer else ["Missing Compliance Disclaimer"],
                "lead_quality_score": sentiment_score
            }
        }

    except Exception as e:
        logger.error(f"Error auditing call: {str(e)}")
        raise HTTPException(status_code=500, detail="Forensic Engine Failure")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
