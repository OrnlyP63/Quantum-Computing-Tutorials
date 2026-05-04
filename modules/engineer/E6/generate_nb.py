import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""# E6 · Quantum Error Correction

**Track:** Engineer | **Module:** E6 of 6

> *"A quantum computer without error correction is a quantum computer with an expiration date."*

## Learning Objectives
1. Understand why quantum error correction (QEC) is fundamentally different from classical ECC.
2. Implement the **3-qubit bit-flip repetition code** — the simplest QEC code.
3. Build and interpret **syndrome measurements** using ancilla qubits.
4. Implement the **3-qubit phase-flip code** and the **9-qubit Shor code**.
5. Understand the **threshold theorem**: below a critical error rate, more qubits → lower logical error.
"""))

# ── Setup ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1 · Setup"))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity, Operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, depolarizing_error

sim_ideal = AerSimulator()
print("Setup complete.")
"""))

# ── Section 2: Why QEC is Hard ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 2 · Why Quantum Error Correction is Hard

Classical error correction exploits:
1. **Copying**: $0 \to 000$, $1 \to 111$ (repetition code)
2. **Measurement**: check parity without disturbing bits

Quantum computing prohibits both:
1. **No-Cloning Theorem**: cannot copy unknown $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$
2. **Measurement collapses superposition**: measuring to diagnose errors destroys the quantum state

### The Key Insight: Syndrome Measurement

QEC works by measuring **error syndromes** — parity checks that detect errors
without revealing the encoded quantum information.

**Example**: For logical qubit $|\psi_L\rangle = \alpha|000\rangle + \beta|111\rangle$,
measure $Z_1Z_2$ (parity of qubits 1,2) and $Z_2Z_3$ (parity of qubits 2,3):

| Error | $Z_1Z_2$ | $Z_2Z_3$ | Syndrome |
|-------|----------|----------|---------|
| None | +1 | +1 | 00 |
| $X_1$ | −1 | +1 | 10 |
| $X_2$ | −1 | −1 | 11 |
| $X_3$ | +1 | −1 | 01 |

The syndrome identifies **which** qubit flipped without disturbing $\alpha, \beta$.
"""))

# ── Section 3: 3-Qubit Bit-Flip Code ─────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 3 · The 3-Qubit Bit-Flip Repetition Code

**Encoding**:
$$|0\rangle \to |0_L\rangle = |000\rangle$$
$$|1\rangle \to |1_L\rangle = |111\rangle$$
$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle \to \alpha|000\rangle + \beta|111\rangle$$

This uses 3 physical qubits to represent 1 logical qubit.

**Corrects**: single bit-flip error on any one of the 3 qubits.
**Cannot correct**: phase-flip errors ($Z$), 2+ simultaneous bit-flips.
"""))

cells.append(nbf.v4.new_code_cell("""\
def encode_bit_flip(qc, data_qubits):
    \"\"\"Encode qubit 0 into 3-qubit bit-flip code. Assumes q[0] holds |ψ⟩.\"\"\"
    q = data_qubits
    qc.cx(q[0], q[1])
    qc.cx(q[0], q[2])
    return qc

def syndrome_measurement_bf(qc, data, anc, syn):
    \"\"\"
    Measure Z1Z2 (ancilla 0) and Z2Z3 (ancilla 1) syndrome.
    data: 3 data qubits, anc: 2 ancilla qubits, syn: 2 classical bits.
    \"\"\"
    # Z1Z2 parity: ancilla 0
    qc.cx(data[0], anc[0])
    qc.cx(data[1], anc[0])
    # Z2Z3 parity: ancilla 1
    qc.cx(data[1], anc[1])
    qc.cx(data[2], anc[1])
    # Measure ancillas
    qc.measure(anc[0], syn[0])
    qc.measure(anc[1], syn[1])
    return qc

def correction_bf(qc, data, syn):
    \"\"\"Classical correction based on syndrome.\"\"\"
    # syndrome 10 → X on qubit 0
    with qc.if_test((syn, 0b10)):
        qc.x(data[0])
    # syndrome 11 → X on qubit 1
    with qc.if_test((syn, 0b11)):
        qc.x(data[1])
    # syndrome 01 → X on qubit 2
    with qc.if_test((syn, 0b01)):
        qc.x(data[2])
    return qc

# Build the full encode-error-decode circuit
data = QuantumRegister(3, "data")
anc  = QuantumRegister(2, "anc")
syn  = ClassicalRegister(2, "syn")
out  = ClassicalRegister(1, "out")

qc_bf = QuantumCircuit(data, anc, syn, out)

# Prepare logical |+⟩ = H|0⟩
qc_bf.h(data[0])
qc_bf.barrier()

# Encode
encode_bit_flip(qc_bf, data)
qc_bf.barrier(label="Encoded")

# Introduce a bit-flip error on qubit 1
qc_bf.x(data[1])
qc_bf.barrier(label="Error X₁")

# Syndrome measurement
syndrome_measurement_bf(qc_bf, data, anc, syn)
qc_bf.barrier(label="Syndrome")

# Correction
correction_bf(qc_bf, data, syn)
qc_bf.barrier(label="Corrected")

# Decode (undo encoding)
qc_bf.cx(data[0], data[2])
qc_bf.cx(data[0], data[1])

# Measure logical qubit
qc_bf.measure(data[0], out[0])

print(qc_bf.draw(fold=100))
"""))

