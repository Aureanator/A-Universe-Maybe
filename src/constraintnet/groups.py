"""Finite group engine for the constraint-network simulator.

The fundamental variables of the simulation are labels on *oriented* edges taking
values in a finite group :math:`G`.  Nothing else about the group is assumed by the
rest of the package beyond the small interface defined here:

    identity, multiply, inverse, generators, conjugacy class, equality

Two implementations ship in this module:

``CyclicGroup(3)``
    :math:`\\mathbb{Z}_3` -- additive, abelian, used as the cheap test group.
``AlternatingGroup4()``
    :math:`A_4` -- the orientation-preserving symmetry group of the tetrahedron,
    12 elements, four conjugacy classes (identity / order-2 / order-3+ / order-3-).

Conventions
-----------
* Elements are plain hashable Python objects (``int`` for :math:`\\mathbb{Z}_n`,
  tuples for permutations), so equality is ``==``.
* ``multiply(a, b)`` means "then" composition in the sense ``(a*b)(x) = a(b(x))``
  for permutation groups.  Products around a loop are taken **left to right in
  traversal order**; this convention is used consistently everywhere and is
  documented in ``docs/CONVENTIONS.md``.
* Conjugation is :math:`x \\mapsto g^{-1} x g`, matching the gauge transformation
  :math:`A_{AB} \\to \\lambda_A^{-1} A_{AB} \\lambda_B`.
"""

from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from collections import deque

__all__ = ["Group", "CyclicGroup", "AlternatingGroup4", "get_group"]


# --------------------------------------------------------------------------- #
# permutation helpers (tuples: p maps i -> p[i])
# --------------------------------------------------------------------------- #
def perm_multiply(p, q):
    """Return ``p o q``, i.e. ``(p*q)(i) == p[q[i]]``."""
    return tuple(p[q[i]] for i in range(len(q)))


def perm_inverse(p):
    inv = [0] * len(p)
    for i, value in enumerate(p):
        inv[value] = i
    return tuple(inv)


def perm_sign(p) -> int:
    """+1 for even, -1 for odd permutations (inversion count)."""
    inversions = 0
    n = len(p)
    for i in range(n):
        pi = p[i]
        for j in range(i + 1, n):
            if pi > p[j]:
                inversions += 1
    return -1 if inversions % 2 else 1


def perm_cycles(p):
    """Return the disjoint cycle decomposition as a list of tuples."""
    seen = [False] * len(p)
    cycles = []
    for start in range(len(p)):
        if seen[start]:
            continue
        cycle, current = [], start
        while not seen[current]:
            seen[current] = True
            cycle.append(current)
            current = p[current]
        if len(cycle) > 1:
            cycles.append(tuple(cycle))
    return cycles


# --------------------------------------------------------------------------- #
# abstract interface
# --------------------------------------------------------------------------- #
class Group(ABC):
    """Abstract finite group.

    Subclasses implement the five primitives named in the specification; every
    other operation is derived here so that physics code never has to care which
    concrete group it is running on.
    """

    name: str = "group"

    # ------------------------------------------------------------------ core
    @property
    @abstractmethod
    def elements(self) -> tuple:
        """All group elements, in a deterministic order."""

    @abstractmethod
    def identity(self):
        """The identity element ``e``."""

    @abstractmethod
    def multiply(self, a, b):
        """Group product ``a * b``."""

    @abstractmethod
    def inverse(self, a):
        """Inverse of ``a``."""

    @abstractmethod
    def generators(self) -> tuple:
        """A small generating set (used for moves and word-length costs)."""

    # ---------------------------------------------------------------- derived
    def order(self) -> int:
        return len(self.elements)

    def equals(self, a, b) -> bool:
        return a == b

    def is_abelian(self) -> bool:
        cached = getattr(self, "_abelian", None)
        if cached is None:
            elems = self.elements
            cached = all(
                self.multiply(a, b) == self.multiply(b, a)
                for a in elems
                for b in elems
            )
            self._abelian = cached
        return cached

    def conjugate(self, g, x):
        """``g^{-1} x g`` -- the gauge action on a holonomy."""
        return self.multiply(self.multiply(self.inverse(g), x), g)

    def conjugacy_class(self, a) -> frozenset:
        """The full conjugacy class of ``a`` (gauge-invariant 'type' of a charge)."""
        cached = getattr(self, "_classes_by_element", None)
        if cached is not None and a in cached:
            return cached[a]
        return frozenset(self.conjugate(g, a) for g in self.elements)

    def conjugacy_classes(self) -> tuple:
        """All conjugacy classes, ordered by first appearance in ``elements``."""
        cached = getattr(self, "_classes", None)
        if cached is not None:
            return cached
        index = {element: i for i, element in enumerate(self.elements)}
        remaining = set(self.elements)
        classes = []
        lookup = {}
        while remaining:
            representative = min(remaining, key=lambda e: index[e])
            cls = self.conjugacy_class(representative)
            classes.append(cls)
            for element in cls:
                lookup[element] = cls
            remaining -= cls
        self._classes = tuple(classes)
        self._classes_by_element = lookup
        return self._classes

    def class_of(self, a):
        """The conjugacy class containing ``a`` (same object identity as in
        :meth:`conjugacy_classes`)."""
        self.conjugacy_classes()  # populate caches
        return self._classes_by_element[a]

    def centralizer(self, a) -> frozenset:
        """``{g : g^{-1} a g == a}`` -- the residual gauge group preserving ``a``."""
        return frozenset(g for g in self.elements if self.conjugate(g, a) == a)

    def order_of(self, a) -> int:
        element = self.identity()
        for step in range(1, self.order() + 2):
            element = self.multiply(element, a)
            if element == self.identity():
                return step
        raise ArithmeticError(f"element {a!r} did not close within group order")

    # ------------------------------------------------------- word metric/cost
    def move_generators(self) -> tuple:
        """Generators together with their inverses -- the elementary relabelling steps.

        Both directions are included so that the word metric is symmetric and so that a
        single move can step in either direction along a Cayley-graph edge.
        """
        out = []
        for g in self.generators():
            inv = self.inverse(g)
            for candidate in (g, inv):
                if candidate != self.identity():
                    out.append(candidate)
        return tuple(dict.fromkeys(out)) or (self.identity(),)

    def word_lengths(self) -> dict:
        """BFS distance from the identity using :meth:`move_generators`.

        This is the prototype cost function: ``word_length(g)`` is the minimum
        number of generator multiplications needed to implement the relabelling
        ``x -> x g``.  It becomes the mass/inertia proxy in module 9.
        """
        cached = getattr(self, "_word_lengths", None)
        if cached is not None:
            return cached
        steps = self.move_generators()
        start = self.identity()
        distances = {start: 0}
        frontier = deque([start])
        while frontier:
            current = frontier.popleft()
            for step in steps:
                nxt = self.multiply(current, step)
                if nxt not in distances:
                    distances[nxt] = distances[current] + 1
                    frontier.append(nxt)
        if len(distances) != self.order():
            raise ValueError(
                f"generators {self.generators()} of {self.name} do not generate the group "
                f"(reached {len(distances)} of {self.order()} elements)"
            )
        self._word_lengths = distances
        return distances

    def word_length(self, g) -> int:
        return self.word_lengths()[g]

    # ------------------------------------------------------------- factories
    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{type(self).__name__} {self.name} order={self.order()}>"


