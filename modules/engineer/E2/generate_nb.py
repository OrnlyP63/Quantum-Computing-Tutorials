import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

cells = []

# ── Section 0: Title ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""# E2 · Noise, Decoherence & Error Characterization

**Track:** Engineer | **Module:** E2 of 6

> *"A quantum computer without noise theory is a quantum computer you cannot trust."*

## Learning Objectives
By the end of this module you will be able to:
1. Distinguish T1 (energy relaxation) from T2 (dephasing) and calculate their effect on circuit fidelity.
2. Build custom `NoiseModel` objects using `qiskit_aer.noise`.
3. Apply depolarizing, bit-flip, phase-flip, and amplitude-damping channels analytically and in simulation.
4. Quantify the fidelity gap between noisy and ideal circuits using TVD and process fidelity.
5. Design noise-aware experiments: calibrate error rates and characterise gate errors.
"""))

# ── Section 1: Setup ─────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1 · Environment Setup"))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import warnings
warnings.filterwarnings("ignore")

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity, process_fidelity, Operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    pauli_error,
    amplitude_damping_error,
    phase_damping_error,
    thermal_relaxation_error,
    ReadoutError,
)

print("All imports successful.")
print(f"AerSimulator: {AerSimulator().name}")
"""))

# ── Section 2: T1 / T2 Theory ─────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 2 · Decoherence: T1 and T2

### 2.1 Energy Relaxation (T1)

A qubit in $|1\rangle$ spontaneously emits a photon and relaxes to $|0\rangle$ with characteristic time $T_1$.

The amplitude-damping channel with damping parameter $\gamma = 1 - e^{-t/T_1}$:

$$\mathcal{E}_{AD}(\rho) = K_0 \rho K_0^\dagger + K_1 \rho K_1^\dagger$$

$$K_0 = \begin{pmatrix} 1 & 0 \\ 0 & \sqrt{1-\gamma} \end{pmatrix}, \quad K_1 = \begin{pmatrix} 0 & \sqrt{\gamma} \\ 0 & 0 \end{pmatrix}$$

The Bloch vector components decay as:
$$x(t) = x_0 e^{-t/T_2}, \quad y(t) = y_0 e^{-t/T_2}, \quad z(t) = z_0 e^{-t/T_1} + (e^{-t/T_1} - 1)$$

### 2.2 Dephasing (T2)

$T_2$ captures total decoherence. The dephasing-only time $T_\phi$ satisfies:

$$\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{\phi}$$

The phase-damping channel collapses off-diagonal elements:

$$\rho = \begin{pmatrix} \rho_{00} & \rho_{01} \\ \rho_{10} & \rho_{11} \end{pmatrix} \xrightarrow{\mathcal{E}_{PD}} \begin{pmatrix} \rho_{00} & \rho_{01}(1-\lambda) \\ \rho_{10}(1-\lambda) & \rho_{11} \end{pmatrix}$$

where $\lambda = 1 - e^{-t/T_\phi}$.

### 2.3 Practical Numbers (IBM Superconducting)

| Property | Typical Value |
|----------|--------------|
| $T_1$ | 50–300 µs |
| $T_2$ | 30–200 µs |
| Single-qubit gate | ~35 ns |
| CNOT gate | ~300–500 ns |
| Max coherent ops (T1) | ~1000–8000 gates |
"""))

cells.append(nbf.v4.new_code_cell("""\
# Bloch vector decay under T1 / T2
T1 = 100e-6   # 100 µs
T2 = 60e-6    # 60 µs

t = np.linspace(0, 3 * T1, 500)

# Start on equator: x0=1, y0=0, z0=0
x0, y0, z0 = 1.0, 0.0, 0.0
x = x0 * np.exp(-t / T2)
y = y0 * np.exp(-t / T2)
z = z0 * np.exp(-t / T1) - (1 - np.exp(-t / T1))   # relaxes to -1 (ground state)

