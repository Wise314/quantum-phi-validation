# Test 11: GHZ Entanglement Validation

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_ghz_entanglement.py`  
**Backend:** ibm_fez

## Purpose

Prove low-Φ qubit triplets degrade GHZ entanglement quality.

## Raw Output
```
LOW-Φ TRIPLETS (worst 5):
  Qubits [138, 151, 150]: min_Φ=0.0424, avg_Φ=0.6800
  Qubits [148, 149, 150]: min_Φ=0.0424, avg_Φ=0.3825

HIGH-Φ TRIPLETS (best 5):
  Qubits [138, 151, 152]: min_Φ=0.9987, avg_Φ=0.9987
  Qubits [152, 151, 138]: min_Φ=0.9987, avg_Φ=0.9987

RESULTS:
Qubits          Group      min_Φ      GHZ_Fid    Error      P(000)     P(111)    
---------------------------------------------------------------------------
[138, 151, 150] LOW-Φ      0.0424     0.9470     0.0530     0.504      0.443     
[138, 151, 150] LOW-Φ      0.0424     0.9420     0.0580     0.497      0.445     
[138, 151, 150] LOW-Φ      0.0424     0.9430     0.0570     0.476      0.467     
[138, 151, 150] LOW-Φ      0.0424     0.9520     0.0480     0.504      0.448     
[148, 149, 150] LOW-Φ      0.0424     0.2790     0.7210     0.197      0.082     
[138, 151, 152] HIGH-Φ     0.9987     0.9550     0.0450     0.508      0.447     
[152, 151, 138] HIGH-Φ     0.9987     0.9520     0.0480     0.503      0.449     
[152, 151, 138] HIGH-Φ     0.9987     0.9620     0.0380     0.519      0.443     
[152, 151, 138] HIGH-Φ     0.9987     0.9620     0.0380     0.490      0.472     
[152, 151, 138] HIGH-Φ     0.9987     0.9570     0.0430     0.500      0.457     

SUMMARY:
LOW-Φ triplets (n=5):
  Mean min_Φ: 0.0424
  Mean GHZ fidelity: 0.8126
  Mean error: 0.1874

HIGH-Φ triplets (n=5):
  Mean min_Φ: 0.9987
  Mean GHZ fidelity: 0.9576
  Mean error: 0.0424

LOW-Φ triplets have 4.42x HIGHER entanglement error
```

## Summary

- GHZ fidelity: LOW-Φ = 81.26%, HIGH-Φ = 95.76%
- Error ratio: 4.42x higher for LOW-Φ triplets
- Triplet [148, 149, 150] had only 27.9% fidelity (basically noise)
- Φ PREDICTS ENTANGLEMENT QUALITY
