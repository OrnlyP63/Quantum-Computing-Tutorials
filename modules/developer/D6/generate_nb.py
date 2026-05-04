#!/usr/bin/env python3
"""generate_nb.py — Module D6: Running on Real IBM Quantum Hardware"""
import nbformat as nbf, os

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"}
}

cells = []

cells.append(nbf.v4.new_markdown_cell(r"""# D6 — Running on Real IBM Quantum Hardware
**Track:** Developer | **Difficulty:** ⭐⭐⭐☆☆ | **Est. Time:** 30 min

| | |
|---|---|
| **Prerequisites** | F1–F4, D1–D5; IBM Quantum account |
| **Qiskit Modules** | `qiskit_ibm_runtime`, `qiskit`, `qiskit_aer` |
| **Companion Video** | Developer Module D6 |
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🎯 Learning Objectives

1. Connect to IBM Quantum via `QiskitRuntimeService` and list available backends
2. **Transpile** a circuit for a specific backend's topology and native gate set
3. Submit a real hardware job and **monitor** its queue position
4. Parse and compare results: **noisy hardware vs ideal simulator**
5. Understand key backend properties: coupling map, T1/T2, error rates
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📖 Real Hardware vs Simulator

| Property | AerSimulator | IBM Quantum Hardware |
|---|---|---|
| Speed | Instant (local) | Minutes to hours (queue) |
| Noise | Zero (ideal) | T1, T2, gate errors, readout errors |
| Qubit count | Unlimited | 5–133 qubits |
| Gate fidelity | 1.0 (perfect) | ~99.5% (CNOT ~98%) |
| Cost | Free | Free tier: 10 min/month |
| Debugging | `Statevector` | Shots only |

### The Backend Abstraction

In Qiskit 1.x with IBM Runtime:
- **Backend** = remote API endpoint (like a REST API server)
- **Transpilation** = build optimization for the specific backend's topology
- **Job** = submitted computation (async, has queue position)
- **Shots** = number of measurement repetitions (handles noise via statistics)

> **Dev Bridge:** Backend = remote API endpoint; transpilation = build optimization/minification; shots = retry count for fault tolerance.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 1 — Connect to IBM Quantum

**Note:** This cell requires an IBM Quantum account. If you don't have one, skip to Step 2 which uses `FakeManhattan` (a realistic noise-simulated backend).
"""))

cells.append(nbf.v4.new_code_cell(r"""# REQUIRES: IBM Quantum account at quantum.ibm.com
# Get your token from: quantum.ibm.com → Account → API Token

# Uncomment to save your credentials (one-time setup):
# from qiskit_ibm_runtime import QiskitRuntimeService
# QiskitRuntimeService.save_account(
#     channel="ibm_quantum",
#     token="YOUR_IBM_QUANTUM_TOKEN_HERE",
#     overwrite=True
# )

# Load saved credentials
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_quantum")
    print("✓ Connected to IBM Quantum")

    # List available backends
    backends = service.backends()
    print(f"\nAvailable backends ({len(backends)}):")
    for b in backends[:8]:  # show first 8
        status = b.status()
        print(f"  {b.name:30s} | Qubits: {b.num_qubits:3d} | "
              f"Queue: {status.pending_jobs:4d} | Operational: {status.operational}")

except Exception as e:
    print(f"IBM Quantum not available: {e}")
    print("\nFalling back to FakeManhattan (realistic noise simulation)")
    service = None
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 2 — FakeManhattan: Realistic Noise Without a Queue"""))

cells.append(nbf.v4.new_code_cell(r"""import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# FakeManhattan: 65-qubit backend simulator with realistic noise
try:
    from qiskit_ibm_runtime.fake_provider import FakeManhattan
    fake_backend = FakeManhattan()
    fake_sim = AerSimulator.from_backend(fake_backend)
    print("✓ FakeManhattan loaded — 65-qubit noisy simulation")
    using_fake = True
except ImportError:
    try:
        from qiskit_aer.primitives import SamplerV2
        from qiskit_aer.noise import NoiseModel
        # Build a simple noise model manually
        from qiskit_aer.noise import depolarizing_error
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.002, 1), ['h', 'x'])
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 2),  ['cx'])
        fake_sim = AerSimulator(noise_model=noise_model)
        print("✓ Custom depolarizing noise model loaded")
        using_fake = False
    except Exception as e:
        print(f"Warning: {e}. Using ideal simulator.")
        fake_sim = AerSimulator()
        using_fake = False

# Ideal simulator for comparison
ideal_sim = AerSimulator()

print(f"\nBackend: {fake_sim.name}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 3 — Inspect Backend Properties"""))

