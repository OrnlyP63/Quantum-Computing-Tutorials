import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""# E5 · Error Mitigation Techniques

**Track:** Engineer | **Module:** E5 of 6

> *"Error mitigation is not error correction — it trades more shots for lower bias."*

## Learning Objectives
1. Distinguish **error mitigation** (statistical post-processing) from **error correction** (redundant encoding).
2. Implement **Zero-Noise Extrapolation (ZNE)**: fold circuits, fit Richardson extrapolation.
3. Apply **Measurement Error Mitigation (MEM)**: calibrate and invert the assignment matrix.
4. Understand **Probabilistic Error Cancellation (PEC)** and its exponential shot overhead.
5. Know when each technique applies and what it costs in circuit time vs shot count.
"""))

# ── Setup ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1 · Setup"))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, state_fidelity, Operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel, depolarizing_error, thermal_relaxation_error, ReadoutError
)

# Standard noisy backend
def make_noise_model(p1q=0.005, p2q=0.02, p_ro=0.03):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p1q, 1), ["u1", "u2", "u3", "h", "x", "rz", "sx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2q, 2), ["cx"])
    ro = ReadoutError([[1-p_ro, p_ro], [p_ro, 1-p_ro]])
    nm.add_all_qubit_readout_error(ro)
    return nm

noise_model = make_noise_model()
sim_noisy = AerSimulator(noise_model=noise_model)
sim_ideal = AerSimulator()

print("Noisy simulator ready.")
print(f"  Gate noise: p1q=0.5%, p2q=2.0%, readout=3.0%")
"""))

# ── Section 2: Baseline ───────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 2 · Baseline: Noise Without Mitigation

We first quantify the raw noise impact on a simple observable.

**Target circuit**: 3-qubit GHZ state. **Observable**: $\langle ZZZ \rangle$.

For ideal GHZ: $|\psi\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$, so $\langle ZZZ \rangle = 1$.

Each CNOT and measurement adds noise. Our goal: recover $\langle ZZZ \rangle \approx 1$
from noisy measurements.
"""))

cells.append(nbf.v4.new_code_cell("""\
def ghz_circuit(n):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def estimate_zzz(counts, n_qubits=3):
    \"\"\"Estimate <ZZZ> = P(even parity) - P(odd parity).\"\"\"
    total = sum(counts.values())
    zzz = 0
    for bitstring, count in counts.items():
        bits = [int(b) for b in bitstring.replace(" ", "")]
        parity = sum(bits) % 2
        zzz += (1 - 2 * parity) * count / total
    return zzz

n = 3
qc_ghz = ghz_circuit(n)
tqc = transpile(qc_ghz, sim_noisy, optimization_level=1)

shots = 32768
counts_ideal = sim_ideal.run(transpile(qc_ghz, sim_ideal), shots=shots).result().get_counts()
counts_noisy = sim_noisy.run(tqc, shots=shots).result().get_counts()

zzz_ideal = estimate_zzz(counts_ideal, n)
zzz_noisy = estimate_zzz(counts_noisy, n)

print(f"Ideal ⟨ZZZ⟩:  {zzz_ideal:.4f}  (should be 1.0)")
print(f"Noisy ⟨ZZZ⟩:  {zzz_noisy:.4f}")
print(f"Bias: {abs(1.0 - zzz_noisy):.4f}  ({abs(1.0 - zzz_noisy)*100:.2f}% error)")
"""))

# ── Section 3: ZNE ────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 3 · Zero-Noise Extrapolation (ZNE)

**Core idea**: Intentionally increase noise, measure the observable at multiple noise levels,
then extrapolate back to zero noise.

### 3.1 Noise Amplification: Circuit Folding

For a noise scale factor $\lambda$, replace each gate $G$ with $G(G^\dagger G)^{(\lambda-1)/2}$.
Since $G^\dagger G = I$, the circuit is logically identical but has $\lambda\times$ as many gates → $\lambda\times$ noise.

### 3.2 Richardson Extrapolation

Given measurements $f(\lambda_i)$ at scale factors $\lambda_1 < \lambda_2 < \cdots < \lambda_k$,
extrapolate to $\lambda = 0$:

$$f(0) \approx \sum_{i=1}^k c_i f(\lambda_i), \quad c_i = \prod_{j \neq i} \frac{\lambda_j}{\lambda_j - \lambda_i}$$

### 3.3 Polynomial Fit (practical ZNE)

Fit a polynomial $p(\lambda)$ to the $(\lambda_i, f(\lambda_i))$ data and evaluate $p(0)$.
Linear fit = 2-point Richardson; quadratic = 3-point, etc.
"""))

