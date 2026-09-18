"""P1 — internal-resolution counts under THREE equivalence relations, cone v * d(Delta^3), A4.

Referee item 1 claims ``resolutions.py`` inflates |I| by up to 12x because the quotient
freezes boundary vertices (apex-only gauge).  This probe measures, for declared flux
patterns on the cone:

* raw   : admissible interiors x, no quotient;
* rigid : apex-only gauge  x_i -> nu^-1 x_i, boundary labels held POINTWISE
          (the current ``resolutions.py`` convention -- boundary as fixed apparatus);
* full  : vertex gauge over ALL five vertices (boundary vertices transform too), i.e.
          orbits of admissible pairs (B, x) under the genuine gauge group; this is what
          "|I| when only the boundary's gauge-invariant content is fixed" means --
          the referee's mu taken in its strongest coherent form.

If full << rigid on patterns with nontrivial flux, the inflation critique reproduces and
the convention must be stated everywhere |I| is quoted.  Pre-registered docs/PREDICTIONS.md P1.
"""

from __future__ import annotations

import itertools
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.groups import AlternatingGroup4, CyclicGroup  # noqa: E402

G = AlternatingGroup4()
ELEMENTS = list(G.elements)
N = len(ELEMENTS)
IDX = {g: i for i, g in enumerate(ELEMENTS)}
E_IDX = IDX[G.identity()]

MUL = [[IDX[G.multiply(a, b)] for b in ELEMENTS] for a in ELEMENTS]
INV = [IDX[G.inverse(a)] for a in ELEMENTS]
CONJ = [[MUL[MUL[INV[m]][x]][m] for x in range(N)] for m in range(N)]

CLASSES = list(G.conjugacy_classes())
CLASS_OF = [next(i for i, c in enumerate(CLASSES) if g in c) for g in ELEMENTS]
V4_CLASS = next(i for i, c in enumerate(CLASSES) if {G.order_of(x) for x in c} == {2})

BORDER = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]   # boundary edges, stored i<j
APEX = 4
CONE_EDGES = BORDER + [(min(APEX, v), max(APEX, v)) for v in range(4)]  # last four: (0,4)..(3,4)
POS = {e: k for k, e in enumerate(CONE_EDGES)}
B_FACES = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def store(i, j):
    """Index into the label tuple for edge {i,j} (stored with ascending endpoints)."""
    return POS[(min(i, j), max(i, j))]


def oriented(L, i, j):
    """Label of edge i->j from stored ascending labels L."""
    g = L[store(i, j)]
    return g if i < j else INV[g]


def face_hol(L, i, j, k):
    return MUL[MUL[oriented(L, i, j)][oriented(L, j, k)]][oriented(L, k, i)]


def gauged(L, lam):
    """Apply vertex gauge lambda (list of 5 indices): A_ij -> lam_i^-1 A_ij lam_j."""
    out = []
    for (i, j) in CONE_EDGES:
        a = oriented(L, i, j)
        g = MUL[MUL[INV[lam[i]]][a]][lam[j]]
        # store with ascending orientation
        out.append(g if i < j else INV[g])
    return tuple(out)


def pair_tables(B):
    T = []
    for (i, j) in BORDER:
        a_ij = oriented(B, i, j)
        T.append([[CLASS_OF[MUL[MUL[a][a_ij]][INV[b]]] for b in range(N)] for a in range(N)])
    return T


def admissible(B, allowed):
    """x with interior-face curvature class == allowed[k] on each cone face over edge k."""
    T = pair_tables(B)
    p01, p02, p12 = store(0, 1), store(0, 2), store(1, 2)
    sols = []
    for x0 in range(N):
        for x1 in range(N):
            if T[0][x0][x1] != allowed[p01]:
                continue
            for x2 in range(N):
                if T[1][x0][x2] != allowed[p02] or T[3][x1][x2] != allowed[p12]:
                    continue
                for x3 in range(N):
                    if (T[2][x0][x3] == allowed[store(0, 3)]
                            and T[4][x1][x3] == allowed[store(1, 3)]
                            and T[5][x2][x3] == allowed[store(2, 3)]):
                        sols.append((x0, x1, x2, x3))
    return sols


