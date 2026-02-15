import re
import os
import json
from tkinter import font
from turtle import width
import psycopg2
import requests
import urllib3
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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def audit_to_ndfe(status, emoji, risks, transcript, shared_id):
    try:
        est_tz = timezone(timedelta(hours=-5))
        payload = {
            "shared_id": shared_id, # <--- Linkage DNA
            "timestamp": datetime.now(est_tz).isoformat(),
            "status": status,
            "emoji": emoji,
            "risks": risks,
            "transcript": transcript,
            "source": "JADE_ASSIST"
        }
        # Dispatches data to the NDFE Brain on Port 8000
        requests.post(
            "http://127.0.0.1:8000/audit", 
            json=payload, 
            timeout=0.5, 
            verify=False
        )
    except Exception as e:
        print(f"📡 BRIDGE ERROR: {e}")
        pass

def is_within_office_hours(dt):
    """Tier 1: Hardwired Base Availability Gate (EST Optimized)"""
    # Force dt into EST (-5 hours) for consistency with J.A.D.E. booking
    est_tz = timezone(timedelta(hours=-5))
    dt_est = dt.astimezone(est_tz)
    if 0 <= dt_est.weekday() <= 5:
        return 9 <= dt_est.hour < 20
    if dt_est.weekday() == 6:
        return 12 <= dt_est.hour < 16
    return False

# --- 1. THE SOVEREIGN VAULT (POSTGRESQL) ---
DATABASE_URL = "postgresql://postgres:aKDmjJPDwCCLqAGxdJfGXFHTSRbKrmkQ@caboose.proxy.rlwy.net:34965/railway"

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
    try:
        data = await request.json()
        print(f"📥 VAULT RECEIPT: Dispatching to Local Monitor...")

        # V1 REDUNDANCY: Use HTTPS but bypass the version check
        try:
            requests.post(
                "http://whitney-untwinned-unfervidly.ngrok-free.dev/audit", 
                json=data, 
                timeout=0.1, 
                verify=False
            )
        except:
            pass 

        return {"status": "vault_relayed"} 
    except Exception as e:
        print(f"❌ RELAY ERROR: {e}")
        return {"status": "relay_failed", "error": str(e)}

def save_to_vault(verdict, emoji, risks, transcript, shared_id):
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
        # This triggers the bridge to Port 8000 with the linked ID
        audit_to_ndfe(verdict, emoji, risks, transcript, shared_id)
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

        # CORRECTION #2: Strict EST Truth Guard
        est_tz = timezone(timedelta(hours=-5))
        now_est = datetime.now(est_tz)
        
        # We use now_est directly for the API to ensure no UTC drift
        timeMin = now_est.isoformat() 
        timeMax = (now_est + timedelta(days=7)).isoformat()
        
        # Tier 3: Get all existing busy appointments
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=timeMin, timeMax=timeMax, 
            singleEvents=True, orderBy='startTime'
        ).execute()
        busy_events = events_result.get('items', [])

        available_slots = []
        # Generate 30-minute test slots for the next 7 days
        for day in range(7):
            for hour in range(9, 21):
                for minute in [0, 30]:
                    # Create the test slot naive (no timezone) to match the loop logic
                    test_dt = (now_est + timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0).replace(tzinfo=None)
                    
                    # CORRECTION #2 (Anchor) & #3 (Buffer)
                    # Create a naive 'now' from our EST anchor
                    now_naive = now_est.replace(tzinfo=None)
                    
                    # TIER 0: 30-Minute Buffer Enforcement (Correction #3)
                    if test_dt < (now_naive + timedelta(minutes=30)):
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

        # CORRECTION #4 & #5: Linguistic Constraint & Date-Lock Awareness
        if not available_slots:
            today_header = now_est.strftime("Today is %A, %B %d, %Y. It is currently after office hours (%I:%M %p EST).")
            return f"{today_header} | Next Available Slots: No more slots today. Check tomorrow."
        else:
            today_header = now_est.strftime("Today is %A, %B %d, %Y. Current time is %I:%M %p EST.")
            return f"{today_header} | Available: {', '.join(available_slots[:5])}"

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

