/**
 * @file main.cpp
 * @brief Test Bench for the Integrity Gate Sovereign Baseline.
 */

#include <iostream>
#include <vector>
#include <iomanip> // For professional currency formatting
#include "integrity_gate.hpp"

int main() {
    // 1. Initialize the Gate
    IntegrityGate gate;

    // 2. Define the Market Data Stream (Asset prices in dollars)
    std::vector<double> data_signals = {10.2, 12.3, 11.5, 13.1, 9.9};

    // 3. Iterative Integration
    for (double s : data_signals) {
        gate.audit_signal(s);
    }

    // 4. Extract Results
    double entropy, volatility;
    gate.report_integrity(entropy, volatility);

    // 5. Forensic Output: Institutional Formatting
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Audit Complete. Sovereign Baseline: $" << gate.get_baseline() << std::endl;
    
    std::cout << std::setprecision(4);
    std::cout << "Variance (Entropy Score): " << entropy << std::endl;
    
    std::cout << std::setprecision(2);
    std::cout << "Standard Deviation (Volatility): $" << volatility << std::endl;

    return 0;
}