# Purity = 0.5*(1 + |r|^2)
purity = 0.5 * (1 + x**2 + y**2 + z**2)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

t_us = t * 1e6
axes[0].plot(t_us, x, label=r"$x(t)$", color="steelblue")
axes[0].plot(t_us, z, label=r"$z(t)$", color="tomato")
axes[0].axhline(-1, color="gray", linestyle="--", linewidth=0.8, label="Ground state z=-1")
axes[0].axvline(T1 * 1e6, color="tomato", linestyle=":", alpha=0.6, label=f"T1={T1*1e6:.0f} µs")
axes[0].axvline(T2 * 1e6, color="steelblue", linestyle=":", alpha=0.6, label=f"T2={T2*1e6:.0f} µs")
axes[0].set_xlabel("Time (µs)")
axes[0].set_ylabel("Bloch component")
axes[0].set_title("Bloch Vector Decay")
axes[0].legend(fontsize=8)
axes[0].grid(alpha=0.3)

axes[1].plot(t_us, purity, color="purple")
axes[1].axhline(0.5, color="gray", linestyle="--", label="Mixed state threshold")
axes[1].set_xlabel("Time (µs)")
axes[1].set_ylabel("Purity Tr(ρ²)")
axes[1].set_title("State Purity Decay")
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.suptitle("Decoherence: T1=100 µs, T2=60 µs, initial |+⟩", fontsize=13)
plt.tight_layout()
plt.savefig("E2_decoherence_decay.png", dpi=120, bbox_inches="tight")
plt.show()
print("Figure saved.")
"""))

# ── Section 3: Noise Channels ─────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 3 · Quantum Noise Channels

### 3.1 Depolarizing Channel

The most common gate-error model. With probability $p$, apply a random Pauli:

$$\mathcal{E}_{dep}(\rho) = (1-p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z)$$

Equivalently $= (1 - \frac{4p}{3})\rho + \frac{p}{3}I$. Shrinks the Bloch sphere uniformly.

### 3.2 Bit-Flip Channel

With probability $p$, apply $X$:
$$\mathcal{E}_{BF}(\rho) = (1-p)\rho + p \, X\rho X$$

### 3.3 Phase-Flip Channel

With probability $p$, apply $Z$ (kills superposition coherence):
$$\mathcal{E}_{PF}(\rho) = (1-p)\rho + p \, Z\rho Z$$

### 3.4 Amplitude Damping

Models spontaneous emission ($|1\rangle \to |0\rangle$):
$$\mathcal{E}_{AD}(\rho) = K_0\rho K_0^\dagger + K_1\rho K_1^\dagger$$

### 3.5 Thermal Relaxation

Combines amplitude damping (T1) and pure dephasing (T2) — the most physically realistic model for superconducting qubits.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Compare Bloch sphere contraction for different channels
def bloch_contraction(channel_type, p):
    \"\"\"Return Bloch vector [x,y,z] scaling factors after channel application.\"\"\"
    if channel_type == "depolarizing":
        s = 1 - 4*p/3
        return s, s, s
    elif channel_type == "bit_flip":
        return 1 - 2*p, 1 - 2*p, 1.0
    elif channel_type == "phase_flip":
        return 1 - 2*p, 1 - 2*p, 1.0   # same as bit-flip in z basis view
    elif channel_type == "amplitude_damping":
        gamma = p
        return np.sqrt(1 - gamma), np.sqrt(1 - gamma), 1 - gamma

p_vals = np.linspace(0, 0.5, 200)
channels = {
    "Depolarizing": "depolarizing",
    "Bit-flip": "bit_flip",
    "Phase-flip": "phase_flip",
    "Amplitude damping": "amplitude_damping",
}

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
labels = ["x-scaling", "y-scaling", "z-scaling"]
for i, ax in enumerate(axes):
    for name, ch in channels.items():
        scales = [bloch_contraction(ch, p)[i] for p in p_vals]
        ax.plot(p_vals, scales, label=name)
    ax.set_xlabel("Error probability p")
    ax.set_ylabel(labels[i])
    ax.set_title(f"Bloch {labels[i]}")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    ax.axhline(0, color="black", linewidth=0.5)

plt.suptitle("Bloch Vector Scaling Under Different Noise Channels", fontsize=12)
plt.tight_layout()
plt.savefig("E2_channel_comparison.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 4: Build NoiseModel ───────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 4 · Building a `NoiseModel` with Qiskit Aer

Qiskit Aer's `NoiseModel` lets you attach error channels to specific gates and qubits.
We'll build three noise models of increasing physical realism.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── Model A: Simple depolarizing ──────────────────────────────────────────────
p1 = 0.01    # single-qubit gate error
p2 = 0.05    # two-qubit gate error

noise_model_A = NoiseModel()
noise_model_A.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ["u1", "u2", "u3", "h", "x", "y", "z"])
noise_model_A.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx"])
print("Model A — Depolarizing:")
print(noise_model_A)
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── Model B: Pauli error (bit-flip + phase-flip independently) ─────────────────
noise_model_B = NoiseModel()
# Single-qubit: bit-flip with p=0.005, phase-flip with p=0.01
bit_phase_error = pauli_error([("X", 0.005), ("Z", 0.01), ("I", 0.985)])
noise_model_B.add_all_qubit_quantum_error(bit_phase_error, ["h", "x", "y", "z", "u3"])
# Two-qubit depolarizing
noise_model_B.add_all_qubit_quantum_error(depolarizing_error(0.04, 2), ["cx"])
print("Model B — Pauli (bit-flip + phase-flip) + 2Q depolarizing:")
print(noise_model_B)
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── Model C: Thermal relaxation (most physical) ────────────────────────────────
T1_ns = 80_000   # 80 µs in nanoseconds
T2_ns = 50_000   # 50 µs in nanoseconds
t_gate1 = 50     # single-qubit gate time ns
t_gate2 = 400    # CX gate time ns

noise_model_C = NoiseModel()
# Single-qubit gates
error_1q = thermal_relaxation_error(T1_ns, T2_ns, t_gate1)
noise_model_C.add_all_qubit_quantum_error(error_1q, ["u1", "u2", "u3", "h", "x"])
# Two-qubit gates
error_2q = thermal_relaxation_error(T1_ns, T2_ns, t_gate2).expand(
    thermal_relaxation_error(T1_ns, T2_ns, t_gate2)
)
noise_model_C.add_all_qubit_quantum_error(error_2q, ["cx"])
# Readout error
ro_err = ReadoutError([[0.95, 0.05], [0.02, 0.98]])
noise_model_C.add_all_qubit_readout_error(ro_err)
print("Model C — Thermal relaxation + readout error:")
print(noise_model_C)
"""))