cells.append(nbf.v4.new_code_cell("""\
def fold_circuit(qc, scale_factor):
    \"\"\"
    Circuit folding for ZNE: replace each CX with CX·(CX·CX)^((s-1)//2).
    scale_factor must be odd integer: 1, 3, 5, ...
    \"\"\"
    if scale_factor == 1:
        return qc.copy()

    # Fold only the CX gates (the dominant noise source)
    qc_folded = QuantumCircuit(*qc.qregs, *qc.cregs)
    k = (scale_factor - 1) // 2   # extra CX·CX pairs per CX

    for instr in qc.data:
        gate = instr.operation
        qubits = instr.qubits
        clbits = instr.clbits
        qc_folded.append(gate, qubits, clbits)
        if gate.name == "cx":
            for _ in range(k):
                qc_folded.cx(*[qc_folded.find_bit(q).index for q in qubits])
                qc_folded.cx(*[qc_folded.find_bit(q).index for q in qubits])
    return qc_folded

# Base circuit (no measurements for folding, add after)
def base_ghz(n=3):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc

scale_factors = [1, 3, 5, 7]
zzz_at_scale = []

qc_base = base_ghz(n=3)
for sf in scale_factors:
    qc_f = fold_circuit(qc_base, sf)
    qc_f.measure_all()
    tqc_f = transpile(qc_f, sim_noisy, optimization_level=0)
    counts_f = sim_noisy.run(tqc_f, shots=32768).result().get_counts()
    zzz_f = estimate_zzz(counts_f, 3)
    zzz_at_scale.append(zzz_f)
    print(f"λ={sf}: ⟨ZZZ⟩={zzz_f:.4f}  (depth={qc_f.depth()})")

print(f"\\nMeasured values at scale factors {scale_factors}:")
for sf, val in zip(scale_factors, zzz_at_scale):
    print(f"  λ={sf}: {val:.4f}")
"""))

