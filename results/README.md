# Results

Output data and analysis from quantum Φ validation.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation/results
```

## Summary (December 31, 2025)

### Single Qubit Analysis (445 qubits)

| Backend | Qubits | GOOD | MARGINAL | BAD |
|---------|--------|------|----------|-----|
| ibm_fez | 156 | 89.7% | 9.6% | 0.6% |
| ibm_torino | 133 | 97.0% | 2.3% | 0.8% |
| ibm_marrakesh | 156 | 78.2% | 19.9% | 1.9% |
| **Total** | **445** | **87.9%** | **11.0%** | **1.1%** |

### Correlations

| Metric | Correlation with Φ |
|--------|-------------------|
| T2/T1 Ratio | r = 0.9458 |
| T2 (coherence) | r = 0.6796 |
| Readout Error | r = -0.1627 |

### Group Comparison

| Group | T2 (μs) | T2/T1 | Readout Error |
|-------|---------|-------|---------------|
| Low-Φ (< 0.25) | 30.9 | 0.204 | 0.064 |
| High-Φ (≥ 0.25) | 132.0 | 0.749 | 0.027 |
| **Difference** | **4.3x** | **3.7x** | **2.4x** |

### Two-Qubit Gate Analysis (1004 gates)

| Condition | Mean Error |
|-----------|------------|
| min_Φ < 0.25 | 7.90% |
| min_Φ ≥ 0.25 | 1.82% |
| **Ratio** | **4.34x** |

### Deep Circuit Execution (10 qubits, 4 depths)

Real circuit execution on IBM Quantum hardware.

| Depth | LOW-Φ Error | HIGH-Φ Error | Ratio |
|-------|-------------|--------------|-------|
| 10 gates | 1.14% | 0.00% | ∞ |
| 50 gates | 1.26% | 0.02% | 63x |
| 100 gates | 1.02% | 0.04% | 25x |
| 200 gates | 1.20% | 0.02% | 60x |

**Key Finding:** LOW-Φ qubits have 25-63x higher circuit execution error.

### Threshold Sensitivity Analysis (445 qubits)

| Threshold | T2 Ratio | Note |
|-----------|----------|------|
| 0.05 | 1.94x | |
| 0.10 | 4.41x | |
| 0.15 | 4.74x | Peak |
| 0.20 | 4.35x | |
| **0.25** | **4.26x** | **Theoretical** |
| 0.30 | 3.95x | |
| 0.35 | 3.34x | |

**Key Finding:** Threshold 0.25 is in optimal plateau (within 10% of peak), validating triality derivation.

### Dead Qubits Identified

| Backend | Qubit | Φ | Fidelity |
|---------|-------|---|----------|
| ibm_fez | Q72 | -0.0343 | 0.0000 |
| ibm_torino | Q53 | -0.0431 | 0.0000 |
| ibm_marrakesh | Q82 | -0.0333 | 0.0000 |
| ibm_marrakesh | Q113 | -0.0264 | 0.0000 |
| ibm_marrakesh | Q119 | -0.0212 | 0.0000 |

**Key Finding:** All 5 qubits with Φ < 0 had fidelity = 0.0000 (completely failed).

---

## Validation Summary

| Test | Systems | Key Result |
|------|---------|------------|
| Single qubit calibration | 445 qubits | r = 0.9458 with T2/T1 |
| Two-qubit gates | 1004 gates | 4.34x error discrimination |
| Circuit execution | 10 qubits × 4 depths | 25-63x error discrimination |
| Threshold validation | 445 qubits | 0.25 in optimal plateau |
| Dead qubit detection | 5 qubits | 100% identification |

**Same formula (Φ = I × ρ - α × S) and threshold (0.25) validated on quantum systems as on classical systems (bearings, grids, neural networks).**
