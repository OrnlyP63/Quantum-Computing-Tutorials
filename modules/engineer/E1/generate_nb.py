#!/usr/bin/env python3
"""generate_nb.py — Module E1: Quantum Hardware Architectures"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# E1 — Quantum Hardware Architectures
**Track:** Engineer | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4; linear algebra, Python; quantum mechanics helpful |
| **Qiskit Modules** | `qiskit`, `qiskit_ibm_runtime` (optional), `qiskit_aer.noise` |
| **Companion Video** | Engineer Module E1 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Compare the three dominant qubit modalities: **superconducting**, **trapped ion**, and **photonic**
2. Query Qiskit backend properties: **coupling map**, **native gate set**, **T1/T2 times**
3. Visualize the **coupling map** of a multi-qubit processor
4. Understand why **qubit connectivity** constrains circuit routing
5. Map hardware limitations to software design decisions in circuit compilation
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Qubit Technology Comparison

### Superconducting Qubits (IBM, Google, Rigetti)

Based on **Josephson junctions** — quantum LC oscillators operating at ~10 mK.

Key characteristics:
- Qubit type: **transmon** (anharmonic oscillator, 2 lowest energy levels used)
- Gate time: ~50–100 ns (single qubit), ~300–500 ns (CNOT)
- T1 ≈ 100–500 μs, T2 ≈ 50–300 μs
- Coupling: fixed capacitive coupling → limited connectivity (sparse coupling map)
- Gate error: ~0.1–0.5% (1Q), ~0.5–2% (2Q)

> **Eng Bridge:** Coupling map = PCB trace routing — qubits can only interact directly if they share a physical connection. Non-adjacent qubit gates require SWAP routing.

### Trapped Ion Qubits (IonQ, Quantinuum, AQT)

Atomic ions (typically $^{171}$Yb$^+$ or $^{40}$Ca$^+$) trapped by electromagnetic fields.

- Gate time: ~10–100 μs (1Q), ~100–1000 μs (2Q)
- T1, T2: seconds to minutes (much longer than superconducting)
- Coupling: **all-to-all** — any qubit can interact with any other (no routing overhead)
- Gate error: ~0.01–0.1% (2Q) — better fidelity at lower speed

### Photonic Qubits (PsiQuantum, Xanadu)

Photons encoded in polarization or path degrees of freedom.

- Operates at room temperature (big advantage)
- Challenge: probabilistic two-qubit gates, photon loss
- Strong suit: networking, quantum communication, Gaussian boson sampling

### Engineering Bridge

| Property | Superconducting | Trapped Ion | Classical Analogy |
|---|---|---|---|
| Gate speed | Fast (ns) | Slow (μs) | CPU clock speed |
| Connectivity | Sparse (neighbors only) | All-to-all | Network topology |
| Coherence | Short (μs) | Long (ms-s) | Memory retention time |
| T1 | ~100-500 μs | Hours | DRAM refresh time |
| Native gates | CX, U, RZ | XX, Ry, Rz | ISA (instruction set) |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Simulated Backend Properties"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Try to load a fake backend with realistic properties
try:
    from qiskit_ibm_runtime.fake_provider import FakeManhattan, FakeNairobi, FakeKyiv
    backend = FakeManhattan()
    BACKEND_NAME = "FakeManhattan (65 qubits)"
    HAS_FAKE = True
except ImportError:
    try:
        from qiskit_aer.primitives import Estimator
        # Create a synthetic coupling map for demonstration
        HAS_FAKE = False
        BACKEND_NAME = "Synthetic 27-qubit backend"
    except:
        HAS_FAKE = False
        BACKEND_NAME = "Synthetic backend"

print(f"Backend: {BACKEND_NAME}")

if HAS_FAKE:
    config = backend.configuration()
    props  = backend.properties()

    print(f"\nConfiguration:")
    print(f"  Qubits: {config.n_qubits}")
    print(f"  Basis gates: {config.basis_gates}")
    print(f"  Coupling map edges: {len(config.coupling_map)}")
    print(f"  Max shots: {config.max_shots}")

    print(f"\nQubit properties (first 5):")
    print(f"  {'Qubit':6s} {'T1 (μs)':10s} {'T2 (μs)':10s} {'Freq (GHz)':12s} {'ReadErr':10s}")
    print(f"  {'─'*50}")
    for q in range(min(5, config.n_qubits)):
        t1  = props.t1(q) * 1e6
        t2  = props.t2(q) * 1e6
        ro  = props.readout_error(q)
        try:
            freq = props.frequency(q) / 1e9
        except:
            freq = 5.0  # typical IBM transmon frequency
        print(f"  Q{q:2d}    {t1:>8.1f}   {t2:>8.1f}   {freq:>8.3f}    {ro:.4f}")
else:
    # Synthetic data representative of IBM 27-qubit system
    print("\nSynthetic 27-qubit backend properties (representative IBM values):")
    n_qubits = 27
    np.random.seed(42)
    T1_vals = np.random.normal(200, 50, n_qubits)   # μs
    T2_vals = np.random.normal(100, 30, n_qubits)   # μs
    T2_vals = np.minimum(T2_vals, 2*T1_vals)         # T2 ≤ 2T1 (physical constraint)
    readout_err = np.random.uniform(0.01, 0.05, n_qubits)

    print(f"  {'Qubit':6s} {'T1 (μs)':10s} {'T2 (μs)':10s} {'ReadErr':10s}")
    for q in range(5):
        print(f"  Q{q:2d}    {T1_vals[q]:>8.1f}   {T2_vals[q]:>8.1f}   {readout_err[q]:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Coupling Map Visualization"""))

