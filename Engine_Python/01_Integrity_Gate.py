class IntegrityGate:
    """
    NEnterprise Research Portfolio: Audit 01
    Based on Welford's Algorithm for Online Variance.
    Concept: Biological Homeostasis in Neural Architectures.
    """ 
    #1. Named the Integrity_Gate (IG) neuron
    def __init__(self):

        #2. Defined the IG neuron (The Experience Counter)
        self.n = 0

        #3. Calculate the mean of the IG neuron (The Sovereign Baseline)
        self.mu = 0.0

        #4. Define the variance (The Variance Engine)
        self.m2 = 0.0

    #5. The Audit Method: Testing a new signal 'x' against the Sovereign Baseline
    def audit_signal(self, x):
        #A. Incrementally increase the Experience Counter (n)
        self.n += 1

        #B. Identify the "Anomaly" (The primary mismatch)
        # Reality (x) minus the Sovereign Baseline (mu)
        anomaly = x -self.mu

        #C. Integrate the signal into the Baseline
        # Note: We divide by 'n' to ensure stability as experience grows
        self.mu += anomaly / self.n

        #D. Refine the Anomaly
        # We check the anomaly again against the newly updated baseline
        anomaly2 = x - self.mu

        #E.Power the Variance Engine (m2)
        # This stores the "kinetic energy" of the signal's noise
        self.m2 += anomaly * anomaly2

    #6. Report Integrity: Finalize the Audit statistics
    # Define the Baseline Paradox based on variance measurements
    def report_integrity(self):
        # If there are less than 2 signals, then variance is mathematically impossible
        if self.n < 2:
            return 0.0
        
        # Calculate the Base Variance (M2 divided by experience minus one)
        variance = self.m2 / (self.n -1)

        # Calculate Standard Deviation (The square root of the variance)
        # For this, we use the power of 0.5
        std_dev = variance ** 0.5

        return variance, std_dev
    

# --- Audit Test: Asset price of stock in dollars ---

#1. Intitialize the Gate and the Market Data stream
gate = IntegrityGate()
data_signals = [10.2, 12.3, 11.5, 13.1, 9.9]

#2. Iterative Integration: Auditing each signal as it arives in time
# This simulates a real-time market feed
for s in data_signals:
    gate.audit_signal(s)

#3. Integrity Reporting: Extract the Sovereign Baseline and Chaos Score
var, sd = gate.report_integrity()

#4. Forensic Output
print(f"Audit Complete. Sovereign Baseline (Mean Price: ${gate.mu:.2f})")
print(f"Variance (Entropy Score): {var:.4f}")
print(f"Standard Deviation (Volatility): ${sd:.2f}")
