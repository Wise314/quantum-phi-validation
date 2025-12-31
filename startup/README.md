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
4. Copy your API token

### 3. Save credentials
```bash
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_TOKEN_HERE', overwrite=True)"
```

### 4. Verify connection
```bash
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; service = QiskitRuntimeService(); print([b.name for b in service.backends()])"
```

## Available Backends (Free Tier)

- ibm_fez (156 qubits)
- ibm_torino (133 qubits)
- ibm_marrakesh (156 qubits)
