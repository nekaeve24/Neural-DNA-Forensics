#include "../integrity_gate.hpp"
#include <iostream>
#include <vector>

int main() {
    IntegrityGate gate;
    std::vector<double> signal_data = {10.5, 11.2, 10.8, 12.5, 11.0, 9.8};

    for (double data_point : signal_data) {
        gate.audit_signal(data_point);
    }

    double var, sd;
    gate.report_integrity(var, sd);
    std::cout << "C++ Audit Complete. Baseline: " << gate.get_baseline() << std::endl;
    return 0;
}