cells.append(nbf.v4.new_code_cell("""\
# Run and verify correction
tqc = transpile(qc_bf, sim_ideal, optimization_level=0)
counts = sim_ideal.run(tqc, shots=4096).result().get_counts()

print("Measurement results (after error + correction):")
for bitstring, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {bitstring}: {count/4096:.3f}")

# Expected: should mostly see out=0 (corresponding to |+⟩ state)
# syn should indicate qubit 1 error was detected and corrected

# Now test all error positions
print("\\nError correction fidelity per error location:")
for err_qubit in [0, 1, 2, None]:
    data2 = QuantumRegister(3, "data")
    anc2  = QuantumRegister(2, "anc")
    syn2  = ClassicalRegister(2, "syn")
    out2  = ClassicalRegister(1, "out")
    qc2   = QuantumCircuit(data2, anc2, syn2, out2)
    qc2.h(data2[0])
    encode_bit_flip(qc2, data2)
    if err_qubit is not None:
        qc2.x(data2[err_qubit])
    syndrome_measurement_bf(qc2, data2, anc2, syn2)
    correction_bf(qc2, data2, syn2)
    qc2.cx(data2[0], data2[2])
    qc2.cx(data2[0], data2[1])
    qc2.measure(data2[0], out2[0])

    tqc2 = transpile(qc2, sim_ideal, optimization_level=0)
    c2 = sim_ideal.run(tqc2, shots=4096).result().get_counts()
    # |+⟩ state → 50% |0⟩, 50% |1⟩ after decoding
    p0 = sum(v for k,v in c2.items() if k.split()[-1] == "0") / 4096
    label = f"X on qubit {err_qubit}" if err_qubit is not None else "No error"
    print(f"  {label}: P(correct) = {min(p0, 1-p0)*2:.3f} (fidelity proxy)")
"""))

# ── Section 4: Logical Error Rate vs Physical Error Rate ─────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 4 · Logical Error Rate vs Physical Error Rate

For the 3-qubit repetition code correcting single-qubit errors with physical error rate $p$:

$$p_L = 3p^2 - 2p^3 \approx 3p^2 \quad (\text{for small } p)$$

The code **helps** only when $p_L < p$, i.e., when $3p^2 < p$, i.e., $p < \frac{1}{3}$.

This critical value $p^* = 1/3$ is the **threshold** for this code.

For distance-$d$ codes (correcting $(d-1)/2$ errors):

$$p_L \approx \binom{d}{(d+1)/2} p^{(d+1)/2}$$

Below threshold, increasing $d$ exponentially suppresses $p_L$.
"""))

cells.append(nbf.v4.new_code_cell("""\
p_phys = np.linspace(0, 0.5, 500)

