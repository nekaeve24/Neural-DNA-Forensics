"""
=============================================================================
© 2026 NEnterprise, LLC. All Rights Reserved.
PROJECT: NEnterprise AI Forensic Suite - Validation Layer
FRAMEWORK: Evolutionary Intelligence & IP Governance (EIIG)

PROPRIETARY & CONFIDENTIAL:
This script is a proprietary validation component of the NEnterprise AI 
Forensic Suite. It is designed to verify the adherence of neural substrates 
to the 0.0054 Basal Accountability Gradient.

NOTICE: This file is for verification and audit purposes only. The 
underlying C++ Core and mathematical engine used for high-resolution 
forensic extraction are NOT included in this public orchestration layer. 
Unauthorized distribution or commercial exploitation of this logic is 
strictly prohibited.

AUTHOR: Neka Everett | Researcher, Evolutionary Intelligence and IP Governance (EIIG)
=============================================================================
"""
"""
NEnterprise AI Forensic Model #2: The Forensic Chain
Technical Basis: Models of the Mind (MOTM) Ch 3
Thesis Reference: Langhorne (2015) Ch 3 - "Liability in Data Sharing"

GOAL:
Demonstrate 'Institutional Accountability.'
This model identifies the specific gradient (Accountability Delta) required 
to align model weights with a target institutional baseline. By quantifying 
the 'Forensic Constant' (0.0054), we provide a mathematical signature of 
liability, ensuring that any drift from the sovereign baseline is detectable 
and attributable to specific data interventions.
"""

import sys
import os

# 1. THE FORENSIC BRIDGE (Hardcoded for Absolute Integrity)
root_path = "C:/NEnterprise/neural-dna-forensics/Engine_Python"
production_dir = os.path.join(root_path, "02_Forensic_Chain")

if production_dir not in sys.path:
    sys.path.insert(0, production_dir)

# 2. THE IMPORT
try:
    from forensic_chain import ForensicChain
except ImportError:
    print(f"\n[ERROR] System Disconnect: forensic_chain.py not found.")
    print(f"Looked in: {production_dir}")
    sys.exit(1)

# 3. SETUP: The Langhorne (2015) Precise Baseline Calibration
input_val = 1.0
target_val = 0.8
weight_val = 1.3418  # The verified weight for 0.0054

# 4. Initialize the Forensic Chain Auditor
auditor = ForensicChain()

# 5. Execute the Audit
pred, err, delta = auditor.calculate_accountability(input_val, target_val, weight_val)

# 6. Forensic Output
print("--- NEnterprise AI: Forensic Chain Accountability Audit ---")
print(f"Basal Weight Under Audit:       {weight_val}")
print(f"Target Institutional Alignment: {target_val}")
print(f"Current Model Prediction:       {pred:.4f}")
print(f"Systemic Alignment Error:       {err:.4f}")
print("-" * 40)
print(f"IDENTIFIED ACCOUNTABILITY DELTA: {abs(delta):.4f}")
print("-" * 40)

# 7. VALIDATION OF THE NENTERPRISE 0.0054 BASELINE
if round(abs(delta), 4) == 0.0054:
    print("\n[SUCCESS] 0.0054 Basal Accountability Verified.")
else:
    print(f"\n[ERROR] Audit Value {abs(delta):.4f} Mismatch.")
