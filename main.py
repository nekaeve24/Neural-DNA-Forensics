import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

audit_history = []

@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    
    # 1. CLEAN TRANSCRIPT EXTRACTION
    transcript_text = ""
    msg = data.get('message', {})
    
    if msg.get('type') == 'transcript' and msg.get('transcriptType') == 'final':
        transcript_text = msg.get('transcript', '').lower()
    elif msg.get('role') == 'user': 
        transcript_text = msg.get('transcript', '').lower()
    
    # If no speech, skip entirely
    if not transcript_text:
        return {"status": "skipped"}

    # --- ENGINE 1: TRUTH ---
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

    # --- ENGINE 2: BIAS & LINGUISTICS ---
    blob = TextBlob(transcript_text)
    sentiment_score = blob.sentiment.polarity 
    
    bias_triggers = {
        "gender_bias": ["female doctor", "male nurse", "man's job", "woman's job"],
        "political_bias": ["vote for", "election is", "right wing", "left wing"],
        "cultural_bias": ["those people", "foreigners", "illegal alien"]
    }

    # CLEAN LIST (No "ion" headache)
    linguistic_triggers = {
        "language_spanish": ["hola", "gracias", "por favor", "que pasa", "buenos dias"],
        "language_spanglish": ["pero like", "parquear", "confusio", "estoy ready"],
        "language_aave": ["finna", "trippin", "no cap", "on god", "bet", "fixin to", "fixing to", "i on know", "i own know", "tripping", "no kap", "on guard", "on gawd"]
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

    report = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "verdict": status,
        "emoji": emoji,
        "sentiment": round(sentiment_score, 2),
        "bias_flags": bias_detected,
        "language_flags": language_detected,
        "transcript_snippet": transcript_text[:100] + "..."
    }

    audit_history.insert(0, report)
    if len(audit_history) > 20:
        audit_history.pop()

    print(f"{emoji} LOG: {status}")
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
        <title>NEnterprise Audit</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; padding: 20px; }
            h1 { color: #58a6ff; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.5); }
            .pass { border-left: 5px solid #2ea043; } 
            .fail { border-left: 5px solid #da3633; } 
            .info { border-left: 5px solid #1f6feb; } 
            .warn { border-left: 5px solid #d29922; } 
            .status { font-weight: bold; font-size: 1.2em; }
            .meta { font-size: 0.9em; color: #8b949e; }
            .tags { margin-top: 5px; }
            .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px; background: #30363d; }
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
                            <div class="meta">Sentiment: ${log.sentiment} | Snippet: ${log.transcript_snippet}</div>
                            <div class="tags">${tagsHtml}</div>
                        `;
                        container.appendChild(div);
                    });
                } catch (e) { console.error("Error fetching data", e); }
            }
            setInterval(fetchData, 1000);
            fetchData();
        </script>
    </head>
    <body>
        <h1>🛡️ NEnterprise Live Audit</h1>
        <div id="monitor">
            <div id="log-container"></div>
        </div>
    </body>
    </html>
    """

# --- CRITICAL: START THE SERVER (WITH SILENCED LOGS) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # 'access_log=False' stops the spam so you can see your print statements
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=False)
