"""Representation theory of A4: primitive quantum sectors from the kernel side.

The specification's quantum structure (Prompt.txt): the residual gauge group preserving a
boundary charge is the centralizer H = C_G(q); internal resolutions form a representation
of H; decomposing into irreducibles gives PRIMITIVE QUANTUM SECTORS; interactions combine
representation spaces by tensor product, and allowed outcomes are the SINGLET sectors
(invariant couplings).  This module supplies exactly that machinery for A4 -- pure kernel
algebra (no RNG, no scheduler), verified against the orthogonality theorems.

Construction (coordinate-free, matching the theory's own tetrahedral geometry):

* V4 = {e} u {order-2 elements} is normal in A4 with quotient Z3; the three 1D irreps
  chi_0, chi_1, chi_2 are omega^{k * phi(g)} where phi: A4 -> Z3 is the abelianization
  map and omega = exp(2 pi i / 3).  phi is DERIVED (membership in cosets of V4) and its
  homomorphism property is asserted by tests, so no convention is smuggled in.
* The 3D irrep is the permutation action on R^4 modulo the diagonal -- the SAME quotient
  W = R^4 / R(1,1,1,1) that selects 3D geometry in the theory.  Its character needs no
  matrices: chi_3(g) = fix(g) - 1 (permutation trace minus the trivial summand).

Verified identities (tests): row/column orthogonality of the character table, sum of
squared dimensions = |G|, chi_3 values (3, -1, 0, 0), and the fusion rules
    3 x 3 = 1 + 1' + 1'' + 2*3        (9 = 1+1+1+6)
    1_i x 1_j = 1_{i+j mod 3}         (the Z3 phase arithmetic of the spec)
Singlet count of a product = multiplicity of the trivial irrep = dimension of the
invariant subspace = number of allowed interaction outcomes.
"""

from __future__ import annotations

import cmath
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .groups import AlternatingGroup4

__all__ = ["Irrep", "a4_irreps", "inner_product", "tensor_characters", "decompose", "singlet_count"]

OMEGA = cmath.exp(2j * cmath.pi / 3)


@dataclass(frozen=True)
class Irrep:
    """An irreducible representation by name and character-on-elements."""

    name: str
    dimension: int
    character: Tuple[complex, ...]  # aligned with group.elements order

    def value_at(self, index: int) -> complex:
        return self.character[index]


def _v4_subgroup(g):
    e = g.identity()
    out = {e}
    for x in g.elements:
        if x != e and g.order_of(x) == 2:
            out.add(x)
    # close under multiplication (it is V4, but verify rather than assume)
    for a in list(out):
        for b in list(out):
            out.add(g.multiply(a, b))
    return frozenset(out)


def _abelianization_map(g):
    """phi: A4 -> Z3 with kernel V4.  Cosets identified empirically; homomorphism asserted."""
    v4 = _v4_subgroup(g)
    elements = list(g.elements)
    # find a 3-cycle and its square's coset to fix the +1/-1 convention consistently:
    sample3 = next(x for x in elements if g.order_of(x) == 3)
    coset_plus = frozenset(g.multiply(v, sample3) for v in v4)
    coset_sq = frozenset(g.multiply(v, g.multiply(sample3, sample3)) for v in v4)

    def phi(x):
        if x in v4:
            return 0
        if x in coset_plus:
            return 1
        if x in coset_sq:
            return 2
        raise AssertionError("abelianization: element outside all cosets")

    for a in elements:
        for b in elements:
            assert phi(g.multiply(a, b)) == (phi(a) + phi(b)) % 3, "phi is not a homomorphism"
    return phi


def a4_irreps():
    """The four irreps of A4: three 1D phase characters and the defining 3D one."""
    g = AlternatingGroup4()
    elements = list(g.elements)
    phi = _abelianization_map(g)

    def fix_count(p):
        return sum(1 for i, image in enumerate(p) if image == i)

    irreps: List[Irrep] = []
    for k in range(3):
        name = "1" if k == 0 else ("1'" if k == 1 else "1''")
        character = tuple(OMEGA ** (k * phi(x)) for x in elements)
        irreps.append(Irrep(name=name, dimension=1, character=character))
    chi3 = tuple(float(fix_count(x) - 1) for x in elements)
    irreps.append(Irrep(name="3", dimension=3, character=chi3))
    return g, tuple(irreps)


def inner_product(g, chi_a, chi_b) -> complex:
    """Standard Hermitian inner product over the group."""
    n = len(g.elements)
    return sum(a * b.conjugate() for a, b in zip(chi_a, chi_b)) / n


def tensor_characters(irreps, i: int, j: int):
    """Pointwise product: the character of rho_i (x) rho_j."""
    return tuple(a * b for a, b in zip(irreps[i].character, irreps[j].character))


def decompose(g, irreps, chi) -> Dict[str, int]:
    """Expand a character into irreducible multiplicities (exact integer rounding)."""
    out: Dict[str, int] = {}
    for irrep in irreps:
        multiplicity = inner_product(g, chi, irrep.character)
        assert abs(multiplicity.imag) < 1e-9, "non-real multiplicity: input is not a character?"
        rounded = round(multiplicity.real)
        assert abs(multiplicity.real - rounded) < 1e-9, "non-integer multiplicity"
        if rounded:
            out[irrep.name] = rounded
    return out


def singlet_count(g, irreps, i: int, j: int) -> int:
    """Number of invariant couplings (singlets) in rho_i (x) rho_j -- allowed outcomes."""
    chi = tensor_characters(irreps, i, j)
    trivial = next(r for r in irreps if r.name == "1")
    multiplicity = inner_product(g, chi, trivial.character)
    return round(multiplicity.real)
