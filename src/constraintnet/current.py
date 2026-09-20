"""Probability transport in a coined arc walk, measured at the shift substep.

q(v,w) = ||(C psi)[v->w]||^2 and J(v,w) = q(v,w)-q(w,v).
The coin preserves vertex density; unitary internal transport and record motion
preserve each shifted arc's norm. Thus rho'(v)-rho(v) = -sum_w J(v,w).
Missing reverse arcs at an absorbing boundary carry zero incoming probability.
This is probability current in the declared walk, not an electromagnetic current.
"""

import numpy as np


def arc_probability(state):
    """Sum over all internal/record indices, retaining the arc index."""
    return np.sum(np.abs(state) ** 2, axis=tuple(range(1, state.ndim)))


def transport_current(walk, state):
    """Return outgoing probabilities and antisymmetric edge currents per arc."""
    if state.ndim < 1 or state.shape[0] != len(walk.arcs):
        raise ValueError("state's first axis must match the walk arcs")
    phi = walk.phi.reshape((-1,) + (1,) * (state.ndim - 1))
    overlap = np.add.reduceat(phi * state, walk.starts, axis=0)
    coined = 2 * phi * overlap[walk.vertex_of_arc] - state
    outgoing = arc_probability(coined)
    incoming = np.zeros_like(outgoing)
    incoming[walk.kept] = outgoing[walk.target[walk.kept]]
    return outgoing, outgoing - incoming


def continuity_residual(walk, before, after, current):
    """Local continuity error at every interior vertex, including open outflow."""
    density_change = np.add.reduceat(arc_probability(after) - arc_probability(before), walk.starts)
    return density_change + np.add.reduceat(current, walk.starts)


def cycle_transport(walk, outgoing, cycle):
    """Oriented cycle flux and traffic; reversing the cycle reverses only flux.

    The bias is net directed crossings / total crossings on the cycle. It is not
    an angular momentum, charge, or a count of completed particle revolutions.
    """
    if len(cycle) < 3 or len(set(cycle)) != len(cycle):
        raise ValueError("cycle must contain at least three distinct vertices")
    steps = list(zip(cycle, cycle[1:] + cycle[:1]))
    fwd = np.array([outgoing[walk.index[a, b]] for a, b in steps])
    rev = np.array([outgoing[walk.index[b, a]] for a, b in steps])
    flux = fwd - rev
    traffic = float(np.sum(fwd + rev))
    signed = float(np.sum(flux))
    return {"edge_flux": flux.tolist(), "signed_crossings": signed,
            "traffic": traffic, "bias": signed / traffic if traffic else 0.0}
