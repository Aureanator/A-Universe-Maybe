"""D(A4) modular data: the full anyonic category Layer-2 asks for.

The kinematic sector of Event-Constraint Dynamics, named: flux = conjugacy class,
charge = irrep of the centralizer, statistics = Drinfeld double D(A4). This module
computes the modular data from first principles and verifies it against every pass
criterion in the Layer-2 brief (item 1):

    * S unitary;  S symmetric;  S^2 = charge conjugation C;  (ST)^3 = S^2
    * vacuum row S_{0a} = d_a / |G| with quantum dimensions d_{([g],pi)} = |cl(g)|*dim(pi)
    * sum_a d_a^2 = |G|^2 = 144
    * Verlinde N^c_ab = sum_x S*_{cx} S_{ax} S_{bx} / S_{0x}: nonnegative integers
    * sub-rules: pure charges fuse as Rep(A4); ([e],rho) x ([g],pi) = (+)([g], pi (x) Res rho);
      the shift rule 1' x F1 = F2; a x abar contains the vacuum exactly once
    * class algebra at flux level: C2^2 = 3 C1 + 2 C2;  C3 C4 = 4 C1 + 4 C2 (exact);
      C3^2 has support {C2, C4} only (no identity term)

S-matrix convention. The brief quotes S ~ (1/|G|) sum_x chi_bar(xhx^-1) chi_bar(x^-1gx).
With characters extended by zero outside their centralizers, that prefactor gives a
vacuum row of dim(pi), not d_a/|G| -- off by |cl(g)|*|cl(h)|/|G|. The correct
normalization (pinned here by the toric-code Z2 control and by the vacuum-row identity) is

    S_{(C,A),(D,B)} = (|C||D| / |G|^2) * sum_x chi_A^*(x b x^-1) chi_B^*(x^-1 a x),

with a, b class representatives and both characters extended by zero. T is the
self-Abrahonov-Bohm twist theta_{(C,A)} = chi_A(a)/dim(A) (a in Z(C_G(a))), matching
reference/opus_audit/fermion.py's table: V4 dyons W2,W3 -> -1; order-3 dyons 1,w,w^2.

Kernel module: no RNG, no scheduler, no coordinates. All values exact up to float
rounding of roots of unity (asserted at construction).
"""

from __future__ import annotations

import cmath
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .groups import AlternatingGroup4, Group
from .reps import a4_irreps

__all__ = [
    "AnyonType", "double_sectors", "quantum_dimensions", "s_matrix", "t_matrix",
    "fusion_coefficients", "charge_conjugation", "class_algebra_product", "sector_report",
]

OMEGA = cmath.exp(2j * cmath.pi / 3)
TOL = 1e-9


# --------------------------------------------------------------------------- sectors

@dataclass(frozen=True)
class AnyonType:
    """A simple object of D(G): flux conjugacy class + centralizer irrep.

    `character` is defined on the centralizer only; use `chi(x)` for the
    extension-by-zero convention used in the S-matrix sum.
    """

    class_index: int
    label: str                      # e.g. "1'", "chi1", "W10"
    representative: Tuple[int, ...]
    flux_class: frozenset
    centralizer: Tuple[Tuple[int, ...], ...]
    character: Dict[Tuple[int, ...], complex]
    dimension: int                  # dim of the centralizer irrep

    @property
    def quantum_dimension(self) -> float:
        return len(self.flux_class) * self.dimension

    def chi(self, x):
        """Character extended by zero outside the centralizer."""
        return self.character.get(x, 0j)

    def __str__(self) -> str:
        return f"([c{self.class_index}], {self.label})"


def _z3_characters(gen: Tuple[int, ...], group: Group):
    """Irreps of <gen> ~ Z3 as element->value dicts, labelled chi0..chi2."""
    e = group.identity()
    powers = [e, gen]
    powers.append(group.multiply(powers[1], gen))
    assert len(set(powers)) == 3 and group.multiply(powers[2], gen) == e
    out = {}
    for k in range(3):
        out[f"chi{k}"] = {p: OMEGA ** (k * j) for j, p in enumerate(powers)}
    return out


def _v4_characters(v4: Tuple[Tuple[int, ...], ...], group: Group):
    """Irreps of V4 ~ Z2 x Z2 via a derived basis; labels W_uv record the basis choice.

    The SET of four characters is canonical (all homomorphisms V4 -> +-1); individual
    labels depend on which two involutions serve as basis -- documented, not hidden.
    """
    e = group.identity()
    nontrivial = sorted(x for x in v4 if x != e)
    assert len(nontrivial) == 3
    a, b = nontrivial[0], nontrivial[1]
    coords: Dict[Tuple[int, ...], Tuple[int, int]] = {e: (0, 0), a: (1, 0), b: (0, 1)}
    coords[group.multiply(a, b)] = (1, 1)
    assert set(coords) == set(v4)
    out = {}
    for u in (0, 1):
        for v in (0, 1):
            label = f"W{u}{v}"
            out[label] = {x: complex((-1) ** (u * ca + v * cb)) for x, (ca, cb) in coords.items()}
    return out


