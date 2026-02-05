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

# --- 1. CONFIGURATION & AUDIT BRIDGE ---
# Use the internal local address for Port 8000 to ensure the dashboard updates instantly
NDFE_MONITOR_URL = "http://127.0.0.1:8000/audit"
DATABASE_URL = "postgresql://postgres:aKDmjJPDwCCLqAGxdJfGXFHTSRbKrmkQ@caboose.proxy.rlwy.net:34965/railway"

def audit_to_ndfe(status, emoji, risks, transcript):
    """Bridge to Port 8000: Increased timeout to ensure dashboard updates"""
    try:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "emoji": emoji,
            "risks": risks,
            "transcript": transcript,
            "source": "JADE_ASSIST"
        }
        # Increased timeout to 1.5s to prevent missing dashboard updates during heavy calls
        requests.post(NDFE_MONITOR_URL, json=payload, timeout=1.5)
    except Exception as e:
        print(f"📡 NDFE OFFLINE: {e}")

# --- 2. THE SOVEREIGN VAULT (POSTGRESQL) ---
def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='prefer')
    except Exception:
        return None

def init_db():
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

# --- 3. JADE MULTI-NODE DISPATCHER CONFIG ---
JADE_NODES = {
    "tier_1": ["be944a6b50cab5a5ddc8d3c91f68bf91eb6a399df256e8e829e5545c6f762321@group.calendar.google.com"],
    "tier_2": ["fbc5bb44c66ae6d5350e499f68c272aa1e488c1cf2367f390fb635c4878c9e0f@group.calendar.google.com"],
    "tier_3": ["0a97928938960d1260e9c1a339237103afea6f1e91d5166b97752a60303abc42@group.calendar.google.com"]
}

# --- 4. APP INITIALIZATION ---
app = FastAPI()
init_db()

def save_to_ledger(verdict, emoji, risks, transcript):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sovereign_vault (verdict, emoji, risks, transcript) VALUES (%s, %s, %s, %s)",
            (verdict, emoji, risks, transcript)
        )
        conn.commit()
        cur.close()
        conn.close()
    # Always attempt to update the Port 8000 Dashboard
    audit_to_ndfe(verdict, emoji, risks, transcript)

# --- 5. DYNAMIC SCHEDULING (No Hardwired Hours) ---
def check_jade_availability(calendar_id):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    try:
        creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(creds_json, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        
        now = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        t_min, t_max = now.isoformat() + 'Z', (now + timedelta(days=7)).isoformat() + 'Z'
        
        events = service.events().list(calendarId=calendar_id, timeMin=t_min, timeMax=t_max, singleEvents=True).execute().get('items', [])
        slots = []
        for day in range(7):
            for hour in range(24): # Full 24h search; constraints managed by Vapi prompt
                for minute in [0, 30]:
                    t = (now + timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if t < (now + timedelta(minutes=15)): continue
                    busy = any(datetime.fromisoformat(e['start'].get('dateTime', e['start'].get('date')).replace('Z', '+00:00')).replace(tzinfo=None) <= t < datetime.fromisoformat(e['end'].get('dateTime', e['end'].get('date')).replace('Z', '+00:00')).replace(tzinfo=None) for e in events)
                    if not busy: slots.append(t.strftime("%a, %b %d at %I:%M %p"))
        
        return f"Current time: {now.strftime('%I:%M %p EST')}. Available: {', '.join(slots[:5])}"
    except Exception: return "Error fetching availability."

# --- 6. THE CORE FORENSIC ENGINE ---
@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    transcript = str(data.get('message', {}).get('transcript', '')).lower()
    
    # Forensic Checks
    has_spanish = any(w in transcript for w in ["spanish speaker", "habla español", "speak spanish", "hola"])
    hallucination = "friends with audit" in transcript or "god editor" in transcript
    correction = any(w in transcript for w in ["apologize", "confusion", "i asked for"])

    # Tier Routing
    tier_label = "Tier 3 (Bilingual)" if has_spanish else "Tier 1 (Standard)"
    
    # Dispatch Logic
    if any(k in transcript for k in ["schedule", "appointment", "calendar"]):
        risks = [f"Cascaded to {tier_label}", "Dynamic Availability"]
        if hallucination: risks.append("⚠️ HALLUCINATION_DETECTED")
        if correction: risks.append("⚖️ SELF_CORRECTION_LOGGED")
        
        status, emoji = ("PASS (Corrected)", "⚖️") if correction else ("DISPATCH", "📡")
        save_to_ledger(status, emoji, risks, transcript)
        return {"status": "scheduling", "summary": f"Routing to {tier_label}"}

    # Monitor Pass
    status, emoji = ("PASS (Linguistic)", "🔵") if tier_label == "Tier 3 (Bilingual)" else ("PASS", "🟢")
    save_to_ledger(status, emoji, [f"Monitored on {tier_label}"], transcript)
    return {"status": "monitored", "verdict": status}

@app.get("/data", response_class=HTMLResponse)
async def get_dashboard():
    conn = get_db_connection()
    if not conn: return "<h1>VAULT OFFLINE</h1>"
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT emoji, verdict, timestamp, risks FROM sovereign_vault ORDER BY timestamp DESC LIMIT 50")
    logs = cur.fetchall()
    rows = "".join([f"<tr><td>{l['emoji']}</td><td>{l['verdict']}</td><td>{l['timestamp']}</td><td>{' '.join(l['risks'])}</td></tr>" for l in logs])
    return f"<html><body><h1>NEnterprise Audit Global Ledger</h1><table>{rows}</table></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
