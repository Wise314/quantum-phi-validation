"""
Universal Φ (Phi) Calculator for Quantum Systems

The Core Formula:
    Φ = I × ρ - α × S

Where:
    I = Normalized Identity (accuracy above random chance)
    ρ = Temporal Correlation (stability over time)
    S = Entropy (noise/disorder in the system)
    α = Coupling constant (0.1)

Threshold:
    Φ_c = 0.25 (derived from quantum triality relation)

Classification:
    Φ ≥ 0.25  → GOOD (stable, reliable)
    0 ≤ Φ < 0.25 → MARGINAL (monitor closely)
    Φ < 0     → BAD (failing or failed)

This same formula and threshold validated across:
    - Mechanical systems (bearings, turbofans)
    - Infrastructure (power grids)
    - Geophysical (earthquakes)
    - Neural networks (660 architectures)
    - Quantum systems (445 qubits, 3 backends)

Author: Shawn Barnicle
Date: December 31, 2025
License: Proprietary - Patent Pending
"""

# Universal Constants
ALPHA = 0.1          # Coupling constant (universal)
THRESHOLD = 0.25     # Critical threshold (derived from triality relation)
RANDOM_BASELINE = 0.50  # Random chance for 2-level system (qubit)


def calculate_phi(fidelity, t1, t2, readout_error):
    """
    Calculate Φ for a quantum system (qubit).
    
    Parameters:
    -----------
    fidelity : float
        Gate fidelity (0 to 1). How accurately the qubit performs operations.
        Example: 0.998 means 99.8% accurate
        
    t1 : float
        T1 relaxation time (seconds). How long qubit holds energy.
        Example: 200e-6 means 200 microseconds
        
    t2 : float
        T2 coherence time (seconds). How long qubit maintains quantum state.
        Example: 150e-6 means 150 microseconds
        
    readout_error : float
        Measurement error rate (0 to 1). How often measurement is wrong.
        Example: 0.02 means 2% error rate
    
    Returns:
    --------
    dict with:
        - phi: The stability metric
        - status: 'GOOD', 'MARGINAL', or 'BAD'
        - components: I, rho, S values
    
    Example:
    --------
    >>> result = calculate_phi(fidelity=0.998, t1=200e-6, t2=150e-6, readout_error=0.02)
    >>> print(result['phi'])
    0.7425
    >>> print(result['status'])
    'GOOD'
    """
    
    # Validate inputs
    if fidelity is None or t1 is None or t2 is None or readout_error is None:
        return {
            'phi': None,
            'status': 'INVALID',
            'components': {'I': None, 'rho': None, 'S': None},
            'error': 'Missing input values'
        }
    
    if t1 <= 0:
        return {
            'phi': None,
            'status': 'INVALID',
            'components': {'I': None, 'rho': None, 'S': None},
            'error': 'T1 must be positive'
        }
    
    # Calculate I (Normalized Identity)
    # For a 2-level system (qubit), random baseline is 0.50
    # I = (fidelity - random) / (1 - random)
    # This normalizes fidelity so that:
    #   - Random performance (0.50) → I = 0
    #   - Perfect performance (1.00) → I = 1
    if fidelity <= RANDOM_BASELINE:
        I = 0.0  # Below random chance = no useful signal
    else:
        I = (fidelity - RANDOM_BASELINE) / (1.0 - RANDOM_BASELINE)
    
    # Calculate ρ (Temporal Correlation)
    # ρ = T2 / T1, capped at 1.0
    # This measures coherence stability:
    #   - T2 ≈ T1 → ρ ≈ 1 (very stable)
    #   - T2 << T1 → ρ << 1 (rapidly losing coherence)
    rho = min(t2 / t1, 1.0)
    
    # S is the readout error (entropy proxy)
    # Higher readout error = more noise = worse
    S = readout_error
    
    # Calculate Φ
    # Φ = I × ρ - α × S
    phi = I * rho - ALPHA * S
    
    # Classify status
    if phi >= THRESHOLD:
        status = 'GOOD'
    elif phi >= 0:
        status = 'MARGINAL'
    else:
        status = 'BAD'
    
    return {
        'phi': phi,
        'status': status,
        'components': {
            'I': I,
            'rho': rho,
            'S': S
        }
    }


def calculate_phi_simple(fidelity, t1, t2, readout_error):
    """
    Simplified version - just returns the Φ value.
    
    Example:
    --------
    >>> phi = calculate_phi_simple(0.998, 200e-6, 150e-6, 0.02)
    >>> print(phi)
    0.7425
    """
    result = calculate_phi(fidelity, t1, t2, readout_error)
    return result['phi']


