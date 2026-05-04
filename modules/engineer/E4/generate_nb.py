import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""# E4 · Pulse-Level Programming with Qiskit Pulse

**Track:** Engineer | **Module:** E4 of 6

> *"Gates are high-level abstractions. Understanding pulses is understanding the machine itself."*

## Learning Objectives
1. Understand the physical mechanism: microwave pulses drive qubit transitions via the Hamiltonian.
2. Define custom pulse schedules using `qiskit.pulse` — Drive, Measure, Acquire channels.
3. Shape pulses: Gaussian, DRAG, flat-top, and their trade-offs.
4. Build a software X gate from a Gaussian pulse and verify with simulation.
5. Analyse pulse-level optimisation: faster gates vs leakage vs crosstalk.
"""))

# ── Setup ─────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1 · Environment Setup"))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# Core Qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator

try:
    import qiskit.pulse as pulse
    from qiskit.pulse import (
        Schedule, DriveChannel, MeasureChannel, AcquireChannel, MemorySlot,
        Play, Delay, Acquire, ShiftPhase, SetFrequency,
    )
    from qiskit.pulse.library import Gaussian, GaussianSquare, Drag, Constant
    PULSE_AVAILABLE = True
    print("Qiskit Pulse available.")
except ImportError:
    PULSE_AVAILABLE = False
    print("Qiskit Pulse not available — will use numpy to illustrate pulse shapes.")

try:
    from qiskit_ibm_runtime.fake_provider import FakeManhattan
    backend = FakeManhattan()
    FAKE_BACKEND = True
    print(f"FakeManhattan: {backend.num_qubits} qubits, dt={backend.configuration().dt*1e9:.2f} ns/sample")
except ImportError:
    FAKE_BACKEND = False
    print("FakeManhattan not available.")
"""))

# ── Section 2: Physical Mechanism ────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 2 · Physical Mechanism: Driving Qubit Transitions

A transmon qubit is a nonlinear LC oscillator with transition frequency $\omega_{01}$.
To perform a gate, we apply a microwave pulse at resonance frequency $\omega_{01}$.

### 2.1 The Rotating Frame Hamiltonian

In the rotating frame at drive frequency $\omega_d$, the control Hamiltonian is:

$$H(t) = -\frac{\delta}{2}\sigma_z + \frac{\Omega(t)}{2}\left[\cos(\phi)\sigma_x + \sin(\phi)\sigma_y\right]$$

where:
- $\delta = \omega_d - \omega_{01}$ — detuning (zero for resonant drive)
- $\Omega(t)$ — pulse envelope amplitude (Rabi frequency)
- $\phi$ — pulse phase (selects axis: $\phi=0$ → X rotation, $\phi=\pi/2$ → Y rotation)

### 2.2 Rotation Angle

The total rotation angle about the drive axis:

$$\theta = \int_0^T \Omega(t)\, dt$$

For an **X gate** ($\theta = \pi$, $\phi = 0$):

$$\int_0^T \Omega(t)\, dt = \pi$$

### 2.3 Pulse Timescales (IBM Transmon)

| Parameter | Typical Value |
|-----------|--------------|
| Qubit frequency $\omega_{01}/2\pi$ | 4.5–5.5 GHz |
| Anharmonicity $\alpha/2\pi$ | -200 to -350 MHz |
| $\pi$-pulse duration | 35–50 ns |
| Sample rate (dt) | 0.222 ns/sample |
| Gaussian $\sigma$ | ~8–12 ns |
"""))

cells.append(nbf.v4.new_code_cell("""\
# Visualise a resonant Gaussian drive
dt = 0.222e-9   # sample period (s)
fs = 1 / dt     # sample rate

def gaussian_envelope(N, sigma_samples):
    \"\"\"Symmetric Gaussian envelope of N samples, width sigma_samples.\"\"\"
    t = np.arange(N)
    mu = N / 2
    env = np.exp(-0.5 * ((t - mu) / sigma_samples)**2)
    return env

