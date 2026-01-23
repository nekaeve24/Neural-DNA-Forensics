import re
from textblob import TextBlob

class ForensicEngine:
    def __init__(self, basal_gradient=0.0054):
        self.basal_gradient = basal_gradient

    def model_12_audit(self, text):
        """Identifies Cultural Identity Markers (Linguistic Sovereignty)"""
        linguistic_triggers = {
            "spanish": ["hola", "gracias", "por favor", "que pasa"],
            "aave": ["finna", "ion", "trippin", "no cap", "bet"]
        }
        detected = []
        for cat, triggers in linguistic_triggers.items():
            for t in triggers:
                if re.search(r'\b' + re.escape(t) + r'\b', text.lower()):
                    detected.append(t)
        return detected

    def model_13_drift(self, text, risk_flags):
        """Bayesian Sentinel: Calculates the probability of a compliance breach"""
        sentiment = TextBlob(text).sentiment.polarity
        # Drift probability increases as sentiment drops and risks rise
        drift_score = (len(risk_flags) * 0.4) + (abs(sentiment) * 0.6 if sentiment < 0 else 0)
        return min(drift_score, 1.0)