# ── Section 5: Noisy vs Ideal Simulation ──────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 5 · Noisy vs Ideal Simulation

We'll simulate a Bell state circuit under each noise model and measure:

$$\text{TVD} = \frac{1}{2}\sum_x |p_{\text{ideal}}(x) - p_{\text{noisy}}(x)|$$

TVD = 0 means perfect agreement; TVD = 1 means completely different distributions.
"""))

cells.append(nbf.v4.new_code_cell("""\
def bell_circuit(n_qubits=2):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc

def run_circuit(qc, noise_model=None, shots=8192):
    sim = AerSimulator(noise_model=noise_model)
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}

def tvd(p_ideal, p_noisy):
    keys = set(p_ideal) | set(p_noisy)
    return 0.5 * sum(abs(p_ideal.get(k, 0) - p_noisy.get(k, 0)) for k in keys)

qc_bell = bell_circuit()
print(qc_bell.draw())

shots = 16384
p_ideal = run_circuit(qc_bell, noise_model=None, shots=shots)
p_A     = run_circuit(qc_bell, noise_model=noise_model_A, shots=shots)
p_B     = run_circuit(qc_bell, noise_model=noise_model_B, shots=shots)
p_C     = run_circuit(qc_bell, noise_model=noise_model_C, shots=shots)

