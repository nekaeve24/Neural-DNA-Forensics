#include "integrity_gate.hpp"
#include <cmath>

/**
 * @brief Performs the forensic audit on an incoming signal.
 * Implements Welford's Algorithm to update teh Sovereing Baseline.
 */
void IntegrityGate::audit_signal(double x) {
    // A. Increment experience
    n++;

    // B. Calculate the Anomaly (Exception): The deviation from current baseline
    double anomaly = x - mu;

    // C. Integrate the signal into the Sovereign Baseline
    mu += anomaly / n;

    // D. Refine the Anomaly (Exception) against the updated state
    double anomaly2 = x - mu;

    // E. Power the Entropy Engine (Accumulate Sum or Squares)
    m2 += anomaly * anomaly2;
}

/**
 * @brief Finalizes the audit statistics.
 * Addresses the Baseline Paradox to ensure statistical integrity
 */
void IntegrityGate::report_integrity(double &variance, double &std_dev) {
    // The Baseline Paradox: Check for sufficient degrees of freedom
    if (n < 2) {
        variance = 0.0;
        std_dev = 0.0;
        return;
    }

    // Calculate Entropy (Sample Variance)
    variance = m2 / (n-1);

    // Calculate Volatility (Standard Deviation)
    std_dev = std::sqrt(variance);
}

#include <iostream>
#include <vector>

int main() {
    IntegrityGate gate;
    
    // Simulate high-frequency forensic data points
    std::vector<double> signal_data = {10.5, 11.2, 10.8, 12.5, 11.0, 9.8};

    std::cout << "--- Executing Integrity Gate Audit ---" << std::endl;

    for (double data_point : signal_data) {
        gate.audit_signal(data_point);
        std::cout << "Processing Signal: " << data_point << " | Baseline Updated." << std::endl;
    }

    double final_variance, final_std_dev;
    gate.report_integrity(final_variance, final_std_dev);

    std::cout << "\n--- Audit Report ---" << std::endl;
    std::cout << "Total Samples: " << signal_data.size() << std::endl;
    std::cout << "Final Variance: " << final_variance << std::endl;
    std::cout << "Volatility (Std Dev): " << final_std_dev << std::endl;

    return 0;
}