def full_labels(B6, x):
    """Full 10-edge label tuple: boundary B6 (6 entries) + apex edges x_0..x_3."""
    return tuple(B6) + tuple(x)


def rigid_count(sols):
    reps = set()
    for x in sols:
        best = min(tuple(CONJ[m][xi] for xi in x) for m in range(N))
        reps.add(best)
    return len(reps)


def appearance_of(L):
    """Boundary face curvature classes -- the gauge-invariant content an outsider sees."""
    return tuple(CLASS_OF[face_hol(L, *f)] for f in B_FACES)


def full_gauge_count(B6, sols, allowed=None):
    """Orbits of admissible (B, x) under the FULL vertex-gauge group A4^5.

    Canonical form = min over gauges of (appearance-canonicalised boundary classes are
    implicit; we canonicalise the whole label tuple).  Cost: |sols| * 12^5 worst case --
    callers keep declaration families small or sample.
    """
    reps = set()
    lams = list(itertools.product(range(N), repeat=5))
    for x in sols:
        L0 = full_labels(B6, x)
        best = None
        for lam in lams:
            cand = gauged(L0, lam)
            if best is None or cand < best:
                best = cand
        reps.add(best)
    return len(reps)


def main():
    t0 = time.time()
    B_flat = tuple([E_IDX] * 6)

    print("class ids:", {i: (len(c), sorted({G.order_of(x) for x in c})) for i, c in enumerate(CLASSES)})

    # ---- Klein-four family on the flat boundary --------------------------------------
    for nflux in range(1, 7):
        # declare class V4 on interior faces over the first `nflux` boundary edges
        decl = [0] * 6
        for k in range(nflux):
            decl[store(*BORDER[k])] = V4_CLASS
        sols = admissible(B_flat, decl)
        if not sols:
            print(f"{nflux} order-2 face(s): raw=0")
            continue
        nr = rigid_count(sols)
        nf = full_gauge_count(B_flat, sols) if len(sols) <= 400 else float("nan")
        print(f"declaration: {nflux} V4 face(s)/rest flat -> raw={len(sols):5d} rigid={nr:3d} full-gauge={nf}")

    # ---- census over tree-gauge boundaries, seeded declaration -------------------------
    rows = []
    for a12, a13, a23 in itertools.product(range(N), repeat=3):
        B = (E_IDX, E_IDX, E_IDX, a12, a13, a23)
        # seeded declaration: classes seen with identity interior
        L0 = full_labels(B, tuple([E_IDX] * 4))
        decl = []
        for (i, j) in BORDER:
            c = MUL[MUL[oriented(L0, APEX, i)][oriented(L0, i, j)]][oriented(L0, j, APEX)]
            decl.append(CLASS_OF[c])
        sols = admissible(B, decl)
        rows.append((B, len(sols), rigid_count(sols) if sols else 0))

    with_sol = [r for r in rows if r[1]]
    print(f"\nboundaries: {len(rows)} (with solutions: {len(with_sol)})")
    print("rigid |I| histogram:", dict(sorted(Counter(r[2] for r in with_sol).items())))

    # full-gauge counts on a sample of boundaries (cost guard)
    import random as _r
    rng = _r.Random(11)
    sample = rng.sample(with_sol, 40)
    collapses = []
    for B, nsol, nr in sample:
        sols = admissible(B, seeded_decl(B))
        nf = full_gauge_count(B, sols) if len(sols) <= 600 else None
        if nf is not None:
            collapses.append((nr, nf, nsol))
    hist_pair = Counter((a, b) for a, b, _ in collapses)
    print("sampled (rigid -> full-gauge) pairs:", dict(sorted(hist_pair.items())))

    z3 = CyclicGroup(3)
    print(f"\nZ3 control: {len(list(z3.conjugacy_classes()))} singleton classes => gauge action trivial"
          f" => all three counts coincide up to |G| factors; control blind by construction")
    print(f"elapsed {time.time() - t0:.1f}s")


def seeded_decl(B):
    L0 = full_labels(B, tuple([E_IDX] * 4))
    decl = []
    for (i, j) in BORDER:
        c = MUL[MUL[oriented(L0, APEX, i)][oriented(L0, i, j)]][oriented(L0, j, APEX)]
        decl.append(CLASS_OF[c])
    return decl


if __name__ == "__main__":
    main()