print("\\nIdeal distribution:", p_ideal)
print("Model A TVD:", f"{tvd(p_ideal, p_A):.4f}")
print("Model B TVD:", f"{tvd(p_ideal, p_B):.4f}")
print("Model C TVD:", f"{tvd(p_ideal, p_C):.4f}")
"""))

cells.append(nbf.v4.new_code_cell("""\
# Visualise all distributions side by side
all_states = ["00", "01", "10", "11"]
distributions = {"Ideal": p_ideal, "Depolarizing": p_A, "Pauli": p_B, "Thermal": p_C}

x = np.arange(len(all_states))
width = 0.18
offsets = np.linspace(-1.5 * width, 1.5 * width, 4)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#2ecc71", "#e74c3c", "#3498db", "#9b59b6"]
for i, (label, probs) in enumerate(distributions.items()):
    vals = [probs.get(s, 0) for s in all_states]
    bars = ax.bar(x + offsets[i], vals, width, label=label, color=colors[i], alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels(all_states, fontsize=12)
ax.set_xlabel("Measurement outcome")
ax.set_ylabel("Probability")
ax.set_title("Bell State: Ideal vs Noisy Distributions")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("E2_noisy_vs_ideal.png", dpi=120, bbox_inches="tight")
plt.show()

tvds = [tvd(p_ideal, p) for p in [p_A, p_B, p_C]]
for name, d in zip(["Depolarizing", "Pauli", "Thermal"], tvds):
    print(f"TVD({name}): {d:.4f}  ({'low' if d < 0.05 else 'moderate' if d < 0.15 else 'high'} noise)")
"""))

# ── Section 6: Error Rate vs Circuit Depth ────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 6 · Fidelity Decay with Circuit Depth

For a depolarizing channel with per-gate error $\varepsilon$, after $d$ gates:

$$F(d) \approx (1 - \varepsilon)^d \approx e^{-\varepsilon d}$$

This exponential decay is the core reason deep circuits fail on NISQ hardware.
The **circuit volume** $V = d \times n$ (depth × qubits) is bounded by coherence.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Build circuits of increasing depth: H-CX repeated d times
def depth_circuit(depth):
    qc = QuantumCircuit(2, 2)
    for _ in range(depth):
        qc.h(0)
        qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

depths = list(range(1, 25))
ideal_00_prob = []
noisy_00_prob = []

for d in depths:
    qc = depth_circuit(d)
    p_id = run_circuit(qc, noise_model=None, shots=8192)
    p_no = run_circuit(qc, noise_model=noise_model_A, shots=8192)
    ideal_00_prob.append(p_id.get("00", 0))
    noisy_00_prob.append(p_no.get("00", 0))

# Fit exponential decay to noisy
from scipy.optimize import curve_fit
def exp_decay(d, eps):
    return np.exp(-eps * np.array(d))

popt, _ = curve_fit(exp_decay, depths, noisy_00_prob, p0=[0.05])
d_fit = np.linspace(1, 24, 200)
y_fit = exp_decay(d_fit, popt[0])
print(f"Fitted per-layer error rate: ε = {popt[0]:.4f}")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(depths, ideal_00_prob, "o--", color="green", label="Ideal", markersize=5)
ax.plot(depths, noisy_00_prob, "s-", color="red", label="Noisy (sim)", markersize=5)
ax.plot(d_fit, y_fit, "--", color="orange", label=f"Fit: exp(-{popt[0]:.3f}·d)", linewidth=2)
ax.set_xlabel("Circuit depth (H-CX layers)")
ax.set_ylabel("P(00)")
ax.set_title("Fidelity Decay vs Circuit Depth")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("E2_fidelity_vs_depth.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 7: Gate Error Characterization (RB sketch) ────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 7 · Error Characterisation: Randomised Benchmarking

**Randomised Benchmarking (RB)** measures the average gate error without state-preparation/measurement (SPAM) errors.

**Protocol:**
1. Apply $m$ random Clifford gates.
2. Append the inverse Clifford (net = Identity).
3. Measure survival probability $P_{\text{surv}}(m)$.
4. Fit: $P_{\text{surv}}(m) = A \cdot p^m + B$

The **error per Clifford** (EPC) = $\frac{(1-p)(2^n - 1)}{2^n}$.

We simulate a simplified version below (single Clifford = Hadamard).
"""))

