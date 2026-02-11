import os
import json
import psycopg2
import requests
from datetime import datetime, timedelta, timezone
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from googleapiclient.discovery import build
from google.oauth2 import service_account

AUDIT_URL = os.getenv("AUDIT_DESTINATION")

def dispatch_audit(payload):
    if AUDIT_URL:
        try:
            requests.post(AUDIT_URL, json=payload, timeout=1.0)
        except Exception:
            pass

# --- 0. THE AUDIT BRIDGE (Option 1 Implementation) ---
def audit_to_ndfe(status, emoji, risks, transcript):
    """Sends audit data to Terminal 1 via network instead of direct import"""
    try:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "emoji": emoji,
            "risks": risks,
            "transcript": transcript,
            "source": "JADE_ASSIST"
        }
        # Dispatches data to the NDFE Brain on Port 8000
        requests.post("https://whitney-untwinned-unfervidly.ngrok-free.dev/audit", json=payload, timeout=0.5)
    except Exception:
        # If Terminal 1 is unavailable, J.A.D.E. Assist continues uninterrupted
        pass

def is_within_office_hours(dt):
    """Tier 1: Hardwired Base Availability Gate (EST Optimized)"""
    # Force dt into EST (-5 hours) for consistency with J.A.D.E. booking
    est_tz = timezone(timedelta(hours=-5))
    dt_est = dt.astimezone(est_tz)

    # Monday (0) to Saturday (5): 9:00 AM - 8:00 PM EST
    if 0 <= dt_est.weekday() <= 5:
        return 9 <= dt_est.hour < 20
    # Sunday (6): 12:00 PM - 4:00 PM EST
    if dt_est.weekday() == 6:
        return 12 <= dt_est.hour < 16
    return False

# --- 1. THE SOVEREIGN VAULT (POSTGRESQL) ---
# Hardwired Local Link - Try this first
DATABASE_URL = "postgresql://postgres:aKDmjJPDwCCLqAGxdJfGXFHTSRbKrmkQ@caboose.proxy.rlwy.net:34965/railway"

def get_db_connection():
    """Safety Valve: Prevents the app from crashing if the Vault is offline"""
    try:
        # If the URL is still a placeholder, don't even try to connect
        if "your_actual_postgresql" in DATABASE_URL:
            return None
        return psycopg2.connect(DATABASE_URL, sslmode='prefer')
    except Exception as e:
        print(f"⚠️ VAULT OFFLINE: {e}")
        return None

def init_db():
    """Initializes the Permanent Audit Ledger - Now Crash-Proof"""
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
        else:
            print("⚠️ VAULT OFFLINE: Local Forensic Mode Active.")
    except Exception as e:
        print(f"⚖️ INIT ERROR: {e}")

# --- 2. JADE MULTI-NODE DISPATCHER CONFIG ---
JADE_NODES = {
    "tier_1": [
        "be944a6b50cab5a5ddc8d3c91f68bf91eb6a399df256e8e829e5545c6f762321@group.calendar.google.com", 
        "070a3fd6dcf01ae92d144af1f958fd20fef589da9fc06e5c4e5674a6925e49c5@group.calendar.google.com", 
        "96aba65ad0d442d90ceef58ecba225ca8cee4f5b863dc2932989e924df89615ca@group.calendar.google.com", 
        "05f1451855a88c7d3f8c5ebdcaa408615fef2410df2bfba35331f66b000e9da6@group.calendar.google.com", 
        "72b73a392ecf7e616b609f5ca8311e3b05ee4642d467b3e0d2e4d506e9b3a01d@group.calendar.google.com"
    ],
    "tier_2": [
        "fbc5bb44c66ae6d5350e499f68c272aa1e488c1cf2367f390fb635c4878c9e0f@group.calendar.google.com", 
        "4dfd9061c9cdb93f48dcc3f42ca322472d514ad37d346895cda403c4f81b1241@group.calendar.google.com", 
        "46a8327e5b24ab39ed1f8bde6099aeef3fc9bc6d924c80a5c93768b4c7e2f1fe@group.calendar.google.com", 
        "8758396170bebd88aa0289452928d3badfd6c7c21a1db855a016ec8d8355ab1e@group.calendar.google.com", 
        "4d6589910ad189591a4dc68be27d78dd5a5a843a04a91903c655773d0b999bf0@group.calendar.google.com"
    ],
    "tier_3": [
        "0a97928938960d1260e9c1a339237103afea6f1e91d5166b97752a60303abc42@group.calendar.google.com", 
        "d4aea929efe17006381c17497a20d48bf1cb2c78a6d226369559ba9433284ea9@group.calendar.google.com"
    ]
}

