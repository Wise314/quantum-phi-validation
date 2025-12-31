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

## Results Summary

| Test | Finding |
|------|---------|
| Single qubit | Φ correlates with coherence (r = 0.9458) |
| Two-qubit gates | min_Φ < 0.25 → 4.34x higher error |
| Dead qubits | All 5 identified by Φ < 0 |