def double_sectors(group: Optional[Group] = None) -> Tuple[AnyonType, ...]:
    """All 14 simple objects of D(A4), canonically ordered; vacuum first."""
    g = group or AlternatingGroup4()
    classes = g.conjugacy_classes()          # order [id, 3-, 3+, 2] per CONVENTIONS.md
    sectors: List[AnyonType] = []

    for ci, cls in enumerate(classes):
        rep = sorted(cls)[0]                 # deterministic representative
        cent = tuple(sorted(g.centralizer(rep)))
        if ci == 0:                          # pure charges: irreps of A4 itself
            _, irreps = a4_irreps()
            for irrep in irreps:
                char = {x: irrep.character[g.elements.index(x)] for x in cent}
                sectors.append(AnyonType(ci, irrep.name, rep, frozenset(cls), cent, char, irrep.dimension))
        elif len(cent) == 3:                 # order-3 flux: centralizer Z3 = <rep>
            for label, char in _z3_characters(rep, g).items():
                sectors.append(AnyonType(ci, label, rep, frozenset(cls), cent, char, 1))
        else:                                # order-2 flux: centralizer V4
            assert len(cent) == 4
            for label, char in _v4_characters(cent, g).items():
                sectors.append(AnyonType(ci, label, rep, frozenset(cls), cent, char, 1))

    assert sectors[0].label == "1" and len(sectors) == 14
    return tuple(sectors)


# --------------------------------------------------------------------------- modular data

def quantum_dimensions(sectors) -> List[float]:
    return [s.quantum_dimension for s in sectors]


def _round_int(z: complex) -> int:
    assert abs(z.imag) < TOL and abs(z.real - round(z.real)) < 1e-6, f"non-real/integer {z}"
    return round(z.real)


def s_matrix(sectors, group: Optional[Group] = None):
    """S_{ab} = (|Ca||Cb|/|G|^2) sum_x chi_a^*(x b x^-1) chi_b^*(x^-1 a x), chars extended by 0.

    CONVENTION WARNING, settled by experiment: the asymmetric conjugation directions
    (first factor by x, second by x^-1 -- as quoted in the Layer-2 brief) are REQUIRED.
    The symmetric variant (both factors conjugated by x^-1) passes unitarity, symmetry,
    vacuum-row and even yields IDENTICAL fusion coefficients, but fails the chirality-
    sensitive modular identity (ST)^3 = (tau/D) S^2 with error O(1). Only this form
    satisfies it exactly. See tests/test_category.py::test_st3_identity_referees_convention.
    """
    g = group or AlternatingGroup4()
    n = len(sectors)
    order = len(g.elements)
    S = [[0j] * n for _ in range(n)]
    for i, A in enumerate(sectors):
        for j, B in enumerate(sectors):
            pref = (len(A.flux_class) * len(B.flux_class)) / order**2
            total = 0j
            for x in g.elements:
                xbxinvgx = g.multiply(g.multiply(x, B.representative), g.inverse(x))  # x b x^-1
                f1 = A.chi(xbxinvgx).conjugate()
                if f1 == 0:
                    continue
                xinvgx = g.multiply(g.multiply(g.inverse(x), A.representative), x)  # x^-1 a x
                total += f1 * B.chi(xinvgx).conjugate()
            S[i][j] = pref * total
    return S


def t_matrix(sectors):
    """theta_{(C,A)} = chi_A(a)/dim(A): self-Aharonov-Bohm twist."""
    return [s.character[s.representative] / s.dimension for s in sectors]


def charge_conjugation(sectors, group: Optional[Group] = None) -> List[int]:
    """Permutation a -> abar = ([a^-1], conjugate character)."""
    g = group or AlternatingGroup4()
    out = []
    for s in sectors:
        inv_rep = g.inverse(s.representative)
        conj_char = {x: v.conjugate() for x, v in s.character.items()}

        def same_character(t):
            if set(t.character) != set(conj_char):
                return False
            return all(abs(t.character[x] - v) < TOL for x, v in conj_char.items())

        match = [
            t for t in sectors
            if t.flux_class == frozenset(g.conjugacy_class(inv_rep)) and same_character(t)
        ]
        assert len(match) == 1, f"charge conjugation of {s} ambiguous or missing"
        out.append(sectors.index(match[0]))
    return out


def fusion_coefficients(S):
    """Verlinde: N^c_ab = sum_x S*_{cx} S_{ax} S_{bx} / S_{0x}. Returns N[c][a][b] ints."""
    n = len(S)
    N = [[[0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                val = sum(
                    S[c][x].conjugate() * S[a][x] * S[b][x] / S[0][x] for x in range(n)
                )
                N[c][a][b] = _round_int(val)
    return N


# --------------------------------------------------------------------------- flux-level class algebra

def class_algebra_product(sectors, group: Optional[Group] = None):
    """Structure constants of the conjugacy-class algebra: [Ci][Cj] = sum_k K[i][j][k] Ck.

    K[i][j][k] = #{(p,q) in Ci x Cj : p q = z} for a fixed z in Ck (class-algebra standard).
    Computed from the 14 sectors' flux classes so it stays tied to the category objects.
    """
    g = group or AlternatingGroup4()
    classes = [frozenset(c) for c in g.conjugacy_classes()]
    n = len(classes)
    K = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            ci, cj = sorted(classes[i]), sorted(classes[j])
            products = [g.multiply(p, q) for p in ci for q in cj]
            counts = []
            for k in range(n):
                z = sorted(classes[k])[0]
                counts.append(products.count(z))
            K[i][j] = tuple(counts)
    return K


# --------------------------------------------------------------------------- report

def sector_report(group: Optional[Group] = None) -> Dict[str, object]:
    """Everything at once, for tests and REPL inspection."""
    g = group or AlternatingGroup4()
    sectors = double_sectors(g)
    S = s_matrix(sectors, g)
    T = t_matrix(sectors)
    N = fusion_coefficients(S)
    Cc = charge_conjugation(sectors, g)
    d = quantum_dimensions(sectors)
    return {
        "sectors": sectors, "S": S, "T": T, "N": N, "charge_conj": Cc,
        "quantum_dims": d, "total_quantum_dim_sq": sum(x * x for x in d),
        "class_algebra": class_algebra_product(sectors, g),
    }