# 3-qubit repetition code (distance 3)
def p_logical_rep(p, d):
    \"\"\"Logical error for distance-d repetition code.\"\"\"
    t = (d - 1) // 2    # number of correctable errors
    # P(logical error) = P(> t errors)
    from math import comb
    pl = sum(comb(d, k) * p**k * (1-p)**(d-k) for k in range(t+1, d+1))
    return pl

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Linear scale
for d, color in [(3, "blue"), (5, "green"), (7, "orange"), (9, "red")]:
    pl = np.array([p_logical_rep(p, d) for p in p_phys])
    axes[0].plot(p_phys, pl, color=color, linewidth=2, label=f"d={d}")

axes[0].plot(p_phys, p_phys, "k--", linewidth=1.5, label="p_L = p (no correction)")
axes[0].axvline(1/3, color="gray", linestyle=":", alpha=0.7, label="Threshold p*=1/3")
axes[0].set_xlabel("Physical error rate p")
axes[0].set_ylabel("Logical error rate p_L")
axes[0].set_title("Repetition Code: Logical vs Physical Error Rate")
axes[0].legend(fontsize=9)
axes[0].grid(alpha=0.3)
axes[0].set_xlim(0, 0.5)
axes[0].set_ylim(0, 0.5)

# Log-log scale (NISQ regime)
p_low = np.logspace(-3, -1, 200)
for d, color in [(3, "blue"), (5, "green"), (7, "orange"), (9, "red")]:
    pl = np.array([p_logical_rep(p, d) for p in p_low])
    axes[1].loglog(p_low, pl, color=color, linewidth=2, label=f"d={d}")
axes[1].loglog(p_low, p_low, "k--", linewidth=1.5, label="p_L = p")
axes[1].set_xlabel("Physical error rate p")
axes[1].set_ylabel("Logical error rate p_L")
axes[1].set_title("Log-Log Scale (NISQ Regime)")
axes[1].legend(fontsize=9)
axes[1].grid(alpha=0.3)
# Annotate suppression factor
p_example = 0.001
for d in [3, 5, 7]:
    pl_ex = p_logical_rep(p_example, d)
    suppression = p_example / pl_ex
    print(f"d={d}, p={p_example}: suppression = {suppression:.0f}×")

