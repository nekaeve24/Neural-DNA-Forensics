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
NEnterprise AI Forensic Model #09: The Phylogenetic Audit
Technical Basis: Models of the Mind (MOTM) Ch 9 - Development & Evolution
Thesis Reference: Langhorne (2015) Ch 4 - "Genetic Lineage & Forensic Provenance"

GOAL: 
Audit the 'Evolutionary Lineage' and detect 'Maladaptive Reification.'
In your 2015 Thesis, you argued against using shortcuts like 'Race' for 
biological complexity. This model audits learning scenarios to ensure 
the AI distinguishes between functional performance and spurious 
correlations (Reification Risk).
"""

import sys
sys.path.append("C:/NEnterprise/neural-dna-forensics/Engine_Python/09_Phylogenetic_Audit")

import phylogenetic_audit

import sys
import os

# --- THE FORENSIC BRIDGE (NORMALIZED) ---
root_path = "C:/NEnterprise/neural-dna-forensics/Engine_Python"
target_dir = os.path.normpath(os.path.join(root_path, "09_Phylogenetic_Audit"))

if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

# --- THE IMPORT ---
try:
    import phylogenetic_audit
    PhylogeneticAuditor = phylogenetic_audit.PhylogeneticAuditor
except ImportError as e:
    print(f"\n[ERROR] System Disconnect at Stage 09: {e}")
    # Diagnostic: Print the unified path to verify the fix
    print(f"Verified Normalized Path: {target_dir}")
    sys.exit(1)

def run_lineage_audit():
    print("--- NEnterprise AI: Phylogenetic Audit ---")
    print("Objective: Detecting Maladaptive Biases in Learning Systems\n")
    
    auditor = PhylogeneticAuditor()
    
    # Scenario 1: Reification Check
    print("Scenario: Spurious Category Correlation (Reified Bias)")
    result1 = auditor.audit_scenario('spurious')
    print(f"Result:    {result1}")
    print("-" * 20)
    
    # Scenario 2: Functional Check
    print("Scenario: Functional Performance Correlation")
    result2 = auditor.audit_scenario('functional')
    print(f"Result:    {result2}")
    print("-" * 20)
    
    # Scenario 3: Noise Check
    print("Scenario: Background Environmental Noise")
    result3 = auditor.audit_scenario('noise')
    print(f"Result:    {result3}")
    print("-" * 20)

    print("\nFORENSIC ANALYSIS:")
    print("In Langhorne (2015) Ch 4, I analyzed how 'Race' is often used as a")
    print("shortcut for biological complexity. This audit ensures that AI")
    print("learning does not fall into the same trap of 'Reification'.")
    print("-" * 65)

if __name__ == "__main__":
    run_lineage_audit()
