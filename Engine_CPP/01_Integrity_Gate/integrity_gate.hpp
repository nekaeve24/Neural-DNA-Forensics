/**
 * @file integrity_gate.hpp
 * @author Neka Everett
 * @brief Audit 01: Integrity Gate for High-Frequency Forensics.
 * * This architecture implements a homeostatic neuron basedon Welford's Algorithmm. It establishes a Sovereign Baseline to detect systemic entropy.
 */

#ifndef INTEGRITY_GATE_HPP
#define INTEGRITY_GATE_HPP

/**
 * @class IntegrityGate
 * @brief A forensic auditory that maintains a real-time sovereign baseline.
 */
class IntegrityGate{
    private:
        long n; //< Experience Counter: Total signals audited.
        double mu; //< Sovereign Baseline The internal mean price/value.
        double m2; //< Entropy Engine: Accumulated sum of squares (M2).

    public:
        /**
         * @brief Consttuctor: Iniaializes the neuro to a zero-state.
         */
        IntegrityGate() : n(0), mu(0.0), m2(0.0) {}

        /**
         * @brief The Audit Method: Interrogates an incoming signal 'x'.
         * @param x The raw signal value to be audited against the baseline.
         */
        void audit_signal(double x);

        /**
         * @brief Report Integrity: Evaluations the Baseline Paradox and returns results.
         * @param[out] variance The calculated Entropy Score (Risk).
         * @param[out] std_dev The calculated Volatility (Standard Deviation).
         */
        void report_integrity(double &variance, double &std_dev);

        /** @name Forensic Vieweers */
        ///@{
        double get_baseline() const { return mu; }
        long get_experience() const { return n; }
        ///@}
};

#endif // INTEGRITY_GATE_HPP