cells.append(nbf.v4.new_code_cell("""\
# Richardson extrapolation to λ=0
def richardson_extrapolate(lambdas, values, order=None):
    \"\"\"Polynomial fit extrapolation to lambda=0.\"\"\"
    if order is None:
        order = len(lambdas) - 1
    lambdas = np.array(lambdas)
    values = np.array(values)
    coeffs = np.polyfit(lambdas, values, deg=min(order, len(lambdas)-1))
    poly = np.poly1d(coeffs)
    return poly(0), poly

lambda_ext = np.array(scale_factors, dtype=float)
f_ext = np.array(zzz_at_scale)

# Linear (2-point), Quadratic (3-point), Full (4-point)
results_zne = {}
for order, label in [(1, "Linear"), (2, "Quadratic"), (3, "Cubic")]:
    val_ext, poly = richardson_extrapolate(lambda_ext[:order+1], f_ext[:order+1], order)
    results_zne[label] = (val_ext, poly)
    improvement = abs(1.0 - val_ext) / abs(1.0 - f_ext[0])
    print(f"{label} ZNE: ⟨ZZZ⟩₀ = {val_ext:.4f}  (bias reduced to {improvement*100:.1f}% of raw)")

# Plot
l_range = np.linspace(0, max(scale_factors), 200)
fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(lambda_ext, f_ext, color="red", zorder=5, s=80, label="Measured at λ")
ax.axhline(1.0, color="green", linestyle="--", linewidth=1.5, label="Ideal ⟨ZZZ⟩=1")
ax.axhline(zzz_noisy, color="red", linestyle=":", linewidth=1.5,
           label=f"Raw noisy: {zzz_noisy:.4f}")

colors = ["steelblue", "orange", "purple"]
for (label, (val, poly)), c in zip(results_zne.items(), colors):
    y_fit = poly(l_range)
    ax.plot(l_range, y_fit, color=c, linestyle="-", linewidth=1.5,
            label=f"{label} ZNE → {val:.4f}")
    ax.scatter([0], [val], color=c, s=120, zorder=6, marker="*")

ax.set_xlabel("Noise scale factor λ")
ax.set_ylabel("⟨ZZZ⟩")
ax.set_title("Zero-Noise Extrapolation on GHZ Circuit")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
ax.set_xlim(-0.2, max(scale_factors) + 0.5)
plt.tight_layout()
plt.savefig("E5_zne.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 4: Measurement Error Mitigation ───────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 4 · Measurement Error Mitigation (MEM)

Readout errors are often **the largest** single source of error in short circuits.

### Calibration Matrix Method

1. **Prepare** each basis state $|0\cdots0\rangle, |0\cdots01\rangle, \ldots, |1\cdots1\rangle$.
2. **Measure** and record the empirical outcome distribution → column $j$ of matrix $A$.
3. **Correct**: given measured distribution $\vec{p}$, invert: $\vec{p}_{\text{true}} = A^{-1}\vec{p}$.

For $n$ qubits, $A$ is $2^n \times 2^n$. At $n > 10$ this becomes intractable → use **tensored** MEM (assume independent readout errors per qubit).

### Tensored MEM (scalable)

$$A = A_0 \otimes A_1 \otimes \cdots \otimes A_{n-1}$$

where $A_i = \begin{pmatrix} 1-e_{0i} & e_{1i} \\ e_{0i} & 1-e_{1i} \end{pmatrix}$ per qubit.
"""))

cells.append(nbf.v4.new_code_cell("""\
def build_assignment_matrix(n_qubits, noise_model, shots=32768):
    \"\"\"
    Build 2^n x 2^n assignment matrix by preparing each basis state
    and measuring. A[i, j] = P(measure i | prepare j).
    \"\"\"
    dim = 2**n_qubits
    A = np.zeros((dim, dim))

    for j in range(dim):
        # Prepare state |j>
        bitstring_j = format(j, f"0{n_qubits}b")
        qc_prep = QuantumCircuit(n_qubits, n_qubits)
        for bit_idx, bit in enumerate(reversed(bitstring_j)):
            if bit == "1":
                qc_prep.x(bit_idx)
        qc_prep.measure_all()
        tqc = transpile(qc_prep, sim_noisy, optimization_level=0)
        counts = sim_noisy.run(tqc, shots=shots).result().get_counts()

        for outcome, count in counts.items():
            i = int(outcome.replace(" ", ""), 2)
            A[i, j] = count / shots

    return A

# Build for 3 qubits (8x8 matrix)
print("Building calibration matrix (3 qubits, 8 basis states)...")
A_cal = build_assignment_matrix(3, noise_model, shots=16384)
print("Assignment matrix A:")
print(np.round(A_cal, 3))
"""))

