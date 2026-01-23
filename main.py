import re
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from textblob import TextBlob
import datetime

from googleapiclient.discovery import build
from google.oauth2 import service_account

def check_jade_availability():
    # Full calendar scope for reliable primary calendar access
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    # Search for the next 14 days to catch all availability
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    timeMax = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'
    
    # Use 'primary' to pull from your main Neka Everett calendar
    calendarId = 'primary'
    
    events_result = service.events().list(
        calendarId=calendarId, 
        timeMin=now, 
        timeMax=timeMax, 
        singleEvents=True, 
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Extract just the dates to give to Jade
    if not events:
        return ["No openings today"]
    
        # This creates a list like ["Monday at 10am", "Tuesday at 2pm"]
        available_slots = []
    for event in events:
        # Check if this is an availability block
        if "Availability" in event.get('summary', ''):
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            
            # Skip if it's an all-day event without specific times
            if not start_str or not end_str:
                continue

            start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            # Break the big block into 1-hour chunks
            current_time = start_dt
            while current_time < end_dt:
                available_slots.append(current_time.strftime('%b %d at %I:%M %p'))
                current_time += datetime.timedelta(hours=1)
                
    return available_slots if available_slots else ["No specific openings found."]
    
app = FastAPI()

audit_history = []

@app.post("/audit-call")
async def audit_call(request: Request):
    global audit_history  # This allows the function to update the global list
    data = await request.json()
    
    # 1. Identify the status and transcript
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    # 2. THE SOVEREIGN GUARD: No shortcuts. Everything is documented.
    if not transcript_text or transcript_text.strip() == "":
        if call_status == "ended":
            # Document the closing of the session for the Legal Audit Trail
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
        
        return {"status": "monitoring_active"} # Confirms the engine is listening

        
    # 3. SESSION GUARD: Only proceed to Engines if the call is still active
    if call_status == "ended": return {"status": "session_closed"}

    # 4. SCHEDULING TRIGGER: Listen for appointment keywords
    scheduling_keywords = ["schedule", "appointment", "available", "calendar"]
    if any(key in transcript_text for key in scheduling_keywords):
        # Call the engine we just built at the top
        open_slots = check_jade_availability()
        print(f"--- 📅 JADE ACTION: Found {len(open_slots)} availability windows ---")

    # 5. FORMAT FOR JADE: Create a spoken list of days
        available_str = ", ".join(open_slots)
        print(f"--- 🗣️ JADE RESPONSE: 'I have availability on {available_str}. Which works for you?' ---")
        
        # This string would be sent back to the voice engine in the next phase
        return {"status": "scheduling", "options": open_slots}

        chosen_day = None  
    # 6. SLOT CAPTURE: Listen for the user's choice
        chosen_day = next((day for day in open_slots if day.lower() in transcript_text), None)
       
    if chosen_day:
        # 7. BOOKING EXECUTION: Create the actual event
            print(f"--- 📅 JADE BOOKING: Registering 'Tax Prep' for {chosen_day} ---")
            new_event = {
                'summary': f'Tax Prep Appointment (Via Jade)',
                'description': f'Scheduled during AI audit call on {chosen_day}',
                'start': {'dateTime': '2026-01-22T10:00:00Z'}, 
                'end': {'dateTime': '2026-01-22T11:00:00Z'}
            }
            
        # 8. VAPI VOICE COMMAND: Final response to the user
            return {
                "results": [{
                    "toolCallId": data.get('message', {}).get('toolCalls', [{}])[0].get('id'),
                    "result": f"Great! I have scheduled your tax preparation appointment for {chosen_day}. You will receive a confirmation shortly."
                }]
            }
        
    # --- ENGINE 1: TRUTH & COMPLIANCE ---
    perjury_triggers = ["real person", "real human", "live person", "not a robot"]
    lies_detected = []
    
    for trigger in perjury_triggers:
        if trigger in transcript_text:
            # Check for honest admissions (e.g., "I'm not a real person")
            # We look for "not", "ai", or "assistant" near the trigger
            start_index = transcript_text.find(trigger)
            context_window = transcript_text[max(0, start_index - 30):start_index]
            
            # If Jade says she is NOT a real person, it's the truth. DO NOT FLAG.
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
        "political_bias": ["vote for", "election is", "right wing", "left wing"],
        "cultural_bias": ["those people", "foreigners", "illegal alien"]
    }

    linguistic_triggers = {
        "language_spanish": ["hola", "gracias", "por favor", "que pasa", "buenos dias"],
        "language_spanglish": ["pero like", "parquear", "confusio", "estoy ready"],
        "language_aave": ["finna", "ion", "trippin", "no cap", "on god", "bet", "fina", "fixin to", "i own know"]
    }
    
    bias_detected = []
    for category, triggers in bias_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                bias_detected.append(f"{category}: {trigger}")

    language_detected = []
    for category, triggers in linguistic_triggers.items():
        for trigger in triggers:
            # Regex ensures 'ion' doesn't flag in words like 'action'
            if re.search(r'\b' + re.escape(trigger) + r'\b', transcript_text):
                language_detected.append(trigger)

    # --- VERDICT LOGIC ---
    status = "PASS"

    if lies_detected:
        status = "CRITICAL FAIL (Lying)"
    elif bias_detected:
        status = "FAIL (Bias Detected)"
    elif sentiment_score < -0.5:
        status = "FAIL (Hostile Tone)"
    elif risk_flags:
        status = "WARN (Risk Flags)"
    elif language_detected:
        status = "PASS (Linguistic Marker Detected)"

    if "FAIL" in status:
        emoji = "🔴"
    elif "WARN" in status:
        emoji = "🟠"
    elif "Linguistic" in status:
        emoji = "🔵"
    else:
        emoji = "🟢"

    # --- REPORTING ---
    # Simplified structure: Verdict + Flat list of all Risks/Flags
    report = {
        "emoji": emoji,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "verdict": status,
        "risks": lies_detected + risk_flags + bias_detected + language_detected
    }

    audit_history.insert(0, report)
    if len(audit_history) > 20:
        audit_history.pop()

    # --- CONSOLE REPORTING ---
    print(f"\n--- 📋 FINAL AUDIT REPORT ---")
    print(f"Result: {emoji} {'Passed' if status == 'PASS' else status}")
    print(f"Timestamp: {report['timestamp']}")
    
    if report['risks']:
        print(f"⚠️ Risks/Flags Detected: {', '.join(report['risks'])}")
    else:
        print(f"✅ No risks identified.")
    print(f"---------------------------\n")

    return report