plt.suptitle("Threshold Theorem: Repetition Code", fontsize=13)
plt.tight_layout()
plt.savefig("E6_threshold.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 5: Phase-Flip Code ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 5 · The 3-Qubit Phase-Flip Code

The bit-flip code corrects $X$ errors but not $Z$ errors.
Apply Hadamards to change basis: $Z$ errors in the $Z$-basis become $X$ errors in the $X$-basis.

**Encoding**:
$$|0\rangle \to |{+}{+}{+}\rangle = \frac{1}{\sqrt{8}}(|0\rangle+|1\rangle)^{\otimes 3}$$
$$|1\rangle \to |{-}{-}{-}\rangle = \frac{1}{\sqrt{8}}(|0\rangle-|1\rangle)^{\otimes 3}$$

Circuit: encode bit-flip code, then apply $H$ to all 3 data qubits.

**Corrects**: single phase-flip ($Z$) on any one qubit.

### Syndrome for Phase-Flip

Measure $X_1X_2$ and $X_2X_3$ (instead of $Z_1Z_2$, $Z_2Z_3$):
- Apply $H$ to ancilla, entangle with data, measure ancilla.
"""))

cells.append(nbf.v4.new_code_cell("""\
def encode_phase_flip(qc, data):
    \"\"\"Encode into phase-flip code: CNOT encoding then H on all data qubits.\"\"\"
    qc.cx(data[0], data[1])
    qc.cx(data[0], data[2])
    qc.h(data[0])
    qc.h(data[1])
    qc.h(data[2])
    return qc

def syndrome_measurement_pf(qc, data, anc, syn):
    \"\"\"Measure X1X2 and X2X3 syndrome for phase-flip code.\"\"\"
    # X syndrome: Hadamard → CNOT → Hadamard
    qc.h(anc[0])
    qc.cx(anc[0], data[0])
    qc.cx(anc[0], data[1])
    qc.h(anc[0])

    qc.h(anc[1])
    qc.cx(anc[1], data[1])
    qc.cx(anc[1], data[2])
    qc.h(anc[1])

    qc.measure(anc[0], syn[0])
    qc.measure(anc[1], syn[1])
    return qc

# Full circuit: encode, Z error, syndrome, correction, decode
data = QuantumRegister(3, "data")
anc  = QuantumRegister(2, "anc")
syn  = ClassicalRegister(2, "syn")
out  = ClassicalRegister(1, "out")

qc_pf = QuantumCircuit(data, anc, syn, out)
qc_pf.h(data[0])  # prepare |+⟩
qc_pf.barrier()

encode_phase_flip(qc_pf, data)
qc_pf.barrier(label="Encoded |+++⟩ or |---⟩")

# Introduce Z error on qubit 1
qc_pf.z(data[1])
qc_pf.barrier(label="Z₁ error")

syndrome_measurement_pf(qc_pf, data, anc, syn)
qc_pf.barrier(label="Syndrome")

# Correction (same logic as bit-flip, in Hadamard basis)
with qc_pf.if_test((syn, 0b10)):
    qc_pf.z(data[0])
with qc_pf.if_test((syn, 0b11)):
    qc_pf.z(data[1])
with qc_pf.if_test((syn, 0b01)):
    qc_pf.z(data[2])
qc_pf.barrier(label="Corrected")

# Decode
qc_pf.h(data[0])
qc_pf.h(data[1])
qc_pf.h(data[2])
qc_pf.cx(data[0], data[2])
qc_pf.cx(data[0], data[1])
qc_pf.measure(data[0], out[0])

tqc_pf = transpile(qc_pf, sim_ideal, optimization_level=0)
counts_pf = sim_ideal.run(tqc_pf, shots=4096).result().get_counts()
print("Phase-flip code results (Z error on qubit 1, should be corrected):")
for k, v in sorted(counts_pf.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v/4096:.3f}")
"""))

# ── Section 6: Shor Code ──────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 6 · The 9-Qubit Shor Code

The Shor code (1995) was the first code to correct **all single-qubit errors** ($X$, $Z$, $Y$).

**Strategy**: Concatenate bit-flip + phase-flip codes:

1. Phase-flip encode: $|0\rangle \to |{+}{+}{+}\rangle$, $|1\rangle \to |{-}{-}{-}\rangle$
2. Bit-flip encode each qubit: $|+\rangle \to \frac{1}{\sqrt{2}}(|000\rangle+|111\rangle)$

$$|0_L\rangle = \frac{1}{2\sqrt{2}}(|000\rangle+|111\rangle)^{\otimes 3}$$
$$|1_L\rangle = \frac{1}{2\sqrt{2}}(|000\rangle-|111\rangle)^{\otimes 3}$$

**Parameters**: [[9, 1, 3]] — 9 physical qubits, 1 logical qubit, distance 3.
**Corrects**: any single-qubit error (including $Y = iXZ$).
"""))

cells.append(nbf.v4.new_code_cell("""\
def shor_encode(qc, logical_qubit, data_start):
    \"\"\"
    Encode logical_qubit (index) into 9 physical qubits starting at data_start.
    Assumes logical qubit state is at qubit data_start (q[0] of the code block).
    \"\"\"
    q = list(range(data_start, data_start + 9))

    # Phase-flip encode: spread across 3 blocks of 3
    qc.cx(q[0], q[3])
    qc.cx(q[0], q[6])

    # Hadamard to enter X basis for each block's first qubit
    for i in [0, 3, 6]:
        qc.h(q[i])

    # Bit-flip encode within each block of 3
    for block_start in [0, 3, 6]:
        qc.cx(q[block_start], q[block_start + 1])
        qc.cx(q[block_start], q[block_start + 2])

    return qc

# Prepare logical |+⟩
n_data = 9
n_anc  = 8   # 2 ancilla per block × 3 blocks + 2 for phase syndromes
data = QuantumRegister(n_data, "d")
out  = ClassicalRegister(1, "out")

qc_shor = QuantumCircuit(data, out)
qc_shor.h(data[0])   # prepare |+⟩ in logical qubit
qc_shor.barrier()

# Encode
shor_encode(qc_shor, 0, 0)
qc_shor.barrier(label="Shor encoded")

# Introduce an arbitrary single-qubit error on qubit 4 (middle of second block)
qc_shor.z(data[4])   # phase-flip in the middle block
qc_shor.barrier(label="Z error on q4")

# Measure all 9 data qubits (simplified — no ancilla decoding here)
qc_shor.measure(data[0], out[0])

print("Shor code encoding structure (9 physical qubits):")
print(qc_shor.draw(fold=100))
print(f"\\nCircuit depth: {qc_shor.depth()}")
print(f"Circuit operations: {dict(qc_shor.count_ops())}")
print(f"Physical qubits: 9, Logical qubits: 1, Rate: 1/9")
"""))