cells.append(nbf.v4.new_code_cell("""\
# Apply MEM to the noisy GHZ distribution
def apply_mem(counts, A_inv, n_qubits):
    \"\"\"Apply calibration matrix inverse to correct measurement distribution.\"\"\"
    dim = 2**n_qubits
    total = sum(counts.values())
    p_meas = np.zeros(dim)
    for bitstr, cnt in counts.items():
        idx = int(bitstr.replace(" ", ""), 2)
        p_meas[idx] = cnt / total

    p_corrected = A_inv @ p_meas
    # Project back to valid probability distribution
    p_corrected = np.clip(p_corrected, 0, 1)
    p_corrected /= p_corrected.sum()
    return p_corrected

A_inv = np.linalg.inv(A_cal)
print(f"Condition number of A: {np.linalg.cond(A_cal):.2f}")

p_corrected = apply_mem(counts_noisy, A_inv, 3)

# Estimate ⟨ZZZ⟩ from corrected distribution
zzz_mem = 0
for i, p in enumerate(p_corrected):
    bitstring = format(i, "03b")
    parity = sum(int(b) for b in bitstring) % 2
    zzz_mem += (1 - 2 * parity) * p

print(f"\\nRaw noisy ⟨ZZZ⟩:      {zzz_noisy:.4f}")
print(f"After MEM ⟨ZZZ⟩:       {zzz_mem:.4f}")
print(f"Ideal ⟨ZZZ⟩:           1.0000")
print(f"MEM improvement: {abs(1 - zzz_noisy) / abs(1 - zzz_mem):.1f}× reduction in bias")

# Visualise
dim = 8
basis_labels = [format(i, "03b") for i in range(dim)]
p_ideal_dist = np.zeros(dim)
p_ideal_dist[0] = 0.5
p_ideal_dist[-1] = 0.5
total_noisy = sum(counts_noisy.values())
p_noisy_dist = np.array([counts_noisy.get(format(i, "03b"), 0) / total_noisy for i in range(dim)])

x = np.arange(dim)
width = 0.25
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(x - width, p_ideal_dist, width, label="Ideal", color="green", alpha=0.8)
ax.bar(x, p_noisy_dist, width, label="Noisy raw", color="red", alpha=0.8)
ax.bar(x + width, p_corrected, width, label="MEM corrected", color="blue", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(basis_labels)
ax.set_xlabel("Bitstring")
ax.set_ylabel("Probability")
ax.set_title("GHZ Distribution: Ideal vs Noisy vs MEM Corrected")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("E5_mem_correction.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 5: ZNE + MEM Combined ────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 5 · Combining ZNE + MEM

In practice, the best results come from applying both mitigations:

1. **MEM first**: correct readout errors — this is essentially free in shot count.
2. **ZNE second**: extrapolate away gate errors.

These are **composable** because readout errors and gate errors have different mechanisms.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Repeat ZNE but with MEM applied at each noise scale
zzz_zne_mem = []
for sf in scale_factors:
    qc_f = fold_circuit(qc_base, sf)
    qc_f.measure_all()
    tqc_f = transpile(qc_f, sim_noisy, optimization_level=0)
    counts_f = sim_noisy.run(tqc_f, shots=32768).result().get_counts()

    # Apply MEM first
    p_corr = apply_mem(counts_f, A_inv, 3)

    # Then compute ⟨ZZZ⟩ from MEM-corrected distribution
    zzz_val = 0
    for i, p in enumerate(p_corr):
        parity = bin(i).count("1") % 2
        zzz_val += (1 - 2 * parity) * p
    zzz_zne_mem.append(zzz_val)
    print(f"λ={sf}: MEM+raw ⟨ZZZ⟩={zzz_val:.4f}")

# Extrapolate
val_combined, poly_combined = richardson_extrapolate(
    list(scale_factors), zzz_zne_mem, order=len(scale_factors)-1)
print(f"\\nZNE+MEM extrapolated ⟨ZZZ⟩ = {val_combined:.4f}")
print(f"Bias reduction vs raw: {abs(1-zzz_noisy)/abs(1-val_combined):.1f}×")

# Summary comparison
methods = ["Ideal", "Raw noisy", "MEM only", "ZNE only", "ZNE+MEM"]
values  = [1.0,    zzz_noisy,   zzz_mem,  results_zne["Quadratic"][0], val_combined]

fig, ax = plt.subplots(figsize=(9, 5))
colors_bar = ["green", "red", "royalblue", "orange", "purple"]
bars = ax.bar(methods, values, color=colors_bar, edgecolor="black", alpha=0.85)
ax.axhline(1.0, color="green", linestyle="--", linewidth=1.5)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f"{val:.3f}", ha="center", va="bottom", fontweight="bold", fontsize=10)
ax.set_ylabel("Estimated ⟨ZZZ⟩")
ax.set_title("Error Mitigation Comparison on GHZ ⟨ZZZ⟩ Observable")
ax.set_ylim(min(values) - 0.1, 1.1)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("E5_mitigation_comparison.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 6: Probabilistic Error Cancellation ───────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 6 · Probabilistic Error Cancellation (PEC)

PEC is the most theoretically rigorous mitigation technique — it provides an **unbiased estimator**
of the noise-free expectation value.

### How it works

Every noisy gate $\tilde{G}$ can be written as:

$$\tilde{G} = \frac{1}{\gamma}\sum_i \alpha_i \mathcal{B}_i$$

where $\{\mathcal{B}_i\}$ are implementable "basis operations", $\alpha_i$ can be negative.

By importance-sampling from $|\alpha_i|/\sum|\alpha_i|$ and tracking signs, we get an
unbiased estimator. **Cost**: shot overhead $\gamma^{2N}$ where $N$ = number of gates.

### Overhead

For depolarizing noise with parameter $p$:

$$\gamma = \frac{1}{1 - p} \approx 1 + p \quad \text{for small } p$$

Total shot overhead for $N$ gates: $\gamma^{2N} \approx e^{2Np}$.

For $N=100$ gates and $p=0.01$: overhead $\approx e^{2} \approx 7.4\times$.
For $N=1000$ gates and $p=0.01$: overhead $\approx e^{20} \approx 5\times10^8$. **Intractable.**

**Conclusion**: PEC is practical only for small circuits with low error rates.
"""))