cells.append(nbf.v4.new_code_cell(r"""import networkx as nx

if HAS_FAKE:
    config = backend.configuration()
    coupling_pairs = config.coupling_map
    n_qubits = config.n_qubits
    t1_vals = [backend.properties().t1(q)*1e6 for q in range(n_qubits)]
else:
    # IBM 27-qubit Falcon R5 coupling map (representative)
    # Linear chain with some cross-connections
    n_qubits = 27
    np.random.seed(42)
    T1_vals = np.random.normal(200, 50, n_qubits)
    # IBM-like coupling: heavy-hex topology approximation
    coupling_pairs = []
    for i in range(n_qubits - 1):
        coupling_pairs.append([i, i+1])
    # Add some cross connections
    for i in range(0, n_qubits - 5, 7):
        coupling_pairs.append([i, i+5])
    t1_vals = T1_vals

# Build networkx graph
G = nx.Graph()
G.add_nodes_from(range(n_qubits))
for edge in coupling_pairs:
    if edge[0] < n_qubits and edge[1] < n_qubits:
        G.add_edge(edge[0], edge[1])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Coupling map
ax = axes[0]
if n_qubits <= 27:
    pos = nx.spring_layout(G, seed=42, k=2)
else:
    # For larger backends, use a grid layout approximation
    n_cols = int(np.ceil(np.sqrt(n_qubits)))
    pos = {i: (i % n_cols, -(i // n_cols)) for i in range(n_qubits)}

node_colors = plt.cm.RdYlGn([(t1 - min(t1_vals)) / (max(t1_vals) - min(t1_vals))
                               for t1 in t1_vals[:n_qubits]])
nx.draw_networkx(G, pos=pos, ax=ax,
                 node_color=node_colors[:n_qubits],
                 node_size=300, font_size=7, font_color="black",
                 edge_color="gray", width=1.5)
ax.set_title(f"Coupling Map ({n_qubits} qubits, {G.number_of_edges()} edges)\n"
             "Color = T1 coherence time (green = better)", fontsize=11, fontweight="bold")
ax.axis("off")

sm = plt.cm.ScalarMappable(cmap="RdYlGn",
                             norm=plt.Normalize(vmin=min(t1_vals), vmax=max(t1_vals)))
plt.colorbar(sm, ax=ax, label="T1 (μs)", fraction=0.046)

# T1/T2 histogram
ax2 = axes[1]
t1_arr = np.array(t1_vals[:n_qubits])
t2_arr = np.array([t * 0.6 + np.random.normal(0, 15) for t in t1_arr])  # T2 ≈ 0.6 × T1
t2_arr = np.clip(t2_arr, 10, 2*t1_arr)

bins = np.linspace(0, max(t1_arr.max(), t2_arr.max()) * 1.1, 20)
ax2.hist(t1_arr, bins=bins, alpha=0.7, color="#2196F3", edgecolor="black", label="T1")
ax2.hist(t2_arr, bins=bins, alpha=0.7, color="#FF9800", edgecolor="black", label="T2")
ax2.axvline(t1_arr.mean(), color="blue", ls="--", lw=2, label=f"Mean T1 = {t1_arr.mean():.1f} μs")
ax2.axvline(t2_arr.mean(), color="orange", ls="--", lw=2, label=f"Mean T2 = {t2_arr.mean():.1f} μs")
ax2.set_xlabel("Coherence Time (μs)"); ax2.set_ylabel("Count")
ax2.set_title("T1/T2 Distribution Across Qubits\n"
              "Spread indicates qubit-to-qubit variability", fontsize=11, fontweight="bold")
ax2.legend(fontsize=10)

plt.suptitle(f"Quantum Backend Properties: {BACKEND_NAME}", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("coupling_map.png", dpi=120, bbox_inches="tight")
plt.show()

print(f"\nGraph properties:")
print(f"  Degree distribution: min={min(dict(G.degree()).values())}, "
      f"max={max(dict(G.degree()).values())}, "
      f"avg={np.mean(list(dict(G.degree()).values())):.2f}")
print(f"  Graph diameter (max shortest path): {nx.diameter(G) if nx.is_connected(G) else 'disconnected'}")
print(f"\nEng insight: diameter = min SWAP depth needed to connect any two qubits.")
print(f"More connections = less routing overhead = shallower circuits = less decoherence.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Native Gate Set Analysis"""))

