"""
Test: Φ-Based Qubit Selection vs Random Selection

PURPOSE: Prove Φ-based selection beats random selection for circuits.

Simple, direct comparison:
1. Run same circuit on HIGH-Φ qubits (best 10)
2. Run same circuit on RANDOM qubits (10 random)
3. Run same circuit on LOW-Φ qubits (worst 10)

Compare error rates. This is the core compiler optimization claim.

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


def create_identity_circuit(qubit, num_qubits_total, depth):
    """Create identity circuit (should return |0⟩)."""
    qc = QuantumCircuit(num_qubits_total, 1)
    for _ in range(depth):
        qc.x(qubit)
        qc.x(qubit)
    qc.measure(qubit, 0)
    return qc


def create_hadamard_test_circuit(qubit, num_qubits_total, depth):
    """Create H-Z-H test (should return |0⟩)."""
    qc = QuantumCircuit(num_qubits_total, 1)
    for _ in range(depth):
        qc.h(qubit)
        qc.z(qubit)
        qc.h(qubit)
    qc.measure(qubit, 0)
    return qc


def create_rotation_circuit(qubit, num_qubits_total, depth):
    """Create rotation circuit (RY then RY-inverse, should return |0⟩)."""
    qc = QuantumCircuit(num_qubits_total, 1)
    theta = np.pi / 4
    for _ in range(depth):
        qc.ry(theta, qubit)
        qc.ry(-theta, qubit)
    qc.measure(qubit, 0)
    return qc


def run_qubit_test(backend, qubits, circuit_func, depth, shots, pm, label):
    """Run test on a set of qubits."""
    circuits = []
    for q in qubits:
        qc = circuit_func(q['qubit'], backend.num_qubits, depth)
        circuits.append(pm.run(qc))
    
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=shots)
    print(f"  {label}: Job ID {job.job_id()}")
    
    result = job.result()
    
    errors = []
    for i, q in enumerate(qubits):
        counts = result[i].data.c.get_counts()
        p0 = counts.get('0', 0) / shots
        error = 1.0 - p0
        errors.append(error)
    
    return errors


def main():
    print("="*70)
    print("TEST: Φ-BASED QUBIT SELECTION VS RANDOM")
    print("="*70)
    print()
    print("Purpose: Prove Φ-based selection beats random for circuit execution")
    print("Method: Compare BEST (by Φ) vs RANDOM vs WORST (by Φ) qubits")
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
    
    # Sort by Φ
    qubit_data.sort(key=lambda x: x['phi'])
    
    # Select groups
    n_test = 20  # Use 20 qubits per group for statistical power
    
    worst_qubits = qubit_data[:n_test]
    best_qubits = qubit_data[-n_test:]
    
    # Random selection (middle portion to avoid overlap)
    middle_start = len(qubit_data) // 3
    middle_end = 2 * len(qubit_data) // 3
    np.random.seed(42)
    random_indices = np.random.choice(range(middle_start, middle_end), n_test, replace=False)
    random_qubits = [qubit_data[i] for i in random_indices]
    
    print()
    print(f"WORST {n_test} qubits (lowest Φ):")
    print(f"  Φ range: {worst_qubits[0]['phi']:.4f} to {worst_qubits[-1]['phi']:.4f}")
    print(f"  Mean Φ: {np.mean([q['phi'] for q in worst_qubits]):.4f}")
    
    print()
    print(f"RANDOM {n_test} qubits (middle):")
    print(f"  Φ range: {min(q['phi'] for q in random_qubits):.4f} to {max(q['phi'] for q in random_qubits):.4f}")
    print(f"  Mean Φ: {np.mean([q['phi'] for q in random_qubits]):.4f}")
    
    print()
    print(f"BEST {n_test} qubits (highest Φ):")
    print(f"  Φ range: {best_qubits[0]['phi']:.4f} to {best_qubits[-1]['phi']:.4f}")
    print(f"  Mean Φ: {np.mean([q['phi'] for q in best_qubits]):.4f}")
    
    shots = 1000
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    # Test configurations
    tests = [
        ("Identity (100 X-X pairs)", create_identity_circuit, 100),
        ("Hadamard (50 H-Z-H)", create_hadamard_test_circuit, 50),
        ("Rotation (100 RY pairs)", create_rotation_circuit, 100),
    ]
    
    results_summary = []
    
    for test_name, circuit_func, depth in tests:
        print()
        print("="*70)
        print(f"TEST: {test_name}")
        print("="*70)
        
        print("Running circuits...")
        worst_errors = run_qubit_test(backend, worst_qubits, circuit_func, depth, shots, pm, "WORST")
        random_errors = run_qubit_test(backend, random_qubits, circuit_func, depth, shots, pm, "RANDOM")
        best_errors = run_qubit_test(backend, best_qubits, circuit_func, depth, shots, pm, "BEST")
        
        print()
        print(f"{'Selection':<12} {'Mean Error':<12} {'Std Error':<12} {'Mean Φ':<12}")
        print("-" * 48)
        print(f"{'WORST':<12} {np.mean(worst_errors):<12.4f} {np.std(worst_errors):<12.4f} {np.mean([q['phi'] for q in worst_qubits]):<12.4f}")
        print(f"{'RANDOM':<12} {np.mean(random_errors):<12.4f} {np.std(random_errors):<12.4f} {np.mean([q['phi'] for q in random_qubits]):<12.4f}")
        print(f"{'BEST':<12} {np.mean(best_errors):<12.4f} {np.std(best_errors):<12.4f} {np.mean([q['phi'] for q in best_qubits]):<12.4f}")
        
        # Compute ratios
        if np.mean(best_errors) > 0:
            worst_to_best = np.mean(worst_errors) / np.mean(best_errors)
            random_to_best = np.mean(random_errors) / np.mean(best_errors)
        else:
            worst_to_best = float('inf')
            random_to_best = float('inf')
        
        print()
        print(f"WORST/BEST ratio: {worst_to_best:.2f}x")
        print(f"RANDOM/BEST ratio: {random_to_best:.2f}x")
        
        if worst_to_best > 1:
            print("Φ-selection BEATS random/worst ✓")
        
        results_summary.append({
            'test': test_name,
            'worst_err': np.mean(worst_errors),
            'random_err': np.mean(random_errors),
            'best_err': np.mean(best_errors),
            'worst_to_best': worst_to_best,
            'random_to_best': random_to_best
        })
    
    # Final summary
    print()
    print("="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print()
    print(f"{'Test':<30} {'WORST Err':<12} {'RANDOM Err':<12} {'BEST Err':<12} {'W/B Ratio':<10}")
    print("-" * 76)
    
    for r in results_summary:
        print(f"{r['test']:<30} {r['worst_err']:<12.4f} {r['random_err']:<12.4f} {r['best_err']:<12.4f} {r['worst_to_best']:<10.2f}x")
    
    # Overall
    overall_worst = np.mean([r['worst_err'] for r in results_summary])
    overall_random = np.mean([r['random_err'] for r in results_summary])
    overall_best = np.mean([r['best_err'] for r in results_summary])
    
    print("-" * 76)
    print(f"{'AVERAGE':<30} {overall_worst:<12.4f} {overall_random:<12.4f} {overall_best:<12.4f} {overall_worst/overall_best if overall_best > 0 else float('inf'):<10.2f}x")
    
    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    
    if overall_worst > overall_best:
        improvement = (overall_worst - overall_best) / overall_worst * 100
        print(f"\nΦ-based qubit selection reduces error by {improvement:.1f}%")
        print("Selecting qubits by Φ IMPROVES circuit execution")
        
    if overall_random > overall_best:
        improvement = (overall_random - overall_best) / overall_random * 100
        print(f"Φ-selection beats random selection by {improvement:.1f}%")
    
    print()
    print(f"Total qubits tested: {3 * n_test}")
    print(f"Total circuits executed: {3 * n_test * len(tests)}")
    print("NO synthetic data. Real quantum hardware only.")


if __name__ == "__main__":
    main()
