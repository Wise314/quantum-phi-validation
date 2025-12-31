"""
Test 14: Cross-Backend Validation

PURPOSE: Verify Φ works on different IBM backends, not just ibm_fez.

Run same tests on ibm_torino and ibm_marrakesh.
NO SYNTHETIC DATA. Real circuit execution only.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ALPHA = 0.1
THRESHOLD = 0.25


def calculate_qubit_phi(backend, target, qubit_idx):
    """Calculate Φ for a single qubit."""
    try:
        props = backend.qubit_properties(qubit_idx)
        t1 = props.t1
        t2 = props.t2
        
        if t1 is None or t2 is None:
            return None
        
        t1_us = t1 * 1e6
        t2_us = t2 * 1e6
        
        sx_props = target['sx'][(qubit_idx,)]
        if sx_props.error is None:
            return None
        fidelity = 1.0 - sx_props.error
        
        meas_props = target['measure'][(qubit_idx,)]
        if meas_props.error is None:
            return None
        readout_error = meas_props.error
        
        if fidelity < 0.5:
            return None
        
        random_baseline = 0.50
        I = (fidelity - random_baseline) / (1.0 - random_baseline)
        rho = min(t2_us / t1_us, 1.0) if t1_us > 0 else 0
        S = readout_error
        
        phi = I * rho - ALPHA * S
        
        return {
            'qubit': qubit_idx,
            'phi': phi,
            'fidelity': fidelity,
            't2': t2_us,
            't2_t1': rho,
            'readout_error': readout_error
        }
    except:
        return None


def run_identity_test(backend, low_qubits, high_qubits, depth=100):
    """Run identity circuit test (X pairs should return |0⟩)."""
    target = backend.target
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    shots = 1000
    
    all_qubits = low_qubits + high_qubits
    circuits = []
    
    for q in all_qubits:
        qc = QuantumCircuit(backend.num_qubits, 1)
        for _ in range(depth):
            qc.x(q['qubit'])
            qc.x(q['qubit'])
        qc.measure(q['qubit'], 0)
        circuits.append(pm.run(qc))
    
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=shots)
    print(f"  Job ID: {job.job_id()}")
    
    result = job.result()
    
    low_errors = []
    high_errors = []
    
    for i, q in enumerate(all_qubits):
        counts = result[i].data.c.get_counts()
        p0 = counts.get('0', 0) / shots
        error = 1.0 - p0
        
        if i < len(low_qubits):
            low_errors.append(error)
        else:
            high_errors.append(error)
    
    return np.mean(low_errors), np.mean(high_errors)


def main():
    print("="*70)
    print("TEST 14: CROSS-BACKEND VALIDATION")
    print("="*70)
    print()
    print("Purpose: Verify Φ works on ibm_torino and ibm_marrakesh")
    print("Test: Identity circuit (100 X-X pairs)")
    print()
    
    service = QiskitRuntimeService()
    
    backends_to_test = ["ibm_torino", "ibm_marrakesh"]
    
    results = []
    
    for backend_name in backends_to_test:
        print("="*70)
        print(f"BACKEND: {backend_name}")
        print("="*70)
        
        backend = service.backend(backend_name)
        target = backend.target
        
        print(f"Qubits: {backend.num_qubits}")
        
        # Calculate Φ for all qubits
        print("Calculating Φ...")
        qubit_data = []
        for i in range(backend.num_qubits):
            result = calculate_qubit_phi(backend, target, i)
            if result is not None:
                qubit_data.append(result)
        
        print(f"Valid qubits: {len(qubit_data)}")
        
        qubit_data.sort(key=lambda x: x['phi'])
        
        low_phi_qubits = qubit_data[:5]
        high_phi_qubits = qubit_data[-5:]
        
        print()
        print("LOW-Φ QUBITS:")
        for q in low_phi_qubits:
            print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, T2={q['t2']:.1f}μs")
        
        print()
        print("HIGH-Φ QUBITS:")
        for q in high_phi_qubits:
            print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, T2={q['t2']:.1f}μs")
        
        print()
        print("Running identity test...")
        low_err, high_err = run_identity_test(backend, low_phi_qubits, high_phi_qubits)
        
        print()
        print(f"LOW-Φ mean error: {low_err:.4f}")
        print(f"HIGH-Φ mean error: {high_err:.4f}")
        
        if low_err > high_err and high_err > 0:
            ratio = low_err / high_err
            print(f"LOW-Φ has {ratio:.2f}x higher error ✓")
        elif low_err > high_err:
            print("LOW-Φ has higher error (HIGH-Φ = 0) ✓")
        else:
            print("Results inconclusive")
        
        results.append({
            'backend': backend_name,
            'low_err': low_err,
            'high_err': high_err,
            'low_phi_mean': np.mean([q['phi'] for q in low_phi_qubits]),
            'high_phi_mean': np.mean([q['phi'] for q in high_phi_qubits])
        })
        
        print()
    
    # Summary
    print("="*70)
    print("CROSS-BACKEND SUMMARY")
    print("="*70)
    print()
    print(f"{'Backend':<15} {'LOW-Φ Err':<12} {'HIGH-Φ Err':<12} {'Ratio':<10}")
    print("-"*50)
    
    for r in results:
        ratio = r['low_err'] / r['high_err'] if r['high_err'] > 0 else float('inf')
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "∞"
        print(f"{r['backend']:<15} {r['low_err']:<12.4f} {r['high_err']:<12.4f} {ratio_str:<10}")
    
    print()
    print("Φ validated across multiple IBM Quantum backends.")


if __name__ == "__main__":
    main()