# --------------------------------------------------------------------------- #
# Z_n
# --------------------------------------------------------------------------- #
class CyclicGroup(Group):
    r""":math:`\mathbb{Z}_n` written additively; elements are ``0 .. n-1``."""

    def __init__(self, n: int = 3, generator: int | None = None):
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n
        self.name = f"Z{n}"
        self._elements = tuple(range(n))
        if generator is None:
            # smallest k generating Z_n, i.e. gcd(k, n) == 1
            generator = next((k for k in range(1, n) if _gcd(k, n) == 1), 0)
        self._generator = generator % n

    @property
    def elements(self) -> tuple:
        return self._elements

    def identity(self):
        return 0

    def multiply(self, a, b):
        return (a + b) % self.n

    def inverse(self, a):
        return (-a) % self.n

    def generators(self) -> tuple:
        return (self._generator,)

    def conjugacy_class(self, a) -> frozenset:
        # abelian: classes are singletons; override for speed
        return frozenset({a})


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


# --------------------------------------------------------------------------- #
# A_4
# --------------------------------------------------------------------------- #
class AlternatingGroup4(Group):
    r"""``A_4`` -- even permutations of four objects, 12 elements.

    Elements are tuples ``p`` with the meaning ``i -> p[i]`` on ``{0,1,2,3}``.
    The conjugacy classes are computed by brute force and come out as

    ================  ======  ==========================================
    class             size    meaning
    ================  ======  ==========================================
    ``{e}``           1       identity
    double transpos.  3       order 2, the Klein four group minus identity
    3-cycles (+)      4       order 3, positive orientation
    3-cycles (-)      4       order 3, negative orientation
    ================  ======  ==========================================

    The ``+``/``-`` split of the eight order-3 elements is *not* imposed; it falls
    out of conjugation by even permutations only.  We label the class containing
    ``(0 1 2)`` as positive for reproducibility.
    """

    IDENTITY = (0, 1, 2, 3)
    # s = (0 1)(2 3), t = (0 1 2): presentation <s,t | s^2 = t^3 = (st)^3 = e>
    DEFAULT_GENERATORS = ((1, 0, 3, 2), (1, 2, 0, 3))

    def __init__(self, generators=None):
        self.name = "A4"
        self._elements = tuple(
            sorted(p for p in itertools.permutations(range(4)) if perm_sign(p) == 1)
        )
        self._generators = tuple(generators) if generators else self.DEFAULT_GENERATORS

    @property
    def elements(self) -> tuple:
        return self._elements

    def identity(self):
        return self.IDENTITY

    def multiply(self, a, b):
        return perm_multiply(a, b)

    def inverse(self, a):
        return perm_inverse(a)

    def generators(self) -> tuple:
        return self._generators

    # ---- human-readable class names (used in reports and tests) -----------
    def class_name(self, a) -> str:
        cls = self.class_of(a)
        if cls == self.class_of(self.IDENTITY):
            return "identity"
        sample_order = self.order_of(next(iter(cls)))
        if sample_order == 2:
            return "order-2 (double transposition)"
        positive_class = self.class_of((1, 2, 0, 3))  # the class of (0 1 2)
        if cls is positive_class or cls == positive_class:
            return "order-3 (+)"
        return "order-3 (-)"

    def format(self, a) -> str:  # pragma: no cover - cosmetic
        cycles = perm_cycles(a)
        if not cycles:
            return "e"
        return "".join("(" + " ".join(str(c + 1) for c in cycle) + ")" for cycle in cycles)


_REGISTRY = {
    "Z2": lambda: CyclicGroup(2),
    "Z3": lambda: CyclicGroup(3),
    "Z4": lambda: CyclicGroup(4),
    "A4": AlternatingGroup4,
}


def get_group(spec) -> Group:
    """Return a group instance from a name (``"Z3"``, ``"A4"``) or a :class:`Group`."""
    if isinstance(spec, Group):
        return spec
    key = str(spec).strip()
    for name, factory in _REGISTRY.items():
        if name.lower() == key.lower():
            return factory()
    raise KeyError(f"unknown group {spec!r}; known: {sorted(_REGISTRY)}")