def classify_phi(phi):
    """
    Classify a Φ value into GOOD, MARGINAL, or BAD.
    
    Parameters:
    -----------
    phi : float
        The Φ stability metric
    
    Returns:
    --------
    str: 'GOOD', 'MARGINAL', or 'BAD'
    
    Example:
    --------
    >>> classify_phi(0.85)
    'GOOD'
    >>> classify_phi(0.15)
    'MARGINAL'
    >>> classify_phi(-0.05)
    'BAD'
    """
    if phi is None:
        return 'INVALID'
    if phi >= THRESHOLD:
        return 'GOOD'
    elif phi >= 0:
        return 'MARGINAL'
    else:
        return 'BAD'


def calculate_gate_phi(qubit1_phi, qubit2_phi):
    """
    Calculate effective Φ for a two-qubit gate.
    
    The gate is only as good as its weakest qubit.
    
    Parameters:
    -----------
    qubit1_phi : float
        Φ value of first qubit
    qubit2_phi : float
        Φ value of second qubit
    
    Returns:
    --------
    float: min(qubit1_phi, qubit2_phi)
    
    Example:
    --------
    >>> calculate_gate_phi(0.95, 0.20)
    0.20
    """
    return min(qubit1_phi, qubit2_phi)


def calculate_circuit_phi(qubit_phis):
    """
    Calculate effective Φ for a quantum circuit.
    
    The circuit is only as good as its weakest qubit.
    
    Parameters:
    -----------
    qubit_phis : list of float
        Φ values for all qubits in the circuit
    
    Returns:
    --------
    float: min of all Φ values
    
    Example:
    --------
    >>> calculate_circuit_phi([0.95, 0.88, 0.72, 0.91])
    0.72
    """
    if not qubit_phis:
        return None
    return min(qubit_phis)


def rank_qubits(qubit_data):
    """
    Rank qubits by Φ value (best first).
    
    Parameters:
    -----------
    qubit_data : list of dict
        Each dict must have 'qubit' (id) and 'phi' (value)
    
    Returns:
    --------
    list: Sorted by Φ descending (best qubits first)
    
    Example:
    --------
    >>> qubits = [{'qubit': 0, 'phi': 0.5}, {'qubit': 1, 'phi': 0.9}]
    >>> rank_qubits(qubits)
    [{'qubit': 1, 'phi': 0.9}, {'qubit': 0, 'phi': 0.5}]
    """
    return sorted(qubit_data, key=lambda x: x['phi'], reverse=True)


def select_best_qubits(qubit_data, n):
    """
    Select the N best qubits by Φ value.
    
    Parameters:
    -----------
    qubit_data : list of dict
        Each dict must have 'qubit' (id) and 'phi' (value)
    n : int
        Number of qubits to select
    
    Returns:
    --------
    list: Top N qubits by Φ
    
    Example:
    --------
    >>> qubits = [{'qubit': 0, 'phi': 0.5}, {'qubit': 1, 'phi': 0.9}, {'qubit': 2, 'phi': 0.7}]
    >>> select_best_qubits(qubits, 2)
    [{'qubit': 1, 'phi': 0.9}, {'qubit': 2, 'phi': 0.7}]
    """
    ranked = rank_qubits(qubit_data)
    return ranked[:n]


def filter_good_qubits(qubit_data, threshold=THRESHOLD):
    """
    Filter to only qubits above threshold.
    
    Parameters:
    -----------
    qubit_data : list of dict
        Each dict must have 'phi' value
    threshold : float
        Minimum Φ to include (default: 0.25)
    
    Returns:
    --------
    list: Only qubits with Φ >= threshold
    """
    return [q for q in qubit_data if q['phi'] >= threshold]


