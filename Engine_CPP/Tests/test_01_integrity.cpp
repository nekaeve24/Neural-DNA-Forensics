/**
 * @file test_01_integrity.cpp
 * @brief Forensic Test Bench for Module 01.
 */

#include "../01_Integrity_Gate.hpp"
#include <iostream>
#include <vector>

int main() {
    IntegrityGate gate;
    
    // Using your original forensic data points
    std::vector<double> signal_data = {10.5, 11.2, 10.8, 12.5, 11.0, 9.8};

    std::cout << "--- Executing Integrity Gate Audit ---" << std::endl;

    for (double data_point : signal_data) {
        gate.audit_signal(data_point);
    }

    double final_variance, final_std_dev;
    gate.report_integrity(final_variance, final_std_dev);

    std::cout << "Audit Complete. Baseline: " << gate.get_baseline() << std::endl;
    std::cout << "Final Variance: " << final_variance << std::endl;
    std::cout << "Volatility: " << final_std_dev << std::endl;

    return 0;
}