def delete_calendar_event(calendar_id, start_time_str):
    """Version 3 Actuation: Removes the original slot to prevent double-booking"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    try:
        google_creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(google_creds_json, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Parse the time JADE wants to remove
        current_year = datetime.now().year
        dt = datetime.strptime(f"{start_time_str} {current_year}", "%b %d at %I:%M %p %Y")
        time_min = dt.isoformat() + 'Z'
        time_max = (dt + timedelta(minutes=1)).isoformat() + 'Z'

        # Find the specific event at that time
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=time_min, timeMax=time_max, singleEvents=True
        ).execute()
        events = events_result.get('items', [])

        for event in events:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            return True
    except Exception as e:
        print(f"📡 DELETION ERROR: {e}")
        return False

# --- 4. THE CORE FORENSIC & DISPATCH ENGINE ---
@app.post("/audit-call")
async def audit_call(request: Request):
    # 1. INITIALIZE & LINKAGE DNA
    start_time = datetime.now()
    shared_id_base = int(start_time.timestamp()) # <--- Shared ID Base Created
    status = "ACTION: MONITORING_SESSION"
    emoji = "⚖️"
    action_log = []
    
    # 2. EXTRACT DATA
    data = await request.json()
    call_status = data.get('message', {}).get('call', {}).get('status')
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()

    if not transcript_text.strip():
        if call_status in ["ended", "completed"]:
            save_to_vault("PASS", "✅", ["Session Closed Cleanly"], "Heartbeat Only", shared_id_base)
            return {"status": "archived"}
        return {"status": "monitoring_active"}

    # 🏛️ Forensic Triage
    user_requested_spanish = any(w in transcript_text for w in ["spanish speaker", "speak spanish"])
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "espanol"])
    scheduling_success = "confirmed" in transcript_text or "got you down" in transcript_text
    scheduling_failure = "technical difficulties" in transcript_text
    appt_cancelled = "cancel" in transcript_text and "confirmed" in transcript_text

    # 🏛️ Forensic Triage & Linguistic Audit
    user_requested_spanish = any(w in transcript_text for w in ["spanish speaker", "speak spanish"])
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "espanol"])
    
    # NEW: Detection for non-EST timezone mentions
    timezone_drift = any(w in transcript_text for w in ["utc", "gmt", "coordinated universal time"])
    
    scheduling_success = "confirmed" in transcript_text or "got you down" in transcript_text
    scheduling_failure = "technical difficulties" in transcript_text
    appt_cancelled = "cancel" in transcript_text and "confirmed" in transcript_text

    # Integrity & Flow Markers
    hallucination_context = "i did not mention" in transcript_text or "as i mentioned" in transcript_text
    task_amnesia = "how can i help you" in transcript_text and len(transcript_text) > 150
    identity_collapse = any(phrase in transcript_text for phrase in ["who is this", "purpose of the call"])
    self_correction = "apologize for the confusion" in transcript_text
    double_greeting = transcript_text.count("hi this is jay") > 1
    latency_violation = (datetime.now() - start_time).total_seconds() > 2.5

    tier_level = "Tier 3 (Bilingual)" if (user_requested_spanish or is_spanish) else "Tier 1 (Standard)"
    action_log = [f"Tier: {tier_level}"]
    
    if scheduling_success: action_log.append("✅ scheduling_success")
    if scheduling_failure: action_log.append("❌ scheduling_failure")
    if appt_cancelled: action_log.append("❌ appt_cancelled")
    if hallucination_context: action_log.append("🟠 HALLUCINATION_CONTEXT")
    if task_amnesia: action_log.append("🟠 HALLUCINATION_AMNESIA")
    if identity_collapse: action_log.append("🟠 HALLUCINATION_IDENTITY")
    if self_correction: action_log.append("🟣 SELF_CORRECTION")
    if double_greeting: action_log.append("🟣 IDENTITY_REPETITION")
    if latency_violation: action_log.append("⏳ LATENCY_VIOLATION")
    if user_requested_spanish and "proceed in english" in transcript_text:
        action_log.append("🔴 TIER_DISPLACEMENT: STUCK_IN_TIER_1")
    if user_requested_spanish and not is_spanish:
        action_log.append("🔵 LINGUISTIC_DNA: BILINGUAL_REQUEST_PENDING")

    # Status Mapping & Governance Flags
    if scheduling_failure or appt_cancelled:
        status, emoji = "ACTION: TASK_FAILED_OR_CANCELLED", "❌"
    elif timezone_drift:
        # This resolves the Pylance 'not accessed' warning
        action_log.append("🚩 TIMEZONE_DISCREPANCY: JADE_MENTIONED_UTC")
        status, emoji = "ACTION: INTEGRITY_RISK", "🟠"
    elif scheduling_success:
        status, emoji = "ACTION: APPT_CONFIRMED", "✅"
    elif any([hallucination_context, task_amnesia, identity_collapse]):
        status, emoji = "ACTION: INTEGRITY_RISK", "🟠"
    else:
        status, emoji = "ACTION: MONITORING_SESSION", "⚖️"

    # Detect verbal confirmation of "moving" or "changing" an appointment
    verbal_move_intent = any(w in transcript_text for w in ["move", "change", "instead of", "actually"])
    verbal_confirmation = any(w in transcript_text for w in ["confirmed", "got you down", "is set"])
    
    # Dishonesty Flag: Jade says it's "moved," but no deletion event triggered
    # (Checking for the absence of the cancel flag)
    dishonesty_flag = verbal_move_intent and verbal_confirmation and not appt_cancelled

    # 1. GENERATE SYSTEM TRUTH (Dynamic)
    est_now = datetime.now(timezone(timedelta(hours=-5)))
    correct_tomorrow = (est_now + timedelta(days=1)).strftime("%B %d").lower() # e.g., "february 12"

    # 2. EXTRACT AI MENTION (Dynamic)
    # Using re to find any month/day pattern in the transcript (e.g., "february 13")
    date_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}"
    ai_date_mention = re.search(date_pattern, transcript_text)
    mentioned_date = ai_date_mention.group(0) if ai_date_mention else None

    # 3. AUDIT THE MISMATCH
    # Triggered if Jade mentions a date and says "tomorrow", but it doesn't match the system date
    time_hallucination = ("tomorrow" in transcript_text and 
                          mentioned_date and 
                          mentioned_date != correct_tomorrow)

    if time_hallucination:
        action_log.append(f"🟠 TIME_HALLUCINATION: AI_SAID_{mentioned_date}_EXPECTED_{correct_tomorrow}")
        status, emoji = "ACTION: INTEGRITY_RISK", "🟠"
        
        # Self-Healing: Use the WRONG date found in the transcript as the target for deletion
        # This removes the duplicate/hallucinated entry Jade just created
        target_timestamp = f"{mentioned_date.title()} at 1:00 PM"
        cleanup_success = delete_calendar_event("primary", target_timestamp)

    # Version 3: Dynamic Self-Healing Actuation
    if dishonesty_flag:
        # 1. DYNAMIC EXTRACTION: Finding the 'Move-From' date in the transcript
        # We use re to find mentions of days (thursday, friday, etc.) near 'cancel' or 'move'
        day_match = re.search(r"(?:cancel|move|instead of|from)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", transcript_text)
        time_match = re.search(r"(\d{1,2})\s*(?:am|pm)", transcript_text)
        
        # 2. VARIABLE ASSIGNMENT: Mapping the target
        # Defaulting to the current mentioned day if a match is found
        target_day = day_match.group(1).capitalize() if day_match else "Thursday" 
        target_time = time_match.group(0).upper() if time_match else "11:00 AM"
        
        # Convert 'Thursday' to 'Feb 12' logic (simplified for this example)
        # In a full v3, this would use a date parser
        target_timestamp = f"Feb 12 at {target_time}" 
        
        action_log.append(f"🧹 SELF_HEALING: TARGETING {target_timestamp}")
        
        # 3. EXECUTION: Calling the tool with dynamic variables
        cleanup_success = delete_calendar_event("primary", target_timestamp)
        
        if cleanup_success:
            action_log.append("🧹 SELF_HEALING: SLOT_REMOVED_SUCCESSFULLY")
            status, emoji = "ACTION: APPT_MOVED_CLEANLY", "🔄"
        else:
            action_log.append("⚠️ SELF_HEALING_FAILED: SLOT_NOT_FOUND")

    # Version 4: Absolute Truth Guard
    est_now = datetime.now(timezone(timedelta(hours=-5)))
    tomorrow_truth = (est_now + timedelta(days=1)).strftime("%A, %B %d, %Y")
    
    # Forensic Flag: If Jade says tomorrow is anything OTHER than tomorrow_truth
    if "tomorrow" in transcript_text and tomorrow_truth.lower() not in transcript_text:
        action_log.append(f"🚩 DATE_HALLUCINATION: AI_SAID_WRONG_DATE")
        # Self-Healing: Force a cleanup of whatever hallucinated date she just booked
        cleanup_success = delete_calendar_event("primary", f"{mentioned_date.title()} at 12:00 PM")

    # Using re to detect complex rescheduling patterns for the Dishonesty Flag
    reschedule_pattern = r"(move|change|instead of|actually).*(appointment|time|slot)"
    verbal_move_intent = bool(re.search(reschedule_pattern, transcript_text))

    # Using TextBlob to audit the user's sentiment/frustration
    analysis = TextBlob(transcript_text)
    user_frustration = analysis.sentiment.polarity < -0.3
    
    if user_frustration:
        action_log.append("🚩 USER_FRUSTRATION_DETECTED")

    # V1 REDUNDANCY: Forces P8000 to update even if forensic logic is slow
    try:
        requests.post("http://whitney-untwinned-unfervidly.ngrok-free.dev/audit", json=data, timeout=0.1)
    except:
        pass

# --- 3. ENHANCED LINKED DATA PAYLOAD ---
    audit_payload = {
        "shared_id": shared_id_base,
        "transcript": transcript_text,
        "result": "PASS" if "✅" in emoji else "FAIL" if "❌" in emoji else "MONITOR",
        "jade_flags": action_log 
    }

    # --- 4. DISPATCH WITH LINKED ID ---
    try:
        requests.post("http://127.0.0.1:8000/audit", json=audit_payload, timeout=0.1)
    except:
        pass

    save_to_vault(status, emoji, action_log, transcript_text, shared_id_base)
    
    return {
        "status": "monitored", 
        "verdict": status, 
        "shared_id": shared_id_base,
        "tier": tier_level
    }

import requests

def send_to_ndfe_live(call_data):
    """Sends live call transcripts to the Forensic Monitor."""
    url = "http://127.0.0.1:8000/process_audit" # Ensure this matches your route
    try:
        response = requests.post(url, json=call_data)
        if response.status_code == 200:
            print("✅ Forensic Audit Updated in Real-Time")
    except Exception as e:
        print(f"❌ Failed to reach NDFE: {e}")

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

        rows = ""
        for log in logs:
            # Reconstruct the ID number safely
            nent_id_num = int(log['timestamp'].timestamp())
            
            # Build the row one by one
            rows += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 15px; text-align: center; font-size: 1.2em;">{log['emoji']}</td>
                <td style="padding: 15px; font-weight: bold; color: {'#d32f2f' if 'FAIL' in log['verdict'] else '#2e7d32' if 'PASS' in log['verdict'] else '#333'};">{log['verdict']}</td>
                <td style="padding: 15px;">
                    <div style="font-weight: bold; color: #2c3e50;">NENT-{nent_id_num} (8001 RELAY)</div>
                    <div style="font-size: 0.85em; color: #666; font-family: monospace;">{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                </td>
                <td style="padding: 15px;">{' '.join([f'<span style="background:#f0f0f0; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:0.85em;">{r}</span>' for r in log['risks']])}</td>
            </tr>
            """

        return f"""
        <html>
            <head>
                <title>Audit Global Ledger</title>
                <style>
                    body { font: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f4f7f6; }
                    .container { max-width: 1400px; margin: 50px auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
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
                            <th style="width: 80px;">Status</th>
                            <th style="width: 120px;">Verdict</th>
                            <th style="width: 280px;">timestamp/id</th>
                            <th>Forensic Risks Detected</th> </tr>
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