cells.append(nbf.v4.new_code_cell("""\
# Visualise the Shor code structure
fig, ax = plt.subplots(figsize=(12, 6))

# Draw qubit layout
block_colors = ["#3498db", "#e74c3c", "#2ecc71"]
block_labels = ["Block 0\\n(bits 0-2)", "Block 1\\n(bits 3-5)", "Block 2\\n(bits 6-8)"]

for block in range(3):
    x_base = block * 4
    color = block_colors[block]

    # Draw qubits
    for i in range(3):
        qidx = block * 3 + i
        circle = plt.Circle((x_base + i, 2), 0.35, color=color, zorder=3)
        ax.add_patch(circle)
        ax.text(x_base + i, 2, f"q{qidx}", ha="center", va="center",
                color="white", fontweight="bold", fontsize=9)

    # CNOT lines within block
    ax.annotate("", xy=(x_base + 1, 2), xytext=(x_base, 2),
                arrowprops=dict(arrowstyle="->", color=color, lw=2))
    ax.annotate("", xy=(x_base + 2, 2), xytext=(x_base, 2),
                arrowprops=dict(arrowstyle="->", color=color, lw=2))

    # Phase-flip level
    phase_circle = plt.Circle((x_base, 4), 0.4, color=color, alpha=0.5, zorder=3)
    ax.add_patch(phase_circle)
    ax.text(x_base, 4, f"H·q{block*3}", ha="center", va="center", fontsize=8)
    ax.plot([x_base, x_base], [2.35, 3.6], color=color, linewidth=2, zorder=2)

# Phase-flip connections at top
for block in range(1, 3):
    ax.annotate("", xy=(block * 4, 4), xytext=(0, 4),
                arrowprops=dict(arrowstyle="->", color="black", lw=2,
                               connectionstyle="arc3,rad=-0.1"))

# Logical qubit
ax.text(6, 5.5, "Logical qubit |ψ_L⟩", ha="center", va="center",
        fontsize=12, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="gold", alpha=0.8))

# Legend
patches = [mpatches.Patch(color=c, label=l)
           for c, l in zip(block_colors, block_labels)]
ax.legend(handles=patches, loc="upper right", fontsize=9)

ax.set_xlim(-0.8, 11)
ax.set_ylim(1, 6.5)
ax.set_title("Shor Code Structure: 9 Physical Qubits → 1 Logical Qubit", fontsize=13)
ax.axis("off")
plt.tight_layout()
plt.savefig("E6_shor_structure.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 7: QEC Codes Overview ────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 7 · QEC Code Comparison

The field has evolved from the Shor code to much more efficient constructions:

| Code | Qubits [[n,k,d]] | Correctable errors | Gate overhead |
|------|-----------------|-------------------|---------------|
| 3-qubit repetition | [[3,1,3]] | Single bit-flip only | Low |
| 3-qubit phase-flip | [[3,1,3]] | Single phase-flip only | Low |
| Shor | [[9,1,3]] | Any single-qubit | Moderate |
| Steane | [[7,1,3]] | Any single-qubit | Moderate |
| Surface code | [[d²,1,d]] | Any ≤(d-1)/2 errors | High (routing) |
| Toric code | [[2d²,2,d]] | Topological | High |

### Surface Code: The Current Favorite

The **surface code** on a $d \times d$ qubit grid achieves:
- **Distance**: $d$ (corrects any $(d-1)/2$ errors)
- **Threshold**: $\sim 1\%$ physical error rate
- **Only nearest-neighbor** gates required (hardware-friendly)
- **Logical error rate**: $p_L \approx 100 \cdot (p/p^*)^{(d+1)/2}$

IBM's goal: demonstrate fault-tolerant logical qubit with surface code distance $d = 7$
using $\sim$100 physical qubits per logical qubit by 2029.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Surface code logical error rate vs distance and physical error rate
p_threshold = 0.01   # ~1% threshold for surface code

p_physical = np.logspace(-3, -1, 200)
fig, ax = plt.subplots(figsize=(10, 6))

ax.loglog(p_physical, p_physical, "k--", linewidth=2, label="No QEC (p_L = p)")
ax.axvline(p_threshold, color="red", linestyle=":", linewidth=1.5,
           label=f"Threshold p* = {p_threshold}")

for d in [3, 5, 7, 9, 11]:
    # Surface code logical error rate model
    pl = 100 * (p_physical / p_threshold) ** ((d + 1) / 2)
    # Only plot where it's below threshold (code helps)
    mask = p_physical < p_threshold
    ax.loglog(p_physical[mask], pl[mask], linewidth=2, label=f"d={d} surface code")
    ax.loglog(p_physical[~mask], pl[~mask], linewidth=1, alpha=0.3,
              color=ax.get_lines()[-1].get_color())

ax.set_xlabel("Physical error rate p")
ax.set_ylabel("Logical error rate p_L")
ax.set_title("Surface Code: Logical Error Rate vs Distance")
ax.legend(fontsize=9)
ax.grid(alpha=0.3, which="both")
ax.set_xlim(1e-3, 0.1)
ax.set_ylim(1e-15, 1)
plt.tight_layout()
plt.savefig("E6_surface_code.png", dpi=120, bbox_inches="tight")
plt.show()

# Physical qubit overhead
print("Physical qubit overhead per logical qubit (surface code):")
print(f"{'Distance d':>12} {'Physical qubits':>18} {'Logical error (p=0.001)':>24}")
for d in [3, 5, 7, 9, 11, 15, 21]:
    n_phys = d**2 + (d-1)**2   # data + ancilla in surface code
    pl = 100 * (0.001 / 0.01)**((d+1)/2)
    print(f"{d:12d} {n_phys:18d} {pl:24.2e}")
"""))

