import re
import os
import json
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from textblob import TextBlob
from googleapiclient.discovery import build
from google.oauth2 import service_account
from forensics import ForensicEngine

# --- 0. ENGINE INITIALIZATION ---
forensic_engine = ForensicEngine()

def is_within_office_hours(dt):
    """Tier 1: Hardwired Base Availability Gate"""
    # Monday (0) to Saturday (5): 9:00 AM - 8:00 PM
    if 0 <= dt.weekday() <= 5:
        return 9 <= dt.hour < 20
    # Sunday (6): 12:00 PM - 4:00 PM
    if dt.weekday() == 6:
        return 12 <= dt.hour < 16
    return False

# --- 1. THE SOVEREIGN VAULT (POSTGRESQL) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is missing!")
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    """Initializes the Permanent Audit Ledger for Institutional Traceability"""
    conn = None
    try:
        conn = get_db_connection()
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
    finally:
        if conn: conn.close()

# --- 2. JADE 1NODE DISPATCHER CONFIG (TESTING ONLY) ---
JADE1_ID = "be944a6b50cab5a5ddc8d3c91f68bf91eb6a399df256e8e829e5545c6f762321%40group.calendar.google.com"

JADE_NODES = {
    "tier_1_2": [JADE1_ID], 
    "tier_3_4": [JADE1_ID], 
    "tier_5_6": [JADE1_ID],           
    "spanish": [JADE1_ID] 
}

# --- 3. APP INITIALIZATION ---
app = FastAPI()
init_db()

def save_to_vault(verdict, emoji, risks, transcript):
    """Writing all NEnterprise interactions to the Permanent Ledger"""
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
        now_dt = datetime.datetime.utcnow()
        timeMin = now_dt.isoformat() + 'Z'
        timeMax = (now_dt + datetime.timedelta(days=7)).isoformat() + 'Z'
        
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
                    test_dt = (now_dt + datetime.timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # TIER 1: Check Hardwired Office Hours (Includes New Sunday 12-4)
                    if is_within_office_hours(test_dt):
                        
                        # TIER 3: Check for Conflicts (Is this slot already booked?)
                        is_busy = False
                        for event in busy_events:
                            start = event['start'].get('dateTime', event['start'].get('date'))
                            end = event['end'].get('dateTime', event['end'].get('date'))
                            ev_start = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None)
                            ev_end = datetime.datetime.fromisoformat(end.replace('Z', '+00:00')).replace(tzinfo=None)
                            
                            if ev_start <= test_dt < ev_end:
                                is_busy = True
                                break
                        
                        if not is_busy:
                            available_slots.append(test_dt.strftime('%b %d at %I:%M %p'))
                            if len(available_slots) >= 5: return available_slots # Return first 5 openings

        return available_slots
    except Exception as e: 
        print(f"📡 SCHEDULING ERROR: {e}")
        return []

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

    # ENGINE 1: TRUTH, COMPLIANCE & COMPLEXITY TRIAGE
    blob = TextBlob(transcript_text)
    complexity_score = sum(2 for word in ["business", "rental", "k-1", "audit", "offshore"] if word in transcript_text)
    if blob.sentiment.polarity < -0.3: complexity_score += 2 # Stress escalation
    
    tier = max(1, min(6, complexity_score))
    
    perjury_triggers = ["real person", "real human", "live person", "not a robot"]
    lies_detected = [t for t in perjury_triggers if t in transcript_text]
    risk_flags = [w for w in ["scam", "illegal", "fraud", "lawsuit"] if w in transcript_text]

    # NEW: Run the Model 12 Audit to detect "Linguistic DNA" (parquear, ion, etc.)
    detected_markers = forensic_engine.model_12_audit(transcript_text)

    # ENGINE 2: BIAS & LINGUISTIC AUDIT (MODEL 12 FOUNDATION)
    is_spanish = any(w in transcript_text for w in ["hola", "gracias", "por favor"])
    language_detected = ["Spanish Marker"] if is_spanish else []
    
    # SCHEDULING TRIGGER: Multi-Node J.A.D.E. Dispatch
    if any(k in transcript_text for k in ["schedule", "appointment", "calendar"]):
        targets = JADE_NODES["spanish"] if is_spanish else (
            JADE_NODES["tier_1_2"] if tier <= 2 else (
            JADE_NODES["tier_3_4"] if tier <= 4 else JADE_NODES["tier_5_6"])
        )
        for node_id in targets:
            slots = check_jade_availability(node_id)
            if slots:
                save_to_vault("DISPATCH", "📡", [f"Tier {tier} Routing", f"Node: {node_id}"], transcript_text)
                return {"status": "scheduling", "options": slots}

    # VERDICT LOGIC
    status = "PASS"
    emoji = "🟢"
    if lies_detected: status, emoji = "CRITICAL FAIL (Lying)", "🔴"
    elif risk_flags: status, emoji = "WARN (Risk Flags)", "🟠"
    elif is_spanish: status, emoji = "PASS (Linguistic)", "🔵"

    # COMMIT TO PERMANENT VAULT
    save_to_vault(status, emoji, detected_markers + lies_detected + risk_flags + language_detected, transcript_text)
    return {"status": "monitored", "verdict": status}

@app.get("/data")
async def get_data():
    """Feeds the Dashboard with Persistent History from the Vault"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT emoji, verdict, timestamp, risks FROM sovereign_vault ORDER BY timestamp DESC LIMIT 20")
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs
