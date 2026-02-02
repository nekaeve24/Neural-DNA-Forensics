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
        requests.post("http://localhost:8000/audit", json=payload, timeout=0.5)
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
        if call_status == "ended":
            save_to_vault("PASS", "✅", ["Session Closed Cleanly"], "Heartbeat Only")
            return {"status": "archived"}
        return {"status": "monitoring_active"}

    # NEW PRIORITY 1: LINGUISTIC DETECTION
    # Detect if the user needs Spanish or a Bilingual Executive first
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor", "spanish", "bilingual", "espanol"])
    
    # NEW PRIORITY 2: TRUTH, COMPLIANCE & COMPLEXITY TRIAGE
    blob = TextBlob(transcript_text)
    complexity_score = sum(2 for word in ["business", "rental", "k-1", "audit", "offshore"] if word in transcript_text)
    if blob.sentiment.polarity < -0.3: complexity_score += 2 # Stress escalation
    
    # ASSIGN TIER (Linguistic needs always override standard complexity for routing)
    if is_spanish:
        tier = 3
    else:
        tier = max(1, min(6, complexity_score))
    
    # TIGHTENED FORENSIC AUDIT: Only triggers on specific user-initiated strings
    perjury_triggers = ["real person", "real human", "live person", "not a robot"]
    lies_detected = [t for t in perjury_triggers if t in transcript_text and "i am an ai" not in transcript_text]
    risk_flags = [w for w in ["scam", "illegal", "fraud", "lawsuit"] if w in transcript_text]

    # Option 1 Modification: Direct local audit markers removed to maintain independence
    detected_markers = [] # Linguistic DNA audit moved to NDFE terminal side

    # ENGINE 2: BIAS & LINGUISTIC AUDIT
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor"])
    language_detected = ["Spanish Marker"] if is_spanish else []
    
    # SCHEDULING TRIGGER: Cascading Multi-Node J.A.D.E. Dispatch
    if any(k in transcript_text for k in ["schedule", "appointment", "calendar", "available"]):
        # Define priority search order based on Tier
        if is_spanish:
            targets = JADE_NODES["tier_3"]
        elif tier == 2:
            targets = JADE_NODES["tier_2"] + JADE_NODES["tier_3"]
        else:
            targets = JADE_NODES["tier_1"] + JADE_NODES["tier_2"] + JADE_NODES["tier_3"]
            
        for node_id in targets:
            slots = check_jade_availability(node_id)
            if slots:
                # Identify which tier the slot was found in
                if node_id in JADE_NODES["tier_3"]:
                    found_tier = "Tier 3 (Bilingual)"
                elif node_id in JADE_NODES["tier_2"]:
                    found_tier = "Tier 2 (Forensic)"
                else:
                    found_tier = "Tier 1 (Standard)"

                has_slots = isinstance(slots, list) and len(slots) > 1
                start_time = slots[1].split(" at ")[1] if has_slots else "9:00 AM"
                        
                is_sunday = has_slots and "Sun" in slots[1]
                end_time = "4:00 PM" if is_sunday else "8:00 PM"           
                
                summary = f"I have matched you with a {found_tier} Executive. Availability is from {start_time} to {end_time}. Slots: {', '.join(slots[1:])}"
                
                save_to_vault("DISPATCH", "📡", [f"Cascaded to {found_tier}", f"Range: {start_time}-{end_time}"], transcript_text)
                return {"status": "scheduling", "options": slots, "availability_summary": summary}

    # ACTUATION TRIGGER: Commits the appointment to the matched Executive's Calendar
    if any(k in transcript_text for k in ["got you down", "appointment confirmed"]):
        time_match = re.search(r'(\d+).*?(\d+[:\d+]*\s*[ap]\.?\s*[m]\.?)', transcript_text)
        if time_match:
            booking_time = time_match.group(0)
            
            # Dynamic ID selection from your list
            final_calendar_id = targets[0] if 'targets' in locals() else JADE_NODES["tier_1"][0]
            
            calendar_link = create_calendar_event(final_calendar_id, booking_time)
            if calendar_link:
                save_to_vault("ACTUATION", "📅", ["Calendar Write Success"], f"Booked on {final_calendar_id}")
                return {"status": "booked", "link": calendar_link}
                
    # ENRICHED LINGUISTIC AUDIT
    # Identifies Model 12 Linguistic DNA for your proprietary auditor
    language_detected = ["SPANISH_DNA_DETECTED"] if is_spanish else []
    
    # FINAL VERDICT LOGIC
    status = "PASS"
    emoji = "🟢"
    if lies_detected: status, emoji = "CRITICAL FAIL (Lying)", "🔴"
    elif risk_flags: status, emoji = "WARN (Risk Flags)", "🟠"
    elif is_spanish: status, emoji = "PASS (Linguistic)", "🔵"

    # CONSOLIDATE ALL FORENSIC DATA
    forensic_payload = detected_markers + lies_detected + risk_flags + language_detected

    # CRITICAL: MOVE THE AUDIT SHOUT ABOVE THE DATABASE SAVE
    # This ensures your NDFE Forensic Monitor (Port 8000) updates instantly
    try:
        audit_to_ndfe(status, emoji, forensic_payload, transcript_text)
    except Exception as e:
        print(f"📡 NDFE BRIDGE OFFLINE: {e}")

    # COMMIT TO PERMANENT VAULT (RAILWAY POSTGRES)
    save_to_vault(status, emoji, forensic_payload, transcript_text)
    
    return {"status": "monitored", "verdict": status}

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