# ── Section 8: Fault Tolerance Roadmap ───────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 8 · The Road to Fault-Tolerant Quantum Computing

### Current State (2025)

| Era | Qubits | Error rate | Logical qubits | Status |
|-----|--------|-----------|---------------|--------|
| NISQ | 100–1000 | 0.1–1% | 0 (unencoded) | Now |
| Early FT | 1000–10000 | 0.1% | 1–10 | ~2027 |
| Fault-tolerant | 100k–1M | 0.01% | 100+ | ~2030+ |

### Error Budget for Fault Tolerance

For a useful fault-tolerant computation with $N_{logical}$ logical qubits
and $N_{gates}$ logical gate operations:

$$p_L \lesssim \frac{1}{N_{logical} \cdot N_{gates}}$$

For Shor's factoring of a 2048-bit RSA number:
- $N_{logical} \approx 4000$ logical qubits
- $N_{gates} \approx 10^{10}$ operations
- Required: $p_L \lesssim 10^{-14}$ per logical gate
- Surface code distance needed: $d \approx 27$ (using ~5000 physical qubits/logical qubit)
- **Total physical qubits**: $\sim 20$ million

This is why quantum error correction is the central engineering challenge.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Timeline and qubit requirements visualisation
milestones = {
    "Noisy repetition code\\n(2021, IBM)": (2021, 7, 0),
    "Logical qubit\\nbelow breakeven (2023)": (2023, 17, 1),
    "Surface code d=5\\n(2024, Google)": (2024, 25, 1),
    "Surface code d=7\\n(target ~2026)": (2026, 50, 1),
    "100 logical qubits\\n(target ~2029)": (2029, 10000, 100),
    "Fault-tolerant Shor\\n(target ~2035+)": (2036, 20_000_000, 4000),
}

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

years = [v[0] for v in milestones.values()]
phys  = [v[1] for v in milestones.values()]
log_q = [v[2] for v in milestones.values()]
labels = list(milestones.keys())

colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(milestones)))

axes[0].semilogy(years, phys, "o-", color="steelblue", linewidth=2, markersize=8)
for y, p, lbl, c in zip(years, phys, labels, colors):
    axes[0].annotate(lbl, (y, p), textcoords="offset points",
                     xytext=(8, 0), fontsize=7, va="center")