cells.append(nbf.v4.new_code_cell(r"""# How non-native gates are decomposed on IBM hardware

from qiskit.quantum_info import Operator

# IBM native gates: CX, ID, RZ, SX, X
# Let's see how H decomposes into native gates

def analyze_gate_decomposition(gate_name: str, backend_native: list):
    '''Show how a gate decomposes into hardware-native gates.'''
    qc = QuantumCircuit(2)
    if gate_name == "h":
        qc.h(0)
    elif gate_name == "swap":
        qc.swap(0, 1)
    elif gate_name == "t":
        qc.t(0)
    elif gate_name == "ccx":
        qc.ccx(0, 1, 2)
        qc = QuantumCircuit(3)
        qc.ccx(0, 1, 2)

    sim_ideal = AerSimulator()
    qc_t = transpile(qc, sim_ideal, basis_gates=["cx", "u", "id"])

    print(f"\n{gate_name.upper()} gate decomposition → native basis {{CX, U}}:")
    print(qc_t.draw(output="text"))
    print(f"  Original depth: 1")
    print(f"  Native depth: {qc_t.depth()}")
    print(f"  Native gate count: {dict(qc_t.count_ops())}")

for gate in ["h", "t", "swap"]:
    analyze_gate_decomposition(gate, ["cx", "u", "id"])

print("\n\nKey insight: every 'abstract' gate costs multiple native operations.")
print("Circuit depth = accumulated error. Minimize non-native gates.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Circuit Routing Overhead"""))

