import re
import os
import json
import psycopg2
import requests
from datetime import datetime, timedelta, timezone
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from textblob import TextBlob
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- 0. CONFIGURATION & AUDIT BRIDGE ---
AUDIT_URL = os.getenv("AUDIT_DESTINATION")
DATABASE_URL = "postgresql://postgres:aKDmjJPDwCCLqAGxdJfGXFHTSRbKrmkQ@caboose.proxy.rlwy.net:34965/railway"

def audit_to_ndfe(status, emoji, risks, transcript):
    """Sends audit data to Port 8000 Monitor for real-time forensic analysis"""
    try:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "emoji": emoji,
            "risks": risks,
            "transcript": transcript,
            "source": "JADE_ASSIST"
        }
        requests.post("http://127.0.0.1:8000/audit", json=payload, timeout=0.5)
    except Exception:
        pass

# --- 1. THE SOVEREIGN VAULT (POSTGRESQL) ---
def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='prefer')
    except Exception as e:
        print(f"⚠️ VAULT OFFLINE: {e}")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sovereign_vault (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verdict TEXT,
                    emoji TEXT,
                    risks TEXT[],
                    transcript TEXT
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ VAULT CONNECTED")
    except Exception as e:
        print(f"⚖️ INIT ERROR: {e}")

# --- 2. JADE MULTI-NODE DISPATCHER CONFIG ---
JADE_NODES = {
    "tier_1": ["be944a6b50cab5a5ddc8d3c91f68bf91eb6a399df256e8e829e5545c6f762321@group.calendar.google.com"],
    "tier_2": ["fbc5bb44c66ae6d5350e499f68c272aa1e488c1cf2367f390fb635c4878c9e0f@group.calendar.google.com"],
    "tier_3": ["0a97928938960d1260e9c1a339237103afea6f1e91d5166b97752a60303abc42@group.calendar.google.com"]
}

# --- 3. APP INITIALIZATION ---
app = FastAPI()
init_db()

def save_to_vault(verdict, emoji, risks, transcript):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sovereign_vault (verdict, emoji, risks, transcript) VALUES (%s, %s, %s, %s)",
            (verdict, emoji, risks, transcript)
        )
        conn.commit()
        cur.close()
        audit_to_ndfe(verdict, emoji, risks, transcript)
    except Exception as e:
        print(f"⚖️ VAULT ERROR: {e}")
    finally:
        if conn: conn.close()

def check_jade_availability(calendar_id='primary'):
    """Queries JADE Nodes using dynamic empty space detection (No hardwired hours)"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    try:
        google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        now_dt = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        timeMin = now_dt.isoformat() + 'Z'
        timeMax = (now_dt + timedelta(days=7)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=timeMin, timeMax=timeMax, 
            singleEvents=True, orderBy='startTime'
        ).execute()
        busy_events = events_result.get('items', [])

        available_slots = []
        for day in range(7):
            for hour in range(24): # Now checking full 24-hour availability
                for minute in [0, 30]:
                    test_dt = (now_dt + timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if test_dt < (now_dt + timedelta(minutes=15)):
                        continue
                        
                    is_busy = False
                    for event in busy_events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        ev_start = datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None)
                        ev_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00')).replace(tzinfo=None)
                        if (test_dt < ev_end) and (test_dt + timedelta(hours=1) > ev_start):
                            is_busy = True
                            break                                    
                    if not is_busy:
                        available_slots.append(test_dt.strftime("%a, %b %d at %I:%M %p"))

        est_now = datetime.now(timezone(timedelta(hours=-5))) 
        return f"Today is {est_now.strftime('%A, %B %d, %Y')}. Current time is {est_now.strftime('%I:%M %p')} EST. | Available: {', '.join(available_slots[:5])}"
    except Exception as e: 
        return []

# --- 4. THE CORE FORENSIC & DISPATCH ENGINE ---
@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    if not transcript_text.strip():
        if call_status == "ended":
            save_to_vault("PASS", "✅", ["Session Closed Cleanly"], "Heartbeat Only")
            return {"status": "archived"}
        return {"status": "monitoring_active"}

    # 🏛️ LINGUISTIC & TIER DETECTION
    user_requested_spanish = any(p in transcript_text for p in ["spanish speaker", "habla español", "speak spanish"])
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor", "espanol"])
    
    # 🏛️ FORENSIC MARKERS: Hallucination & Self-Correction Detection
    hallucination_detected = "friend's a god editor" in transcript_text
    self_correction = any(phrase in transcript_text for phrase in ["apologize for the confusion", "allow me to check", "i said i wanted"])

    # Assign Tier: Bilingual requests trigger Tier 3
    if user_requested_spanish or is_spanish:
        tier = 3
        found_tier = "Tier 3 (Bilingual)"
    elif "forensic audit" in transcript_text:
        tier = 2
        found_tier = "Tier 2 (Forensic)"
    else:
        tier = 1
        found_tier = "Tier 1 (Standard)"

    # 🏛️ DISPATCH & SCHEDULING LOGIC
    if any(k in transcript_text for k in ["schedule", "appointment", "calendar", "available"]):
        # Removed hardwired hours for dynamic Vapi parameter control
        forensic_risks = [f"Cascaded to {found_tier}", "Dynamic Availability Active"]
        
        if self_correction:
            forensic_risks.append("⚖️ SELF_CORRECTION_LOGGED")
        if hallucination_detected:
            forensic_risks.append("⚠️ HALLUCINATION_DETECTED")

        status = "PASS (Corrected)" if self_correction else "DISPATCH"
        emoji = "⚖️" if self_correction else "📡"

        save_to_vault(status, emoji, forensic_risks, transcript_text)
        return {"status": "scheduling", "availability_summary": f"Matched with {found_tier} Executive."}

    # Final Monitored Pass using Circle UI
    status = "PASS (Linguistic)" if tier == 3 else "PASS"
    emoji = "🔵" if tier == 3 else "🟢"
    save_to_vault(status, emoji, [f"Monitored on {found_tier}"], transcript_text)
    return {"status": "monitored", "verdict": status}

@app.get("/data", response_class=HTMLResponse)
async def get_dashboard():
    """Renders the Audit Global Ledger (Port 8001)"""
    conn = get_db_connection()
    if conn is None:
        return "<h1>🏛️ VAULT OFFLINE</h1>"
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT emoji, verdict, timestamp, risks FROM sovereign_vault ORDER BY timestamp DESC LIMIT 50")
    logs = cur.fetchall()
    cur.close()
    conn.close()

    rows = "".join([f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 15px; text-align: center; font-size: 1.2em;">{log['emoji']}</td>
            <td style="padding: 15px; font-weight: bold; color: {'#d32f2f' if 'FAIL' in log['verdict'] else '#2e7d32' if 'PASS' in log['verdict'] else '#333'};">{log['verdict']}</td>
            <td style="padding: 15px; color: #666;">{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td style="padding: 15px;">{' '.join([f'<span style="background:#f0f0f0; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:0.85em;">{r}</span>' for r in log['risks']])}</td>
        </tr>
    """ for log in logs])
    return f"""
    <html>
        <head><title>Audit Global Ledger</title></head>
        <body style="font-family: sans-serif; margin: 20px;">
            <h1>NEnterprise Audit Global Ledger</h1>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="text-align: left; background: #eee;">
                        <th>Status</th><th>Verdict</th><th>Timestamp</th><th>Forensic Risks</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
