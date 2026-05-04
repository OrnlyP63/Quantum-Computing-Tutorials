import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""# E3 · Transpilation & Circuit Optimization

**Track:** Engineer | **Module:** E3 of 6

> *"The gap between your circuit and what runs on hardware is where most quantum engineers lose performance."*

## Learning Objectives
1. Understand the full transpilation pipeline: unrolling → routing → scheduling → optimization.
2. Compare optimization levels 0–3 and their trade-offs (compile time vs circuit quality).
3. Analyse depth, gate count, and SWAP overhead as functions of coupling map topology.
4. Write custom transpiler passes using Qiskit's `PassManager`.
5. Measure transpilation's impact on output fidelity.
"""))

# ── Setup ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1 · Setup"))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator, state_fidelity, Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error

try:
    from qiskit_ibm_runtime.fake_provider import FakeManhattan
    backend = FakeManhattan()
    FAKE_BACKEND = True
    print(f"FakeManhattan loaded: {backend.num_qubits} qubits")
except ImportError:
    FAKE_BACKEND = False
    print("FakeManhattan unavailable — using AerSimulator with coupling map")

# Build a simple 5-qubit linear coupling map if no backend
from qiskit.transpiler import CouplingMap
linear_coupling = CouplingMap.from_line(5)
"""))

# ── Section 2: Transpilation Pipeline ────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 2 · The Transpilation Pipeline

Transpilation transforms a logical circuit into one that can execute on a specific backend.
The pipeline has four major stages:

```
Logical Circuit
      │
      ▼
1. Unrolling      — decompose gates into backend's basis gate set
      │
      ▼
2. SWAP Routing   — map logical qubits to physical qubits, insert SWAPs
      │             where connectivity is missing
      ▼
3. Optimization   — peephole optimisation, commutation, cancellation
      │
      ▼
4. Scheduling     — assign timing (for pulse-level control)
      │
      ▼
Hardware-Native Circuit
```

### Basis Gates (IBM Superconducting)

$$\{RZ(\theta),\ SX,\ X,\ CNOT,\ Reset,\ Measure\}$$

Every gate you write (H, T, Toffoli…) is decomposed into these. The cost is measured in **CNOT count** (the dominant error source).
"""))

cells.append(nbf.v4.new_code_cell("""\
# Demonstrate gate decomposition
from qiskit.circuit.library import TGate, CCXGate

# Show how expensive Toffoli (CCX) is in native gates
qc_toffoli = QuantumCircuit(3)
qc_toffoli.ccx(0, 1, 2)

if FAKE_BACKEND:
    toffoli_decomposed = transpile(qc_toffoli, backend=backend, optimization_level=1)
    print("Toffoli decomposed into native gates:")
    print(f"  Original: 1 CCX gate, depth=1")
    print(f"  Transpiled: {toffoli_decomposed.count_ops()} operations, depth={toffoli_decomposed.depth()}")
    cx_count = toffoli_decomposed.count_ops().get("cx", 0)
    print(f"  CNOT count: {cx_count}  (each ~5× more error than single-qubit)")
else:
    print("Toffoli = 6 CNOTs + single-qubit gates (standard decomposition)")
    print("This is why Toffoli gates are avoided on NISQ hardware.")
"""))

# ── Section 3: Optimization Levels ───────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 3 · Optimization Levels 0–3

Qiskit's `transpile()` accepts `optimization_level` ∈ {0, 1, 2, 3}:

| Level | Strategy | Use case |
|-------|----------|----------|
| 0 | Only mandatory transforms (routing + basis) | Fastest compile, worst circuit |
| 1 | Light optimization: 1Q gate cancellation | Good default for quick runs |
| 2 | Full peephole: commutativity, layout search | Production use |
| 3 | Heaviest: noise-adaptive layout, Hoare logic | Maximum fidelity, slow compile |

Higher levels trade **compilation time** for **circuit quality**.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Test circuit: 5-qubit QFT (moderate depth, many CNOTs)
from qiskit.circuit.library import QFT

n = 5
qc_test = QFT(n, do_swaps=False)
print(f"QFT({n}) logical circuit: depth={qc_test.decompose().depth()}, "
      f"ops={dict(qc_test.decompose().count_ops())}")

results = {}
for level in range(4):
    if FAKE_BACKEND:
        tqc = transpile(qc_test, backend=backend, optimization_level=level, seed_transpiler=42)
    else:
        tqc = transpile(
            qc_test,
            coupling_map=linear_coupling,
            basis_gates=["cx", "u1", "u2", "u3"],
            optimization_level=level,
            seed_transpiler=42,
        )
    results[level] = {
        "depth": tqc.depth(),
        "cx_count": tqc.count_ops().get("cx", 0),
        "total_ops": sum(tqc.count_ops().values()),
        "swap_count": tqc.count_ops().get("swap", 0),
    }
    print(f"Level {level}: depth={tqc.depth():4d}, "
          f"CX={tqc.count_ops().get('cx', 0):4d}, "
          f"total_ops={sum(tqc.count_ops().values()):5d}, "
          f"SWAPs={tqc.count_ops().get('swap', 0):3d}")
"""))

