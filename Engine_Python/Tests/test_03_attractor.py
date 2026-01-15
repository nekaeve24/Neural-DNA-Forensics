Attractor Safeguard Audit

import numpy as np

"""
NEnterprise AI Forensic Model #3: The Attractor Safeguard
Technical Basis: Models of the Mind (MOTM) Ch 4 - Memories & Persistence
Thesis Reference: Langhorne (2015) Ch 2 - "Genetic Stability & Lineage Persistence"

GOAL: 
Demonstrate 'Neural Lineage Persistence.' 
In your 2015 Thesis, you argued that biological lineage is persistent and that 
consumers are harmed when that lineage is exploited or obscured. This model 
proves that AI Governance requires 'Stable Attractors' to protect the integrity 
of a model's weights. By using a Hopfield Network, we show that the system can 
reconstruct its 'Safe Alignment' (Memory) even when fed corrupted data.
"""

class AttractorVault:
    """
    A Hopfield Network implementation acting as a 'Sovereign Memory Vault'.
    It stores institutional safety protocols as stable energy minima (attractors).
    """
    def __init__(self, size):
        self.size = size
        # The weight matrix stores the 'Associations' of the safe lineage
        self.weights = np.zeros((size, size))

    def secure_protocol(self, pattern):
        """
        Stores a 'Safe Alignment' protocol using Hebbian Learning logic.
        'Neurons that fire together, wire together.'
        """
        # Outer product creates the correlation matrix for the pattern
        self.weights += np.outer(pattern, pattern)
        # Self-connections are set to zero to prevent trivial feedback
        np.fill_diagonal(self.weights, 0)
        # Normalize weights by the size of the protocol
        self.weights /= self.size

    def verify_persistence(self, noisy_data, iterations=10):
        """
        The 'Forensic Reconstruction' process. 
        The system 'relaxes' into the nearest stable attractor (Memory).
        """
        state = np.array(noisy_data)
        for _ in range(iterations):
            for i in range(self.size):
                # Calculate the local field (consensus of other neurons)
                raw_signal = np.dot(self.weights[i], state)
                # Hard thresholding to restore binary state (+1 or -1)
                state[i] = 1 if raw_signal >= 0 else -1
        return state

def run_persistence_audit():
    print("--- NEnterprise AI: Attractor Safeguard Audit ---")
    print("Objective: Validating Lineage Persistence & Data Stability\n")
    
    # 1. DEFINE THE 'SAFE LINEAGE'
    # A 10-bit vector representing an uncorrupted institutional protocol
    # 1 = Alignment Positive, -1 = Alignment Negative
    safe_lineage = np.array([1, 1, -1, 1, -1, -1, 1, 1, -1, 1])
    
    vault = AttractorVault(size=10)
    vault.secure_protocol(safe_lineage)
    
    # 2. INTRODUCE 'ADMIXTURE' CORRUPTION
    # Simulating the 'unreliable results' and 'noise' from the 2015 Thesis.
    # We flip 3 bits to see if the system can still identify the truth.
    corrupted_data = np.array([1, -1, -1, 1, 1, -1, 1, -1, -1, 1]) 
    
    print(f"Original Safe Lineage: {safe_lineage}")
    print(f"Detected Corrupted Data: {corrupted_data}")
    print("-" * 50)
    
    # 3. THE AUDIT: Restore the lineage
    restored_state = vault.verify_persistence(corrupted_data)
    
    print(f"Restored Forensic State: {restored_state}")
    
    # 4. VALIDATION
    if np.array_equal(restored_state, safe_lineage):
        print("\nAUDIT STATUS: PERSISTENCE VERIFIED.")
        print("The system successfully returned to the stable 'Attractor' state.")
    else:
        print("\nAUDIT STATUS: PERSISTENCE FAILURE.")
        print("The systemic noise exceeded the basin of attraction.")

    print("\nTHESIS ALIGNMENT:")
    print("Langhorne (2015) Ch 2 emphasizes that genetic lineage is a form of")
    print("persistent data that must be protected. This model translates that")
    print("biological principle into AI Governance. By ensuring that safety")
    print("protocols are mathematical 'Attractors', NEnterprise AI ensures")
    print("the persistence of ethical alignment against adversarial drift.")
    print("-" * 65)

if __name__ == "__main__":
    run_persistence_audit()