N = 256         # ~56.8 ns at 0.222 ns/sample
sigma = 32      # samples (~7 ns)
freq_qubit = 5.0e9   # Hz
t_ns = np.arange(N) * dt * 1e9  # nanoseconds

env = gaussian_envelope(N, sigma)
carrier = np.cos(2 * np.pi * freq_qubit * np.arange(N) * dt)
pulse_signal = env * carrier

# Area under envelope = θ; normalise for π-pulse
theta = np.trapz(env, dx=dt)
amp_norm = np.pi / theta
env_norm = env * amp_norm
theta_check = np.trapz(env_norm, dx=dt)
print(f"Gaussian pulse area (normalised): {theta_check:.4f} rad (target: π = {np.pi:.4f})")

fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

axes[0].plot(t_ns, env_norm, color="steelblue", linewidth=2)
axes[0].set_ylabel("Amplitude Ω(t) [rad/s]", fontsize=10)
axes[0].set_title("Gaussian Pulse Envelope (normalised for π rotation)", fontsize=11)
axes[0].fill_between(t_ns, 0, env_norm, alpha=0.3, color="steelblue")
axes[0].grid(alpha=0.3)

axes[1].plot(t_ns, carrier, color="gray", linewidth=0.6, alpha=0.7)
axes[1].set_ylabel("Carrier cos(ω₀₁·t)", fontsize=10)
axes[1].set_title("Microwave Carrier (5 GHz — oscillations too fast to resolve at this scale)", fontsize=10)
axes[1].grid(alpha=0.3)

axes[2].plot(t_ns, env_norm * carrier, color="tomato", linewidth=0.8, alpha=0.8)
axes[2].fill_between(t_ns, 0, env_norm * carrier, alpha=0.2, color="tomato")
axes[2].set_ylabel("Modulated signal", fontsize=10)
axes[2].set_xlabel("Time (ns)", fontsize=10)
axes[2].set_title("Gaussian-Modulated Microwave Pulse (baseband view)", fontsize=11)
axes[2].grid(alpha=0.3)