cells.append(nbf.v4.new_code_cell(r"""# Inspect backend properties — like reading API documentation
try:
    props = fake_backend.properties()
    config = fake_backend.configuration()

    print(f"Backend: {fake_backend.name}")
    print(f"Qubits: {config.n_qubits}")
    print(f"Basis gates: {config.basis_gates}")
    print(f"Coupling map (first 10 pairs): {config.coupling_map[:10]}")
    print()

    # T1, T2 coherence times for first 5 qubits
    print("Qubit coherence times (microseconds):")
    print(f"{'Qubit':6s} {'T1 (μs)':12s} {'T2 (μs)':12s} {'Readout err':12s}")
    print("-" * 45)
    for q in range(min(5, config.n_qubits)):
        t1  = props.t1(q) * 1e6
        t2  = props.t2(q) * 1e6
        ro  = props.readout_error(q)
        print(f"  Q{q:2d}: {t1:>8.1f}    {t2:>8.1f}    {ro:.4f}")

    # Gate error rates
    print("\nCNOT error rates (first 5 edges):")
    coupling = config.coupling_map[:5]
    for edge in coupling:
        try:
            err = props.gate_error("cx", edge)
            print(f"  CNOT({edge[0]},{edge[1]}): {err:.4f} ({err*100:.2f}%)")
        except Exception:
            pass

except Exception as e:
    print(f"Backend properties not available: {e}")
    print("Using placeholder values (typical for IBM 65-qubit systems):")
    print("  T1 ≈ 100-200 μs, T2 ≈ 50-150 μs, CNOT fidelity ≈ 98-99%")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 4 — Transpile for Real Hardware"""))

cells.append(nbf.v4.new_code_cell(r"""# Build a simple Bell state circuit (abstract)
qc_abstract = QuantumCircuit(2, 2, name="Bell State")
qc_abstract.h(0)
qc_abstract.cx(0, 1)
qc_abstract.measure([0,1],[0,1])

print("Abstract circuit (backend-agnostic):")
print(qc_abstract.draw(output="text"))
print(f"\nAbstract depth: {qc_abstract.depth()}")
print(f"Gates: {dict(qc_abstract.count_ops())}")

# Transpile at different optimization levels
print("\n" + "=" * 60)
print("Transpilation comparison:")
print(f"{'Opt. Level':12s} {'Depth':8s} {'CX count':10s} {'Gate count':10s}")
print("-" * 45)

try:
    backend_for_transpile = fake_backend
except NameError:
    backend_for_transpile = ideal_sim

for opt_level in [0, 1, 2, 3]:
    try:
        qc_t = transpile(qc_abstract, backend=backend_for_transpile,
                         optimization_level=opt_level)
        cx_count = dict(qc_t.count_ops()).get("cx", 0)
        gate_count = sum(dict(qc_t.count_ops()).values())
        print(f"  Level {opt_level}:    {qc_t.depth():6d}    {cx_count:8d}    {gate_count:8d}")
    except Exception as e:
        qc_t = transpile(qc_abstract, optimization_level=opt_level)
        print(f"  Level {opt_level}:    {qc_t.depth():6d}    (local transpile)")

print("\nNote: Higher optimization = fewer gates = less decoherence")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 5 — Noisy vs Ideal Comparison"""))