cells.append(nbf.v4.new_code_cell("""\
# PEC shot overhead analysis
p_gate = 0.01   # 1% depolarizing error per gate
N_gates = np.arange(1, 200)
gamma = 1 / (1 - p_gate)
overhead = gamma**(2 * N_gates)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Linear scale (early regime)
mask = N_gates <= 50
axes[0].plot(N_gates[mask], overhead[mask], color="purple", linewidth=2)
axes[0].axhline(1000, color="red", linestyle="--", label="1000× overhead (practical limit)")
axes[0].set_xlabel("Number of noisy gates N")
axes[0].set_ylabel("Shot overhead γ^{2N}")
axes[0].set_title(f"PEC Shot Overhead (p={p_gate})")
axes[0].legend()
axes[0].grid(alpha=0.3)

# Log scale (full range)
axes[1].semilogy(N_gates, overhead, color="purple", linewidth=2)
axes[1].axhline(1e3, color="red", linestyle="--", alpha=0.6, label="10³×")
axes[1].axhline(1e6, color="orange", linestyle="--", alpha=0.6, label="10⁶× (impractical)")
axes[1].set_xlabel("Number of noisy gates N")
axes[1].set_ylabel("Shot overhead (log scale)")
axes[1].set_title("PEC Overhead — Exponential in Gate Count")
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.suptitle(f"Probabilistic Error Cancellation: Shot Overhead Analysis (p_gate={p_gate})", fontsize=12)
plt.tight_layout()
plt.savefig("E5_pec_overhead.png", dpi=120, bbox_inches="tight")
plt.show()

# Find crossover
n_practical = np.argmax(overhead > 1000)
print(f"PEC becomes 1000× overhead at N ≈ {N_gates[n_practical]} gates (p={p_gate})")
"""))

# ── Section 7: Mitigation Techniques Comparison ───────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 7 · Technique Comparison & Selection Guide

| Technique | Bias | Variance | Shot overhead | Circuit overhead | When to use |
|-----------|------|----------|--------------|-----------------|-------------|
| ZNE | Low | Medium | $\lambda\times$ | $\lambda\times$ gates | Gate-error dominated |
| MEM | Zero (readout) | Low | ~1× | 0 | Always (low cost) |
| PEC | Zero | High | $\gamma^{2N}$ exponential | 0 | Small circuits only |
| Symmetry verification | Low | Low | ~1× | +ancilla | Known symmetry circuits |
| Clifford data regression | Low | Medium | polynomial | 0 | Observable estimation |

