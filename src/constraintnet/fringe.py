"""D2 fringe test: discrete Aharonov-Bohm coherence of a two-path interferometer.

Geometry: cone over triangle (0,1,2) with apex ``*``. A loop leaves vertex 0 through the
apex and returns along the boundary edge: L = 0 -> * -> 2 -> 0, i.e. the difference of
two paths -- through the interior (where hidden state lives) or along the boundary.
The object's internal assignments x (admissible interiors from M3's resolution machinery,
flux classes as prescribed there) are the ensemble; no probabilities -- every count is
exact and character-weighted via reps.py-style characters (here: cyclic chi for Z_n and
chi_3 = fix - 1 for A4).

Coherence definitions (integer-counting observables, NOT amplitudes):

* ``coherence``   fraction of admissible interiors with TRIVIAL loop holonomy;
* ``visibility``  |mean of chi(Phi_L)| over the ensemble, normalized by chi(e) in [0,1].

Measured structure (tests lock it in):

* FLAT patch, no flux: every resolution forces Phi_L = e -- perfect coherence (C = V = 1)
  EVEN WHEN |I| > 1: hidden multiplicity alone does not decohere;
* FLUX threading a face of the interferometer: loop holonomy is pinned to the flux class
  -- coherence collapses to 0. Curvature IS which-path information: discrete AB effect;
* Z3 control reproduces both with omega-weighted counts (abelian AB).

This is the fringe visibility Qwen cloud's D2 asked for, computed as counting over
hidden histories -- no amplitudes inserted, no collapse anywhere.
"""

from __future__ import annotations

import cmath
from typing import Dict, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group

__all__ = ["loop_holonomy_through_apex", "fringe_coherence"]


def loop_holonomy_through_apex(group: Group, x: Sequence, a_02, apex_index: int = None):
    r"""Phi_L for L = 0 -> * -> 2 -> 0 with x_i := A_{*i}.

    Path via apex: A_{0*} A_{*2} = x_0^{-1} x_2. Return along boundary: A_{20} = a_02^{-1}.
    """
    return group.multiply(group.multiply(group.inverse(x[0]), x[2]), group.inverse(a_02))


def _chi3_value(group, element) -> float:
    if element == group.identity():
        return 3.0
    order = group.order_of(element)
    return -1.0 if order == 2 else 0.0


def fringe_coherence(
    cx: SimplicialComplex,
    apex: int,
    boundary: Sequence[int],
    solutions: List[Tuple],
    a_02,
) -> Dict:
    """Coherence + visibility of the two-path loop over an ensemble of admissible interiors.

    ``solutions`` comes from resolutions.enumerate_internal_resolutions (assignments of
    apex-edge labels x_i aligned with ``boundary`` order); ``a_02`` is the boundary label
    A_{02} closing the return path.  Exact counts only.
    """
    group = cx.group
    if not solutions:
        return {"n_resolutions": 0, "coherence": None, "visibility": None}

    trivial = group.identity()
    n = len(solutions)
    holonomies = [loop_holonomy_through_apex(group, x, a_02) for x in solutions]
    coherence = sum(1 for h in holonomies if h == trivial) / n

    if group.is_abelian():
        # cyclic character omega^k: identify element as power of generator 1 (Z_n additive)
        def chi(h):
            k = int(h) % group.order()
            return cmath.exp(2j * cmath.pi * k / group.order())

        norm = 1.0
    else:
        chi = lambda h: _chi3_value(group, h)  # noqa: E731
        norm = 3.0

    mean = sum(chi(h) for h in holonomies) / n
    return {"n_resolutions": n, "coherence": coherence, "visibility": abs(mean) / norm}
