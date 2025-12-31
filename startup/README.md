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

### Threshold validation
```bash
python test_quantum_phi_threshold_sweep.py
```

## Free Tier Limits

- 10 minutes quantum time per month
- Access to 3 backends
- No historical calibration data
- Queue times vary (usually 1-5 minutes)

## Troubleshooting

### "Instance was not set" warning

This is normal on free tier. Tests will still run.

### Job stuck in queue

Free tier has lower priority. Wait or try a different backend.

### Token invalid

Regenerate token at https://quantum.ibm.com → Account settings → API keys
