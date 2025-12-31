"""
Test 4b: Deep Circuit Validation

PURPOSE: Prove low-Φ qubits fail on DEEPER circuits where coherence matters.

A single Hadamard gate takes ~50ns.
T2 times are ~10-200μs.

For coherence to matter, we need circuits that take longer.
This test runs repeated gates to stress the coherence.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ALPHA = 0.1


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


def create_identity_circuit(qubit_idx, num_qubits, depth):
    """
    Create a circuit that SHOULD return to |0⟩.
    
    Apply X gate 'depth' times. Even depth = should measure 0.
    Errors accumulate with depth, revealing coherence issues.
    """
    qc = QuantumCircuit(num_qubits, 1)
    
    for _ in range(depth):
        qc.x(qubit_idx)
    
    qc.measure(qubit_idx, 0)
    return qc


def main():
    print("="*70)
    print("TEST 4b: DEEP CIRCUIT VALIDATION")
    print("="*70)
    print()
    print("Purpose: Prove low-Φ qubits fail on deeper circuits")
    print("Method: Run many X gates (even number = should return to |0⟩)")
    print("        Errors accumulate, revealing coherence differences")
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
    
    low_phi_qubits = qubit_data[:5]
    high_phi_qubits = qubit_data[-5:]
    
    print()
    print("LOW-Φ QUBITS (worst 5):")
    for q in low_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, T2={q['t2']:.1f}μs, T2/T1={q['t2_t1']:.3f}")
    
    print()
    print("HIGH-Φ QUBITS (best 5):")
    for q in high_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, T2={q['t2']:.1f}μs, T2/T1={q['t2_t1']:.3f}")
    
    # Test at multiple depths
    depths = [10, 50, 100, 200]
    shots = 1000
    
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    all_test_qubits = low_phi_qubits + high_phi_qubits
    
    for depth in depths:
        print()
        print("="*70)
        print(f"DEPTH = {depth} X gates (even, should return |0⟩)")
        print("="*70)
        
        circuits = []
        for q_data in all_test_qubits:
            qc = create_identity_circuit(q_data['qubit'], backend.num_qubits, depth)
            qc_transpiled = pm.run(qc)
            circuits.append(qc_transpiled)
        
        print(f"Submitting {len(circuits)} circuits...")
        
        sampler = SamplerV2(mode=backend)
        job = sampler.run(circuits, shots=shots)
        print(f"Job ID: {job.job_id()}")
        print("Waiting...")
        
        result = job.result()
        
        low_errors = []
        high_errors = []
        
        print()
        print(f"{'Qubit':<8} {'Group':<8} {'Φ':<8} {'T2(μs)':<10} {'P(0)':<8} {'Error':<8}")
        print("-"*58)
        
        for i, q_data in enumerate(all_test_qubits):
            counts = result[i].data.c.get_counts()
            p0 = counts.get('0', 0) / shots
            error = 1.0 - p0  # Should be 0, so error = 1 - p0
            
            group = "LOW-Φ" if i < 5 else "HIGH-Φ"
            print(f"Q{q_data['qubit']:<6} {group:<8} {q_data['phi']:<8.4f} {q_data['t2']:<10.1f} {p0:<8.3f} {error:<8.3f}")
            
            if i < 5:
                low_errors.append(error)
            else:
                high_errors.append(error)
        
        print()
        print(f"LOW-Φ mean error:  {np.mean(low_errors):.4f}")
        print(f"HIGH-Φ mean error: {np.mean(high_errors):.4f}")
        
        if np.mean(low_errors) > np.mean(high_errors):
            ratio = np.mean(low_errors) / np.mean(high_errors) if np.mean(high_errors) > 0 else float('inf')
            print(f"LOW-Φ has {ratio:.2f}x HIGHER error ✓")
        else:
            print("No significant difference at this depth")
    
    print()
    print("="*70)
    print("INTERPRETATION")
    print("="*70)
    print("If errors increase MORE for low-Φ qubits at higher depth,")
    print("then Φ predicts coherence-limited circuit performance.")


if __name__ == "__main__":
    main()
