/**
 * @file 01_Integrity_Gate.cpp
 * @author Neka Everett
 * @brief Production Implementation of the Integrity Gate.
 */

#include "01_Integrity_Gate.hpp"
#include <cmath>

void IntegrityGate::audit_signal(double x) {
    // A. Increment experience
    n++;

    // B. Calculate the Anomaly (Exception): The deviation from current baseline
    double anomaly = x - mu;

    // C. Integrate the signal into the Sovereign Baseline
    mu += anomaly / n;

    // D. Refine the Anomaly (Exception) against the updated state
    double anomaly2 = x - mu;

    // E. Power the Entropy Engine (Accumulate Sum of Squares)
    m2 += anomaly * anomaly2;
}

void IntegrityGate::report_integrity(double &variance, double &std_dev) {
    // The Baseline Paradox: Check for sufficient degrees of freedom
    if (n < 2) {
        variance = 0.0;
        std_dev = 0.0;
        return;
    }

    // Calculate Entropy (Sample Variance)
    variance = m2 / (n - 1);

    // Calculate Volatility (Standard Deviation)
    std_dev = std::sqrt(variance);
}