cells.append(nbf.v4.new_code_cell("""\
# Simplified RB: repeat H^2m = I, measure survival
def rb_circuit(m):
    \"\"\"Apply 2m Hadamards — always identity, net |0><0|. Returns circuit.\"\"\"
    qc = QuantumCircuit(1, 1)
    for _ in range(2 * m):
        qc.h(0)
    qc.measure(0, 0)
    return qc

m_vals = list(range(0, 60, 5))
p_surv_ideal = []
p_surv_noisy = []

for m in m_vals:
    qc = rb_circuit(m if m > 0 else 1)
    pi = run_circuit(qc, noise_model=None, shots=8192)
    pn = run_circuit(qc, noise_model=noise_model_A, shots=8192)
    p_surv_ideal.append(pi.get("0", 0))
    p_surv_noisy.append(pn.get("0", 0))

# Fit exponential
def rb_model(m, A, p, B):
    return A * p**np.array(m) + B

from scipy.optimize import curve_fit
popt_rb, _ = curve_fit(rb_model, m_vals, p_surv_noisy, p0=[0.5, 0.97, 0.5], maxfev=5000)
A_fit, p_fit, B_fit = popt_rb
epc = (1 - p_fit) * 1 / 2   # n=1 qubit
print(f"RB fit: A={A_fit:.3f}, p={p_fit:.4f}, B={B_fit:.3f}")
print(f"Error per Clifford (EPC) ≈ {epc:.4f}  ({epc*100:.2f}%)")

m_fit = np.linspace(0, 59, 200)
y_fit_rb = rb_model(m_fit, *popt_rb)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(m_vals, p_surv_ideal, "go--", label="Ideal", markersize=6)
ax.plot(m_vals, p_surv_noisy, "rs", label="Noisy", markersize=6)
ax.plot(m_fit, y_fit_rb, "--", color="orange", label=f"RB fit p={p_fit:.4f}", linewidth=2)
ax.axhline(0.5, color="gray", linestyle=":", label="Random guess")
ax.set_xlabel("m (Clifford layers)")
ax.set_ylabel("Survival probability P(0)")
ax.set_title("Randomised Benchmarking (Simulated)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("E2_rb_curve.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 8: Readout Error ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 8 · Readout (SPAM) Error

Measurement errors are often the dominant source of error at low gate counts.

The **assignment matrix** $A$ maps true states to measured probabilities:
$$\vec{p}_{\text{meas}} = A \cdot \vec{p}_{\text{true}}$$

where $A_{ij} = P(\text{measure } i \,|\, \text{prepared } j)$.

**Calibration**: prepare $|0\rangle$ and $|1\rangle$ separately, measure to get columns of $A$.
**Correction**: invert $A$ and apply to measured distribution.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Simulate readout calibration
# A[i,j] = P(measure i | state j)
e0 = 0.04   # P(1|0) — false positive
e1 = 0.06   # P(0|1) — false negative
A = np.array([[1 - e0, e1],
              [e0,     1 - e1]])
print("Assignment matrix A:")
print(A)

# Generate a noisy distribution
p_true = np.array([0.5, 0.5])   # ideal Bell |00>+|11> → marginal 50/50
p_meas = A @ p_true
print(f"\\nTrue marginal:    {p_true}")
print(f"Measured marginal: {p_meas}")

# Invert for correction
A_inv = np.linalg.inv(A)
p_corrected = A_inv @ p_meas
p_corrected = np.clip(p_corrected, 0, 1)
p_corrected /= p_corrected.sum()
print(f"Corrected:         {p_corrected}")

fig, ax = plt.subplots(figsize=(6, 4))
states = ["0", "1"]
x = np.arange(2)
ax.bar(x - 0.2, p_true, 0.18, label="True", color="green", alpha=0.8)
ax.bar(x,       p_meas, 0.18, label="Noisy measured", color="red", alpha=0.8)
ax.bar(x + 0.2, p_corrected, 0.18, label="Corrected", color="blue", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(["P(0)", "P(1)"])
ax.set_ylabel("Probability")
ax.set_title(f"Readout Error Mitigation (e0={e0}, e1={e1})")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("E2_readout_correction.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 9: Summary ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 9 · Summary & Key Takeaways

| Concept | Key Formula | Engineering Impact |
|---------|------------|-------------------|
| T1 (energy relaxation) | $\gamma = 1 - e^{-t/T_1}$ | Limits circuit depth |
| T2 (dephasing) | $\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{T_\phi}$ | Kills superposition |
| Depolarizing | $\mathcal{E}(\rho) = (1-p)\rho + \frac{p}{3}\sum_i P_i\rho P_i^\dagger$ | Most common gate model |
| Fidelity decay | $F \approx e^{-\varepsilon d}$ | Exponential depth penalty |
| RB error rate | EPC $= \frac{(1-p)(2^n-1)}{2^n}$ | Standard benchmarking metric |
| Readout error | $A\vec{p}_{\text{true}} = \vec{p}_{\text{meas}}$ | Correctable with calibration |

### Design Rules for NISQ Circuits
1. **Minimise gate count** — every gate adds $O(\varepsilon)$ error.
2. **Optimise for native gates** — avoid costly decompositions.
3. **Parallelise** — depth matters more than gate count.
4. **Calibrate readout** — low-cost, high-impact error mitigation.
5. **Know your T1/T2** — circuit time must be $\ll T_2$.

### Next Module
**E3 · Transpilation & Circuit Optimization** — how Qiskit transforms your high-level circuit into hardware-native gates, routes SWAP operations, and reduces depth.
"""))

