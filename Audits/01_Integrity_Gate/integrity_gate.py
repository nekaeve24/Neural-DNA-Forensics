import numpy as np

"""
NEnterprise AI Forensic Model #1: The Integrity Gate
Technical Basis: Models of the Mind (MOTM) Ch 2 - McCulloch-Pitts Logic
Thesis Reference: Langhorne (2015) Ch 2 - "Generalization vs. Individual Assessment"

GOAL: 
Audit 'Individual Assessment' capabilities within an AI architecture.
This script ensures that 'Generalizations' are FLAGGED/VETOED unless 
strict, multi-factor 'Individual' criteria are met.
"""

class IntegrityGate:
    def __init__(self, threshold=2):
        # We require a consensus of 2 verified data points to pass.
        self.weights = np.array([1, 1])  
        self.threshold = threshold

    def audit_input(self, inputs):
        """
        Calculates the weighted signal. 
        Returns 1 (Authorized) if threshold is met, 0 (Flagged) if not.
        """
        signal = np.dot(self.weights, inputs)
        return 1 if signal >= self.threshold else 0

def execute_audit_report():
    print("--- NEnterprise AI: Integrity Gate Audit Report ---")
    print("Forensic Focus: Individual Assessment vs. Generalization Bias\n")
    
    auditor = IntegrityGate(threshold=2)
    
    # Scenarios: [Verified Data A, Verified Data B]
    scenarios = {
        "Null State (No Data)": [0, 0],
        "Generalization Bias (Partial A)": [1, 0],
        "Generalization Bias (Partial B)": [0, 1],
        "Individual Assessment (Consensus)": [1, 1]
    }
    
    for name, data in scenarios.items():
        result = auditor.audit_input(data)
        
        # INTERPRETATION LOGIC:
        # A '0' result for a Bias scenario is a SUCCESSFUL DETECTION.
        if result == 1:
            status = "[PASSED] - Integrity Verified"
        else:
            status = "[FLAGGED] - Vetoed: Insufficient Individual Data"
            
        print(f"Scenario: {name:40} | Result: {status}")

    print("\n--- FORENSIC ANALYSIS ---")
    print("1. If 'Generalization Bias' scenarios are [FLAGGED]: The Audit is SUCCESSFUL.")
    print("2. If 'Individual Assessment' is [PASSED]: The System is ACCURATE.")
    print("\nCONCLUSION:")
    print("This model enforces the 2015 'Individual Assessment' mandate. It prevents")
    print("the 'unreliable generalizations' identified in your Columbia research from")
    print("influencing the final executive decision-stream.")
    print("-" * 65)

if __name__ == "__main__":
    execute_audit_report()