cells.append(nbf.v4.new_code_cell(r"""# Run the same circuit on ideal vs noisy backend and compare

circuits = {
    "Bell State": (QuantumCircuit(2, 2), 2),
    "GHZ-4":      (QuantumCircuit(4, 4), 4),
}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for row, (circuit_name, (qc_base, n)) in enumerate(circuits.items()):
    # Build circuit
    qc_base.h(0)
    for i in range(n - 1):
        qc_base.cx(i, i+1)
    qc_base.measure(range(n), range(n))

    all_outcomes = [f"{i:0{n}b}" for i in range(2**n)]
    n_shots = 4096

    for col, (sim_name, sim_obj) in enumerate([
        ("Ideal (AerSimulator)", ideal_sim),
        ("Noisy (Fake Backend)", fake_sim),
    ]):
        ax = axes[row][col]

        try:
            qc_t = transpile(qc_base, sim_obj, optimization_level=1)
            job = sim_obj.run(qc_t, shots=n_shots)
            counts = job.result().get_counts()
        except Exception as e:
            # Fallback
            qc_t = transpile(qc_base, ideal_sim)
            job = ideal_sim.run(qc_t, shots=n_shots)
            counts = job.result().get_counts()
            sim_name += " (fallback ideal)"

        total = sum(counts.values())
        vals  = [counts.get(o, 0) / total for o in all_outcomes]
        expected_states = [f"{0:0{n}b}", f"{2**n - 1:0{n}b}"]  # |00...0⟩ and |11...1⟩
        colors = ["#4CAF50" if o in expected_states else "#FF5722" for o in all_outcomes]

        bars = ax.bar(all_outcomes, vals, color=colors, edgecolor="black", width=0.7)
        ax.set_title(f"{circuit_name} — {sim_name}", fontsize=10, fontweight="bold")
        ax.set_ylabel("Probability"); ax.set_ylim(0, 0.7)
        ax.tick_params(axis="x", rotation=45)

        # Error metric: total variation distance from ideal
        ideal_probs = [0.5 if o in expected_states else 0 for o in all_outcomes]
        tvd = 0.5 * sum(abs(v - p) for v, p in zip(vals, ideal_probs))
        ax.text(0.02, 0.92, f"TVD from ideal: {tvd:.3f}",
                transform=ax.transAxes, fontsize=9, color="darkred",
                bbox=dict(boxstyle="round", facecolor="#FFCDD2", alpha=0.8))

plt.suptitle("Ideal vs Noisy Simulation: Total Variation Distance Measures Noise Impact",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("ideal_vs_noisy.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 💻 Step 6 — Submit to Real Hardware (Optional)"""))

cells.append(nbf.v4.new_code_cell(r"""# This cell only runs if you have IBM Quantum credentials and `service` is set

if 'service' in dir() and service is not None:
    from qiskit_ibm_runtime import SamplerV2 as Sampler, Session
    from qiskit.primitives import StatevectorSampler

    # Select least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Selected backend: {backend.name}")
    print(f"Queue: {backend.status().pending_jobs} jobs")

    # Build and transpile circuit
    qc_hw = QuantumCircuit(2, 2)
    qc_hw.h(0); qc_hw.cx(0, 1); qc_hw.measure([0,1],[0,1])
    qc_hw_t = transpile(qc_hw, backend=backend, optimization_level=1)
    print(f"\nTranspiled circuit depth: {qc_hw_t.depth()}")

    # Submit job via Sampler primitive
    with Session(backend=backend) as session:
        sampler = Sampler(session=session)
        job = sampler.run([qc_hw_t], shots=1024)
        print(f"\nJob submitted! Job ID: {job.job_id()}")
        print("Waiting for result (this may take several minutes due to queue)...")

        # Retrieve result
        result = job.result()
        counts_hw = result[0].data.meas.get_counts()
        print(f"\nHardware result: {counts_hw}")
        total_hw = sum(counts_hw.values())
        p00 = counts_hw.get("00", 0) / total_hw
        p11 = counts_hw.get("11", 0) / total_hw
        print(f"P(00) = {p00:.3f}  P(11) = {p11:.3f}  (ideal: 0.5, 0.5)")

else:
    print("IBM Quantum service not configured.")
    print("To use real hardware:")
    print("  1. Create account at quantum.ibm.com")
    print("  2. Get API token from Account settings")
    print("  3. Run: QiskitRuntimeService.save_account(channel='ibm_quantum', token='YOUR_TOKEN')")
    print("  4. Re-run this cell")
    print("\nContinue with the noisy simulation results above for now.")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🧪 Exercises

### Exercise 1 — Circuit Efficiency for Hardware

Compare circuit depth and CNOT count for GHZ state on 3, 5, and 7 qubits at transpilation optimization levels 0 and 3. Plot the trade-off.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — transpilation efficiency analysis

qubit_counts = [3, 5, 7]
opt_levels   = [0, 1, 2, 3]
results = {}

for n in qubit_counts:
    qc_ghz = QuantumCircuit(n, n)
    qc_ghz.h(0)
    for i in range(n-1): qc_ghz.cx(i, i+1)
    qc_ghz.measure(range(n), range(n))

    for opt in opt_levels:
        qc_t = transpile(qc_ghz, ideal_sim, optimization_level=opt)
        results[(n, opt)] = {
            "depth":    qc_t.depth(),
            "cx_count": dict(qc_t.count_ops()).get("cx", 0),
        }

# YOUR CODE HERE: plot results
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, metric in zip(axes, ["depth", "cx_count"]):
    for n in qubit_counts:
        vals = [results[(n, opt)][metric] for opt in opt_levels]
        ax.plot(opt_levels, vals, "o-", lw=2, ms=7, label=f"{n} qubits")
    ax.set_xlabel("Optimization Level"); ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(f"GHZ Circuit: {metric.replace('_', ' ').title()} vs Optimization Level")
    ax.legend(); ax.grid(True, alpha=0.3); ax.set_xticks(opt_levels)
plt.suptitle("Transpilation Impact on Circuit Efficiency")
plt.tight_layout(); plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""### Exercise 2 — Noise Characterization

Build a circuit that measures the **readout error** of your backend: prepare $|0\rangle$ and measure, then prepare $|1\rangle$ and measure. Compare to the backend-reported error rates.
"""))

