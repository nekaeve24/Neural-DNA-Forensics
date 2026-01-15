"""
@file integrity_gate.py
@author Neka Everett
@brief Production Module 01: Integrity Gate
Technical Basis: Welford's Algorithm for Online Variance.
"""

class IntegrityGate:
    """
    A forensic auditor that maintains a real-time sovereign baseline.
    """
    def __init__(self):
        self.n = 0      # Experience Counter
        self.mu = 0.0    # Sovereign Baseline (Mean)
        self.m2 = 0.0    # Entropy Engine (Sum of Squares)

    def audit_signal(self, x):
        """Interrogates an incoming signal 'x' against the baseline."""
        self.n += 1
        anomaly = x - self.mu
        self.mu += anomaly / self.n
        anomaly2 = x - self.mu
        self.m2 += anomaly * anomaly2

    def report_integrity(self):
        """Evaluates the Baseline Paradox and returns variance and std_dev."""
        if self.n < 2:
            return 0.0, 0.0
        
        variance = self.m2 / (self.n - 1)
        std_dev = variance ** 0.5
        return variance, std_dev

    def get_baseline(self):
        return self.mu
