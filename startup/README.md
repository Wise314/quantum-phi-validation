# Startup

Setup scripts and IBM Quantum configuration.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation
```

## Prerequisites

1. Python 3.8+
2. IBM Quantum account (free): https://quantum.ibm.com

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get IBM Quantum API token

1. Go to https://quantum.ibm.com
2. Sign in or create account
3. Click profile icon → Account settings
4. Create new API key (name it anything, e.g., "phi-quantum-test")
5. Copy your API token

### 3. Save credentials
```bash
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_TOKEN_HERE', overwrite=True)"
```

### 4. Verify connection
```bash
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; service = QiskitRuntimeService(); print([b.name for b in service.backends()])"
```

Expected output:
```
['ibm_fez', 'ibm_torino', 'ibm_marrakesh']
```

## Available Backends (Free Tier)

| Backend | Qubits | Architecture |
|---------|--------|--------------|
| ibm_fez | 156 | Heron r2 |
| ibm_torino | 133 | Heron r1 |
| ibm_marrakesh | 156 | Heron r2 |

## Running Tests

### Quick test (single backend)
```bash
cd ~/Desktop/quantum-phi-validation/experiments
python test_quantum_phi.py
```

### Full validation (all backends)
```bash
python test_quantum_phi_all_backends.py
```

### Two-qubit gate analysis
```bash
python test_quantum_phi_2qubit_gates.py
```

### Circuit execution test (runs on real hardware)
```bash
python test_quantum_phi_deep_circuit.py
```

### Depth scaling test (10-500 gates)
```bash
python test_quantum_phi_depth_scaling.py
```

### Threshold validation
```bash
python test_quantum_phi_threshold_sweep.py
```

### GHZ entanglement test
```bash
python test_quantum_phi_ghz_entanglement.py
```

### Bell state test
```bash
python test_quantum_phi_bell_states.py
```

### Stress tests (T-gate and identity)
```bash
python test_quantum_phi_random_circuit.py
```

### Cross-backend validation
```bash
python test_quantum_phi_cross_backend.py
```

### Qubit selection test
```bash
python test_quantum_phi_qubit_selection.py
```

### Error correction test
```bash
python test_quantum_phi_error_correction.py
```

### Variational circuit test
```bash
python test_quantum_phi_variational.py
```

## Utility Scripts

### Daily Φ data collection (run daily for temporal prediction)
```bash
python daily_phi_collection.py
```

### Real-time monitoring dashboard
```bash
python realtime_monitor.py
```

## All Tests Summary

| Test | Script | Time | Result |
|------|--------|------|--------|
| Single backend | test_quantum_phi.py | ~1 min | r = 0.9458 |
| All backends | test_quantum_phi_all_backends.py | ~2 min | 445 qubits |
| Two-qubit gates | test_quantum_phi_2qubit_gates.py | ~2 min | 4.34x |
| Deep circuit | test_quantum_phi_deep_circuit.py | ~5 min | 25-63x |
| Depth scaling | test_quantum_phi_depth_scaling.py | ~10 min | 8-18x |
| Threshold sweep | test_quantum_phi_threshold_sweep.py | ~2 min | 0.25 validated |
| GHZ entanglement | test_quantum_phi_ghz_entanglement.py | ~3 min | 4.42x |
| Bell states | test_quantum_phi_bell_states.py | ~3 min | Inconclusive |
| Stress tests | test_quantum_phi_random_circuit.py | ~5 min | 16x-∞ |
| Cross-backend | test_quantum_phi_cross_backend.py | ~10 min | 2.5x-5.75x |
| Qubit selection | test_quantum_phi_qubit_selection.py | ~5 min | 5.99x, 83% |
| Error correction | test_quantum_phi_error_correction.py | ~5 min | 1.22x |
| Variational | test_quantum_phi_variational.py | ~5 min | Inconclusive |

## Utility Scripts Summary

| Script | Purpose | Frequency |
|--------|---------|-----------|
| daily_phi_collection.py | Collect Φ snapshots for temporal prediction | Daily |
| realtime_monitor.py | Live monitoring dashboard | On demand |

## Free Tier Limits

- 10 minutes quantum time per month
- Access to 3 backends
- No historical calibration data via API
- Queue times vary (usually 1-5 minutes)

## Troubleshooting

### "Instance was not set" warning

This is normal on free tier. Tests will still run.

### Job stuck in queue

Free tier has lower priority. Wait or try a different backend.

### Token invalid

Regenerate token at https://quantum.ibm.com → Account settings → API keys

### Out of quantum time

Free tier gives 10 min/month. Check usage at https://quantum.ibm.com → Dashboard.

### Circuit execution errors

Some qubits may be temporarily offline. The scripts skip invalid qubits automatically.
