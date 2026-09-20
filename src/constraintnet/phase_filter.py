"""Phase-resolved Cesaro filters for a supplied linear unitary step.

For z on the unit circle, F_T = sum(t=0..T-1) z**(-t) U**t psi / T.
This is a finite spectral window, NOT an eigenprojector at finite T. In particular,
(U-z)F_T = z * (z**(-T) U**T psi - psi) / T.
The normalized residual bound is 2*||psi|| / (T*||F_T||), not simply 2/T.
"""

import numpy as np


def phase_averages(step, initial, phases, checkpoints):
    """Yield (T, averages) with independent arrays for every requested phase.

    ``phases`` are arguments of the eigenvalues of U (U psi = exp(i*phase) psi).
    No normalization, phase fitting, or projection onto a spatial region occurs.
    ``step`` must return a new array without mutating its input.
    """
    checkpoints = tuple(checkpoints)
    if (not checkpoints or any(not isinstance(t, (int, np.integer)) or t < 1
                               for t in checkpoints)
            or tuple(sorted(set(checkpoints))) != checkpoints):
        raise ValueError("checkpoints must be strictly increasing positive integers")
    phases = tuple(float(p) for p in phases)
    if not phases or not np.all(np.isfinite(phases)):
        raise ValueError("phases must be nonempty and finite")
    state = np.array(initial, dtype=complex, copy=True)
    sums = [np.zeros_like(state) for _ in phases]
    points = set(checkpoints)
    for t in range(checkpoints[-1]):
        for phase, acc in zip(phases, sums):
            acc += np.exp(-1j * phase * t) * state
        if t + 1 in points:
            yield t + 1, [acc / (t + 1) for acc in sums]
        if t + 1 < checkpoints[-1]:
            state = step(state)


def eigen_residual(step, state, phase):
    """Full-state residual, plus the best phase for this vector (not a new filter).

    The best phase minimizes ||U x - z x|| over |z|=1; it need not match a true
    eigenphase. Return the advanced normalized state for additional observables.
    """
    norm = float(np.linalg.norm(state))
    if not np.isfinite(norm) or norm == 0:
        raise ValueError("state must have finite nonzero norm")
    x = state / norm
    advanced = step(x)
    overlap = np.vdot(x, advanced)
    best = float(np.angle(overlap))
    return {
        "filtered_weight": norm * norm,
        "target_phase": float(phase),
        "target_residual": float(np.linalg.norm(advanced - np.exp(1j * phase) * x)),
        "best_phase": best,
        "best_phase_residual": float(np.linalg.norm(advanced - np.exp(1j * best) * x)),
    }, advanced