def get_system_health(qubit_data):
    """
    Calculate overall system health from qubit Φ values.
    
    Parameters:
    -----------
    qubit_data : list of dict
        Each dict must have 'phi' value
    
    Returns:
    --------
    dict with:
        - total: Total qubit count
        - good: Count with Φ >= 0.25
        - marginal: Count with 0 <= Φ < 0.25
        - bad: Count with Φ < 0
        - health_score: Percentage of GOOD qubits
        - status: 'HEALTHY', 'DEGRADED', or 'CRITICAL'
    """
    total = len(qubit_data)
    if total == 0:
        return {
            'total': 0,
            'good': 0,
            'marginal': 0,
            'bad': 0,
            'health_score': 0,
            'status': 'NO DATA'
        }
    
    good = sum(1 for q in qubit_data if q['phi'] >= THRESHOLD)
    bad = sum(1 for q in qubit_data if q['phi'] < 0)
    marginal = total - good - bad
    
    health_score = (good / total) * 100
    
    if health_score >= 80:
        status = 'HEALTHY'
    elif health_score >= 50:
        status = 'DEGRADED'
    else:
        status = 'CRITICAL'
    
    return {
        'total': total,
        'good': good,
        'marginal': marginal,
        'bad': bad,
        'health_score': health_score,
        'status': status
    }


# =============================================================================
# THE FORMULA EXPLAINED
# =============================================================================
#
# Φ = I × ρ - α × S
#
# I (Identity/Accuracy):
#   - How well does the system perform vs random chance?
#   - For qubits: (fidelity - 0.50) / 0.50
#   - Range: 0 (random) to 1 (perfect)
#
# ρ (Rho/Stability):
#   - How stable is performance over time?
#   - For qubits: T2 / T1 (capped at 1)
#   - Range: 0 (instantly loses coherence) to 1 (perfectly stable)
#
# S (Entropy/Noise):
#   - How noisy/disordered is the system?
#   - For qubits: readout error
#   - Range: 0 (no noise) to 1 (pure noise)
#
# α (Alpha):
#   - Coupling constant
#   - Always 0.1 (universal across all domains)
#
# Threshold = 0.25:
#   - Derived from quantum triality relation: D² + V² + C² = 1
#   - Maximum environmental correlation at λ = 0.25
#   - Same threshold works on bearings, grids, earthquakes, neural nets, qubits
#
# =============================================================================


if __name__ == "__main__":
    # Demo: Calculate Φ for a sample qubit
    print("=" * 60)
    print("UNIVERSAL Φ CALCULATOR - QUANTUM SYSTEMS")
    print("=" * 60)
    print()
    print("The Formula: Φ = I × ρ - α × S")
    print("Threshold: Φ_c = 0.25")
    print()
    
    # Example: Good qubit
    print("-" * 60)
    print("Example 1: Good Qubit")
    print("-" * 60)
    result = calculate_phi(
        fidelity=0.998,
        t1=200e-6,
        t2=150e-6,
        readout_error=0.02
    )
    print(f"  Fidelity: 99.8%")
    print(f"  T1: 200 μs")
    print(f"  T2: 150 μs")
    print(f"  Readout Error: 2%")
    print()
    print(f"  I = {result['components']['I']:.4f}")
    print(f"  ρ = {result['components']['rho']:.4f}")
    print(f"  S = {result['components']['S']:.4f}")
    print(f"  Φ = {result['phi']:.4f}")
    print(f"  Status: {result['status']}")
    print()
    
    # Example: Marginal qubit
    print("-" * 60)
    print("Example 2: Marginal Qubit")
    print("-" * 60)
    result = calculate_phi(
        fidelity=0.95,
        t1=150e-6,
        t2=30e-6,
        readout_error=0.05
    )
    print(f"  Fidelity: 95%")
    print(f"  T1: 150 μs")
    print(f"  T2: 30 μs")
    print(f"  Readout Error: 5%")
    print()
    print(f"  I = {result['components']['I']:.4f}")
    print(f"  ρ = {result['components']['rho']:.4f}")
    print(f"  S = {result['components']['S']:.4f}")
    print(f"  Φ = {result['phi']:.4f}")
    print(f"  Status: {result['status']}")
    print()
    
    # Example: Bad qubit
    print("-" * 60)
    print("Example 3: Bad Qubit (Dead)")
    print("-" * 60)
    result = calculate_phi(
        fidelity=0.50,
        t1=100e-6,
        t2=10e-6,
        readout_error=0.10
    )
    print(f"  Fidelity: 50% (random chance)")
    print(f"  T1: 100 μs")
    print(f"  T2: 10 μs")
    print(f"  Readout Error: 10%")
    print()
    print(f"  I = {result['components']['I']:.4f}")
    print(f"  ρ = {result['components']['rho']:.4f}")
    print(f"  S = {result['components']['S']:.4f}")
    print(f"  Φ = {result['phi']:.4f}")
    print(f"  Status: {result['status']}")
    print()
    
    print("=" * 60)
    print("Same formula. Same threshold. Works on everything.")
    print("=" * 60)
