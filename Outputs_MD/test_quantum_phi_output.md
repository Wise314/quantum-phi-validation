# Test: Single Backend Φ Analysis

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi.py`  
**Backend:** ibm_fez (156 qubits)

## Purpose

Validate Φ = I × ρ - α × S on real IBM Quantum calibration data. This is the same formula validated on bearings, turbofans, power grids, earthquakes, and 660 neural network architectures.

## Raw Output
```
======================================================================
QUANTUM SENSOR Φ TEST - REAL IBM QUANTUM DATA
======================================================================

Formula: Φ = I × ρ - α × S
Threshold: 0.25 (same as bearings, grids, neural nets)
Alpha: 0.1

qiskit_runtime_service.__init__:WARNING:2025-12-31 14:06:03,663: Instance was not set at service instantiation. Free and trial plan instances will be prioritized. Based on the following filters: (tags: None, region: us-east, eu-de), and available plans: (open), the available account instances are: open-instance. If you need a specific instance set it explicitly either by using a saved account with a saved default instance or passing it in directly to QiskitRuntimeService().
Pulling calibration data from: ibm_fez

qiskit_runtime_service.backends:WARNING:2025-12-31 14:06:03,663: Using instance: open-instance, plan: open
Number of qubits: 156

Analyzing qubits (REAL DATA ONLY - skipping if unavailable)...
----------------------------------------------------------------------
Qubit    Fidelity   T1(μs)     T2(μs)     ReadErr    Φ          Status    
----------------------------------------------------------------------
0        0.9986     55.3       50.4       0.0122     0.9071     GOOD      
9        0.9998     173.4      33.6       0.0077     0.1928     MARGINAL  
10       0.9998     194.5      128.3      0.0057     0.6590     GOOD      
20       0.9996     119.8      154.4      0.0055     0.9987     GOOD      
30       0.9997     149.0      126.8      0.0068     0.8502     GOOD      
40       0.9998     175.9      190.1      0.0179     0.9978     GOOD      
46       0.9996     180.1      13.2       0.0060     0.0726     MARGINAL  
50       0.9997     160.1      119.5      0.0071     0.7451     GOOD      
53       0.9998     173.6      14.3       0.0485     0.0777     MARGINAL  
60       0.9996     129.3      45.8       0.0317     0.3504     GOOD      
63       0.9994     170.9      14.2       0.0332     0.0795     MARGINAL  
66       0.9997     85.8       14.8       0.0115     0.1711     MARGINAL  
70       0.9997     92.4       79.4       0.0038     0.8582     GOOD      
72       0.0000     6.7        99.2       0.3428     -0.0343    BAD       
78       0.9996     117.4      9.7        0.0498     0.0780     MARGINAL  
80       0.9997     118.4      88.0       0.0555     0.7377     GOOD      
81       0.9998     180.8      21.6       0.0212     0.1174     MARGINAL  
85       0.9998     186.5      35.0       0.0120     0.1863     MARGINAL  
90       0.9996     136.0      131.0      0.0060     0.9617     GOOD      
91       0.9998     148.5      19.9       0.0233     0.1320     MARGINAL  
98       0.9997     119.9      18.8       0.0063     0.1564     MARGINAL  
100      0.9989     103.4      31.4       0.0085     0.3022     GOOD      
110      0.9998     174.1      119.3      0.0046     0.6843     GOOD      
113      0.9998     188.4      41.9       0.0760     0.2146     MARGINAL  
120      0.9998     143.9      161.9      0.0074     0.9988     GOOD      
130      0.9996     100.6      119.1      0.0024     0.9989     GOOD      
140      0.9997     118.1      192.9      0.0138     0.9981     GOOD      
146      0.9999     152.9      15.1       0.0035     0.0986     MARGINAL  
149      0.9990     57.5       6.4        0.0493     0.1067     MARGINAL  
150      0.9990     174.7      7.5        0.0050     0.0424     MARGINAL  
155      0.9998     255.1      15.7       0.0149     0.0599     MARGINAL  
----------------------------------------------------------------------

======================================================================
SUMMARY
======================================================================
Total qubits on device: 156
Qubits with complete data: 156
Qubits skipped (incomplete data): 0

GOOD (Φ ≥ 0.25):         140 (89.7%)
MARGINAL (0 ≤ Φ < 0.25): 15 (9.6%)
BAD (Φ < 0):             1 (0.6%)

WORST 5 QUBITS (lowest Φ):
  Qubit 72: Φ=-0.0343, fidelity=0.0000, T2/T1=1.000
  Qubit 150: Φ=0.0424, fidelity=0.9990, T2/T1=0.043
  Qubit 155: Φ=0.0599, fidelity=0.9998, T2/T1=0.061
  Qubit 46: Φ=0.0726, fidelity=0.9996, T2/T1=0.073
  Qubit 53: Φ=0.0777, fidelity=0.9998, T2/T1=0.083

BEST 5 QUBITS (highest Φ):
  Qubit 130: Φ=0.9989, fidelity=0.9996, T2/T1=1.000
  Qubit 144: Φ=0.9991, fidelity=0.9998, T2/T1=1.000
  Qubit 103: Φ=0.9991, fidelity=0.9998, T2/T1=1.000
  Qubit 142: Φ=0.9991, fidelity=0.9997, T2/T1=1.000
  Qubit 132: Φ=0.9992, fidelity=0.9997, T2/T1=1.000

======================================================================
WHAT THIS MEANS
======================================================================
This is REAL calibration data from IBM Quantum.
NO synthetic data. NO hardcoded values.

The Φ formula is IDENTICAL to what predicted:
  - UK power blackout (Φ = 0.178)
  - Tohoku M9.1 earthquake (Φ = -0.357)
  - 660 neural network architectures
```

## Summary

- Total qubits analyzed: 156
- GOOD (Φ ≥ 0.25): 140 (89.7%)
- MARGINAL (0 ≤ Φ < 0.25): 15 (9.6%)
- BAD (Φ < 0): 1 (0.6%)
- Dead qubit identified: Q72 (Φ = -0.0343, fidelity = 0.0000)