cells.append(nbf.v4.new_code_cell("""\
# Visualise optimization level comparison
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
levels = list(results.keys())
metrics = [("depth", "Circuit Depth"), ("cx_count", "CNOT Count"), ("total_ops", "Total Operations")]
colors = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db"]

for ax, (key, title) in zip(axes, metrics):
    vals = [results[l][key] for l in levels]
    bars = ax.bar(levels, vals, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Optimization Level")
    ax.set_ylabel(title)
    ax.set_title(title)
    ax.set_xticks(levels)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

plt.suptitle(f"QFT({n}) Transpilation: Optimization Level Comparison", fontsize=12)
plt.tight_layout()
plt.savefig("E3_optimization_levels.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 4: SWAP Routing ───────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 4 · SWAP Routing & Coupling Map Topology

Hardware qubits are not all-to-all connected. A CNOT between non-adjacent qubits
requires SWAP gates to move qubit states along the connectivity graph.

**SWAP cost**: each SWAP = 3 CNOTs → adds significant error.

The routing problem is NP-hard in general. Qiskit uses heuristic algorithms:
- **Basic** (level 0): trivial insertion
- **Stochastic SWAP** (level 1-2): randomised search
- **SABRE** (level 3): look-ahead routing

### Coupling map topologies

| Topology | SWAP overhead | Qubit count |
|----------|--------------|-------------|
| Linear chain | High | Scalable |
| Grid (2D lattice) | Medium | Scalable |
| Heavy-hex (IBM) | Low | IBM production |
| All-to-all | Zero | Small (trapped ion) |
"""))

cells.append(nbf.v4.new_code_cell("""\
import networkx as nx

# Build different coupling maps and visualise
def make_coupling_graph(coupling_map):
    G = nx.DiGraph()
    edges = list(coupling_map.get_edges())
    G.add_edges_from(edges)
    return G

# Three topologies
topologies = {
    "Linear (5Q)": CouplingMap.from_line(5),
    "Grid (2x3)": CouplingMap.from_grid(2, 3),
    "Full (5Q)": CouplingMap.from_full(5),
}

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, (name, cm) in zip(axes, topologies.items()):
    G = make_coupling_graph(cm)
    # Layout
    if "Linear" in name:
        pos = {i: (i, 0) for i in range(5)}
    elif "Grid" in name:
        pos = {0: (0,1), 1: (1,1), 2: (2,1), 3: (0,0), 4: (1,0), 5: (2,0)}
    else:
        pos = nx.circular_layout(G)

    nx.draw_networkx(G, pos=pos, ax=ax, with_labels=True,
                     node_color="steelblue", node_size=600,
                     font_color="white", font_weight="bold",
                     edge_color="gray", arrows=True, arrowsize=15,
                     connectionstyle="arc3,rad=0.1")
    ax.set_title(name)
    ax.axis("off")

plt.suptitle("Coupling Map Topologies", fontsize=13)
plt.tight_layout()
plt.savefig("E3_coupling_maps.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_code_cell("""\
# SWAP overhead vs distance in linear chain
def worst_case_cnot_cost(n_qubits):
    \"\"\"CNOT between qubit 0 and qubit n-1 on linear chain requires (n-2) SWAPs.\"\"\"
    swaps = max(0, n_qubits - 2)
    cnots = 1 + 3 * swaps
    return swaps, cnots

sizes = range(2, 21)
swap_counts = []
cnot_costs = []
for n in sizes:
    sw, cx = worst_case_cnot_cost(n)
    swap_counts.append(sw)
    cnot_costs.append(cx)

fig, ax1 = plt.subplots(figsize=(9, 4))
ax2 = ax1.twinx()
ax1.plot(sizes, swap_counts, "b-o", markersize=5, label="SWAPs inserted")
ax2.plot(sizes, cnot_costs, "r-s", markersize=5, label="Total CNOTs")
ax1.set_xlabel("Number of qubits (linear chain)")
ax1.set_ylabel("SWAP count", color="blue")
ax2.set_ylabel("Equivalent CNOT count", color="red")
ax1.set_title("SWAP Routing Overhead: Long-Range CNOT on Linear Chain")
ax1.tick_params(axis="y", labelcolor="blue")
ax2.tick_params(axis="y", labelcolor="red")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
ax1.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("E3_swap_overhead.png", dpi=120, bbox_inches="tight")
plt.show()

print("SWAP routing overhead table:")
print(f"{'Qubits':>8} {'SWAPs':>8} {'Equiv. CNOTs':>14}")
for n, sw, cx in zip(sizes, swap_counts, cnot_costs):
    print(f"{n:8d} {sw:8d} {cx:14d}")
"""))

# ── Section 5: Custom PassManager ────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 5 · Custom PassManager

Qiskit's transpiler is built from **passes** — individual transformations.
You can compose passes into a `PassManager` for fine-grained control.

### Pass categories
- **Analysis passes**: collect information (don't modify circuit)
- **Transformation passes**: modify the circuit DAG
- **Routing passes**: insert SWAPs for connectivity

For most use cases, `optimization_level=3` is sufficient. Custom passes are used when:
1. You have domain knowledge about your circuit structure.
2. You want to inject noise-aware layout choices.
3. You're targeting a non-standard backend.
"""))

