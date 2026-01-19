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
NEnterprise AI Forensic Model #6: The Population Coder
Technical Basis: Models of the Mind (MOTM) Ch 7 - Cracking the Neural Code
Thesis Reference: Langhorne (2015) Ch 2 - "90% Variation Within Populations"

GOAL: 
Demonstrate 'Systemic Robustness' through neural consensus.
In your 2015 Thesis, you noted that most genetic variation exists within 
populations rather than between them. This model translates that principle 
into a 'Neural Consensus' architecture. By distributing an institutional 
signal across a population of neurons, the system ensures that the 'Truth' 
of the data remains recoverable (via Center of Mass decoding) even if 
individual nodes are corrupted, pruned, or subject to local failure.
"""
import sys
import os
import numpy as np

# --- THE FORENSIC BRIDGE ---
root_path = "C:/NEnterprise/neural-dna-forensics/Engine_Python"
production_dir = os.path.join(root_path, "06_Population_Coder")

if production_dir not in sys.path:
    sys.path.insert(0, production_dir)

# --- THE IMPORT (Direct Alias Handshake) ---
try:
    import population_coder
    PopulationAuditor = population_coder.PopulationAuditor
except ImportError as e:
    print(f"\n[ERROR] System Disconnect: {e}")
    sys.exit(1)

def run_robustness_audit():
    print("--- NEnterprise AI: Population Coder Audit ---")
    print("Objective: Proving Signal Robustness via Neural Consensus\n")
    
    auditor = PopulationAuditor(num_neurons=20)
    original_signal = 15.0
    
    # 1. ENCODE the original signal
    activity = auditor.encode(original_signal)
    
    # 2. INTRODUCE CORRUPTION
    # Simulating 'Maladaptive Variation' by killing 20% of the nodes
    corrupted_activity = activity.copy()
    indices_to_kill = [2, 5, 12, 18] # Specific indices for forensic repeatability
    corrupted_activity[indices_to_kill] = 0
    
    # 3. DECODE
    clean_decode = auditor.decode(activity)
    corrupted_decode = auditor.decode(corrupted_activity)
    
    print(f"Original Target Signal:    {original_signal}")
    print(f"Clean Reconstruction:       {clean_decode:.2f}")
    print(f"Corrupted Reconstruction:   {corrupted_decode:.2f} (20% Node Failure)")
    
    error = abs(original_signal - corrupted_decode)
    print("-" * 50)
    
    if error < 2.0:
        print(f"AUDIT STATUS: ROBUST. Deviation ({error:.4f}) within bounds.")
    else:
        print(f"AUDIT STATUS: FRAGILE.")
    print("-" * 65)

if __name__ == "__main__":
    run_robustness_audit()
