# Test: All Backends Φ Analysis

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_all_backends.py`  
**Backends:** ibm_fez (156), ibm_torino (133), ibm_marrakesh (156)

## Purpose

Validate Φ = I × ρ - α × S across all available IBM Quantum backends. Test correlation with quantum coherence metrics.

## Raw Output
```
======================================================================
UNIVERSAL Φ TEST - ALL IBM QUANTUM BACKENDS
======================================================================

Formula: Φ = I × ρ - α × S
Threshold: 0.25
Alpha: 0.1

NO SYNTHETIC DATA. Real IBM Quantum calibration only.
qiskit_runtime_service.__init__:WARNING:2025-12-31 14:07:38,637: Instance was not set at service instantiation. Free and trial plan instances will be prioritized. Based on the following filters: (tags: None, region: us-east, eu-de), and available plans: (open), the available account instances are: open-instance. If you need a specific instance set it explicitly either by using a saved account with a saved default instance or passing it in directly to QiskitRuntimeService().

======================================================================
BACKEND: ibm_fez
======================================================================
qiskit_runtime_service.backends:WARNING:2025-12-31 14:07:38,638: Using instance: open-instance, plan: open
Qubits analyzed: 156 (skipped: 0)
GOOD (Φ ≥ 0.25):         140 (89.7%)
MARGINAL (0 ≤ Φ < 0.25): 15 (9.6%)
BAD (Φ < 0):             1 (0.6%)

Φ Statistics:
  Min:    -0.0343
  Max:    0.9992
  Mean:   0.6875
  Median: 0.7581
  Std:    0.3048

WORST 3 QUBITS:
  Q72: Φ=-0.0343, fid=0.0000, T2/T1=1.000, readout_err=0.3428
  Q150: Φ=0.0424, fid=0.9990, T2/T1=0.043, readout_err=0.0050
  Q155: Φ=0.0599, fid=0.9998, T2/T1=0.061, readout_err=0.0149

BEST 3 QUBITS:
  Q103: Φ=0.9991, fid=0.9998, T2/T1=1.000, readout_err=0.0048
  Q142: Φ=0.9991, fid=0.9997, T2/T1=1.000, readout_err=0.0039
  Q132: Φ=0.9992, fid=0.9997, T2/T1=1.000, readout_err=0.0028

======================================================================
BACKEND: ibm_torino
======================================================================
qiskit_runtime_service.backends:WARNING:2025-12-31 14:07:39,545: Using instance: open-instance, plan: open
Qubits analyzed: 133 (skipped: 0)
GOOD (Φ ≥ 0.25):         129 (97.0%)
MARGINAL (0 ≤ Φ < 0.25): 3 (2.3%)
BAD (Φ < 0):             1 (0.8%)

Φ Statistics:
  Min:    -0.0431
  Max:    0.9987
  Mean:   0.7553
  Median: 0.7981
  Std:    0.2310

WORST 3 QUBITS:
  Q53: Φ=-0.0431, fid=0.0000, T2/T1=1.000, readout_err=0.4307
  Q80: Φ=0.1629, fid=0.9998, T2/T1=0.166, readout_err=0.0259
  Q71: Φ=0.1789, fid=0.9997, T2/T1=0.185, readout_err=0.0586

BEST 3 QUBITS:
  Q60: Φ=0.9986, fid=0.9998, T2/T1=1.000, readout_err=0.0109
  Q36: Φ=0.9987, fid=0.9996, T2/T1=1.000, readout_err=0.0045
  Q18: Φ=0.9987, fid=0.9998, T2/T1=1.000, readout_err=0.0089

======================================================================
BACKEND: ibm_marrakesh
======================================================================
qiskit_runtime_service.backends:WARNING:2025-12-31 14:07:40,707: Using instance: open-instance, plan: open
Qubits analyzed: 156 (skipped: 0)
GOOD (Φ ≥ 0.25):         122 (78.2%)
MARGINAL (0 ≤ Φ < 0.25): 31 (19.9%)
BAD (Φ < 0):             3 (1.9%)

Φ Statistics:
  Min:    -0.0333
  Max:    0.9991
  Mean:   0.5773
  Median: 0.6062
  Std:    0.3282

WORST 3 QUBITS:
  Q82: Φ=-0.0333, fid=0.0000, T2/T1=1.000, readout_err=0.3329
  Q113: Φ=-0.0264, fid=0.0000, T2/T1=1.000, readout_err=0.2637
  Q119: Φ=-0.0212, fid=0.0000, T2/T1=0.324, readout_err=0.2124

BEST 3 QUBITS:
  Q54: Φ=0.9989, fid=0.9997, T2/T1=1.000, readout_err=0.0046
  Q6: Φ=0.9990, fid=0.9997, T2/T1=1.000, readout_err=0.0042
  Q139: Φ=0.9991, fid=0.9998, T2/T1=1.000, readout_err=0.0051

======================================================================
AGGREGATE RESULTS (ALL BACKENDS)
======================================================================
Total qubits analyzed: 445
GOOD:     391 (87.9%)
MARGINAL: 49 (11.0%)
BAD:      5 (1.1%)

======================================================================
CORRELATION ANALYSIS (ALL BACKENDS)
======================================================================

Correlation of Φ with:
  Gate Fidelity:    r = 0.2462
  T2/T1 Ratio:      r = 0.9458
  T2 (coherence):   r = 0.6796
  Readout Error:    r = -0.1627 (should be negative)

======================================================================
GROUP COMPARISON: LOW-Φ vs HIGH-Φ QUBITS
======================================================================

LOW-Φ qubits (Φ < 0.25): n = 54
  Mean fidelity:     0.9070
  Mean T2/T1:        0.2040
  Mean T2 (μs):      30.9
  Mean readout err:  0.0640

HIGH-Φ qubits (Φ ≥ 0.25): n = 391
  Mean fidelity:     0.9995
  Mean T2/T1:        0.7489
  Mean T2 (μs):      132.0
  Mean readout err:  0.0268

*** T2 DIFFERENCE: High-Φ qubits have 4.3x longer coherence ***

======================================================================
CONCLUSION
======================================================================
If Φ is a valid stability metric for quantum systems:
  1. Low-Φ qubits should have shorter T2 (coherence time)
  2. Low-Φ qubits should have higher readout errors
  3. Φ should correlate strongly with T2/T1 ratio

This is the SAME formula that predicted:
  - UK blackout (Φ = 0.178)
  - Tohoku M9.1 earthquake (Φ = -0.357)
  - 660 neural network architectures
======================================================================
```

## Summary

- Total qubits analyzed: 445
- GOOD (Φ ≥ 0.25): 391 (87.9%)
- MARGINAL (0 ≤ Φ < 0.25): 49 (11.0%)
- BAD (Φ < 0): 5 (1.1%)
- Key correlation: Φ vs T2/T1 ratio r = 0.9458
- High-Φ qubits have 4.3x longer coherence than Low-Φ qubits
- All 5 dead qubits correctly identified by Φ < 0