plt.suptitle("Physical Pulse Decomposition: Envelope × Carrier", fontsize=13)
plt.tight_layout()
plt.savefig("E4_gaussian_pulse.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 3: Pulse Shapes ───────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 3 · Pulse Shapes: Trade-offs

### 3.1 Gaussian

$$\Omega(t) = A\,e^{-(t-\mu)^2 / 2\sigma^2}$$

- **Pro**: smooth → minimal spectral leakage, low bandwidth
- **Con**: tails require truncation; slightly longer gate time

### 3.2 DRAG (Derivative Removal via Adiabatic Gate)

$$\Omega_X(t) = \Omega_G(t), \quad \Omega_Y(t) = -\frac{\beta}{\alpha}\dot{\Omega}_G(t)$$

Adds a quadrature component proportional to the time-derivative of the Gaussian.
**Pro**: suppresses leakage to $|2\rangle$ state (transmon anharmonicity).
**Con**: requires calibrating the DRAG coefficient $\beta$.

### 3.3 Gaussian Square (CNOT pulses)

$$\Omega(t) = \begin{cases} \text{Gaussian rise} & t \in [0, r] \\ A & t \in [r, T-r] \\ \text{Gaussian fall} & t \in [T-r, T] \end{cases}$$

Used for CR (cross-resonance) pulses driving CNOT gates — needs longer flat section.

### 3.4 Rectangular (simple but problematic)

$$\Omega(t) = A \cdot \mathbf{1}_{[0,T]}(t)$$

Sharp edges → wide bandwidth → spectral leakage → drives neighbouring qubits.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Compare pulse shapes in time and frequency domain
N = 256
sigma = 32
drag_beta = 0.5 / (2 * np.pi * 200e6)  # β/(2π × anharmonicity)
t = np.arange(N)
mu = N / 2

# Gaussian
gauss = np.exp(-0.5 * ((t - mu) / sigma)**2)
gauss /= np.trapz(gauss) / np.pi   # normalise for π rotation

# DRAG (quadrature = -β/α × dΩ/dt)
d_gauss = np.gradient(gauss)
drag_quad = -drag_beta * d_gauss * 200e6  # scale by anharmonicity/2π

# Gaussian Square
rise_fall = 48
gs = np.zeros(N)
for i in range(N):
    if i < rise_fall:
        gs[i] = np.exp(-0.5 * ((i - rise_fall) / 16)**2)
    elif i >= N - rise_fall:
        gs[i] = np.exp(-0.5 * ((i - (N - rise_fall)) / 16)**2)
    else:
        gs[i] = 1.0
gs /= np.trapz(gs) / np.pi

# Rectangular
rect = np.ones(N) * np.pi / N

shapes = {
    "Gaussian": gauss,
    "Gaussian Square": gs,
    "Rectangular": rect,
}

fig, axes = plt.subplots(2, len(shapes), figsize=(14, 8))
freqs = np.fft.rfftfreq(N, d=dt * 1e9)   # GHz units

for j, (name, shape) in enumerate(shapes.items()):
    # Time domain
    axes[0, j].plot(t * dt * 1e9, shape, color="steelblue", linewidth=2)
    if name == "Gaussian":
        axes[0, j].plot(t * dt * 1e9, drag_quad * 0.5, color="orange",
                        linewidth=1.5, linestyle="--", label="DRAG quadrature")
        axes[0, j].legend(fontsize=8)
    axes[0, j].fill_between(t * dt * 1e9, 0, shape, alpha=0.25, color="steelblue")
    axes[0, j].set_title(name, fontsize=11)
    axes[0, j].set_xlabel("Time (ns)")
    axes[0, j].grid(alpha=0.3)

    # Frequency domain (power spectrum)
    spectrum = np.abs(np.fft.rfft(shape))**2
    axes[1, j].plot(freqs, 10 * np.log10(spectrum + 1e-10), color="tomato")
    axes[1, j].set_xlabel("Frequency offset (GHz-scale normalised)")
    axes[1, j].set_ylabel("Power (dB)")
    axes[1, j].set_title(f"{name} — Spectrum")
    axes[1, j].set_xlim(0, 0.3)
    axes[1, j].grid(alpha=0.3)

axes[0, 0].set_ylabel("Ω(t) [rad/ns]")
axes[1, 0].set_ylabel("Power (dB)")

plt.suptitle("Pulse Shape Comparison: Time & Frequency Domain", fontsize=13)
plt.tight_layout()
plt.savefig("E4_pulse_shapes.png", dpi=120, bbox_inches="tight")
plt.show()
print("Key insight: Rectangular pulse has largest spectral spread → drives neighbouring qubits!")
"""))

# ── Section 4: Qiskit Pulse Schedule ─────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 4 · Building Pulse Schedules with Qiskit Pulse

`qiskit.pulse` provides a hardware-level abstraction with:
- **Channels**: `DriveChannel(i)`, `MeasureChannel(i)`, `AcquireChannel(i)`
- **Instructions**: `Play(pulse, channel)`, `Delay(duration, channel)`, `ShiftPhase(angle, channel)`
- **Schedules**: ordered collection of (time, instruction) pairs
"""))

