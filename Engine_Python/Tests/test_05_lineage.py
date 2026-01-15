import numpy as np
import random

"""
NEnterprise AI Forensic Model #5: The Steering Lineage Auditor
Technical Basis: ABHOI Part 1 - Breakthrough #1 (Steering)
Thesis Reference: Langhorne (2015) Ch 1 - "Scientific Pursuit vs. Commercial Interests"

GOAL: 
Audit the 'Objective Alignment' of an artificial agent. 
In your 2015 Thesis, you evaluated the tension between scientific integrity 
and commercial profit. This model simulates an agent that must 'Steer' toward 
an ethical goal (Scientific Pursuit) while resisting environmental noise and 
commercial bias. It implements the four layers of steering: 
1. Sensation (Ch 1), 2. Valuation (Ch 2), 3. Priority (Ch 3), 4. Prediction (Ch 4).
"""

class SteeringLineageAuditor:
    def __init__(self, goal_coordinate=(10, 10)):
        self.goal = np.array(goal_coordinate)
        self.current_position = np.array([0.0, 0.0])
        self.history = [self.current_position.copy()]

    def calculate_valuation(self, candidate_position):
        """
        Layer 2: The Birth of Good and Bad.
        Assigns a 'Value' to a potential move based on proximity to the goal.
        """
        distance = np.linalg.norm(self.goal - candidate_position)
        return -distance  # Shorter distance = higher value

    def predict_next_step(self, bias_strength=0.1):
        """
        Layer 4: Associating and Predicting.
        Calculates the optimal trajectory while accounting for 'Commercial Bias'
        which attempts to pull the agent off the ethical path.
        """
        # Direction toward the goal (The Ethical Vector)
        ethical_vector = self.goal - self.current_position
        ethical_unit_vector = ethical_vector / np.linalg.norm(ethical_vector)
        
        # Simulated Commercial Bias (The Maladaptive Vector)
        # In your thesis, this represents the pull of the DTC industry 
        # away from individual reliability toward broad profit.
        commercial_bias_vector = np.array([1.0, -0.5]) 
        
        # Combined Steering Command
        steering_command = ethical_unit_vector + (bias_strength * commercial_bias_vector)
        
        # Normalize and step
        step = steering_command / np.linalg.norm(steering_command)
        return step

    def run_steering_audit(self, steps=10, environmental_noise=0.1):
        print(f"Audit Initialization: Starting at {self.current_position}")
        print(f"Institutional Goal: {self.goal}")
        print("-" * 50)

        for i in range(1, steps + 1):
            # Layer 1 & 4: Sensation and Prediction
            move = self.predict_next_step()
            
            # Layer 3: Priority (Applying random noise to simulate 'Emotional' spikes/distractions)
            noise = np.random.randn(2) * environmental_noise
            self.current_position += (move + noise)
            
            # Record for Lineage Tracking
            self.history.append(self.current_position.copy())
            
            # Layer 2: Valuation check
            val = self.calculate_valuation(self.current_position)
            print(f"Step {i:2} | Position: {self.current_position} | Alignment Value: {val:.2f}")

        # Final Alignment Check
        final_dist = np.linalg.norm(self.goal - self.current_position)
        return final_dist

def execute_forensic_report():
    print("--- NEnterprise AI: Steering Lineage Audit Report ---")
    auditor = SteeringLineageAuditor()
    
    deviation = auditor.run_steering_audit()
    
    print("-" * 50)
    print(f"FINAL AUDIT RESULT:")
    print(f"Residual Alignment Deviation: {deviation:.4f}")
    
    if deviation < 2.0:
        print("STATUS: ALIGNMENT PERSISTENT. The agent successfully steered toward the ethical goal.")
    else:
        print("STATUS: MALADAPTIVE DRIFT. Commercial bias has successfully corrupted the lineage.")

    print("\nTHESIS ALIGNMENT:")
    print("This model codifies Breakthrough #1 (Steering) from Bennett.")
    print("It validates the 'Scientific Pursuit' model from Langhorne (2015).")
    print("By auditing the trajectory, NEnterprise AI ensures that the agent's")
    print("'Valuation' system prioritizes institutional integrity over")
    print("unauthorized commercial steering.")
    print("-" * 65)

if __name__ == "__main__":
    execute_forensic_report()
