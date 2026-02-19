# Experiments

Test scripts for validating Φ on quantum hardware.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation/experiments
```

## Tests (14 Total)

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

### test_quantum_phi_ghz_entanglement.py
GHZ state (3-qubit entanglement) validation.
```bash
python test_quantum_phi_ghz_entanglement.py
```
**Key Result:** LOW-Φ triplets have 4.42x higher entanglement error

### test_quantum_phi_bell_states.py
Bell state (2-qubit entanglement) validation.
```bash
python test_quantum_phi_bell_states.py
```
**Key Result:** Inconclusive (gate quality varies independently of qubit Φ)

### test_quantum_phi_random_circuit.py
Stress tests with T-gates and heavy identity circuits.
```bash
python test_quantum_phi_random_circuit.py
```
**Key Result:** LOW-Φ has 16x-∞ higher error on stress tests

### test_quantum_phi_cross_backend.py
Cross-backend validation on ibm_torino and ibm_marrakesh.
```bash
python test_quantum_phi_cross_backend.py
```
**Key Result:** Φ validated on all backends (2.5x-5.75x discrimination)

### test_quantum_phi_qubit_selection.py
Φ-based qubit selection vs random selection. Core compiler optimization test.
```bash
python test_quantum_phi_qubit_selection.py
```
**Key Result:** 5.99x improvement, 83% error reduction, beats random by 74%

### test_quantum_phi_error_correction.py
Error correction qubit selection using 3-qubit bit-flip code.
```bash
python test_quantum_phi_error_correction.py
```
**Key Result:** 1.22x improvement in logical error rate (weak but positive)

### test_quantum_phi_variational.py
Variational circuit (VQE-style) performance testing.
```bash
python test_quantum_phi_variational.py
```
**Key Result:** Inconclusive (small effect size, noisy metric)

### test_quantum_phi_depth_scaling.py
Circuit depth scaling analysis (10-500 gates).
```bash
python test_quantum_phi_depth_scaling.py
```
**Key Result:** 8-18x discrimination consistent across all depths

## Utility Scripts

### daily_phi_collection.py
Temporal data collection for prediction test. Run daily.
```bash
python daily_phi_collection.py
```

### realtime_monitor.py
Real-time Φ monitoring dashboard.
```bash
python realtime_monitor.py
```

## Results Summary

| Test | Finding | Status |
|------|---------|--------|
| Single qubit | 156 qubits, 1 dead identified | ✓ |
| All backends | r = 0.9458 correlation with T2/T1 | ✓ |
| Two-qubit gates | 4.34x higher error when min_Φ < 0.25 | ✓ |
| Simple circuit | Inconclusive (single gate too fast) | ⚠️ |
| Deep circuit | 25-63x higher error for low-Φ qubits | ✓ |
| Threshold sweep | 0.25 validated in optimal plateau | ✓ |
| GHZ entanglement | 4.42x higher error for low-Φ triplets | ✓ |
| Bell states | Inconclusive (gate quality varies) | ⚠️ |
| Stress tests | 16x-∞ higher error for low-Φ | ✓ |
| Cross-backend | 2.5x-5.75x on torino/marrakesh | ✓ |
| Qubit selection | 5.99x improvement, 83% error reduction | ✓ |
| Error correction | 1.22x improvement in logical error | ✓ (weak) |
| Variational | Inconclusive (small effect) | ⚠️ |
| Depth scaling | 8-18x discrimination (10-500 gates) | ✓ |

**10/13 tests validate Φ. 1 weak positive. 2 inconclusive (not contradictory). 1 deprecated diagnostic (simple circuit).**