cells.append(nbf.v4.new_code_cell("""\
if PULSE_AVAILABLE:
    with pulse.build(name="x_gate_qubit0") as x_sched:
        d0 = DriveChannel(0)
        # Gaussian pulse: amp=0.5, sigma=32 samples, duration=256 samples
        gauss_pulse = Gaussian(duration=256, amp=0.5, sigma=32)
        Play(gauss_pulse, d0)

    print("X gate schedule:")
    print(x_sched)

    # Build a CNOT-like schedule (sketch: CR + echo)
    with pulse.build(name="cx_gate_q0q1") as cx_sched:
        d0, d1 = DriveChannel(0), DriveChannel(1)
        cr_pulse = GaussianSquare(duration=800, amp=0.3, sigma=32, risefall_sigma_ratio=3)
        echo_pulse = Gaussian(duration=256, amp=0.5, sigma=32)

        # Cross-resonance drive on d1 at qubit 0 frequency
        Play(cr_pulse, d1)
        # Echo X on control qubit
        Play(echo_pulse, d0)
        Delay(cr_pulse.duration, d0)

    print("\\nCR (CNOT) sketch schedule:")
    print(cx_sched)

else:
    print("Demonstrating schedule structure conceptually (qiskit.pulse not available).")
    print(\"\"\"
Schedule: 'x_gate_qubit0'
  t=0: Play(Gaussian(duration=256, amp=0.5, sigma=32), DriveChannel(0))
  total duration: 256 samples (~56.8 ns)
Schedule: 'cx_gate_q0q1'
  t=0: Play(GaussianSquare(800, amp=0.3), DriveChannel(1))  ← CR drive
  t=0: Play(Gaussian(256, amp=0.5), DriveChannel(0))         ← echo X
  ...: Delay(800, DriveChannel(0))
  total duration: ~178 ns
\"\"\")
"""))

cells.append(nbf.v4.new_code_cell("""\
if PULSE_AVAILABLE:
    # Phase-shifted pulse: Y gate (shift phase by π/2)
    with pulse.build(name="y_gate_qubit0") as y_sched:
        d0 = DriveChannel(0)
        gauss_pulse = Gaussian(duration=256, amp=0.5, sigma=32)
        ShiftPhase(np.pi / 2, d0)   # rotate frame by π/2 → Y axis
        Play(gauss_pulse, d0)
        ShiftPhase(-np.pi / 2, d0)  # restore frame

    print("Y gate (phase-shifted Gaussian):")
    print(y_sched)

    # Z gate: pure virtual — no pulse, just frame rotation
    with pulse.build(name="rz_gate_qubit0") as rz_sched:
        ShiftPhase(-np.pi / 2, DriveChannel(0))   # RZ(π/2) = virtual Z

    print("\\nRZ(π/2) = virtual Z gate (zero duration!):")
    print(rz_sched)
    print("Key insight: Z gates are FREE on hardware — they're frame updates, not pulses.")
else:
    print("Virtual Z gate concept: Z rotation = phase shift on subsequent pulses.")
    print("Duration = 0 samples. This is why RZ is in IBM's native gate set.")
"""))

# ── Section 5: Pulse Simulation ───────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 5 · Qubit State Evolution Under a Pulse

We simulate the Bloch vector evolution during a Gaussian pulse using the rotating-wave
approximation (RWA) Hamiltonian:

$$\dot{\vec{r}} = \vec{\omega}(t) \times \vec{r}$$

where $\vec{\omega}(t) = (\Omega(t)\cos\phi,\, \Omega(t)\sin\phi,\, \delta)$ for detuning $\delta$.
"""))

cells.append(nbf.v4.new_code_cell("""\
from scipy.integrate import solve_ivp

def bloch_ode(t_val, r, omega_func, phi, delta):
    \"\"\"Bloch vector ODE: dr/dt = omega(t) × r\"\"\"
    ox = omega_func(t_val) * np.cos(phi)
    oy = omega_func(t_val) * np.sin(phi)
    oz = delta
    return [oy * r[2] - oz * r[1],
            oz * r[0] - ox * r[2],
            ox * r[1] - oy * r[0]]

# Gaussian envelope
T_pulse = 56.8e-9   # seconds (~256 samples)
sigma_s = 7.1e-9    # seconds (~32 samples)
A_norm = np.pi / (sigma_s * np.sqrt(2 * np.pi))  # area = π

def omega_gauss(t_val):
    mu = T_pulse / 2
    return A_norm * np.exp(-0.5 * ((t_val - mu) / sigma_s)**2)

