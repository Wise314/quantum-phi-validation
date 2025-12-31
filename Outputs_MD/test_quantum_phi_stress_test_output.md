# Test 13: Stress Test Circuits

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_random_circuit.py`  
**Backend:** ibm_fez

## Purpose

Stress test Φ prediction with T-gates and heavy identity circuits.

## Raw Output
```
LOW-Φ QUBITS:
  Q150: Φ=0.0424
  Q155: Φ=0.0599
  Q46: Φ=0.0726
  Q53: Φ=0.0777
  Q78: Φ=0.0780

HIGH-Φ QUBITS:
  Q130: Φ=0.9989
  Q144: Φ=0.9991
  Q103: Φ=0.9991
  Q142: Φ=0.9991
  Q132: Φ=0.9992

======================================================================
T-GATE STRESS TEST (T^24 should = I, measure |0⟩)
======================================================================
Qubit    Group      Φ          P(0)       Error     
------------------------------------------------
Q150    LOW-Φ      0.0424     1.000      0.000     
Q155    LOW-Φ      0.0599     0.998      0.002     
Q46     LOW-Φ      0.0726     0.998      0.002     
Q53     LOW-Φ      0.0777     0.957      0.043     
Q78     LOW-Φ      0.0780     0.993      0.007     
Q130    HIGH-Φ     0.9989     1.000      0.000     
Q144    HIGH-Φ     0.9991     1.000      0.000     
Q103    HIGH-Φ     0.9991     1.000      0.000     
Q142    HIGH-Φ     0.9991     1.000      0.000     
Q132    HIGH-Φ     0.9992     1.000      0.000     

LOW-Φ mean error: 0.0108
HIGH-Φ mean error: 0.0000
LOW-Φ has inf x higher error ✓

======================================================================
HEAVY IDENTITY TEST (200 X gates, should measure |0⟩)
======================================================================
Qubit    Group      Φ          P(0)       Error     
------------------------------------------------
Q150    LOW-Φ      0.0424     1.000      0.000     
Q155    LOW-Φ      0.0599     0.998      0.002     
Q46     LOW-Φ      0.0726     0.996      0.004     
Q53     LOW-Φ      0.0777     0.957      0.043     
Q78     LOW-Φ      0.0780     0.985      0.015     
Q130    HIGH-Φ     0.9989     1.000      0.000     
Q144    HIGH-Φ     0.9991     1.000      0.000     
Q103    HIGH-Φ     0.9991     0.999      0.001     
Q142    HIGH-Φ     0.9991     0.997      0.003     
Q132    HIGH-Φ     0.9992     1.000      0.000     

LOW-Φ mean error: 0.0128
HIGH-Φ mean error: 0.0008
LOW-Φ has 16.00x higher error ✓

======================================================================
OVERALL SUMMARY
======================================================================
T-gate test: LOW-Φ error = 0.0108, HIGH-Φ error = 0.0000
Identity test: LOW-Φ error = 0.0128, HIGH-Φ error = 0.0008
```

## Summary

| Test | LOW-Φ Error | HIGH-Φ Error | Ratio |
|------|-------------|--------------|-------|
| T-gate stress | 1.08% | 0.00% | ∞ |
| Heavy identity | 1.28% | 0.08% | 16x |

## Key Finding

- Q53 consistently problematic (4.3% error)
- HIGH-Φ qubits essentially perfect on both tests
- Φ predicts stress test performance
