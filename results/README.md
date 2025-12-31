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

### Dead Qubits Identified

| Backend | Qubit | Φ | Fidelity |
|---------|-------|---|----------|
| ibm_fez | Q72 | -0.0343 | 0.0000 |
| ibm_torino | Q53 | -0.0431 | 0.0000 |
| ibm_marrakesh | Q82 | -0.0333 | 0.0000 |
| ibm_marrakesh | Q113 | -0.0264 | 0.0000 |
| ibm_marrakesh | Q119 | -0.0212 | 0.0000 |