cells.append(nbf.v4.new_code_cell(r"""# SWAP routing: when qubits aren't adjacent, we need SWAP gates
# Each SWAP = 3 CNOT gates → significant overhead

# A circuit requiring all-to-all connectivity
qc_full = QuantumCircuit(5)
# Entangle qubit 0 with all others (like a "star" connectivity)
for i in range(1, 5):
    qc_full.cx(0, i)
qc_full.measure_all()

print("Abstract circuit (star connectivity):")
print(qc_full.draw(output="text"))
print(f"  Abstract depth: {qc_full.depth()}")
print(f"  CX count: {dict(qc_full.count_ops()).get('cx', 0)}")

# Transpile for a linear coupling map [0-1-2-3-4]
from qiskit.transpiler import CouplingMap
linear_coupling = CouplingMap([[0,1],[1,0],[1,2],[2,1],[2,3],[3,2],[3,4],[4,3]])

qc_t_linear = transpile(qc_full, coupling_map=linear_coupling,
                         basis_gates=["cx","u","id"],
                         optimization_level=3)
print(f"\nAfter transpile (linear coupling [0-1-2-3-4]):")
print(f"  Depth: {qc_t_linear.depth()}")
print(f"  Gate count: {dict(qc_t_linear.count_ops())}")
print(f"  Overhead: {qc_t_linear.depth()} vs {qc_full.depth()} = "
      f"{qc_t_linear.depth()/qc_full.depth():.1f}× deeper")

fig, ax = plt.subplots(figsize=(10, 3))
ax.axis("off")
ax.text(0.05, 0.7, "Abstract (star):", transform=ax.transAxes, fontsize=10, fontweight="bold")
ax.text(0.05, 0.3, str(qc_full.draw(output="text"))[:200],
        transform=ax.transAxes, fontsize=8, fontfamily="monospace")
plt.title("Star Connectivity Requires SWAP Routing on Linear Hardware", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("routing_overhead.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — SWAP Cost Analysis

For a CNOT between non-adjacent qubits separated by distance $d$ in a linear chain, determine the minimum number of SWAP gates needed and express the total CNOT cost.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — SWAP cost analysis

def min_swap_count(d: int) -> int:
    '''Minimum SWAPs needed to perform CNOT between qubits distance d apart in a chain.'''
    return None  # YOUR CODE HERE: d - 1

def total_cnot_cost(d: int) -> int:
    '''Total CNOTs including the SWAPs (each SWAP = 3 CNOTs).'''
    n_swaps = min_swap_count(d)
    return None  # YOUR CODE HERE: 3 * n_swaps + 1  (3 per SWAP + 1 actual CNOT)

distances = range(1, 8)
print(f"{'Distance':10s} {'SWAPs':8s} {'CNOTs total':12s} {'Overhead':10s}")
print("-" * 43)
for d in distances:
    n_sw = min_swap_count(d)
    n_cx = total_cnot_cost(d)
    overhead = n_cx / 1 if n_cx else "N/A"
    print(f"{d:10d} {str(n_sw):>8s} {str(n_cx):>12s} {str(overhead):>10s}")

# YOUR CODE HERE: Verify numerically
print("\nVerification: transpile CNOT(q0, q{d}) on linear chain and count CNOTs")
for d in [1, 2, 3]:
    qc_v = QuantumCircuit(d+1)
    qc_v.cx(0, d)
    linear_cm = CouplingMap([[i, i+1] for i in range(d)] + [[i+1, i] for i in range(d)])
    qc_vt = transpile(qc_v, coupling_map=linear_cm, basis_gates=["cx","u"],
                      optimization_level=3)
    cx_count = dict(qc_vt.count_ops()).get("cx", 0)
    print(f"  CNOT(0, {d}) on linear chain: {cx_count} native CNOTs")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Coherence Time Constraint

Given T1 = 200 μs, T2 = 100 μs, CNOT time = 400 ns, single-qubit gate time = 50 ns:

Calculate the **maximum circuit depth** before the state decoheres to 50% fidelity.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — coherence time constraint

T1_us = 200   # microseconds
T2_us = 100   # microseconds (T2 ≤ 2T1)
T_CNOT_ns = 400   # nanoseconds
T_1Q_ns   = 50    # nanoseconds

# Convert to same units (ns)
T1_ns = T1_us * 1e3
T2_ns = T2_us * 1e3

# Decoherence model: amplitude damping (T1) and dephasing (T2)
# Fidelity after time t: F(t) ≈ exp(-t/T1) for amplitude damping
# For 50% fidelity: 0.5 = exp(-t/T1) → t = T1 * ln(2)
t_half_fidelity_T1 = T1_ns * np.log(2)
t_half_fidelity_T2 = T2_ns * np.log(2)

# Minimum of the two (both channels contribute)
t_critical = min(t_half_fidelity_T1, t_half_fidelity_T2)

print("Coherence Time Constraint Analysis:")
print(f"  T1 = {T1_ns:.0f} ns,  T2 = {T2_ns:.0f} ns")
print(f"  Time to 50% fidelity (T1): {t_half_fidelity_T1:.0f} ns")
print(f"  Time to 50% fidelity (T2): {t_half_fidelity_T2:.0f} ns")
print(f"  Critical time: {t_critical:.0f} ns")
print()
print(f"Maximum circuit complexity:")
print(f"  Using only 1Q gates ({T_1Q_ns} ns each): {t_critical/T_1Q_ns:.0f} gates")
print(f"  Using only CNOT gates ({T_CNOT_ns} ns each): {t_critical/T_CNOT_ns:.0f} gates")
print(f"  Mixed (assume 1 CNOT per 5 single-qubit gates):")
# YOUR CODE: mixed depth calculation
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement a **qubit quality ranking** algorithm that combines T1, T2, gate error, and readout error into a single quality metric for each qubit, then recommend the best subset of $k$ qubits for a $k$-qubit circuit:

$$Q_i = w_1 T_1 + w_2 T_2 - w_3 \epsilon_{\text{gate}} - w_4 \epsilon_{\text{readout}}$$

1. Compute $Q_i$ for all qubits using the backend properties
2. Find the best $k$-qubit subset that is **connected** in the coupling map
3. Visualize the selected qubits on the coupling map
4. Show that transpiling to this subset reduces expected error vs random selection
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Qubit Quality Ranking

def qubit_quality_score(t1, t2, gate_err, readout_err,
                         w1=0.3, w2=0.3, w3=0.2, w4=0.2) -> float:
    '''Combine qubit properties into a quality score (higher = better).'''
    # Normalize to [0,1] — YOUR CODE HERE
    return None

# YOUR CODE HERE:
# 1. Extract properties for all qubits (or use synthetic data)
# 2. Compute quality scores
# 3. Find best connected k-qubit subset using networkx
# 4. Visualize on coupling map

n_q = min(n_qubits, 27)
# Synthetic properties
np.random.seed(42)
T1_q = np.random.normal(200, 50, n_q)
T2_q = np.random.normal(100, 30, n_q)
ge_q = np.random.uniform(0.001, 0.01, n_q)
re_q = np.random.uniform(0.01, 0.05, n_q)

# YOUR CODE HERE: quality scores and best subset selection
quality_scores = [qubit_quality_score(T1_q[i], T2_q[i], ge_q[i], re_q[i])
                  for i in range(n_q)]
print("Qubit quality scores:", [f"{q:.3f}" if q else "None" for q in quality_scores[:5]])
print("Challenge: implement quality scoring and find best 5-qubit connected subset.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **IBM Quantum Hardware** — "IBM Falcon, Eagle, Heron" — ibm.com/quantum/systems
2. **Krantz et al. (2019)** — "A Quantum Engineer's Guide to Superconducting Qubits" — arXiv:1904.06560
3. **Bruzewicz et al. (2019)** — "Trapped-ion quantum computing: Progress and challenges" — arXiv:1904.04178
4. **Qiskit: Backend Properties** — `qiskit_ibm_runtime.IBMBackend.properties()`
5. **Sabre routing algorithm** — Li et al. (2019) "Tackling the Qubit Mapping Problem" — key transpiler paper
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "E1_hardware_architectures.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