# Solve for resonant drive (δ=0, φ=0: X rotation)
t_span = (0, T_pulse)
t_eval = np.linspace(0, T_pulse, 500)
r0 = [0.0, 0.0, 1.0]   # start at |0⟩ (north pole)

sol = solve_ivp(bloch_ode, t_span, r0, t_eval=t_eval, args=(omega_gauss, 0, 0), rtol=1e-8)
x, y, z = sol.y

# Final state
print(f"Initial state (Bloch): {r0}")
print(f"Final state  (Bloch): [{x[-1]:.4f}, {y[-1]:.4f}, {z[-1]:.4f}]")
print(f"Expected after π-pulse: [0, 0, -1] → |1⟩")
print(f"Fidelity proxy |⟨1|ψ⟩|² = {(1 - z[-1])/2:.4f} (should be ~1.0)")

t_ns = t_eval * 1e9

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Bloch components vs time
axes[0].plot(t_ns, x, label=r"$x$ (off-axis)", color="steelblue")
axes[0].plot(t_ns, y, label=r"$y$ (transverse)", color="orange")
axes[0].plot(t_ns, z, label=r"$z$ (population)", color="tomato")
axes[0].axhline(-1, color="gray", linestyle="--", alpha=0.5, label="|1⟩ target")
# Overlay pulse envelope
ax2 = axes[0].twinx()
t_env = np.linspace(0, T_pulse, 500)
ax2.plot(t_ns, [omega_gauss(t_) * 1e-6 for t_ in t_env],
         color="green", alpha=0.4, linewidth=2, linestyle="-.", label="Ω(t) [MHz]")
ax2.set_ylabel("Ω(t) [MHz]", color="green")
ax2.tick_params(axis="y", labelcolor="green")
axes[0].set_xlabel("Time (ns)")
axes[0].set_ylabel("Bloch component")
axes[0].set_title("Bloch Vector Evolution During Gaussian π-pulse")
axes[0].legend(loc="lower left", fontsize=8)
axes[0].grid(alpha=0.3)

# 3D Bloch sphere trajectory
from mpl_toolkits.mplot3d import Axes3D
ax3d = fig.add_subplot(122, projection="3d")
ax3d.remove()
ax3d = fig.add_subplot(122, projection="3d")

# Sphere wireframe
u = np.linspace(0, 2*np.pi, 30)
v = np.linspace(0, np.pi, 30)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))
ax3d.plot_wireframe(xs, ys, zs, color="lightgray", alpha=0.2, linewidth=0.5)

# Trajectory
sc = ax3d.scatter(x, y, z, c=t_ns, cmap="viridis", s=4)
ax3d.scatter([0], [0], [1], color="green", s=80, zorder=5, label="|0⟩ start")
ax3d.scatter([0], [0], [-1], color="red", s=80, zorder=5, label="|1⟩ target")
ax3d.set_xlabel("x"), ax3d.set_ylabel("y"), ax3d.set_zlabel("z")
ax3d.set_title("Bloch Sphere Trajectory")
ax3d.legend(fontsize=8)
plt.colorbar(sc, ax=ax3d, label="Time (ns)", shrink=0.6)