cells.append(nbf.v4.new_code_cell("""\
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import (
    Unroller,
    CXCancellation,
    CommutativeCancellation,
    Optimize1qGates,
    SetLayout,
)
from qiskit.transpiler.layout import Layout

# Build a minimal custom pass manager
basis = ["cx", "u1", "u2", "u3"]

custom_pm = PassManager([
    Unroller(basis),           # decompose to basis gates
    CXCancellation(),          # cancel adjacent CX pairs: CX·CX = I
    CommutativeCancellation(), # exploit gate commutativity
    Optimize1qGates(),         # merge consecutive single-qubit rotations
])

# Test on a circuit with redundant gates
qc_redundant = QuantumCircuit(2)
qc_redundant.h(0)
qc_redundant.cx(0, 1)
qc_redundant.cx(0, 1)   # cancels with previous CX
qc_redundant.h(0)       # H·H = I
qc_redundant.cx(0, 1)

print("Original circuit:")
print(qc_redundant.draw())
print(f"Original: depth={qc_redundant.depth()}, ops={dict(qc_redundant.count_ops())}")

qc_opt = custom_pm.run(qc_redundant)
print("\\nOptimised circuit:")
print(qc_opt.draw())
print(f"Optimised: depth={qc_opt.depth()}, ops={dict(qc_opt.count_ops())}")
print(f"Gates removed: {sum(qc_redundant.count_ops().values()) - sum(qc_opt.count_ops().values())}")
"""))

# ── Section 6: Transpilation Fidelity Impact ──────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 6 · Measuring Transpilation's Impact on Fidelity

Deeper circuits accumulate more noise. We quantify this by comparing:
- **Ideal statevector** (from logical circuit)
- **Noisy simulation** of transpiled circuit (realistic execution)

$$F = |\langle\psi_{\text{ideal}}|\psi_{\text{noisy}}\rangle|^2$$
"""))

cells.append(nbf.v4.new_code_cell("""\
# Build a noise model matching the assumed gate error rates
p_1q = 0.001   # 0.1% single-qubit error
p_cx = 0.01    # 1% CNOT error

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(depolarizing_error(p_1q, 1), ["u1", "u2", "u3", "h"])
noise_model.add_all_qubit_quantum_error(depolarizing_error(p_cx, 2), ["cx"])
sim_noisy = AerSimulator(noise_model=noise_model)
sim_ideal = AerSimulator()

# Test: GHZ state on 4 qubits (needs 3 CNOTs minimum)
def ghz_circuit(n):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc

n_qubits_range = range(2, 8)
fidelities = {level: [] for level in range(4)}

for n in n_qubits_range:
    qc = ghz_circuit(n)
    sv_ideal = Statevector.from_instruction(qc)

    for level in range(4):
        # Add measurements for simulation
        qc_meas = qc.copy()
        qc_meas.measure_all()

        if FAKE_BACKEND:
            tqc = transpile(qc_meas, backend=backend, optimization_level=level, seed_transpiler=0)
        else:
            tqc = transpile(
                qc_meas,
                coupling_map=linear_coupling if n <= 5 else CouplingMap.from_line(n),
                basis_gates=["cx", "u1", "u2", "u3"],
                optimization_level=level,
                seed_transpiler=0,
            )

        result = sim_noisy.run(tqc, shots=4096).result()
        counts = result.get_counts()

        # Compute TVD-based proxy fidelity
        total = sum(counts.values())
        ideal_counts = {
            "0" * n: 0.5,
            "1" * n: 0.5,
        }
        tvd = 0.5 * sum(
            abs(counts.get(k, 0) / total - ideal_counts.get(k, 0))
            for k in set(counts) | set(ideal_counts)
        )
        fidelities[level].append(1 - tvd)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db"]
for level in range(4):
    ax.plot(list(n_qubits_range), fidelities[level], "o-",
            color=colors[level], label=f"Level {level}", markersize=6)