# --- 3. APP INITIALIZATION ---
app = FastAPI()
init_db()

@app.post("/audit")
async def relay_audit(request: Request):
    """Bridge Relay: Receives cloud dispatches and pushes to Terminal 1"""
    try:
        data = await request.json()
        print(f"📥 VAULT RECEIPT: Dispatching to Local Monitor...")
        
        # This relays the data to your Terminal 1 (Monitor) on Port 8000
        # Replace the URL below with your actual Terminal 1 address if different
        requests.post("http://127.0.0.1:8000/audit", json=data, timeout=1.0)
        
        return {"status": "vault_relayed"}
    except Exception as e:
        print(f"❌ RELAY ERROR: {e}")
        return {"status": "relay_failed", "error": str(e)}

def save_to_vault(verdict, emoji, risks, transcript):
    """Writing all NEnterprise interactions to the Permanent Ledger and Audit Bridge"""
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
        
        # Option 1: Trigger the network-based audit instead of a local function call
        audit_to_ndfe(verdict, emoji, risks, transcript)
        
    except Exception as e:
        print(f"⚖️ VAULT ERROR: {e}")
    finally:
        if conn: conn.close()

def check_jade_availability(calendar_id='primary'):
    """Queries JADE Nodes using 3-Tier Logic (Empty Space Detection)"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    try:
        google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Set search window: Now until 7 days out
        now_dt = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        timeMin = now_dt.isoformat() + 'Z'
        timeMax = (now_dt + timedelta(days=7)).isoformat() + 'Z'
        
        # Tier 3: Get all existing busy appointments
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=timeMin, timeMax=timeMax, 
            singleEvents=True, orderBy='startTime'
        ).execute()
        busy_events = events_result.get('items', [])

        available_slots = []
        # Generate 30-minute test slots for the next 7 days
        for day in range(7):
            for hour in range(9, 21):  # Covers the widest possible window (9am-8pm)
                for minute in [0, 30]:
                    test_dt = (now_dt + timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0)

                    # TIER 0: Time-Travel Prevention
                    if test_dt < (now_dt + timedelta(minutes=15)):
                        continue
                        
                    # TIER 1: Check Hardwired Office Hours
                    if is_within_office_hours(test_dt):
                        
                        # TIER 3: Check for Conflicts (Is this slot already booked?)
                        is_busy = False
                        for event in busy_events:
                            start = event['start'].get('dateTime', event['start'].get('date'))
                            end = event['end'].get('dateTime', event['end'].get('date'))
                            ev_start = datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None)
                            ev_end = datetime.fromisoformat(end.replace('Z', '+00:00')).replace(tzinfo=None)
                            
                            # Validates the 1-hour block doesn't overlap an existing event
                            proposed_end = test_dt + timedelta(hours=1)
                            if (test_dt < ev_end) and (proposed_end > ev_start):
                                is_busy = True
                                break                                    
                        if not is_busy:
                            available_slots.append(test_dt.strftime("%a, %b %d at %I:%M %p"))

        # Force the server to use EST for the J.A.D.E. header
        est_now = datetime.now(timezone(timedelta(hours=-5))) 
        today_header = est_now.strftime("Today is %A, %B %d, %Y. Current time is %I:%M %p EST.")
        return f"{today_header} | Available: {', '.join(available_slots[:5])}"

    except Exception as e: 
        print(f"📡 SCHEDULING ERROR: {e}")
        return []

def create_calendar_event(calendar_id, start_time_str):
    """Tier 3 Actuation: Commits the appointment to the Sovereign Ledger"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    try:
        google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Parse the time string JADE sends back (e.g., "Feb 01 at 02:00 PM")
        current_year = datetime.now().year
        dt = datetime.strptime(f"{start_time_str} {current_year}", "%b %d at %I:%M %p %Y")
        
        # Define the EST offset (-5 hours)
        est_tz = timezone(timedelta(hours=-5))
        
        event = {
            'summary': 'H&R Block Consultation | JADE1',
            'description': 'Automated booking via NEnterprise Sovereign Guard.',
            'start': {'dateTime': dt.replace(tzinfo=est_tz).isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': (dt + timedelta(hours=1)).replace(tzinfo=est_tz).isoformat(), 'timeZone': 'America/New_York'}
        }

        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        return event_result.get('htmlLink')
    except Exception as e:
        print(f"📡 BOOKING ERROR: {e}")
        return None

# --- 4. THE CORE FORENSIC & DISPATCH ENGINE ---
@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    # SOVEREIGN GUARD: End-of-Session Integrity
    if not transcript_text.strip():
        if call_status in ["ended", "completed"]:
            save_to_vault("PASS", "✅", ["Session Closed Cleanly"], "Heartbeat Only")
            return {"status": "archived"}
        return {"status": "monitoring_active"}

    # 🏛️ 1. LINGUISTIC & SELF-CORRECTION DETECTION
    user_requested_spanish = any(w in transcript_text for w in ["spanish speaker", "habla español", "speak spanish"])
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor", "espanol"])
    self_correction = any(phrase in transcript_text for phrase in ["apologize for the confusion", "allow me to check"])
    spanish_loop = transcript_text.count("continuar esta conversación en español") > 1

    # 🏛️ 2. IDENTITY & DISPOSITION DETECTION
    double_greeting = transcript_text.count("hi this is jay") > 1
    is_hang_up = call_status in ["ended", "completed"]

    # 🏛️ 3. TIER TRIAGE
    tier_level = "Tier 3 (Bilingual)" if (user_requested_spanish or is_spanish) else "Tier 1 (Standard)"

# --- 4. THE CORE FORENSIC & DISPATCH ENGINE (REWORKED) ---
@app.post("/audit-call")
async def audit_call(request: Request):
    # Record start time for Latency Tracking
    start_time = datetime.now()
    
    data = await request.json()
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    # SOVEREIGN GUARD: End-of-Session Integrity
    if not transcript_text.strip():
        if call_status in ["ended", "completed"]:
            save_to_vault("ACTION: SESSION_CLOSED_CLEANLY", "⚖️", ["Session Closed Cleanly"], "Heartbeat Only")
            return {"status": "archived"}
        return {"status": "monitoring_active"}

    # 🏛️ 1. LINGUISTIC DETECTION
    user_requested_spanish = any(w in transcript_text for w in ["spanish speaker", "habla español", "speak spanish"])
    user_requested_english = any(w in transcript_text for w in ["speak english", "in english", "english speaker"])
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor", "espanol"])
    
    # 🏛️ 2. IDENTITY & DISPOSITION DETECTION
    double_greeting = transcript_text.count("hi this is jay") > 1
    is_hang_up = call_status in ["ended", "completed"]
    
    # 🏛️ 3. SCHEDULING & TASK DETECTION
    # Success is confirmed if we see keywords + lack of failure phrases
    scheduling_success = any(k in transcript_text for k in ["confirmed", "scheduled", "appointment set", "got you down"])
    scheduling_failure = any(phrase in transcript_text for phrase in ["technical difficulties", "issue booking", "try again later", "couldn't book"])
    appt_cancelled = "cancel" in transcript_text and "confirmed" in transcript_text

    # 🏛️ 4. HALLUCINATION & INTEGRITY DETECTION
    hallucination_context = "i did not mention" in transcript_text or "as i mentioned" in transcript_text
    # Task Amnesia: Dropping the ball mid-call (Generic greeting after significant dialogue)
    task_amnesia = "how can i help you" in transcript_text and len(transcript_text) > 150
    # Identity Collapse: Forgetting who/what she is
    identity_collapse = any(phrase in transcript_text for phrase in ["who is this", "what is the purpose", "i am a human", "why did i call"])
    # Self-Correction: AI catching its own mistake
    self_correction = any(phrase in transcript_text for phrase in ["i apologize, i misspoke", "allow me to correct that", "i am sorry, i meant"])
    # Availability Hallucination: This would be expanded with logic comparing to JADE_NODES
    hallucination_availability = False # Placeholder for node-comparison logic

    # 🏛️ 5. PERFORMANCE (LATENCY) TRACKING
    processing_time = (datetime.now() - start_time).total_seconds()
    latency_violation = processing_time > 2.5

    # 🏛️ 6. TIER TRIAGE
    tier_level = "Tier 3 (Bilingual)" if (user_requested_spanish or is_spanish) else "Tier 1 (Standard)"

    # 🏛️ 7. ACTION LOG COMPILATION (PORT 8001 DASHBOARD)
    # We collect all actions performed into this list
    action_log = [f"Tier: {tier_level}"]
    
    # Task Actions
    if scheduling_success: action_log.append("✅ scheduling_success")
    if scheduling_success: action_log.append("✅ appt_scheduled")
    if scheduling_failure: action_log.append("❌ scheduling_failure")
    if appt_cancelled: action_log.append("❌ appt_cancelled")
    if any(k in transcript_text for k in ["schedule", "appointment"]) and not (scheduling_success or scheduling_failure):
        action_log.append("📡 DISPATCH")

    # Integrity & Hallucination (Orange Circles)
    if hallucination_context: action_log.append("🟠 HALLUCINATION_CONTEXT")
    if task_amnesia: action_log.append("🟠 HALLUCINATION_AMNESIA")
    if identity_collapse: action_log.append("🟠 HALLUCINATION_IDENTITY")
    if hallucination_availability: action_log.append("🟠 HALLUCINATION_AVAILABILITY")
    
    # Logic & Flow (Purple Circles)
    if self_correction: action_log.append("🟣 SELF_CORRECTION")
    if double_greeting: action_log.append("🟣 IDENTITY_REPETITION")

    # Performance & Language
    if latency_violation: action_log.append("⏳ LATENCY_VIOLATION")
    if user_requested_spanish: action_log.append("🔵 ENGLISH-SPANISH")
    if user_requested_english: action_log.append("🔵 SPANISH-ENGLISH")

    # 🏛️ 8. NEUTRAL STATUS MAPPING (Port 8001 - No Pass/Fail)
    if scheduling_failure or appt_cancelled:
        status, emoji = "ACTION: TASK_FAILED_OR_CANCELLED", "❌"
    elif scheduling_success:
        status, emoji = "ACTION: APPT_CONFIRMED", "✅"
    elif identity_collapse or task_amnesia or hallucination_context:
        status, emoji = "ACTION: INTEGRITY_RISK_DETECTED", "🟠"
    else:
        status, emoji = "ACTION: MONITORING_SESSION", "⚖️"

    # 🏛️ 9. DUAL BROADCAST
    # Port 8000 receives this data to perform the "Judge" function (Pass/Fail)
    try:
        audit_to_ndfe(status, emoji, action_log, transcript_text)
    except Exception as e:
        print(f"📡 NDFE BRIDGE OFFLINE: {e}")

    # Port 8001 records the flight data neutrally
    save_to_vault(status, emoji, action_log, transcript_text)

    return {
        "status": "logged", 
        "action": status, 
        "tier": tier_level
    }

@app.get("/data", response_class=HTMLResponse)
async def get_dashboard():
    """Renders the Sovereign Vault as a high-fidelity audit ledger"""
    conn = get_db_connection()
    
    # NEW: If database is offline, show a clean "Offline" message instead of crashing
    if conn is None:
        return f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>🏛️ NEnterprise Global Ledger</h1>
                <div style="background: #fff3cd; color: #856404; padding: 20px; border-radius: 10px; display: inline-block;">
                    <strong>STATUS: OFFLINE</strong><br>
                    The Sovereign Vault is currently in Local Forensic Mode. 
                    <br>Live database logs are unavailable.
                </div>
                <p><a href="/data">Retry Connection</a></p>
            </body>
        </html>
        """

    try:
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
            <head>
                <title>Audit Global Ledger</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f4f7f6; }}
                    .container {{ max-width: 1100px; margin: 50px auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    header {{ border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th {{ text-align: left; background: #f8f9fa; padding: 15px; color: #555; text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <header>
                        <h1 style="margin: 0; color: #333;">NEnterprise Audit <span style="font-weight: 300; color: #999;">Global Ledger</span></h1>
                        <div style="background: #2e7d32; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8em;">SYSTEM LIVE</div>
                    </header>
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 50px;">Status</th>
                                <th>Verdict</th>
                                <th>Timestamp</th>
                                <th>Forensic Risks Detected</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error loading ledger: {e}</h1>"

# --- 6. SYSTEM IGNITION ---
if __name__ == "__main__":
    import uvicorn
    print("🚀 NEnterprise Sovereign Guard: Launching Interface...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