cells.append(nbf.v4.new_code_cell(r"""# YOUR CODE HERE — readout error characterization

shots = 8192
results_ro = {}

for prepared_state, gate_fn in [(0, lambda qc: None), (1, lambda qc: qc.x(0))]:
    qc_ro = QuantumCircuit(1, 1)
    gate_fn(qc_ro)
    qc_ro.measure(0, 0)

    job = fake_sim.run(transpile(qc_ro, fake_sim), shots=shots)
    counts = job.result().get_counts()
    total = sum(counts.values())

    results_ro[prepared_state] = {
        "p_wrong": counts.get(str(1 - prepared_state), 0) / total,
        "p_right": counts.get(str(prepared_state), 0) / total,
    }

print("Readout Error Characterization:")
print(f"{'Prepared':10s} {'P(correct)':12s} {'P(wrong)':12s}")
print("-" * 36)
for state, res in results_ro.items():
    print(f"|{state}⟩        {res['p_right']:.4f}        {res['p_wrong']:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 🏆 Challenge

Implement **measurement error mitigation** using a calibration matrix:

1. Run calibration circuits: $|0\rangle \to |0\rangle$ and $|1\rangle \to |0\rangle$ (both measured)
2. Build the 2×2 calibration matrix $A$ where $A_{ij} = P(\text{measure } i | \text{prepare } j)$
3. Run your Bell state experiment and record the raw noisy counts
4. Apply the **pseudo-inverse** of $A$ to mitigate readout errors
5. Compare raw vs mitigated results against the ideal 50/50 split

This is the simplest form of quantum error mitigation.
"""))

cells.append(nbf.v4.new_code_cell(r"""# CHALLENGE — Measurement Error Mitigation

# Step 1: Build calibration matrix (2×2 for single qubit)
cal_matrix = np.zeros((2, 2))

for prep_state in [0, 1]:
    qc_cal = QuantumCircuit(1, 1)
    if prep_state == 1: qc_cal.x(0)
    qc_cal.measure(0, 0)
    job = fake_sim.run(transpile(qc_cal, fake_sim), shots=8192)
    counts = job.result().get_counts()
    total = sum(counts.values())
    cal_matrix[0, prep_state] = counts.get("0", 0) / total  # P(measure 0 | prepare prep_state)
    cal_matrix[1, prep_state] = counts.get("1", 0) / total  # P(measure 1 | prepare prep_state)

print("Calibration matrix A:")
print(f"  A = [[P(0|prep0), P(0|prep1)],")
print(f"       [P(1|prep0), P(1|prep1)]]")
print(np.round(cal_matrix, 4))

# Step 2: YOUR CODE HERE — apply pseudo-inverse mitigation to Bell state results
# Run Bell state on noisy sim, then: p_mitigated = A^{-1} @ p_raw

print("\nChallenge: Apply A_inv @ p_raw for each marginal qubit distribution")
print("and show how the mitigated results are closer to the ideal 0.5")
"""))

cells.append(nbf.v4.new_markdown_cell(r"""## 📚 Further Reading

1. **Qiskit IBM Runtime Docs** — [https://docs.quantum.ibm.com/api/qiskit-ibm-runtime](https://docs.quantum.ibm.com/api/qiskit-ibm-runtime)
2. **IBM Quantum Platform** — [https://quantum.ibm.com](https://quantum.ibm.com) — Job submission and monitoring
3. **Qiskit Patterns** — Workflow best practices for production quantum programs
4. **Error mitigation in Qiskit** — `qiskit_ibm_runtime.options.ResilienceOptionsV2`
5. **IBM Quantum Systems** — Hardware specs for all available backends: qiskit.ibm.com/services/devices
"""))

nb.cells = cells
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D6_real_hardware.ipynb")
nbf.write(nb, open(out, "w"))
print(f"✓ Generated: {out}")