plt.tight_layout()
plt.savefig("E4_bloch_trajectory.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 6: Detuning & Calibration ────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 6 · Detuning, Rabi Oscillations & Pulse Calibration

A perfect gate requires exact resonance $\delta = 0$. Off-resonance pulses rotate about
a tilted axis, causing **over/under-rotation** errors.

**Rabi experiment**: sweep pulse amplitude $A$, measure $P(|1\rangle)$. Fit sine to find $A_\pi$.

$$P(|1\rangle) = \sin^2\!\left(\frac{\theta(A)}{2}\right) = \sin^2\!\left(\frac{\pi A}{2 A_\pi}\right)$$

**Ramsey experiment**: two $\pi/2$ pulses with delay $\tau$, measure fringe oscillation at
frequency $\delta$ — calibrates qubit frequency.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Simulate Rabi oscillations: sweep amplitude
def rabi_prob(A, A_pi):
    theta = np.pi * A / A_pi
    return np.sin(theta / 2)**2

A_pi = 0.5       # true π amplitude (arbitrary units)
A_range = np.linspace(0, 2 * A_pi, 200)
p_1 = rabi_prob(A_range, A_pi)

# Add shot noise
rng = np.random.default_rng(42)
shots = 1024
A_measured = np.linspace(0, 2 * A_pi, 25)
p_noisy = rabi_prob(A_measured, A_pi) + rng.normal(0, 1/np.sqrt(shots), len(A_measured))
p_noisy = np.clip(p_noisy, 0, 1)

# Fit to extract A_pi
from scipy.optimize import curve_fit
def rabi_fit(A, A_pi_fit):
    return np.sin(np.pi * A / (2 * A_pi_fit))**2

popt, _ = curve_fit(rabi_fit, A_measured, p_noisy, p0=[0.4])
A_pi_fitted = popt[0]
print(f"True A_π:   {A_pi:.4f}")
print(f"Fitted A_π: {A_pi_fitted:.4f}  (error: {abs(A_pi_fitted - A_pi)/A_pi*100:.2f}%)")

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

# Rabi plot
axes[0].plot(A_range, p_1, "b-", linewidth=2, label="Theory")
axes[0].scatter(A_measured, p_noisy, color="red", zorder=5, s=40, label="Simulated data")
axes[0].plot(A_range, rabi_fit(A_range, A_pi_fitted), "orange", linestyle="--",
             linewidth=1.5, label=f"Fit: A_π={A_pi_fitted:.3f}")
axes[0].axvline(A_pi_fitted, color="orange", linestyle=":", alpha=0.5)
axes[0].set_xlabel("Pulse amplitude A (a.u.)")
axes[0].set_ylabel("P(|1⟩)")
axes[0].set_title("Rabi Oscillation (Amplitude Calibration)")
axes[0].legend()
axes[0].grid(alpha=0.3)

# Ramsey fringe: sweep delay τ at near-resonance
T2 = 60e-6
delta_freq = 1.5e6  # 1.5 MHz detuning
tau = np.linspace(0, 3e-6, 300)  # 0–3 µs delay
ramsey_signal = 0.5 * (1 + np.exp(-tau / T2) * np.cos(2 * np.pi * delta_freq * tau))
ramsey_noisy = ramsey_signal + rng.normal(0, 0.02, len(tau))

axes[1].plot(tau * 1e6, ramsey_signal, "b-", linewidth=1.5, label="Theory (δ=1.5 MHz)")
axes[1].scatter(tau[::10] * 1e6, ramsey_noisy[::10], color="red", s=20, alpha=0.7, label="Noisy data")
axes[1].set_xlabel("Delay τ (µs)")
axes[1].set_ylabel("P(|0⟩)")
axes[1].set_title(f"Ramsey Fringe (Frequency Calibration, T2={T2*1e6:.0f} µs)")
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.suptitle("Pulse Calibration Experiments", fontsize=13)
plt.tight_layout()
plt.savefig("E4_calibration.png", dpi=120, bbox_inches="tight")
plt.show()
"""))

# ── Section 7: Gate Circuit from Custom Schedule ──────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 7 · Attaching Pulse Schedules to Gate Circuits

In Qiskit, you can attach a custom pulse schedule to a gate using `InstructionScheduleMap`,
then transpile your circuit with `inst_map` to use the custom pulse on hardware.

This is the workflow for **pulse calibration** and **custom gate design**.
"""))

