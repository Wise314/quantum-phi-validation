"""
Test E: Variational Circuit Performance

PURPOSE: Test Φ impact on variational circuits (VQE/QAOA style).

Variational circuits:
- Many parameterized rotation gates
- Entangling layers
- Multiple repetitions (ansatz depth)

These are the bread-and-butter of near-term quantum computing.
More realistic workload than simple gate tests.

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


def find_connected_pairs(backend, qubit_data):
    """Find connected pairs for 2-qubit variational circuits."""
    coupling_map = backend.coupling_map
    qubit_dict = {q['qubit']: q for q in qubit_data}
    
    pairs = []
    seen = set()
    
    for edge in coupling_map:
        q1, q2 = edge
        
        if q1 not in qubit_dict or q2 not in qubit_dict:
            continue
        
        pair_key = tuple(sorted([q1, q2]))
        if pair_key in seen:
            continue
        seen.add(pair_key)
        
        min_phi = min(qubit_dict[q1]['phi'], qubit_dict[q2]['phi'])
        avg_phi = (qubit_dict[q1]['phi'] + qubit_dict[q2]['phi']) / 2
        
        pairs.append({
            'qubits': [q1, q2],
            'min_phi': min_phi,
            'avg_phi': avg_phi,
            'data': [qubit_dict[q1], qubit_dict[q2]]
        })
    
    return pairs


def create_variational_circuit(qubits, num_qubits_total, layers=4, seed=42):
    """
    Create a VQE-style variational circuit.
    
    Structure per layer:
    - RY rotation on each qubit
    - RZ rotation on each qubit
    - CNOT entangling gate
    
    Final state should be deterministic given fixed parameters.
    We use fixed parameters to test circuit fidelity, not optimization.
    """
    np.random.seed(seed)
    
    qc = QuantumCircuit(num_qubits_total, 2)
    q0, q1 = qubits
    
    for layer in range(layers):
        # Rotation layer
        theta_y0 = np.random.uniform(0, np.pi)
        theta_y1 = np.random.uniform(0, np.pi)
        theta_z0 = np.random.uniform(0, 2*np.pi)
        theta_z1 = np.random.uniform(0, 2*np.pi)
        
        qc.ry(theta_y0, q0)
        qc.ry(theta_y1, q1)
        qc.rz(theta_z0, q0)
        qc.rz(theta_z1, q1)
        
        # Entangling layer
        qc.cx(q0, q1)
        
        qc.barrier()
    
    # Final measurement
    qc.measure(q0, 0)
    qc.measure(q1, 1)
    
    return qc


def create_hardware_efficient_ansatz(qubits, num_qubits_total, layers=6, seed=42):
    """
    Create hardware-efficient ansatz (common in VQE).
    
    More complex than basic variational circuit.
    """
    np.random.seed(seed)
    
    qc = QuantumCircuit(num_qubits_total, 2)
    q0, q1 = qubits
    
    # Initial layer
    qc.h(q0)
    qc.h(q1)
    
    for layer in range(layers):
        # Single qubit rotations (RY, RZ)
        qc.ry(np.random.uniform(0, np.pi), q0)
        qc.ry(np.random.uniform(0, np.pi), q1)
        qc.rz(np.random.uniform(0, 2*np.pi), q0)
        qc.rz(np.random.uniform(0, 2*np.pi), q1)
        
        # Entangling gate
        qc.cx(q0, q1)
        
        # More rotations
        qc.ry(np.random.uniform(0, np.pi), q0)
        qc.ry(np.random.uniform(0, np.pi), q1)
        
        qc.barrier()
    
    qc.measure(q0, 0)
    qc.measure(q1, 1)
    
    return qc


def compute_distribution_error(counts, reference_counts, shots):
    """
    Compute total variation distance between measured and reference distributions.
    
    Lower = more accurate circuit execution.
    """
    all_outcomes = set(counts.keys()) | set(reference_counts.keys())
    
    tvd = 0
    for outcome in all_outcomes:
        p_measured = counts.get(outcome, 0) / shots
        p_reference = reference_counts.get(outcome, 0) / shots
        tvd += abs(p_measured - p_reference)
    
    return tvd / 2  # TVD is half the L1 distance


def main():
    print("="*70)
    print("TEST E: VARIATIONAL CIRCUIT PERFORMANCE")
    print("="*70)
    print()
    print("Purpose: Test Φ impact on VQE/QAOA-style variational circuits")
    print("Method: Run identical circuits on HIGH-Φ vs LOW-Φ qubit pairs")
    print("Metric: Consistency of output distribution across repeated runs")
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
    
    print(f"Valid qubits: {len(qubit_data)}")
    
    # Find connected pairs
    print("Finding connected pairs...")
    pairs = find_connected_pairs(backend, qubit_data)
    pairs.sort(key=lambda x: x['min_phi'])
    
    low_phi_pairs = [p for p in pairs if p['min_phi'] < THRESHOLD]
    high_phi_pairs = [p for p in pairs if p['min_phi'] >= THRESHOLD]
    
    print(f"LOW-Φ pairs (min_Φ < 0.25): {len(low_phi_pairs)}")
    print(f"HIGH-Φ pairs (min_Φ ≥ 0.25): {len(high_phi_pairs)}")
    
    # Select test pairs
    n_test = min(15, len(low_phi_pairs), len(high_phi_pairs))
    test_low = low_phi_pairs[:n_test]
    test_high = high_phi_pairs[-n_test:]
    
    print(f"\nTesting {n_test} pairs from each group")
    
    # Test configurations
    layer_counts = [2, 4, 6, 8]
    shots = 1000
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    print()
    print("="*70)
    print("RUNNING VARIATIONAL CIRCUITS")
    print("="*70)
    
    all_pairs = test_low + test_high
    
    for n_layers in layer_counts:
        print()
        print(f"Ansatz depth: {n_layers} layers")
        print("-" * 50)
        
        # Create circuits with same seed for all pairs
        circuits = []
        for p in all_pairs:
            qc = create_hardware_efficient_ansatz(
                p['qubits'], backend.num_qubits, 
                layers=n_layers, seed=42
            )
            circuits.append(pm.run(qc))
        
        # Run twice to measure consistency
        print(f"Submitting {len(circuits)} circuits (run 1)...")
        sampler = SamplerV2(mode=backend)
        job1 = sampler.run(circuits, shots=shots)
        print(f"Job ID: {job1.job_id()}")
        
        print(f"Submitting {len(circuits)} circuits (run 2)...")
        job2 = sampler.run(circuits, shots=shots)
        print(f"Job ID: {job2.job_id()}")
        
        print("Waiting for results...")
        result1 = job1.result()
        result2 = job2.result()
        
        # Analyze consistency between runs
        low_consistency = []
        high_consistency = []
        
        for i, p in enumerate(all_pairs):
            counts1 = result1[i].data.c.get_counts()
            counts2 = result2[i].data.c.get_counts()
            
            # Compute TVD between two runs (consistency metric)
            tvd = compute_distribution_error(counts1, counts2, shots)
            
            if i < n_test:
                low_consistency.append(tvd)
            else:
                high_consistency.append(tvd)
        
        low_mean = np.mean(low_consistency)
        high_mean = np.mean(high_consistency)
        
        print()
        print(f"{'Group':<12} {'Mean TVD':<12} {'Std TVD':<12} {'n':<6}")
        print("-" * 42)
        print(f"{'LOW-Φ':<12} {low_mean:<12.4f} {np.std(low_consistency):<12.4f} {n_test:<6}")
        print(f"{'HIGH-Φ':<12} {high_mean:<12.4f} {np.std(high_consistency):<12.4f} {n_test:<6}")
        
        if high_mean > 0:
            ratio = low_mean / high_mean
            print(f"\nTVD ratio: {ratio:.2f}x (higher = less consistent)")
            if ratio > 1:
                print("LOW-Φ pairs are LESS consistent ✓")
    
    # Summary across all depths
    print()
    print("="*70)
    print("FINAL ANALYSIS: Entropy of Output Distributions")
    print("="*70)
    print()
    print("Higher entropy = more random/noisy output (worse)")
    print()
    
    # Run one more test measuring output entropy
    circuits = []
    for p in all_pairs:
        qc = create_hardware_efficient_ansatz(
            p['qubits'], backend.num_qubits,
            layers=6, seed=123  # Different seed
        )
        circuits.append(pm.run(qc))
    
    print(f"Submitting {len(circuits)} circuits for entropy analysis...")
    job = sampler.run(circuits, shots=shots)
    print(f"Job ID: {job.job_id()}")
    print("Waiting...")
    
    result = job.result()
    
    low_entropy = []
    high_entropy = []
    
    for i, p in enumerate(all_pairs):
        counts = result[i].data.c.get_counts()
        
        # Compute Shannon entropy
        probs = np.array([v/shots for v in counts.values()])
        probs = probs[probs > 0]  # Remove zeros
        entropy = -np.sum(probs * np.log2(probs))
        
        if i < n_test:
            low_entropy.append(entropy)
        else:
            high_entropy.append(entropy)
    
    print()
    print(f"{'Group':<12} {'Mean Entropy':<14} {'Std':<12}")
    print("-" * 38)
    print(f"{'LOW-Φ':<12} {np.mean(low_entropy):<14.4f} {np.std(low_entropy):<12.4f}")
    print(f"{'HIGH-Φ':<12} {np.mean(high_entropy):<14.4f} {np.std(high_entropy):<12.4f}")
    
    # Max entropy for 2 qubits = 2 bits
    print(f"\n(Max entropy for 2 qubits = 2.0 bits)")
    
    if np.mean(low_entropy) > np.mean(high_entropy):
        diff = np.mean(low_entropy) - np.mean(high_entropy)
        print(f"\nLOW-Φ pairs have {diff:.4f} bits HIGHER entropy (more noise)")
        print("Φ PREDICTS VARIATIONAL CIRCUIT QUALITY")
    
    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    print()
    print("This is REAL variational circuit execution on REAL quantum hardware.")
    print("NO synthetic data. NO simulation.")
    print(f"Total pairs tested: {2 * n_test}")
    print(f"Total circuit configurations: {len(layer_counts) + 1}")


if __name__ == "__main__":
    main()