ax.set_xlabel("Number of qubits (GHZ circuit)")
ax.set_ylabel("Estimated fidelity (1 - TVD)")
ax.set_title("GHZ State Fidelity vs Qubit Count — Optimization Level Comparison")
ax.legend()
ax.grid(alpha=0.3)
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig("E3_fidelity_vs_level.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 7: Layout Strategies ─────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 7 · Qubit Layout Strategies

**Layout** = the mapping of logical qubits to physical qubits.

A good layout minimises:
1. SWAP count (place frequently-connected qubits near each other).
2. Total error (place sensitive qubits on lowest-error physical qubits).

### Qiskit layout algorithms

| Algorithm | Level | Strategy |
|-----------|-------|----------|
| `TrivialLayout` | 0 | q0→0, q1→1, … |
| `DenseLayout` | 1–2 | Minimise CNOT distance |
| `NoiseAdaptiveLayout` | 3 | Minimise expected error |
| `SabreLayout` | 2–3 | Iterative routing-aware layout |
"""))

cells.append(nbf.v4.new_code_cell("""\
# Compare TrivialLayout vs SabreLayout on a 5-qubit circuit
qc_5q = QuantumCircuit(5)
qc_5q.h(0)
for i in range(4):
    qc_5q.cx(i, i+1)
qc_5q.cx(4, 0)    # long-range connection — expensive on linear chain!
qc_5q.measure_all()

layout_results = {}
for level, label in [(0, "Trivial (L0)"), (3, "Sabre (L3)")]:
    if FAKE_BACKEND:
        tqc = transpile(qc_5q, backend=backend, optimization_level=level, seed_transpiler=0)
    else:
        tqc = transpile(qc_5q, coupling_map=linear_coupling,
                        basis_gates=["cx", "u1", "u2", "u3"],
                        optimization_level=level, seed_transpiler=0)
    layout_results[label] = {
        "depth": tqc.depth(),
        "cx": tqc.count_ops().get("cx", 0),
        "swaps": tqc.count_ops().get("swap", 0),
    }
    print(f"{label}: depth={tqc.depth()}, CX={tqc.count_ops().get('cx',0)}, "
          f"SWAPs={tqc.count_ops().get('swap',0)}")

# Summary bar chart
fig, axes = plt.subplots(1, 3, figsize=(11, 4))
metrics = ["depth", "cx", "swaps"]
titles = ["Circuit Depth", "CNOT Count", "SWAP Count"]
colors = ["#3498db", "#e74c3c"]
for ax, m, t in zip(axes, metrics, titles):
    vals = [layout_results[k][m] for k in layout_results]
    bars = ax.bar(list(layout_results.keys()), vals, color=colors, edgecolor="black")
    ax.set_title(t)
    ax.set_ylabel(t)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

plt.suptitle("Layout Strategy Comparison (5-qubit ring circuit)", fontsize=12)
plt.tight_layout()
plt.savefig("E3_layout_comparison.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 8: Summary ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 8 · Summary

| Topic | Key Insight |
|-------|------------|
| Basis decomposition | All gates → {RZ, SX, X, CX}; CNOT is the costly primitive |
| Optimization levels | Level 3 gives best circuits; level 0 is fastest compile |
| SWAP routing | O(n) SWAPs for long-range CNOT on linear chain; topology matters |
| Layout selection | Noise-adaptive layout at level 3 can cut error 2–5× |
| Custom PassManager | Use for domain-specific optimisations beyond level 3 |

### Engineering Checklist Before Running on Hardware
- [ ] Transpile at `optimization_level=3` with `seed_transpiler` fixed for reproducibility
- [ ] Check `transpiled.depth()` vs your T2/gate_time budget
- [ ] Review CNOT count — each adds ~1% error on current devices
- [ ] Use `coupling_map` matching exact backend, not approximations
- [ ] Profile transpilation time for circuits in hot loops (it can be slow!)

### Next Module
**E4 · Pulse-Level Programming** — going below the gate abstraction to microwave pulses,
Gaussian envelopes, and direct Hamiltonian control.
"""))

cells.append(nbf.v4.new_markdown_cell("""## Challenge: Transpilation-Aware Circuit Design

**Task**: Design a 5-qubit circuit that is *topology-aware* from the start.

1. Choose the IBM heavy-hex or linear-5 coupling map.
2. Write a CNOT-entangling circuit that **only uses adjacent qubit pairs** (no long-range CNOTs).
3. Transpile at levels 0 and 3 — verify that SWAP count = 0 for both.
4. Compare its fidelity (via noisy simulation) to an equivalent circuit with long-range CNOTs.
5. Quantify the "topology-aware design dividend" in fidelity percentage points.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Your topology-aware circuit design here
# Hint: only use cx(i, i+1) for i in range(n-1)
print("Challenge: implement topology-aware circuit and compare fidelity.")
"""))

nb.cells = cells
path = "E3_transpilation.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Notebook written → {path}")
