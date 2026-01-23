import re
import os
import json
import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from textblob import TextBlob

from googleapiclient.discovery import build
from google.oauth2 import service_account

def check_jade_availability():
    # Full calendar scope for reliable primary calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    timeMax = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'
    
    calendarId = 'primary'
    
    events_result = service.events().list(
        calendarId=calendarId, 
        timeMin=now, 
        timeMax=timeMax, 
        singleEvents=True, 
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    available_slots = [] # FIXED: Moved out of the 'if not events' block

    if not events:
        return ["No openings today"]
    
    for event in events:
        if "Availability" in event.get('summary', ''):
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            
            if not start_str or not end_str:
                continue

            start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            current_time = start_dt
            while current_time < end_dt:
                available_slots.append(current_time.strftime('%b %d at %I:%M %p'))
                current_time += datetime.timedelta(hours=1)
                
    return available_slots if available_slots else ["No specific openings found."]

app = FastAPI()
audit_history = []

@app.post("/audit-call")
async def audit_call(request: Request):
    global audit_history
    data = await request.json()
    
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    # 2. THE SOVEREIGN GUARD: No shortcuts. Everything is documented.
    if not transcript_text or transcript_text.strip() == "":
        if call_status == "ended":
            new_report = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "verdict": "PASS", 
                "emoji": "✅",
                "risks": ["Session Closed Cleanly"],
                "type": "POST_CALL_SUMMARY"
            }
            audit_history.insert(0, new_report)

            print(f"\n--- 🏁 CALL COMPLETED: FINAL AUDIT REPORT ---")
            print(f"Result: {new_report['emoji']} {new_report['verdict']}")
            print(f"Timestamp: {new_report['timestamp']}")
            print("--- DATA PRESERVED IN SOVEREIGN VAULT ---\n")
            
            return {"status": "archived", "audit_id": new_report['timestamp']}
        
        return {"status": "monitoring_active"} 

    # 3. SESSION GUARD: Only proceed if active
    if call_status == "ended": 
        return {"status": "session_closed"}

    # 4. SCHEDULING TRIGGER
    scheduling_keywords = ["schedule", "appointment", "available", "calendar"]
    if any(key in transcript_text for key in scheduling_keywords):
        open_slots = check_jade_availability()
        available_str = ", ".join(open_slots)
        
        # Tool response for Vapi
        return {"status": "scheduling", "options": open_slots}

    # 6. SLOT CAPTURE & BOOKING
    # Note: For production, we'd iterate through open_slots to match transcript_text
    # But first, we handle the forensic analysis for the Global View
       
    # --- ENGINE 1: TRUTH & COMPLIANCE ---
    perjury_triggers = ["real person", "real human", "live person", "not a robot"]
    lies_detected = []
    
    for trigger in perjury_triggers:
        if trigger in transcript_text:
            start_index = transcript_text.find(trigger)
            context_window = transcript_text[max(0, start_index - 30):start_index]
            if "not" in context_window or "ai" in context_window:
                continue 
            lies_detected.append(trigger)

    risk_keywords = ["scam", "illegal", "fraud", "stop calling", "lawsuit", "police"]
    risk_flags = [word for word in risk_keywords if word in transcript_text]

    # --- ENGINE 2: THE BIAS & LINGUISTIC AUDIT (Model 12) ---
    blob = TextBlob(transcript_text)
    sentiment_score = blob.sentiment.polarity 
    
    bias_triggers = {
        "gender_bias": ["female doctor", "male nurse", "man's job", "woman's job"],
        "cultural_bias": ["those people", "foreigners", "illegal alien"]
    }

    linguistic_triggers = {
        "language_spanish": ["hola", "gracias", "por favor"],
        "language_aave": ["finna", "ion", "no cap", "on god"]
    }
    
    bias_detected = []
    for category, triggers in bias_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                bias_detected.append(f"{category}: {trigger}")

    language_detected = []
    for category, triggers in linguistic_triggers.items():
        for trigger in triggers:
            if re.search(r'\b' + re.escape(trigger) + r'\b', transcript_text):
                language_detected.append(trigger)

    # --- VERDICT LOGIC ---
    status = "PASS"
    if lies_detected: status = "CRITICAL FAIL (Lying)"
    elif bias_detected: status = "FAIL (Bias Detected)"
    elif sentiment_score < -0.5: status = "FAIL (Hostile Tone)"
    elif risk_flags: status = "WARN (Risk Flags)"
    elif language_detected: status = "PASS (Linguistic Marker Detected)"

    emoji = "🟢"
    if "FAIL" in status: emoji = "🔴"
    elif "WARN" in status: emoji = "🟠"
    elif "Linguistic" in status: emoji = "🔵"

    report = {
        "emoji": emoji,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "verdict": status,
        "risks": lies_detected + risk_flags + bias_detected + language_detected
    }

    audit_history.insert(0, report)
    if len(audit_history) > 20: audit_history.pop()

    return report

@app.get("/data")
async def get_data():
    return audit_history

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Dashboard code remains the same as your functional original
    pass
