# Test 12: Bell State Validation

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_bell_states.py`  
**Backend:** ibm_fez

## Purpose

Test Φ prediction on Bell states (2-qubit entanglement).

## Raw Output
```
LOW-Φ PAIRS (worst 10):
  Qubits [149, 150]: min_Φ=0.0424
  Qubits [150, 151]: min_Φ=0.0424
  Qubits [139, 155]: min_Φ=0.0599
  Qubits [154, 155]: min_Φ=0.0599
  Qubits [45, 46]: min_Φ=0.0726
  Qubits [46, 47]: min_Φ=0.0726
  Qubits [39, 53]: min_Φ=0.0777
  Qubits [52, 53]: min_Φ=0.0777
  Qubits [53, 54]: min_Φ=0.0777
  Qubits [69, 78]: min_Φ=0.0780

HIGH-Φ PAIRS (best 10):
  Qubits [131, 138]: min_Φ=0.9910
  Qubits [101, 116]: min_Φ=0.9935
  Qubits [32, 33]: min_Φ=0.9956
  Qubits [87, 88]: min_Φ=0.9958
  Qubits [87, 97]: min_Φ=0.9958
  Qubits [33, 39]: min_Φ=0.9976
  Qubits [92, 93]: min_Φ=0.9976
  Qubits [147, 148]: min_Φ=0.9984
  Qubits [138, 151]: min_Φ=0.9987
  Qubits [151, 152]: min_Φ=0.9987

RESULTS:
Qubits       Group      min_Φ      Bell_Fid   Error      P(00)    P(11)   
----------------------------------------------------------------------
[149, 150]   LOW-Φ      0.0424     0.8750     0.1250     0.644    0.231   
[150, 151]   LOW-Φ      0.0424     0.9810     0.0190     0.473    0.508   
[139, 155]   LOW-Φ      0.0599     0.9840     0.0160     0.505    0.479   
[154, 155]   LOW-Φ      0.0599     0.9800     0.0200     0.498    0.482   
[45, 46]     LOW-Φ      0.0726     0.9610     0.0390     0.497    0.464   
[46, 47]     LOW-Φ      0.0726     0.9310     0.0690     0.459    0.472   
[39, 53]     LOW-Φ      0.0777     0.9300     0.0700     0.484    0.446   
[52, 53]     LOW-Φ      0.0777     0.9390     0.0610     0.492    0.447   
[53, 54]     LOW-Φ      0.0777     0.9560     0.0440     0.508    0.448   
[69, 78]     LOW-Φ      0.0780     0.9710     0.0290     0.480    0.491   
[131, 138]   HIGH-Φ     0.9910     0.9490     0.0510     0.483    0.466   
[101, 116]   HIGH-Φ     0.9935     0.9440     0.0560     0.506    0.438   
[32, 33]     HIGH-Φ     0.9956     0.6340     0.3660     0.321    0.313   
[87, 88]     HIGH-Φ     0.9958     0.9560     0.0440     0.482    0.474   
[87, 97]     HIGH-Φ     0.9958     0.9560     0.0440     0.506    0.450   
[33, 39]     HIGH-Φ     0.9976     0.9710     0.0290     0.507    0.464   
[92, 93]     HIGH-Φ     0.9976     0.9600     0.0400     0.493    0.467   
[147, 148]   HIGH-Φ     0.9984     0.9680     0.0320     0.504    0.464   
[138, 151]   HIGH-Φ     0.9987     0.9760     0.0240     0.482    0.494   
[151, 152]   HIGH-Φ     0.9987     0.9800     0.0200     0.492    0.488   

SUMMARY:
LOW-Φ pairs (n=10):
  Mean min_Φ: 0.0661
  Mean Bell fidelity: 0.9508
  Mean error: 0.0492

HIGH-Φ pairs (n=10):
  Mean min_Φ: 0.9963
  Mean Bell fidelity: 0.9294
  Mean error: 0.0706

Correlation (min_Φ vs error): r = 0.1424
```

## Summary

| Group | Mean Φ | Bell Fidelity | Error |
|-------|--------|---------------|-------|
| LOW-Φ | 0.0661 | 95.08% | 4.92% |
| HIGH-Φ | 0.9963 | 92.94% | 7.06% |

## Key Finding

**INCONCLUSIVE** - Results opposite to prediction.

**Explanation:** Pair [32, 33] has high Φ (0.9956) but only 63.4% Bell fidelity. This indicates a bad two-qubit GATE, not bad qubits. Φ measures single-qubit quality; two-qubit gate quality varies independently.

This is why the calibration-based two-qubit gate test (4.34x discrimination) is more accurate - it uses the actual gate error data.