cells.append(nbf.v4.new_code_cell("""\
if PULSE_AVAILABLE and FAKE_BACKEND:
    from qiskit.pulse import InstructionScheduleMap

    # Get the backend's default instruction schedule map
    inst_map = backend.defaults().instruction_schedule_map
    available_gates = inst_map.instructions
    print("Available pulse instructions on FakeManhattan:")
    print(available_gates[:10], "...")

    # Inspect the default X gate pulse
    x_default = inst_map.get("x", 0)
    print("\\nDefault X gate on qubit 0:")
    print(x_default)

else:
    print("InstructionScheduleMap workflow (requires real/fake backend):")
    print(\"\"\"
# Get the backend's default schedule map
inst_map = backend.defaults().instruction_schedule_map

# Build a custom X gate with different amplitude
with pulse.build(backend) as my_x_gate:
    pulse.play(Gaussian(256, amp=0.48, sigma=32), pulse.drive_channel(0))

# Register and use in transpilation
inst_map.add('x', 0, my_x_gate)
qc = QuantumCircuit(1)
qc.x(0)
tqc = transpile(qc, backend, inst_map=inst_map)
\"\"\")
"""))

# ── Section 8: Summary ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""## 8 · Summary

| Concept | Key Formula / Mechanism |
|---------|------------------------|
| Rabi rotation | $\theta = \int_0^T \Omega(t)\,dt$ — area under pulse = rotation angle |
| Virtual Z gate | Phase shift on subsequent pulses — zero duration, zero error |
| Gaussian vs DRAG | DRAG adds quadrature to cancel $\|2\rangle$ leakage |
| Rabi calibration | Sweep amplitude, fit sine → find $A_\pi$ |
| Ramsey calibration | Two $\pi/2$ pulses + delay → measure qubit frequency offset |
| Leakage | $\|2\rangle$ state excitation; mitigated by DRAG and anharmonicity |

### Pulse Engineering Design Flow
1. **Characterise**: run Rabi + Ramsey → calibrate $\omega_{01}$, $A_\pi$
2. **Choose shape**: Gaussian for single-qubit, GaussianSquare for CR/CNOT
3. **Add DRAG**: calibrate $\beta$ with DRAG sequence to suppress leakage
4. **Minimise duration**: shorter pulse → less decoherence; but too short → wider spectrum
5. **Verify**: randomised benchmarking to confirm EPC matches prediction

### Next Module
**E5 · Error Mitigation Techniques** — ZNE, measurement error mitigation, and
probabilistic error cancellation — getting better results from NISQ hardware without fixing the hardware.
"""))

cells.append(nbf.v4.new_markdown_cell("""## Challenge: DRAG Coefficient Calibration

**Task**: Calibrate the DRAG coefficient $\\beta$.

1. Build a 1-qubit circuit: apply $N$ repetitions of $X \\cdot X$ (net = Identity).
2. Vary the DRAG quadrature coefficient $\\beta$ from -0.5 to 0.5.
3. Simulate using `qiskit_aer` with leakage to $|2\\rangle$ (use 3-level transmon model if available,
   else model leakage as $Z$ errors with rate $\\propto \\beta^2$).
4. Plot $P(|0\\rangle)$ vs $\\beta$ for $N = \\{1, 5, 10, 20\\}$ repetitions.
5. Find $\\beta^*$ that maximises $P(|0\\rangle)$ at high $N$.

**Physical intuition**: The optimal $\\beta$ exactly cancels leakage-induced population transfer.
At the correct $\\beta$, $P(|0\\rangle) \\approx 1$ even for many repetitions.
"""))

cells.append(nbf.v4.new_code_cell("""\
# Your DRAG calibration implementation here
beta_vals = np.linspace(-0.5, 0.5, 41)
N_reps = [1, 5, 10, 20]

# TODO: for each (beta, N):
#   1. Build circuit with N X·X pairs and DRAG quadrature ∝ beta
#   2. Simulate with leakage noise model
#   3. Extract P(|0>)
# TODO: plot and find optimal beta

print("Challenge: Implement DRAG calibration above.")
print(f"Sweep β in {beta_vals[[0,-1]]} over {len(beta_vals)} points.")
"""))

nb.cells = cells
path = "E4_pulse_programming.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Notebook written → {path}")