axes[0].set_xlabel("Year")
axes[0].set_ylabel("Physical qubits (log scale)")
axes[0].set_title("Physical Qubit Count Roadmap")
axes[0].grid(alpha=0.3)

axes[1].semilogy(years[1:], [l if l > 0 else 0.1 for l in log_q[1:]], "s-",
                 color="tomato", linewidth=2, markersize=8)
axes[1].set_xlabel("Year")
axes[1].set_ylabel("Logical qubits (log scale)")
axes[1].set_title("Logical Qubit Count Roadmap")
axes[1].grid(alpha=0.3)

plt.suptitle("Fault-Tolerant Quantum Computing Roadmap", fontsize=13)
plt.tight_layout()
plt.savefig("E6_roadmap.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 9: Summary ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 9 · Summary & Series Conclusion

### Module E6 Key Takeaways

| Concept | Key Result |
|---------|-----------|
| No-cloning theorem | Cannot copy unknown qubits — QEC must use entanglement |
| Syndrome measurement | Detect errors without disturbing encoded information |
| 3-qubit repetition | Corrects single $X$ (or $Z$) errors; uses 3× resources |
| Shor code [[9,1,3]] | First universal QEC code; corrects any single-qubit error |
| Threshold theorem | Below $p^*$, larger codes give exponentially lower $p_L$ |
| Surface code | $\sim1\%$ threshold, nearest-neighbor gates, hardware-friendly |

### Engineer Track Complete ✓

You have now completed the full Engineer track:

| Module | Topic |
|--------|-------|
| E1 | Hardware architectures: superconducting, trapped ion, photonic |
| E2 | Noise, decoherence: T1/T2, noise models, error characterization |
| E3 | Transpilation: basis gates, SWAP routing, optimization levels |
| E4 | Pulse-level programming: Gaussian pulses, DRAG, calibration |
| E5 | Error mitigation: ZNE, MEM, PEC, trade-offs |
| E6 | Error correction: repetition code, Shor code, surface code, threshold |

### Full Series Complete ✓

Congratulations — you have completed the entire quantum computing tutorial series:
- **Foundation (F1–F4)**: Concepts, Qiskit basics, qubits, measurement
- **Student (S1–S5)**: Gates, entanglement, circuits, real-world applications
- **Developer (D1–D6)**: Python→quantum, algorithms, Deutsch-Jozsa, Grover, hardware
- **Data Scientist (DS1–DS6)**: QML, encoding, VQC, QNN, kernels, benchmarking
- **Engineer (E1–E6)**: Hardware, noise, transpilation, pulses, mitigation, correction

The field is moving fast. Come back in 6 months — the hardware will have improved.
"""))

cells.append(nbf.v4.new_markdown_cell("""## Challenge: Simulate Syndrome Extraction Under Noise

**Task**: Test the 3-qubit bit-flip code under realistic depolarizing noise.

1. Build the full encode-error-syndrome-correct-decode circuit.
2. Sweep the physical error rate $p \\in [0.001, 0.4]$.
3. For each $p$, apply bit-flip noise to each data qubit independently with probability $p$.
4. Run the full QEC protocol (syndrome + correction).
5. Measure the logical error rate $p_L$ (rate at which the decoded qubit is incorrect).
6. Plot $p_L$ vs $p$ and verify the theoretical curve $p_L \\approx 3p^2$.
7. Mark the threshold $p^* = 1/3$ and show the code crossing the $p_L = p$ line.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Your syndrome-under-noise simulation here

p_vals = np.linspace(0.005, 0.4, 25)
p_logical = []

for p_err in p_vals:
    # Build noisy QEC circuit
    # Add depolarizing error p_err to each data qubit after encoding
    # Run syndrome measurement + correction
    # Measure logical error rate
    pass  # TODO

# TODO: plot p_L vs p, overlay theory 3p^2

print("Challenge: Implement noisy syndrome measurement and plot p_L vs p.")
print(f"Theoretical threshold: p* = 1/3 ≈ {1/3:.3f}")
print(f"Below p*: 3p² < p → code helps")
print(f"Above p*: 3p² > p → code hurts")
"""))

nb.cells = cells
path = "E6_error_correction.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Notebook written → {path}")
