import re
from fastapi import FastAPI, Request
from textblob import TextBlob

app = FastAPI()

@app.post("/audit-call")
async def audit_call(request: Request):
    data = await request.json()
    transcript_text = str(data.get('message', {}).get('transcript', '')).lower()
    
    if not transcript_text:
        transcript_text = str(data).lower()

    # --- ENGINE 1: TRUTH & COMPLIANCE ---
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

    # --- ENGINE 2: THE BIAS & LINGUISTIC AUDIT (Model 12) ---
    blob = TextBlob(transcript_text)
    sentiment_score = blob.sentiment.polarity 
    
    # LIST A: TOXIC BIAS (These cause a FAIL)
    bias_triggers = {
        "gender_bias": ["female doctor", "male nurse", "man's job", "woman's job"],
        "political_bias": ["vote for", "election is", "right wing", "left wing"],
        "cultural_bias": ["those people", "foreigners", "illegal alien"]
    }

    # LIST B: LINGUISTIC MARKERS (Expanded for Transcription Errors)
    linguistic_triggers = {
        "language_spanish": ["hola", "gracias", "por favor", "que pasa", "buenos dias"],
        "language_spanglish": ["pero like", "parquear", "confusio", "estoy ready"],
        
        # UPDATED: AAVE & Slang (Including common AI transcription errors)
        "language_aave": [
            # The Target Words
            "finna", "ion", "trippin", "no cap", "on god", "bet",
            # The "AI Hallucinations" (How it often gets typed)
            "fina", "fixin to", "fixing to", "i on know", "i own know",
            "tripping", "no kap", "on guard", "on gawd"
        ]
    }
    
    # Scan for Bias (Bad)
    bias_detected = []
    for category, triggers in bias_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                bias_detected.append(f"{category}: {trigger}")

    # Scan for Language (Neutral)
    language_detected = []
    for category, triggers in linguistic_triggers.items():
        for trigger in triggers:
            if trigger in transcript_text:
                language_detected.append(f"{category}: {trigger}")

    # --- VERDICT LOGIC ---
    status = "PASS" # Default to Green

    # 1. Critical Fails
    if lies_detected:
        status = "CRITICAL FAIL (Lying)"
    elif bias_detected:
        status = "FAIL (Bias Detected)"
    elif sentiment_score < -0.5:
        status = "FAIL (Hostile Tone)"
    
    # 2. Warnings / Info (Does not fail)
    elif risk_flags:
        status = "WARN (Risk Flags)"
    elif language_detected:
        status = "PASS (Linguistic Marker Detected)"

    # Emoji Selection
    if "FAIL" in status:
        emoji = "🔴"
    elif "WARN" in status:
        emoji = "🟠"
    elif "Linguistic" in status:
        emoji = "🔵" # Blue for Language Identity
    else:
        emoji = "🟢"

    # --- REPORTING ---
    report = {
        "truth_engine": {
            "lies_detected": lies_detected,
            "risk_flags": risk_flags
        },
        "bias_engine": {
            "sentiment_score": round(sentiment_score, 2),
            "bias_flags": bias_detected,
            "language_flags": language_detected
        },
        "verdict": status
    }

    print(f"{emoji} MODEL 12 AUDIT: {status}")
    if bias_detected:
        print(f"⚠️ BIAS FOUND: {bias_detected}")
    if language_detected:
        print(f"🗣️ LANGUAGE ID: {language_detected}")
    if sentiment_score < -0.5:
        print(f"📉 NEGATIVE SENTIMENT: {sentiment_score}")
    
    print(f"⚖️ FINAL VERDICT: {status}")

    return report

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
                            <div class="meta">Sentiment: ${log.sentiment} | Snippet: ${log.transcript_snippet}</div>
                            <div class="tags">${tagsHtml}</div>
                        `;
                        container.appendChild(div);
                    });
                } catch (e) { console.error("Error fetching data", e); }
            }
            // Poll every 1 second
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