### Decision tree

```
Is readout error dominant?
├── Yes → Apply MEM first (always cheap)
└── No ↓

Is circuit < 20 gates?
├── Yes → PEC is feasible, most rigorous
└── No ↓

Are scale factors λ ≤ 7 affordable?
├── Yes → ZNE with polynomial extrapolation
└── No → Use symmetry verification or accept raw results
```
"""))

# ── Section 8: Qiskit Runtime Estimator ──────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 8 · Built-in Mitigation via Qiskit Runtime Estimator

For production use, Qiskit Runtime provides error mitigation integrated into the `Estimator` primitive.
On IBM hardware, setting `resilience_level` enables automatic mitigation.
"""))

cells.append(nbf.v4.new_code_cell("""\
print(\"\"\"
Qiskit Runtime Estimator with error mitigation:

from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2, Options

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

# Options control mitigation level
options = Options()
options.resilience_level = 2   # 0=none, 1=M3, 2=ZNE, 3=PEC

estimator = EstimatorV2(backend=backend, options=options)

job = estimator.run(
    [(circuit, observable, parameter_values)]
)
result = job.result()
exp_value = result[0].data.evs   # mitigated expectation value
\"\"\")
print("Resilience levels:")
print("  0 — No mitigation (raw)")
print("  1 — Measurement error mitigation (M3 matrix-free method)")
print("  2 — ZNE with gate folding")
print("  3 — PEC (requires noise characterisation, high shot count)")
"""))

# ── Section 9: Summary ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 9 · Summary

| Concept | Key Formula | Engineering Impact |
|---------|------------|-------------------|
| ZNE | Extrapolate $f(\lambda_i) \to f(0)$ | Reduces gate-error bias; needs $\lambda \leq 7$ |
| MEM | $\vec{p}_{\text{true}} = A^{-1}\vec{p}_{\text{meas}}$ | Corrects readout; essentially free |
| PEC | Overhead $= \gamma^{2N}$ | Unbiased but exponential cost |
| MEM+ZNE | Combined pipeline | Best practical NISQ results |

### Practical Engineering Checklist
- [ ] Always apply MEM — it's free and often the biggest win.
- [ ] For ZNE, use odd integer scale factors {1, 3, 5} with Richardson extrapolation.
- [ ] Monitor variance — mitigation increases variance; compensate with more shots.
- [ ] Never apply ZNE without sufficient shots — noise in the extrapolation dominates.
- [ ] Use `resilience_level=2` in Qiskit Runtime for production IBM runs.

### Next Module
**E6 · Quantum Error Correction** — going beyond mitigation to true fault tolerance:
the 3-qubit repetition code, syndrome measurement, and the road to logical qubits.
"""))

cells.append(nbf.v4.new_markdown_cell("""## Challenge: Adaptive ZNE

**Task**: Implement adaptive ZNE that automatically selects the optimal extrapolation order.

1. Run ZNE with scale factors $\\lambda \\in \\{1, 3, 5, 7, 9\\}$.
2. For each subset of size $k = 2, 3, 4, 5$, compute the Richardson-extrapolated value.
3. Plot the extrapolated values as a function of $k$ — at what $k$ does the estimate stabilise?
4. Define a convergence criterion: $|f_k(0) - f_{k-1}(0)| < \\varepsilon = 0.01$.
5. Report the optimal order and the final mitigated estimate.

**Insight**: Higher extrapolation order isn't always better — it can amplify noise in the measured points.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Your adaptive ZNE implementation here
scale_factors_full = [1, 3, 5, 7, 9]
# TODO: run ZNE for all 5 scale factors
# TODO: for k in range(2, 6): compute extrapolation using first k points
# TODO: plot extrapolated value vs k
# TODO: find convergence

print("Challenge: Implement adaptive ZNE and find optimal extrapolation order.")
"""))

nb.cells = cells
path = "E5_error_mitigation.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Notebook written → {path}")
