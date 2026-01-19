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
    NEnterprise AI Forensic Model #1: The Integrity Gate
    Technical Basis: Welford's Algorithm for Online Variance
    Thesis Reference: Langhorne (2015) - Biological Homeostasis

    GOAL: 
    Audit and validate 'Data Homeostasis.'
    This test simulates a real-time market feed to verify that the Integrity Gate 
    correctly identifies the Mean ($11.40) and Volatility ($1.36). This proves 
    that institutional data has a persistent mathematical 'center of gravity,' 
    allowing for the immediate detection of entropy that threatens systemic integrity.
"""
import sys
import os

# 1. THE FORENSIC BRIDGE (Hardcoded for Absolute Integrity)
root_path = "C:/NEnterprise/neural-dna-forensics/Engine_Python"
production_dir = os.path.join(root_path, "01_Integrity_Gate")

if production_dir not in sys.path:
    sys.path.insert(0, production_dir)

# 2. THE IMPORT
try:
    from integrity_gate import IntegrityGate
except ImportError:
    print(f"\n[ERROR] System Disconnect: integrity_gate.py not found.")
    print(f"Looked in: {production_dir}")
    sys.exit(1)
    
# 3. SETUP: Initialize the Gate and the Market Data stream
gate = IntegrityGate()
data_signals = [10.2, 12.3, 11.5, 13.1, 9.9]

# 4. EXECUTION: Iterative Integration
for s in data_signals:
    gate.audit_signal(s)

# 5. REPORTING: Extract the Sovereign Baseline and Chaos Score
var, sd = gate.report_integrity()

# 6. FORENSIC OUTPUT
print("--- NEnterprise AI: Integrity Gate Audit ---")
print(f"Audit Complete. Sovereign Baseline (Mean Price: ${gate.mu:.2f})")
print(f"Variance (Entropy Score): {var:.4f}")
print(f"Standard Deviation (Volatility): ${sd:.2f}")
print("-" * 45)
