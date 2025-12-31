# Experiments

Test scripts for validating Φ on quantum hardware.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation/experiments
```

## Tests

### test_quantum_phi.py

Single backend test (ibm_fez). Quick validation.
```bash
python test_quantum_phi.py
```

**Key Result:** 156 qubits analyzed, 1 dead qubit identified

### test_quantum_phi_all_backends.py

All 3 backends (445 qubits). Includes correlation analysis.
```bash
python test_quantum_phi_all_backends.py
```

**Key Result:** r = 0.9458 correlation between Φ and T2/T1

### test_quantum_phi_2qubit_gates.py

Two-qubit gate error analysis (1004 gates).
```bash
python test_quantum_phi_2qubit_gates.py
```

**Key Result:** Low-Φ gates have 4.34x higher error

### test_quantum_phi_circuit_validation.py

Simple single-gate circuit test. Inconclusive - gate too fast for coherence effects.
```bash
python test_quantum_phi_circuit_validation.py
```

**Key Result:** Inconclusive (replaced by deep circuit test)

### test_quantum_phi_deep_circuit.py

Deep circuit validation with 10-200 X gates. Proves low-Φ qubits fail on real circuits.
```bash
python test_quantum_phi_deep_circuit.py
```

**Key Result:** LOW-Φ qubits have 25-63x higher circuit error

### test_quantum_phi_threshold_sweep.py

Threshold sensitivity analysis. Validates 0.25 is in optimal range.
```bash
python test_quantum_phi_threshold_sweep.py
```

**Key Result:** Threshold 0.25 in optimal plateau (4.26x discrimination)

## Results Summary

| Test | Finding |
|------|---------|
| Single qubit | 156 qubits, 1 dead identified |
| All backends | r = 0.9458 correlation with T2/T1 |
| Two-qubit gates | 4.34x higher error when min_Φ < 0.25 |
| Simple circuit | Inconclusive (single gate too fast) |
| Deep circuit | 25-63x higher error for low-Φ qubits |
| Threshold sweep | 0.25 validated in optimal plateau |