# ── Challenge ─────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## Challenge: Cross-Entropy Benchmarking

**Task**: Implement a simplified version of Google's Cross-Entropy Benchmarking (XEB).

1. Generate random single-qubit circuits of depths 1–20 (use `Rx`, `Ry`, `Rz` with random angles).
2. Compute the ideal output distribution for each circuit (use `Statevector`).
3. Simulate each circuit with Model A and collect measured probabilities.
4. Compute XEB fidelity: $F_{XEB} = 2^n \\langle p_{\\text{ideal}}(x) \\rangle_{\\text{noisy}} - 1$
5. Plot $F_{XEB}$ vs depth and compare to the theoretical prediction.

**Hint**: For $n=1$: $F_{XEB}(d) \\approx (1 - \\varepsilon)^d$ where $\\varepsilon$ is the per-gate depolarizing error.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Your XEB implementation here
# Step 1: random single-qubit circuit
import random

def random_1q_circuit(depth):
    qc = QuantumCircuit(1, 1)
    for _ in range(depth):
        gate = random.choice(["rx", "ry", "rz"])
        angle = random.uniform(0, 2 * np.pi)
        getattr(qc, gate)(angle, 0)
    return qc

# TODO: compute Statevector for ideal distribution
# TODO: run with noise model A
# TODO: compute XEB fidelity per depth
# TODO: plot F_XEB vs depth
print("Challenge: Implement XEB above and compare to theory.")
"""))

nb.cells = cells
path = "E2_noise_decoherence.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Notebook written → {path}")