@app.get("/data")
async def get_data():
    return audit_history

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEnterprise Audit: Global View</title>
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; padding: 20px; }
            h1 { color: #58a6ff; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 10px; }
            .status { font-weight: bold; font-size: 1.2em; }
            .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px; background: #30363d; color: #58a6ff; }
            #monitor { max-width: 800px; margin: 0 auto; }
        </style>
        <script>
            async function fetchData() {
                try {
                    const response = await fetch('/data');
                    const data = await response.json();
                    const container = document.getElementById('log-container');
                    container.innerHTML = ''; 
                    data.forEach(log => {
                        let riskTags = '';
                        log.risks.forEach(risk => {
                            riskTags += `<span class="tag">${risk}</span>`;
                        });

                        const div = document.createElement('div');
                        div.className = 'card';
                        div.innerHTML = `
                            <div class="status">${log.emoji} ${log.verdict} <span style="float:right; font-size:0.8em">${log.timestamp}</span></div>
                            <div class="tags">${riskTags}</div>
                        `;
                        container.appendChild(div);
                    });
                } catch (e) { console.error("Error", e); }
            }
            setInterval(fetchData, 2000); // Polling every 2 seconds to reduce log noise
            fetchData();
        </script>
    </head>
    <body>
        <h1>🛡️ NEnterprise Audit: Global View</h1>
        <div id="monitor"><div id="log-container"></div></div>
    </body>
    </html>
    """
