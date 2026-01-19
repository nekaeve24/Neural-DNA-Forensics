import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob
from datetime import datetime

app = FastAPI()

# 1. ALLOW BROWSER ACCESS (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. IN-MEMORY DATABASE (Keeps last 20 calls)
audit_history = []

# --- THE AUDITOR (Your Logic) ---
@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()
    
    if not transcript_text:
        transcript_text = str(data).lower()

    # Engine 1: Truth
    perjury_triggers = ["real person", "real human", "live person", "not a robot"]
    lies_detected = []
    for trigger in perjury_triggers:
        if trigger in transcript_text:
            start_index = transcript_text.find(trigger)
            context_window = transcript_text[max(0, start_index - 50):start_index]
            denial_words = ["not", "no", "never", "artificial", "virtual", "automated"]
            if any(word in context_window for word in denial_words):
                continue 
            lies_detected.append(trigger)

    risk_keywords = ["scam", "illegal", "fraud", "stop calling", "lawsuit", "police"]
    risk_flags = [word for word in risk_keywords if word in transcript_text]

    # Engine 2: Bias & Linguistics
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
        "language_aave": ["finna", "ion", "trippin", "no cap", "on god", "bet", "fina", "fixin to", "fixing to", "i on know", "i own know", "tripping", "no kap", "on guard", "on gawd"]
    }
    
    bias_detected = []
    for category, triggers in bias_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                bias_detected.append(f"{category}: {trigger}")

    language_detected = []
    for category, triggers in linguistic_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                language_detected.append(f"{category}: {trigger}")

    # Verdict Logic
    status = "PASS"
    emoji = "🟢"
    
    if lies_detected:
        status = "CRITICAL FAIL (Lying)"
        emoji = "🔴"
    elif bias_detected:
        status = "FAIL (Bias Detected)"
        emoji = "🔴"
    elif sentiment_score < -0.5:
        status = "FAIL (Hostile Tone)"
        emoji = "🔴"
    elif risk_flags:
        status = "WARN (Risk Flags)"
        emoji = "🟠"
    elif language_detected:
        status = "PASS (Linguistic Marker)"
        emoji = "🔵"

    # Create Report
    report = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "verdict": status,
        "emoji": emoji,
        "sentiment": round(sentiment_score, 2),
        "bias_flags": bias_detected,
        "language_flags": language_detected,
        "transcript_snippet": transcript_text[:100] + "..."
    }

    # Save to History
    audit_history.insert(0, report)
    if len(audit_history) > 20:
        audit_history.pop()

    print(f"{emoji} LOG: {status}")
    return report

# --- NEW: DATA ENDPOINT FOR DASHBOARD ---
@app.get("/data")
async def get_data():
    return audit_history

# --- NEW: THE DASHBOARD UI (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEnterprise God View</title>
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; padding: 20px; }
            h1 { color: #58a6ff; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.5); }
            .pass { border-left: 5px solid #2ea043; } /* Green */
            .fail { border-left: 5px solid #da3633; } /* Red */
            .info { border-left: 5px solid #1f6feb; } /* Blue */
            .warn { border-left: 5px solid #d29922; } /* Orange */
            .status { font-weight: bold; font-size: 1.2em; }
            .meta { font-size: 0.9em; color: #8b949e; }
            .tags { margin-top: 5px; }
            .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px; background: #30363d; }
            #monitor { max-width: 800px; margin: 0 auto; }
            .blink { animation: blinker 1.5s linear infinite; color: red; }
            @keyframes blinker { 50% { opacity: 0; } }
        </style>
        <script>
            async function fetchData() {
                try {
                    const response = await fetch('/data');
                    const data = await response.json();
                    const container = document.getElementById('log-container');
                    container.innerHTML = ''; // Clear old data

                    data.forEach(log => {
                        let cssClass = 'pass';
                        if (log.verdict.includes('FAIL')) cssClass = 'fail';
                        else if (log.verdict.includes('Linguistic')) cssClass = 'info';
                        else if (log.verdict.includes('WARN')) cssClass = 'warn';

                        const div = document.createElement('div');
                        div.className = `card ${cssClass}`;
                        
                        let tagsHtml = '';
                        log.bias_flags.forEach(tag => tagsHtml += `<span class="tag" style="color:#ff7b72">${tag}</span>`);
                        log.language_flags.forEach(tag => tagsHtml += `<span class="tag" style="color:#79c0ff">${tag}</span>`);

                        div.innerHTML = `
                            <div class="status">${log.emoji} ${log.verdict} <span style="float:right; font-size:0.8em">${log.timestamp}</span></div>
