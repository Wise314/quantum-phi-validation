"""
Test 13: Random Circuit Sampling

PURPOSE: Test Φ on more complex circuits (random unitaries).

This stress-tests qubits with varied operations, not just specific gates.
More realistic workload than Bell/GHZ states.

NO SYNTHETIC DATA. Real circuit execution only.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.circuit.library import EfficientSU2

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


def create_random_circuit(qubit_idx, num_qubits_total, depth=10, seed=None):
    """
    Create a random single-qubit circuit.
    
    Apply random rotations, then measure.
    Compare final state to expected (computed classically).
    """
    if seed is not None:
        np.random.seed(seed)
    
    qc = QuantumCircuit(num_qubits_total, 1)
    
    for _ in range(depth):
        # Random rotation angles
        theta = np.random.uniform(0, 2*np.pi)
        phi = np.random.uniform(0, 2*np.pi)
        lam = np.random.uniform(0, 2*np.pi)
        
        # Apply U3 gate (most general single-qubit gate)
        qc.u(theta, phi, lam, qubit_idx)
    
    # Final Hadamard to create superposition for measurement
    qc.h(qubit_idx)
    qc.measure(qubit_idx, 0)
    
    return qc


def create_repeated_identity_circuit(qubit_idx, num_qubits_total, depth=50):
    """
    Create circuit that should return to |0⟩.
    
    Apply pairs of gates that cancel: X-X, Y-Y, etc.
    Any deviation from |0⟩ indicates accumulated error.
    """
    qc = QuantumCircuit(num_qubits_total, 1)
    
    for _ in range(depth):
        # X-X cancels
        qc.x(qubit_idx)
        qc.x(qubit_idx)
    
    qc.measure(qubit_idx, 0)
    
    return qc


def create_t_gate_stress_test(qubit_idx, num_qubits_total, depth=20):
    """
    Stress test with T gates (non-Clifford, harder to implement).
    
    T gate has known higher error on most hardware.
    Circuit: T^8 = I, so depth=8n should return to |0⟩
    """
    qc = QuantumCircuit(num_qubits_total, 1)
    
    # T^8 = I (T is pi/4 rotation, 8 of them = 2*pi = identity)
    for _ in range(depth):
        qc.t(qubit_idx)
    
    qc.measure(qubit_idx, 0)
    
    return qc


def main():
    print("="*70)
    print("TEST 13: STRESS TEST CIRCUITS")
    print("="*70)
    print()
    print("Purpose: Test Φ prediction on various circuit types")
    print("Circuits: Identity (X-X pairs), T-gate stress test")
    print()
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    target = backend.target
    
    print(f"Backend: {backend.name}")
    print()
    
    # Calculate Φ for all qubits
    print("Calculating Φ for all qubits...")
    qubit_data = []
    for i in range(backend.num_qubits):
        result = calculate_qubit_phi(backend, target, i)
        if result is not None:
            qubit_data.append(result)
    
    qubit_data.sort(key=lambda x: x['phi'])
    
    # Select test qubits
    low_phi_qubits = qubit_data[:5]
    high_phi_qubits = qubit_data[-5:]
    
    print()
    print("LOW-Φ QUBITS:")
    for q in low_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}")
    
    print()
    print("HIGH-Φ QUBITS:")
    for q in high_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}")
    
    all_qubits = low_phi_qubits + high_phi_qubits
    shots = 1000
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    # Test 1: T-gate stress (T^8 = I, so T^24 = I)
    print()
    print("="*70)
    print("T-GATE STRESS TEST (T^24 should = I, measure |0⟩)")
    print("="*70)
    
    circuits = []
    for q in all_qubits:
        qc = create_t_gate_stress_test(q['qubit'], backend.num_qubits, depth=24)
        circuits.append(pm.run(qc))
    
    print(f"Submitting {len(circuits)} circuits...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=shots)
    print(f"Job ID: {job.job_id()}")
    print("Waiting...")
    
    result = job.result()
    
    print()
    print(f"{'Qubit':<8} {'Group':<10} {'Φ':<10} {'P(0)':<10} {'Error':<10}")
    print("-"*48)
    
    low_errors_t = []
    high_errors_t = []
    
    for i, q in enumerate(all_qubits):
        counts = result[i].data.c.get_counts()
        p0 = counts.get('0', 0) / shots
        error = 1.0 - p0
        
        group = "LOW-Φ" if i < 5 else "HIGH-Φ"
        print(f"Q{q['qubit']:<6} {group:<10} {q['phi']:<10.4f} {p0:<10.3f} {error:<10.3f}")
        
        if i < 5:
            low_errors_t.append(error)
        else:
            high_errors_t.append(error)
    
    print()
    print(f"LOW-Φ mean error: {np.mean(low_errors_t):.4f}")
    print(f"HIGH-Φ mean error: {np.mean(high_errors_t):.4f}")
    
    if np.mean(low_errors_t) > np.mean(high_errors_t):
        ratio_t = np.mean(low_errors_t) / np.mean(high_errors_t) if np.mean(high_errors_t) > 0 else float('inf')
        print(f"LOW-Φ has {ratio_t:.2f}x higher error ✓")
    
    # Test 2: Heavy identity (100 X-X pairs = 200 X gates)
    print()
    print("="*70)
    print("HEAVY IDENTITY TEST (200 X gates, should measure |0⟩)")
    print("="*70)
    
    circuits = []
    for q in all_qubits:
        qc = create_repeated_identity_circuit(q['qubit'], backend.num_qubits, depth=100)
        circuits.append(pm.run(qc))
    
    print(f"Submitting {len(circuits)} circuits...")
    job = sampler.run(circuits, shots=shots)
    print(f"Job ID: {job.job_id()}")
    print("Waiting...")
    
    result = job.result()
    
    print()
    print(f"{'Qubit':<8} {'Group':<10} {'Φ':<10} {'P(0)':<10} {'Error':<10}")
    print("-"*48)
    
    low_errors_id = []
    high_errors_id = []
    
    for i, q in enumerate(all_qubits):
        counts = result[i].data.c.get_counts()
        p0 = counts.get('0', 0) / shots
        error = 1.0 - p0
        
        group = "LOW-Φ" if i < 5 else "HIGH-Φ"
        print(f"Q{q['qubit']:<6} {group:<10} {q['phi']:<10.4f} {p0:<10.3f} {error:<10.3f}")
        
        if i < 5:
            low_errors_id.append(error)
        else:
            high_errors_id.append(error)
    
    print()
    print(f"LOW-Φ mean error: {np.mean(low_errors_id):.4f}")
    print(f"HIGH-Φ mean error: {np.mean(high_errors_id):.4f}")
    
    if np.mean(low_errors_id) > np.mean(high_errors_id):
        ratio_id = np.mean(low_errors_id) / np.mean(high_errors_id) if np.mean(high_errors_id) > 0 else float('inf')
        print(f"LOW-Φ has {ratio_id:.2f}x higher error ✓")
    
    # Summary
    print()
    print("="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    print()
    print(f"T-gate test: LOW-Φ error = {np.mean(low_errors_t):.4f}, HIGH-Φ error = {np.mean(high_errors_t):.4f}")
    print(f"Identity test: LOW-Φ error = {np.mean(low_errors_id):.4f}, HIGH-Φ error = {np.mean(high_errors_id):.4f}")


if __name__ == "__main__":
    main()
