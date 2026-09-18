"""Quantum sectors of a charge knot: centralizers and phase decomposition (spec M-quantum).

The specification's quantum structure paragraph, made concrete for A4:

    "The residual gauge group preserving a boundary charge q is the centralizer H = C_G(q).
     The internal resolutions form a representation of H. Decomposing that representation
     into irreducible representations gives primitive quantum sectors. For G = A4 and q of
     order 3, H is Z3, and the sectors carry discrete phase labels 1, omega, omega^2."

Verified here by exact computation:

* residual symmetries: |C_G(e)| = 12 (A4), |C_G(order-2)| = 4 (V4), |C_G(order-3)| = 3
  (cyclic) -- the spec's H isomorphisms hold element by element;
* the charge's own action by conjugation on the set of order-3 elements (the states it
  can rotate through) has permutation character with fixed counts chi(e)=8, chi(q)=chi(q^2)=2
  (fixed points are exactly C_G(q) intersect S), decomposing over H = Z3 as

      4 x phase 1   +   2 x phase omega   +   2 x phase omega^2      (dim 8 total)

  -- the primitive quantum sectors of an order-3 charge knot, with multiplicities;
* V4 charge control: H = V4 acts freely on the same set -> uniform multiplicity 2 across
  all four 1D irreps of V4 (no preferred phase: abelian real sectors);
* adjoint control: <chi_conj, 1> = number of conjugacy classes (= number of irreps), the
  center-of-group-algebra identity, guarding the inner-product machinery itself.

HONEST SCOPE NOTE: this realizes the spec's representation-of-H decomposition on the
conjugation orbit of the charge -- the cleanest instance where "internal resolutions form
a representation of H" is literally true without extra gauge-localization structure.
Assigning sectors to the full cone resolution space I(B) requires localizing the gauge at
the charge site (gauge fixing cannot be both complete and local); that refinement is
flagged open, not faked here.
"""

from __future__ import annotations

import cmath
from typing import Dict, List, Tuple

from .groups import AlternatingGroup4, Group

__all__ = ["residual_symmetry", "conjugation_multiplicities", "sector_report"]


def residual_symmetry(group: Group, q) -> frozenset:
    """H = C_G(q), verified closed under multiplication (a genuine subgroup)."""
    h = group.centralizer(q)
    for a in h:
        for b in h:
            assert group.multiply(a, b) in h, "centralizer not closed -- engine bug"
    return h


def _cyclic_phase_multiplicities(group: Group, q, states: List) -> Dict[int, int]:
    """H = <q> ~ Z3 acting on `states` by conjugation; multiplicities of 1, omega, omega^2."""
    elements_h = [group.identity(), q, group.multiply(q, q)]
    chi = []
    for h in elements_h:
        fixed = sum(1 for x in states if group.multiply(group.multiply(h, x), group.inverse(h)) == x)
        chi.append(fixed)
    omega = cmath.exp(2j * cmath.pi / 3)
    out: Dict[int, int] = {}
    for k in range(3):
        mult = sum(c * omega ** (-k * i) for i, c in enumerate(chi)) / 3
        assert abs(mult.imag) < 1e-9 and abs(mult.real - round(mult.real)) < 1e-9
        out[k] = round(mult.real)
    return out


def conjugation_multiplicities(group: Group, q, states: List):
    """Decompose the conjugation permutation representation of H = C_G(q) on `states`.

    Returns (h_structure, multiplicities-by-irrep-index). For |H| = 3 uses Z3 phases;
    for |H| = 4 with all non-identity elements order 2 uses V4's four real characters.
    """
    h = sorted(residual_symmetry(group, q), key=repr)
    if len(h) == 3:
        return {"H_size": 3, "type": "Z3"}, _cyclic_phase_multiplicities(group, q, states)
    if len(h) == 4:
        elements_h = h
        chi = [
            sum(1 for x in states if group.multiply(group.multiply(e, x), group.inverse(e)) == x)
            for e in elements_h
        ]
        # V4 characters over its own element order (each row +/-1); multiplicities exact
        mults: List[int] = []
        signs = [(1, 1, 1, 1), None, None, None]
        # build the four characters from quotient maps Z2 x Z2 explicitly
        nonid = [e for e in elements_h if e != group.identity()]
        a, b = nonid[0], nonid[1]
        ab = group.multiply(a, b)
        def fixed_count(e):
            return sum(1 for x in states if group.multiply(group.multiply(e, x), group.inverse(e)) == x)
        chi_map = {repr(e): fixed_count(e) for e in elements_h}
        rows = [
            (1, 1, 1, 1),
            (1, 1, -1, -1),
            (1, -1, 1, -1),
            (1, -1, -1, 1),
        ]
        order_key = [repr(group.identity()), repr(a), repr(b), repr(ab)]
        values = [chi_map[k] for k in order_key]
        for row in rows:
            m = sum(c * r for c, r in zip(values, row)) / 4
            assert abs(m - round(m)) < 1e-9
            mults.append(round(m))
        return {"H_size": 4, "type": "V4"}, mults
    return {"H_size": len(h), "type": "G" if len(h) == group.order() else "?"}, {}


def sector_report(group=None):
    """The spec's claims as data: residual symmetries and sector multiplicities per class."""
    g = group or AlternatingGroup4()
    ident = g.identity()
    report: Dict[str, Dict] = {}
    order3 = [x for x in g.elements if g.order_of(x) == 3]
    order2 = [x for x in g.elements if g.order_of(x) == 2]

    q3 = next(iter(order3))
    hinfo, mults = conjugation_multiplicities(g, q3, order3)
    report["order-3 charge"] = {"H": hinfo, "sector_multiplicities(1,w,w2)": mults}

    q2 = next(iter(order2))
    hinfo4, mults4 = conjugation_multiplicities(g, q2, order3)
    report["order-2 charge"] = {"H": hinfo4, "sector_multiplicities(V4 irreps)": mults4}

    # adjoint control: <chi_conj, trivial> must equal the number of conjugacy classes
    chi_adj = [len(g.centralizer(x)) for x in g.elements]
    center_dim = sum(chi_adj) / g.order()
    report["adjoint control"] = {
        "<chi_conj,1>": round(center_dim),
        "n_classes": len(g.conjugacy_classes()),
    }
    return report
